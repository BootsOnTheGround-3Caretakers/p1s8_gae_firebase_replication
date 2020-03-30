from __future__ import unicode_literals



class FunctionReturnCodes():
    #anything below this number is retried, above is perma-failed
    retry_threshold = 1000
    failed_retry = False
    success = True
    firebase_replication_retry = 3
    sql_failure = 4
    datastore_failure = 5
    memcache_failure = 6
    
    
    #anything above 1000 will not be retried in a task queue
    input_validation_failed = 1001
    ACL_check_failed = 1002
    queuing_task_failed = 1003
    delete_task_failed = 1005
    billing_error = 1006
    firebase_replication_failure = 1007
    datastore_failed_no_retry = 1008
