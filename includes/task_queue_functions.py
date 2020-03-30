from __future__ import unicode_literals
import logging
import json
import string
import random
import six
from six import text_type as unicode
from six import integer_types
if len(integer_types) == 1:
    long = integer_types[0]
if six.PY2:
    from urllib import urlencode
    from google.appengine.ext import ndb
    from google.appengine.api import app_identity
    from google.appengine.api import taskqueue
    from google.appengine.api import urlfetch
    try:
        # Only python2 pull worker will be bundled with this package
        from googleapiclient.discovery import build
    except:
        pass
else:
    import os
    import uuid
    from urllib.parse import urlencode
    from google.cloud import ndb, pubsub_v1, tasks_v2
    from google.protobuf import timestamp_pb2
    import requests

    G_region_map = {
        's': 'us-central1',
    }
    G_region = G_region_map[os.environ.get('GAE_APPLICATION').split('~')[0]]

from datetime import datetime, timedelta
from datavalidation import DataValidation
from GCP_return_codes import FunctionReturnCodes as RC

### datastores for logging data

class LogSuccess(ndb.Model):
    task_id=ndb.StringProperty(required=False)
    params=ndb.TextProperty(required=False)
    name=ndb.StringProperty(required=False)
    transaction_id=ndb.StringProperty(required=False)
    error_msg=ndb.StringProperty(required=False)
    debug_data=ndb.TextProperty(required=False)
    transaction_user_uid=ndb.StringProperty(required=False)
    datetime_stamp = ndb.DateTimeProperty(required=False,auto_now_add=True)


class LogGeneralError(ndb.Model):
    task_id=ndb.StringProperty(required=False)
    params=ndb.TextProperty(required=False)
    name=ndb.StringProperty(required=False)
    transaction_id=ndb.StringProperty(required=False)
    error_msg=ndb.StringProperty(required=False)
    debug_data=ndb.TextProperty(required=False)
    transaction_user_uid=ndb.StringProperty(required=False)
    datetime_stamp = ndb.DateTimeProperty(required=False,auto_now_add=True)

class LogFirebaseReplication(ndb.Model):
    task_id=ndb.StringProperty(required=False)
    params=ndb.TextProperty(required=False)
    name=ndb.StringProperty(required=False)
    transaction_id=ndb.StringProperty(required=False)
    error_msg=ndb.StringProperty(required=False)
    debug_data=ndb.TextProperty(required=False)
    transaction_user_uid=ndb.StringProperty(required=False)
    datetime_stamp = ndb.DateTimeProperty(required=False,auto_now_add=True)

class LogDatastoreFailure(ndb.Model):
    task_id=ndb.StringProperty(required=False)
    params=ndb.TextProperty(required=False)
    name=ndb.StringProperty(required=False)
    transaction_id=ndb.StringProperty(required=False)
    error_msg=ndb.StringProperty(required=False)
    debug_data=ndb.TextProperty(required=False)
    transaction_user_uid=ndb.StringProperty(required=False)
    datetime_stamp = ndb.DateTimeProperty(required=False,auto_now_add=True)



class LogSqlFailure(ndb.Model):
    task_id=ndb.StringProperty(required=False)
    params=ndb.TextProperty(required=False)
    name=ndb.StringProperty(required=False)
    transaction_id=ndb.StringProperty(required=False)
    error_msg=ndb.StringProperty(required=False)
    debug_data=ndb.TextProperty(required=False)
    transaction_user_uid=ndb.StringProperty(required=False)
    datetime_stamp = ndb.DateTimeProperty(required=False,auto_now_add=True)




class LogInputValidation(ndb.Model):
    task_id=ndb.StringProperty(required=False)
    params=ndb.TextProperty(required=False)
    name=ndb.StringProperty(required=False)
    transaction_id=ndb.StringProperty(required=False)
    error_msg=ndb.StringProperty(required=False)
    debug_data=ndb.TextProperty(required=False)
    transaction_user_uid=ndb.StringProperty(required=False)
    datetime_stamp = ndb.DateTimeProperty(required=False,auto_now_add=True)



class LogAclCheck(ndb.Model):
    task_id=ndb.StringProperty(required=False)
    params=ndb.TextProperty(required=False)
    name=ndb.StringProperty(required=False)
    transaction_id=ndb.StringProperty(required=False)
    error_msg=ndb.StringProperty(required=False)
    debug_data=ndb.TextProperty(required=False)
    transaction_user_uid=ndb.StringProperty(required=False)
    datetime_stamp = ndb.DateTimeProperty(required=False,auto_now_add=True)



class DeleteTaskLog(ndb.Model):
    task_id=ndb.StringProperty(required=False)
    params=ndb.TextProperty(required=False)
    name=ndb.StringProperty(required=False)
    transaction_id=ndb.StringProperty(required=False)
    error_msg=ndb.StringProperty(required=False)
    debug_data=ndb.TextProperty(required=False)
    transaction_user_uid=ndb.StringProperty(required=False)
    datetime_stamp = ndb.DateTimeProperty(required=False,auto_now_add=True)

class LogQueuing(ndb.Model):
    task_id=ndb.StringProperty(required=False)
    params=ndb.TextProperty(required=False)
    name=ndb.StringProperty(required=False)
    transaction_id=ndb.StringProperty(required=False)
    error_msg=ndb.StringProperty(required=False)
    debug_data=ndb.TextProperty(required=False)
    transaction_user_uid=ndb.StringProperty(required=False)
    datetime_stamp = ndb.DateTimeProperty(required=False,auto_now_add=True)


class LogBillingError(ndb.Model):
    task_id=ndb.StringProperty(required=False)
    params=ndb.TextProperty(required=False)
    name=ndb.StringProperty(required=False)
    transaction_id=ndb.StringProperty(required=False)
    error_msg=ndb.StringProperty(required=False)
    debug_data=ndb.TextProperty(required=False)
    transaction_user_uid=ndb.StringProperty(required=False)
    datetime_stamp = ndb.DateTimeProperty(required=False,auto_now_add=True)



class LogTransactionCreated(ndb.Model):
    params=ndb.TextProperty(required=True)
    transaction_id=ndb.StringProperty(required=True)
    datetime_stamp = ndb.DateTimeProperty(required=False,auto_now_add=True)
    _use_cache = False
    _use_memcache = False
#used to track the active number of transactions
class TransactionFinishedLog(ndb.Model):
    transaction_id=ndb.StringProperty(required=True)
    datetime_stamp = ndb.DateTimeProperty(required=False,auto_now_add=True)
    _use_cache = False
    _use_memcache = False

#used to track the active number of transactions


class LogTransactionFailed(ndb.Model):
    transaction_id=ndb.StringProperty(required=True)
    datetime_stamp = ndb.DateTimeProperty(required=False,auto_now_add=True)
    success_code = ndb.IntegerProperty(required=False)
    _use_cache = False
    _use_memcache = False



class TaskQueueFunctions(DataValidation):
    #~these values matche those in back_end_global_settings.py FunctionReturnCodes
    log_destinations = [[RC.failed_retry,LogGeneralError],
                        [RC.success,LogSuccess],
                        [RC.ACL_check_failed,LogAclCheck],
                        [RC.input_validation_failed,LogInputValidation],
                        [RC.queuing_task_failed,LogQueuing],
                        [RC.firebase_replication_retry,LogFirebaseReplication],
                        [RC.delete_task_failed,DeleteTaskLog],
                        [RC.datastore_failure,LogDatastoreFailure],
                        [RC.sql_failure,LogSqlFailure],
                        [RC.billing_error,LogBillingError]
                        ]


    #~log an error to the transaction-logging service by creating a task in its task_queue.  If this fails it logs the information to the standard error log.
    def logError(self,error_type=None,task_id=None,params=None,name=None,transaction_id=None,error_msg=None,debug_data=None,transaction_user_uid=None):
        error_data = {}

        log_id = None
    ## generate a unique id for this log entry if possible
        if type(transaction_id) == unicode and len(transaction_id) > 20:
            log_id = transaction_id
        elif  type(task_id) == unicode and len(task_id) > 1:
            chars=string.ascii_lowercase + string.ascii_uppercase + string.digits
            log_id = task_id + "-"
            log_id += ''.join(random.choice(chars) for _ in range(10))
            log_id += "-" + unicode(datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f'))
        else:
            log_id= None
    ##</end> generate a unique id for this log entry if possible

    ## set which log this entry should go to, if one isn't specified go to the failed retry log
        log_entry = None
        for destination in self.log_destinations:
            if destination[0] == error_type:
                if log_id != None:
                    log_entry = destination[1](id=transaction_id)
                else:
                    log_entry = destination[1]()

        if log_entry == None:
            if log_id != None:
                log_entry = LogGeneralError(id=transaction_id)
            else:
                log_entry = LogGeneralError()
    ##</end> set which log this entry should go to, if one isn't specified go to the failed retry log

        #~the transaction ID that was generated by the create transaction service
        if transaction_id != None:
            log_entry.transaction_id = unicode(transaction_id)
            error_data['transaction_id'] = transaction_id
        #~the user who created  the call to the create transaction service
        if transaction_user_uid != None:
            log_entry.transaction_user_uid = unicode(transaction_user_uid)
            error_data['transaction_user_uid'] = transaction_user_uid
        #~the identifier for which service, task_queue, and class created the error message.  The format for this should be "service:task_queue:class name"
        if task_id != None:
            log_entry.task_id = unicode(task_id)
            error_data['task_id'] = task_id
        #~the parameters that the task creating the error log entry received
        if params != None:
            log_entry.params = unicode(params)
            error_data['params'] = params
        #~the name of the task, this is the result of task.name
        if name != None:
            log_entry.name = unicode(name)
            error_data['name'] = name
        #~an overall description of the error
        if error_msg != None:
            log_entry.error_msg = unicode(error_msg)
            error_data['error_msg'] = error_msg
        #~detailed debug information, when possible this should include the list debug_data
        if debug_data != None:
            log_entry.debug_data = unicode(debug_data)
            error_data['debug_data'] = debug_data

        try:
            log_entry._put()
        except Exception as e:
            logging.error(["error writing log entry",e])
            logging.error(error_data)


    #~log when a transaction is started, used for performance testing
    def logTransactionStarted(self,transaction_id=None,params=None):
        call_result = {}
        debug_data = []
        return_msg = "TaskQueueFunctions:logTransactionStarted "

    ## input validation
        call_result = self.checkValues([[transaction_id,True,unicode,"len>10"],
                                        [params,True,dict,"len1"]
                                        ])
        if call_result['success'] == False:
            return_msg += "input validation failed"
            logging.error([return_msg,call_result])
            return {'success': True, 'return_msg': return_msg,'debug_data' :debug_data}
    ##</end> input validation

        log_entry = LogTransactionCreated(id=transaction_id)
        log_entry.transaction_id = transaction_id
        log_entry.params = unicode(params)
        try:
            log_entry._put()
        except Exception as e:
            return_msg +="transaction Started but couldnt write to datastore due to exception:%s" % e
            #logging.info([return_msg, transaction_id,params])


        return {'success': True, 'return_msg': return_msg,'debug_data' :debug_data}

    #~log when a transaction is completed used for performance testing

    def logTransactionFinished(self,transaction_id):
        call_result = {}
        debug_data = []
        return_msg = "TaskQueueFunctions:logTransactionFinished "
    ## input validation
        call_result = self.checkValues([[transaction_id,True,unicode,"len>10"]])
        if call_result['success'] == False:
            return_msg += "input validation failed"
            logging.error([return_msg,call_result])
            return {'success': True, 'return_msg': return_msg,'debug_data' :debug_data}
    ##</end> input validation


        created_log_key = ndb.Key(LogTransactionCreated._get_kind(),transaction_id)
        try:
            created_log_key.delete()
        except Exception as e:
            return_msg += "transaction finished but couldnt delete transaction created entry due to exeception:%s" % e
            #logging.info([return_msg, transaction_id])


        return {'success': True, 'return_msg': return_msg,'debug_data' :debug_data}



    #~add a task to a task_queue


    def logTransactionFailed(self,transaction_id, success_code=None):
        call_result = {}
        debug_data = []
        return_msg = "TaskQueueFunctions:logTransactionFailed "
        if success_code is True:
            success_code = 1
        if success_code is False:
            success_code = 0
    ## input validation
        call_result = self.checkValues([[transaction_id,True,unicode,"len>10"],
                                        [success_code, False, int]])
        if call_result['success'] == False:
            return_msg += "input validation failed"
            logging.error([return_msg,call_result])
            return {'success': True, 'return_msg': return_msg,'debug_data' :debug_data}
    ##</end> input validation

        log_entry = LogTransactionFailed(id=transaction_id)
        log_entry.transaction_id = transaction_id
        if success_code is not None:
            log_entry.success_code = success_code
        try:
            log_entry._put()
        except Exception as e:
            return_msg += "transaction finished but couldnt write to datastore due to exeception:%s" % e
            logging.error([return_msg, transaction_id])

        return {'success': True, 'return_msg': return_msg,'debug_data' :debug_data}



    #~add a task to a task_queue


    def add(self,queue_name=None,method=None,params={},url=None,name=None,delay=0):
        call_result = {}
        debug_data = []
        return_msg = "TaskQueueFunctions:add "
        #~the task_queue name to add the task to
        call_result = self.checkValues([[queue_name,True,unicode,"len1","len<151"],
                                          #~the method to use when adding the task, either push or pull.
                                          [method,True,unicode,"len1","len<151","task_queue_method"],
                                          #~ the parameters to pass to the task
                                          [params,False,dict],
                                          #~the task_queue entry name to use.  If this value isn't set the API will auto generate one. only set this if you can guarantee it will be universally unique.
                                          [name,False,unicode,"len1","len<151"],
                                          #~the URL to use to add the task to a PUSH task_queue
                                          [url,False,unicode,"len<1000"],
                                          [delay,True,long]
                                          ])

        debug_data.append(call_result)
        if call_result['success'] != True:
            return_msg+= "input validation failed"
            return {'success': RC.queuing_task_failed, 'return_msg': return_msg,'debug_data' :debug_data}

        try:
            if six.PY2:
                queue = taskqueue.Queue(queue_name)
                queue.add(taskqueue.Task(method=method,params=params,url=url,name=name,countdown=delay))
            else:
                if method == 'PULL':
                    publisher = pubsub_v1.PublisherClient()
                    topic_path = publisher.topic_path(os.environ.get('GOOGLE_CLOUD_PROJECT'), queue_name)
                    future = publisher.publish(topic_path, json.dumps(params).encode())
                    future.result()
                else:
                    d = datetime.utcnow() + timedelta(seconds=delay)

                    # Create Timestamp protobuf.
                    schedule_time = timestamp_pb2.Timestamp()
                    schedule_time.FromDatetime(d)

                    task_client = tasks_v2.CloudTasksClient()
                    queue = task_client.queue_path(os.environ.get("GOOGLE_CLOUD_PROJECT"), G_region, queue_name)
                    task_path = task_client.task_path(os.environ.get("GOOGLE_CLOUD_PROJECT"), G_region, queue_name, str(uuid.uuid4()))
                    task = {
                        'name': task_path,
                        'app_engine_http_request': {
                            'http_method': method,
                            'relative_uri': url,
                            'headers': {
                                'Content-Type': 'application/x-www-form-urlencoded'
                            },
                            'body': urlencode(params).encode(),
                        },
                        'schedule_time': schedule_time,
                    }
                    task_client.create_task(queue, task)
        except Exception as e:
            return_msg += 'execption occurred creating task. Exception:%s' % e
            return {'success': RC.queuing_task_failed, 'return_msg': return_msg,'debug_data' :debug_data}


        return {'success': True, 'return_msg': return_msg,'debug_data' :debug_data}

    #~delete a task from a task_queue

    def delete(self, task_queue, task, is_pubsub_message=False):
        call_result = {}
        debug_data = []
        return_msg = "TaskQueueFunctions:delete "
        #~task_queue name to delete the task from
        if is_pubsub_message:
            if six.PY2:
                call_result = self.checkValues([[task_queue, True, taskqueue.Queue],
                                                [task, True, dict]
                                                ])
            else:
                call_result = self.checkValues([[task_queue, True, unicode, "len1"],
                                                [task, True, dict]
                                                ])
        else:
            if six.PY2:
                call_result = self.checkValues([[task_queue,True,taskqueue.Queue],
                                                #~task name to delete, this is the result of task.name
                                                [task,True,taskqueue.Task]
                                                ])
            else:
                call_result = self.checkValues([[task_queue, True, unicode, "len1"],
                                                [task, True, unicode, "len1"]
                                                ])
        debug_data.append(call_result)
        if call_result == False:
            return_msg+= "input validation failed"
            return {'success': False, 'return_msg': return_msg,'debug_data' :debug_data}

        try:
            if six.PY2:
                if is_pubsub_message:
                    pubsub_service = build('pubsub', 'v1')
                    subscription_path = 'projects/{project_id}/subscriptions/{subscription_id}'.format(
                        project_id= unicode(app_identity.get_application_id()),
                        subscription_id=task_queue.name,
                    )
                    pubsub_service.projects().subscriptions().acknowledge(subscription=subscription_path, body={
                        "ackIds": [task['ackId']]
                    }).execute()
                else:
                    task_queue.delete_tasks(task)
            else:
                if is_pubsub_message:
                    subscriber = pubsub_v1.SubscriberClient()
                    subscription_path = subscriber.subscription_path(
                        os.environ.get('GOOGLE_CLOUD_PROJECT'), task_queue
                    )
                    subscriber.acknowledge(subscription_path, [task['ackId']])
                else:
                    task_client = tasks_v2.CloudTasksClient()
                    task_path = task_client.task_path(os.environ.get("GOOGLE_CLOUD_PROJECT"), G_region, task_queue, task)
                    task_client.delete_task(task_path)
        except Exception as e:
            return_msg += 'execption occurred creating task. Exception:%s' % unicode(e)
            return {'success': False, 'return_msg': return_msg,'debug_data' :debug_data}

        return {'success': True, 'return_msg': return_msg,'debug_data' :debug_data}

    #~takes the input parameters passed to the current task, the results of the current task. it then assigns parameter values as needed and passes the parameters on to the next task for this transaction

    def nextTask(self,origin_id=None,task_results=None,params=None):
        call_result = {}
        debug_data = []
        return_msg = "TaskQueueFunctions:nextTask "

    ## input validation
        try:
            task_sequence = json.JSONDecoder().decode(params['_task_sequence_list'])
        except Exception as e:
            return_msg+= "input validation failed. JSON decoding of task sequence failed with exception %s" % e
            return {'success': RC.queuing_task_failed, 'return_msg': return_msg,'debug_data' :debug_data}

        try:
            params['_task_sequence_index'] = unicode(params['_task_sequence_index'])
            params['_task_sequence_last_index'] = unicode(params['_task_sequence_last_index'])
        except Exception as e:
            return_msg+= "input validation failed. forced conversion to unicode failed with exception %s" % e
            return {'success': RC.queuing_task_failed, 'return_msg': return_msg,'debug_data' :debug_data}


        #~the identifier for which service, task_queue, and class created the request.  The format for this should be "service:task_queue:class name"
        call_result = self.checkValues([[origin_id,True,unicode,"len1","len<151"],
                                        #~this dictionary contains the return keys that the task_queue generated
                                        [task_results,True,dict],
                                        #~the parameters that were passed to the origin task, these will be passed on to the next task.
                                        [params,True,dict],
                                        [params['_task_sequence_index'],True,unicode,"bigint"],
                                        [params['_task_sequence_last_index'],True,unicode,"bigint"],
                                        [task_sequence,True,list,"task_queue_list"]
                                        ])
        debug_data.append(call_result)
        if call_result['success'] != True:

            return_msg+= "input validation failed"
            return {'success': RC.queuing_task_failed, 'return_msg': return_msg,'debug_data' :debug_data}

        #check if the origin task is the last one in the list to run
        task_index = int(params['_task_sequence_index'])
        if task_index == int(params['_task_sequence_last_index']):
            self.logTransactionFinished(unicode(params['transaction_id']))
            return {'success': True, 'return_msg': return_msg,'debug_data' :debug_data}

    ##</end> input validation

    ## add or modify the parameters based off the rules specified for the current task in the sequence

        try:
            result_asignments = task_sequence[task_index]['RSA']
            for key in result_asignments:
                params[key] = task_results[result_asignments[key]]
        except Exception as e:
            return_msg+= "error assigning task results %s" % e
            return {'success': RC.queuing_task_failed, 'return_msg': return_msg,'debug_data' :debug_data}

    ##</end> add our modify the parameters based off the rules specified for the current task in the sequence

    ## set parameters based off the rules specified in the rules of the next task
        next_task_index = task_index +1
        param_assignments = task_sequence[next_task_index]['PMA']
        for key in param_assignments:
            params[key] = param_assignments[key]
    ##</end> set parameters based off the rules specified in the rules of the next task

    ## get the information for the next task to call and call it
        queue_name = task_sequence[next_task_index]['name']
        url =  task_sequence[next_task_index]['url']
        method = task_sequence[next_task_index]['method']
        delay = long(task_sequence[next_task_index]['delay'])
        params['_task_sequence_index'] = unicode(next_task_index)

        call_result = self.add(queue_name,method,params,url,delay=delay)
        debug_data.append(call_result)
        if call_result == False:
            return_msg+= "creating new task failed"
            return {'success': RC.queuing_task_failed, 'return_msg': return_msg,'debug_data' :debug_data}
    ##</end> get the information for the next task to call and call it

        return {'success': True, 'return_msg': return_msg,'debug_data' :debug_data}




class CreateTransactionFunctions(DataValidation):

    def createTransaction(self,project_id=None,user_uid=None,task_name=None,task_sequence=None,transaction_id=None,params=None,external_transaction=False,org_uid=None):
        call_result = {}
        debug_data = []
        return_msg = "CreateTransactionFunctions:createTransaction "

    ## basic input validation
        call_result = self.checkValues([[project_id,True,unicode,"len1"],
                                        [user_uid,True,unicode,"bigint","greater0"],
                                        [task_name,True,unicode,"len1","len<151"],
                                        [task_sequence,True,unicode,"len1"],
                                        [transaction_id,False,unicode,"len>10"],
                                        [params,False,dict],
                                        [external_transaction,False,bool],
                                        [org_uid,False,unicode,"bigint","greater0"]
                                        ])
        debug_data.append(call_result)
        if call_result['success'] != True:
            return_msg += "input validation failed"
            return {'success': RC.input_validation_failed, 'return_msg': return_msg,'debug_data' :debug_data}
    ##</end> basic input validation

        call_result = self.verifyUpdateTaskSequence(task_sequence)
        debug_data.append(call_result)
        if call_result['success'] != True:
            return_msg += "task sequence validation failed"
            return {'success': RC.input_validation_failed, 'return_msg': return_msg,'debug_data' :debug_data}

        task_sequence = call_result['updated_task_sequence']


    ##create the transaction_id if we weren't passed one
        if transaction_id == None:
            chars=string.ascii_lowercase + string.ascii_uppercase + string.digits
            transaction_id = unicode(project_id) + "-" + unicode(user_uid) + "-"
            transaction_id += unicode(task_name) + "-"
            transaction_id += ''.join(random.choice(chars) for _ in range(20))
            transaction_id += "-" + unicode(datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f'))
    ##</end> create the transaction_id if we weren't passed one



    ## send the task_queue off to its first task.
        if params == None:
            params = {}
        #add params we modify or create
        params['_task_sequence_list'] = json.JSONEncoder().encode(task_sequence)
        params['_task_sequence_index'] =  unicode(0)
        params['_task_sequence_last_index'] = unicode(len(task_sequence) - 1)
        params['transaction_id'] = transaction_id
        params['transaction_user_uid'] = user_uid
        #organization 1 is the watchdog catch all organization
        if org_uid == None:
            org_uid = "1"
        params['transaction_org_uid'] = org_uid

        #create the new task

        #set any params that need to be set
        for key in task_sequence[0]['PMA']:
            params[key] = task_sequence[0]['PMA'][key]


        task_functions = TaskQueueFunctions()
        call_result = task_functions.add(task_sequence[0]['name'],task_sequence[0]['method'],params,
                                         task_sequence[0]['url'])
        debug_data.append(call_result)
        if call_result['success'] != True:
            return_msg+= "creating new task failed"
            return {'success': RC.queuing_task_failed, 'return_msg': return_msg,'debug_data' :debug_data}

        task_functions.logTransactionStarted(transaction_id,params)
    ##</end> send the task_queue off to its first task.

        return {'success': True,'return_msg':return_msg,'debug_data':debug_data}

    def verifyUpdateTaskSequence(self,task_sequence):
        from p1_services import Services as BES

        call_result = {}
        debug_data = []
        return_msg = "CreateTransactionFunctions:verifyTaskSequence "
        updated_task_sequence = []

        ## verify the task_sequence list is a valid data structure
        try:
            task_sequence = json.JSONDecoder().decode(task_sequence)
        except Exception as e:
            return_msg+= "JSON decoding of task sequence failed with exception %s" % e
            return {'success': RC.input_validation_failed, 'return_msg': return_msg,'debug_data' :debug_data,'updated_task_sequence':updated_task_sequence}

        call_result = self.checkValues([[task_sequence,True,list,"list_of_dicts"]])
        debug_data.append(call_result)
        if call_result['success'] != True:
            return_msg += "input validation failed _task_sequence_list list isn't a list of dictionaries "
            return {'success': RC.input_validation_failed,'return_msg': return_msg,'debug_data':debug_data,'updated_task_sequence':updated_task_sequence}

        #create a copy since we'll be changing things
        updated_task_sequence[:] = task_sequence[:]

        #add default values where they don't exist on optional fields
        for tasks in updated_task_sequence:
            if "RSA" not in tasks:
                tasks['RSA'] = {}

            if "PMA" not in tasks:
                tasks['PMA'] = {}

            if "method" not in tasks:
                tasks['method'] = "POST"

            if "url" not in tasks:
                tasks['url'] = ""

            if "delay" not in tasks:
                tasks['delay'] = "0"


        call_result = self.checkValues([[updated_task_sequence,True,list,"task_queue_list"]])
        debug_data.append(call_result)
        if call_result['success'] != True:
            return_msg += "_task_sequence_list input validation failed"
            return {'success': RC.input_validation_failed,'return_msg':return_msg,'debug_data':debug_data,'updated_task_sequence':updated_task_sequence}
    ##</end> verify the task_sequence list is a valid data structure


    ## verify that each item in the task_queue is a valid service,task and fix any wrong URLs or methods
        #check the task against the GlobalSettings services classes
        task_sequence_valid = True
        for index1,task in enumerate(updated_task_sequence):
            task_found_flag = False
            #only search the project the task is from
            if task['name'][:2] == "p1":
                service_list = BES.service_list
            else:
                return_msg += "msg:service / task not found for index %d in task_seuquence_list. " % index1
                task_sequence_valid = False
                continue

            #first check back-end services
            for service in service_list:
                for service_task in service.task_list:
                    if task['name'] == service_task.name:
                        task_found_flag = True

                        #set incorrect or empty values from the global settings
                        if  task['url'] != service_task.url:
                            task['url'] = service_task.url

                        if  task['method'] != service_task.method:
                            task['method'] = service_task.method

            if task_found_flag != True:
                return_msg += "msg:service / task not found for index %d in task_seuquence_list. " % index1
                task_sequence_valid = False
                continue

        if task_sequence_valid != True:
            return_msg += "some tasks in task_seuquence_list where not found in the GlobalSettings services class."
            return {'success': RC.input_validation_failed,'return_msg':return_msg,'debug_data':debug_data,'updated_task_sequence':updated_task_sequence}
    ##</end> verify that each item in the task_queue is a valid service,task and fix any wrong URLs or methods

    ## verify that there is a sequence list to send
        if len(updated_task_sequence) <1:
            return_msg += "updated task sequence has no entries."
            return {'success': RC.input_validation_failed,'return_msg':return_msg,'debug_data':debug_data,'updated_task_sequence':updated_task_sequence}

    ##</end> verify that there is a sequence list to send

        return {'success': True,'return_msg': return_msg,'debug_data':debug_data,'updated_task_sequence':updated_task_sequence}

class ExternalProjectTransactionFunctions(DataValidation):

    def sendTransaction(self,app_security_id=None,receiving_project_id=None,current_task_index=None,transaction_id=None,user_uid=None,task_sequence=None,task_name=None,url=None,params={}):
        call_result = {}
        debug_data = []
        return_msg = "ExternalProjectTransactionFunctions:sendTransaction "


        call_result = self.checkValues([[app_security_id,True,unicode,"len>10"],
                                        [receiving_project_id,True,unicode,"len1"],
                                        [current_task_index,True,unicode,"bigint"],
                                        [transaction_id,True,unicode,"len>10","len<1000"],
                                        [user_uid,True,unicode,"bigint","greater0"],
                                        [task_sequence,True,unicode,"len1","len<102400"],
                                        [task_name,False,unicode,"len1"],
                                        [url,True,unicode,"len1","len<1000"],
                                        [params,False,dict]
                                        ])
        debug_data.append(call_result)
        if call_result['success'] != True:
            return_msg += "input validation failed"
            return {'success': RC.input_validation_failed,'return_msg':return_msg,'debug_data':debug_data}
        current_task_index = long(current_task_index)
    ##</end> basic input data validation



    ## verify the task sequence and add any default values to it
        transaction_functions = CreateTransactionFunctions()
        call_result = transaction_functions.verifyUpdateTaskSequence(task_sequence)
        debug_data.append(call_result)
        if call_result['success'] != True:
            return_msg += "task sequence validation failed"
            return {'success': RC.input_validation_failed,'return_msg':return_msg,'debug_data':debug_data}

        #the current running task counts as a task in that list
        if ((len(call_result['updated_task_sequence'])) - current_task_index) < 1:
            return_msg += "no tasks in task sequence to pass to user-interface project"
            return {'success': RC.input_validation_failed,'return_msg':return_msg,'debug_data':debug_data}

        #only get the tasks after what we are excuting now since we don't need to pass the already processed tasks to another projects services
        task_sequence = call_result['updated_task_sequence'][current_task_index+1:]
    ##</end> verify the task sequence and add any default values to it

    ## clean the params of anything not specified for this project
        new_params = {}
        for key in params:
            if key[:2] == receiving_project_id:
                new_params[key] = unicode(params[key])
    ##</end> clean the params of anything not specified for this project

        try:
            new_params['_task_sequence_list'] = json.JSONEncoder().encode(task_sequence)
        except Exception as e:
            return_msg += "JSON encoding of task_queue failed with exeception: %s" % e
            return {'success': RC.input_validation_failed,'return_msg':return_msg,'debug_data':debug_data}

        new_params['transaction_id'] = transaction_id
        new_params['transaction_user_uid'] = user_uid
        new_params['app_security_id'] = app_security_id

        try:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            if six.PY2:
                param_data = urlencode(new_params)
                post_result = urlfetch.fetch(url,
                                             payload=param_data,
                                             method=urlfetch.POST,
                                             headers=headers,
                                             follow_redirects=False)
            else:
                post_result = requests.post(url, data=new_params, headers=headers, allow_redirects=False)
        except Exception as e:
            return_msg += "execption occuring while sending post request to add task to user-interface project. exeception: %s" % e
            return {'success': RC.failed_retry,'return_msg':return_msg,'debug_data':debug_data}

        if post_result.status_code == 200:
            return {'success': True,'return_msg':return_msg,'debug_data':debug_data}
        else:
            return_msg += "post result status code was not 200 it was %d" % post_result.status_code
            return {'success': RC.failed_retry,'return_msg':return_msg,'debug_data':debug_data}