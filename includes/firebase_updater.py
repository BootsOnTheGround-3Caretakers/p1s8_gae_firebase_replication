#currently no auth
from __future__ import unicode_literals
from __future__ import absolute_import
from google.appengine.ext import vendor
vendor.add('lib')
import sys
sys.path.insert(0,'lib')
sys.path.insert(0,'lib/python-firebase-gae-1.0.1')
from firebase import firebase
#firebasedb = firebase.FirebaseApplication('https://watchdog-user-interface.firebaseio.com') 
from datavalidation import DataValidation
from GCP_return_codes import FunctionReturnCodes as RC

class FirebaseUpdater(DataValidation):

    def initialize(self,firebase_url=None,firebase_key=None,auth_domain=None,firebase_id=None):
        call_result = {}
        return_msg = "firebase_manager:initialize "
        debug_data = []
        
        ## input validation
        call_result = self.checkValues([[firebase_url,True,unicode,"len>10"],
                                        [firebase_key,True,unicode,"len>1"],
                                        [auth_domain,True,unicode,"len>10"],
                                        [firebase_id,True,long]
                                        ])
        debug_data.append(call_result)
        if call_result['success'] != True:
            return_msg += "input validation failed"
            return {'success': RC.input_validation_failed,'return_msg':return_msg,'debug_data':debug_data}
        ##</end> input validation
        
        try:
            self.firebasedb = firebase.FirebaseApplication(firebase_url, authentication=None)
            authentication = firebase.FirebaseAuthentication(firebase_key, auth_domain, extra={'id': firebase_id})
            self.firebasedb.authentication = authentication
        except Exception as e:
            return_msg += "failed to connect to firebase with exception:%s" % unicode(e)
            return {'success': RC.failed_retry,'return_msg':return_msg,'debug_data':debug_data}
        
        
        return {'success': RC.success,'return_msg':return_msg,'debug_data':debug_data}
             
    
    def process_request(self,fields=None):
        '''
        PURPOSE:    process data recieved from post
        PARAMETERS: fields
        RETURNS:    dict : {'success': bool,'return_msg':return_msg,'debug_data':debug_data}
        '''
        debug_data = []
        return_msg = "update_firebase:__process_request "
    ## input validation
    
        call_result = self.checkValues([[fields,True,list,'firebase_instruction',"len1"]
                                      ])
        debug_data.append(call_result)
        if call_result['success'] != True:
            return_msg += "input validation failed"
            return {'success': RC.input_validation_failed,'return_msg':return_msg,'debug_data':debug_data}
    ##</end> input validation
    
    
    #write new entity if function is 'update'; delete entity if function is 'delete'
        for item in fields:
            if 'delete' in item['function']:
                call_result = self.delete_data(item['id'], item['key'])
                debug_data.append(call_result)
            elif 'update' in item['function']:
                call_result = self.send_data(item['id'], item['key'], item['value'])
                debug_data.append(call_result)
            elif 'append' in item['function']:
                call_result = self.get_data(item['id'], item['key'])
                debug_data.append(call_result)
                if call_result['success'] == True:
                    existing_data = unicode(call_result['result'])
                    #only put the last 10000 characters in firebase
                    new_data = existing_data + item['value']
                    if len(new_data) > 10000:
                        new_data = new_data[len(new_data) - 10000:]
                    call_result = self.send_data(item['id'], item['key'], new_data)
                    debug_data.append(call_result)
    ##</end> write new entry
    
        for result in debug_data:
            if result['success'] != True:
                return_msg += 'Failed to delete or update entry in firebase DB'
                return {'success': RC.failed_retry,'return_msg':return_msg,'debug_data':debug_data}
            
            
        return {'success': RC.success,'return_msg':return_msg,'debug_data':debug_data}




    def send_data(self,path,key,value):
        '''
        PURPOSE:    send data to the database
        PARAMETERS: path : REST path to get to key
                    key : reference to the values to send
                    value : value of the key item to send
        RETURNS:    dict : {'success': bool,'return_msg':return_msg,'debug_data':debug_data}
        '''
        send_result = None
        return_msg = "firebase_manager:send_data"
        debug_data = []
        #write new entity, currently no authentication
        if '.' in key:
            key = unicode(str(key).replace('.','\\'))
        
        try:
            send_result = self.firebasedb.put(path,key,value)
        except Exception as e:
            return_msg += 'exception occurred sending data to  firebase db. exception:%s' % unicode(e)
            return {'success': False,'return_msg':return_msg,'debug_data':debug_data}
        if send_result == None:
            return_msg += 'Failed to send data to firebase db'
            return {'success': False,'return_msg':return_msg,'debug_data':debug_data}
        return {'success': True,'return_msg':return_msg,'debug_data':debug_data}
    
    
    
    
    def get_data(self,path,key):
        '''
        PURPOSE:    discover if a value exists
        PARAMETERS: path : REST path to get to key
                    key : name of the values to delete
        RETURNS:    dict : {'success': bool,'return_msg':return_msg,'debug_data':debug_data}
        '''
        return_msg = 'firebase_manager:get_data '
        debug_data = []
        if '.' in key:
            key = unicode(str(key).replace('.','\\'))
        try:
            get_result = self.firebasedb.get(path,key)
            return {'success': True,'return_msg':return_msg,'debug_data':debug_data,'result':get_result}
        except Exception as e:
            return_msg += 'exception occurred receiving data to  firebase db. exception:%s' % unicode(e)
            return {'success': False,'return_msg':return_msg,'debug_data':debug_data,'result':get_result}




    def delete_data(self,path,key):
        '''
        PURPOSE:    discover if a value exists
        PARAMETERS: path : REST path to get to key
                    key : name of the values to delete
        RETURNS:    dict : {'success': bool,'return_msg':return_msg,'debug_data':debug_data}
        '''
        return_msg = "firebase_manager:delete_data "
        debug_data = []
        #delete entity, currently no authentication
        call_result =self.checkIfExists(path,key)
        debug_data.append(call_result)
        if call_result['success'] != True:
            return_msg += "failed to check for value : "+key
            return {'success': False,'return_msg':return_msg,'debug_data':debug_data}
        elif not call_result['check_result']:
            #if item is not available to be deleted, objective complete
            return_msg += 'cannot delete '+key+': does not exist in database'
            return {'success': True,'return_msg':return_msg,'debug_data':debug_data}
        
        try:
            self.firebasedb.delete(path,key)
        except Exception as e:
            return_msg += 'exception occurred deleting data from firebase db. exception:%s' % unicode(e)
            return {'success': False,'return_msg':return_msg,'debug_data':debug_data}
        return {'success': True,'return_msg':return_msg,'debug_data':debug_data}
    





    def checkIfExists(self,path,key):
        '''
        PURPOSE:    discover if a value exists
        PARAMETERS: path from root to get to key
        RETURNS:    True if the value is in the database, false if either the check fails to
                    connect to the database or the key is not present in the database
        '''
        return_msg = "firebase_manager:checkIfExists "
        check_result = False
        debug_data = []
        #write new entity, currently no authentication
        try:
            get_result = self.firebasedb.get(path,key)
            check_result = get_result != None
        except Exception as e:
            return_msg += "exception ocurred checking if key exists. exception:%s" % e
            return {'success': False,'return_msg':return_msg,'debug_data':debug_data,'check_result':check_result}
            
        return {'success': True,'return_msg':return_msg,'debug_data':debug_data,'check_result':check_result}
        


