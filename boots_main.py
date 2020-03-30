from __future__ import unicode_literals
from __future__ import absolute_import
import os
import sys
import webapp2
import json
import time
from google.appengine.ext import ndb
from google.appengine.api import app_identity
from google.appengine.api import urlfetch

import urllib
cwd = os.getcwd()
sys.path.insert(0,'includes')
from datavalidation import DataValidation
from GCP_return_codes import FunctionReturnCodes as RC
from firebase_updater import FirebaseUpdater
from p1_services import Services
from p1_services import TaskArguments
from error_handling import RDK
from error_handling import ErrorFunctions as EF
from task_queue_functions import TaskQueueFunctions


app_id = unicode(app_identity.get_application_id()).lower()

global FIREBASE_URL
global FIREBASE_KEY
global FIREBASE_DOMAIN
global FIREBASE_ID
FIREBASE_URL = unicode(os.environ.get('FIREBASE_URL'))
FIREBASE_KEY = unicode(os.environ.get('FIREBASE_KEY'))
FIREBASE_DOMAIN = unicode(os.environ.get('FIREBASE_DOMAIN'))
FIREBASE_ID = int(os.environ.get('FIREBASE_ID'))

DEV_FLAG = ""
   
        
class PushFirebaseChange(webapp2.RequestHandler,DataValidation):
    def post(self):
        task_id = "user-interface-tx:PushFirebaseChange:post"
        debug_data = []
        call_result = self.__ProcessPushTask()
        debug_data.append(call_result)
        
        params= {}
        for key in self.request.arguments():
            params[key] = self.request.get(key,None)
        task_functions = TaskQueueFunctions()
                        
        if call_result['success'] != True:            
            
            task_functions.logError(call_result['success'],task_id, params, self.request.get('X-AppEngine-TaskName',None), self.request.get('transaction_id',None), call_result['return_msg'], debug_data, self.request.get('transaction_user_uid',None))
            task_functions.logTransactionFailed(self.request.get('transaction_id',None), call_result['success'])
            
            if call_result['success'] == RC.failed_retry:
                self.response.set_status(500)
            elif call_result['success'] == RC.input_validation_failed:
                self.response.set_status(200)
            elif call_result['success'] == RC.ACL_check_failed:
                self.response.set_status(200)
            else:
                self.response.set_status(200)
            return
        
    ## go to the next function
        task_functions = TaskQueueFunctions()       
        #just a place holder since this task doesn't create results
        task_results = {}
        #most requests to this function are single tasks requests and we have to have a delay so the created transaction record exists so we can succuessfully delete it
        time.sleep(1)
        call_result = task_functions.nextTask(task_id,task_results,params)
        debug_data.append(call_result)
        if call_result['success'] != True:
            task_functions.logError(call_result['success'],task_id, params, self.request.get('X-AppEngine-TaskName',None), self.request.get('transaction_id',None), call_result['return_msg'], debug_data, self.request.get('transaction_user_uid',None))
    ##</end> go to the next function
        self.response.set_status(200)
            
    
    def __ProcessPushTask(self):
        return_msg = "PushFirebaseChange:__processPushTask "
        task_id = "user-interface-tx:PushFirebaseChange:__processPushTask"
        call_result = {}
        debug_data = []
        task_results = {}
        global FIREBASE_URL
        global FIREBASE_KEY
        global FIREBASE_DOMAIN
        global FIREBASE_ID

    ## verify input data we can skip verifying fields since the WatchdogFirebase class will
        try:
            fields = json.JSONDecoder().decode(self.request.get( TaskArguments.s8t3_fields))
        except Exception as e:
            return_msg += "exception when decoding json data. exception:%s" % e
            return {'success': RC.input_validation_failed,'return_msg':return_msg,'debug_data':debug_data, 'task_results': task_results}

        call_result = self.checkValues([[fields,True,list,'firebase_instruction',"len1"]
                                      ])
        debug_data.append(call_result)
        if call_result['success'] != True:
            return_msg += "input validation failed"
            return {'success': RC.input_validation_failed,'return_msg':return_msg,'debug_data':debug_data}
    ##</end> verify input data we can skip verifying fields since the WatchdogFirebase class will   


        fb_update = FirebaseUpdater()
        call_result = fb_update.initialize(FIREBASE_URL, FIREBASE_KEY, FIREBASE_DOMAIN, FIREBASE_ID)
        debug_data.append(call_result)
        if call_result['success'] != True:
            return_msg += "failed to initialize firebase updater classs"
            return {'success': call_result['success'],'return_msg':return_msg,'debug_data':debug_data, 'task_results': task_results}
      
        call_result = fb_update.process_request(fields)
        debug_data.append(call_result)
        if call_result['success'] != True:
            return_msg += "failed to update or delete firebase entry"
            return {'success': call_result['success'],'return_msg':return_msg,'debug_data':debug_data, 'task_results': task_results}

        return {'success': RC.success,'return_msg':return_msg,'debug_data':debug_data, 'task_results': task_results}


    
app = webapp2.WSGIApplication([
    (Services.firebase_replication.push_firebase_change.url,PushFirebaseChange),
    (Services.firebase_replication.push_mass_firebase_changes.url,PushFirebaseChange),
], debug=True)
