from __future__ import unicode_literals

import six
if six.PY2:
    from google.appengine.ext import ndb
    from google.appengine.api import namespace_manager
else:
    from google.cloud import ndb
    namespace_manager = None

from six import integer_types
if len(integer_types) == 1:
    long = integer_types[0]
from six import text_type as unicode

from datetime import datetime
from datavalidation import DataValidation
from GCP_return_codes import FunctionReturnCodes as RC
import datavalidation
#~this class exists so we can use issubclass without a circlular dependency issue when doing firebase replication


class ReplicateToDatastoreFlag():
    pass

class ReplicateToFirebaseFlag():
    pass

class DatastoreDeletedItems(ndb.Model):
    #key is the urlsafe key of the entity that was duplicated into the datastore

    #the user who deleted the entity
    user_uid = ndb.IntegerProperty(required=True)
    delete_date = ndb.DateTimeProperty(required=True)
    #the name of the datastore the entity exists in
    datastore_name = ndb.StringProperty(required=True)



class DatastoreFunctions(DataValidation):
    @ndb.transactional(xg=True)
    def kput(self,replicate=True):
        return_msg  = 'DatastoreFunctions:kput '
        call_result = {}
        debug_data = []
        fail_flag = False
        put_result = None
    ## find each _rule_ variable, its associated data and validate the data
        for key in self.__class__.__dict__:
            #ignore non rule vars
            if ((len(key) > 6 and key[0:6] != "_rule_") or len(key) < 7):
                continue

            #rules to check value against
            args = self.__class__.__dict__[key][:]
            #value to check against, none is put in if no value is found so datavalidation can check against that
            if key[6:] in self.__dict__['_values']:
                arg = getattr(self,key[6:])
                args.insert(0,arg)
            else:
                args.insert(0,None)

            call_result = self.checkValues([args])
            debug_data.append(call_result)
            if call_result['success'] == False:
                return_msg += "msg: validation failed for %s." % key[6:]
                fail_flag = True

            continue


    ##</end> find each _rule_ variable, its associated data and validate the data
        if fail_flag == True:
            return {'success': RC.input_validation_failed, 'put_result': put_result,'return_msg': return_msg, 'debug_data': debug_data,'args':self.__dict__['_values']}

        try:
            put_result = self.__class__._put(self)
        except Exception as e:
            return_msg += "_put failed with exception %s" % e
            return {'success': RC.datastore_failure, 'put_result': put_result,'return_msg': return_msg, 'debug_data': debug_data,'args':self.__dict__['_values'] }

        if replicate == True and issubclass(self.__class__,ReplicateToFirebaseFlag):
            self.replicateEntityToFirebase()

        if replicate == True and issubclass(self.__class__,ReplicateToDatastoreFlag):
            self.replicateCreateEntityToDatastore()




        return {'success': RC.success, 'put_result': put_result,'return_msg': return_msg, 'debug_data': debug_data,'args':self.__dict__['_values'] }

    def kputNonTransactional(self, replicate=True):
        return_msg = 'DatastoreFunctions:kput '
        call_result = {}
        debug_data = []
        fail_flag = False
        put_result = None
        ## find each _rule_ variable, its associated data and validate the data
        for key in self.__class__.__dict__:
            # ignore non rule vars
            if ((len(key) > 6 and key[0:6] != "_rule_") or len(key) < 7):
                continue

            # rules to check value against
            args = self.__class__.__dict__[key][:]
            # value to check against, none is put in if no value is found so datavalidation can check against that
            if key[6:] in self.__dict__['_values']:
                arg = getattr(self, key[6:])
                args.insert(0, arg)
            else:
                args.insert(0, None)

            call_result = self.checkValues([args])
            debug_data.append(call_result)
            if call_result['success'] == False:
                return_msg += "msg: validation failed for %s." % key[6:]
                fail_flag = True

            continue

        ##</end> find each _rule_ variable, its associated data and validate the data
        if fail_flag == True:
            return {'success': RC.input_validation_failed, 'put_result': put_result, 'return_msg': return_msg,
                    'debug_data': debug_data, 'args': self.__dict__['_values']}

        try:
            put_result = self.__class__._put(self)
        except Exception as e:
            return_msg += "_put failed with exception %s" % e
            return {'success': RC.datastore_failure, 'put_result': put_result, 'return_msg': return_msg,
                    'debug_data': debug_data, 'args': self.__dict__['_values']}

        if replicate == True and issubclass(self.__class__, ReplicateToFirebaseFlag):
            self.replicateEntityToFirebase()

        if replicate == True and issubclass(self.__class__, ReplicateToDatastoreFlag):
            self.replicateCreateEntityToDatastore()

        return {'success': RC.success, 'put_result': put_result, 'return_msg': return_msg, 'debug_data': debug_data,
                'args': self.__dict__['_values']}

    @ndb.transactional(xg=True)
    def kupdate(self,replicate=True):
        return_msg  = 'DatastoreFunctions:kupdate '
        call_result = {}
        debug_data = []
        fail_flag = False
        update_result = None

    ## check each value that has been updated against its rule
        for key in self.__dict__['_values']:

            #ignore values that have not been updated
            if type(self.__dict__['_values'][key]) == ndb.model._BaseValue:
                    continue

            #make sure a value variable exists for this rule
            if ("_rule_" + key) not in self.__class__.__dict__:
                return_msg += "msg: no rule found for value %s" % key
                continue


            args = self.__class__.__dict__["_rule_" + key][:]
            args.insert(0,self.__dict__['_values'][key])

            call_result = self.checkValues([args])
            debug_data.append(call_result)
            if call_result['success'] == False:
                return_msg += "msg: validation failed for %s." % key
                fail_flag = True

            continue
    ##</end> check each value that has been updated against its rule

        if fail_flag == True:
            return {'success': RC.input_validation_failed, 'update_result': update_result,'return_msg': return_msg, 'debug_data': debug_data }

        try:
            update_result = self.__class__._put(self)
        except Exception as e:
            return_msg += "_put failed with exception %s" % e
            return {'success': RC.datastore_failure, 'update_result': update_result,'return_msg': return_msg, 'debug_data': debug_data }

        if replicate == True and issubclass(self.__class__,ReplicateToFirebaseFlag):
            self.replicateEntityToFirebase()

        if replicate == True and issubclass(self.__class__,ReplicateToDatastoreFlag):
            self.replicateUpdateEntityToDatastore()

        return {'success': RC.success, 'update_result': update_result,'return_msg': return_msg, 'debug_data': debug_data }

    def kupdateNonTransactional(self, replicate=True):
        return_msg = 'DatastoreFunctions:kupdateNonTransactional '
        call_result = {}
        debug_data = []
        fail_flag = False
        update_result = None

        ## check each value that has been updated against its rule
        for key in self.__dict__['_values']:

            # ignore values that have not been updated
            if type(self.__dict__['_values'][key]) == ndb.model._BaseValue:
                continue

            # make sure a value variable exists for this rule
            if ("_rule_" + key) not in self.__class__.__dict__:
                return_msg += "msg: no rule found for value %s" % key
                continue

            args = self.__class__.__dict__["_rule_" + key][:]
            args.insert(0, self.__dict__['_values'][key])

            call_result = self.checkValues([args])
            debug_data.append(call_result)
            if call_result['success'] == False:
                return_msg += "msg: validation failed for %s." % key
                fail_flag = True

            continue
        ##</end> check each value that has been updated against its rule

        if fail_flag == True:
            return {'success': RC.input_validation_failed, 'update_result': update_result, 'return_msg': return_msg,
                    'debug_data': debug_data}

        try:
            update_result = self.__class__._put(self)
        except Exception as e:
            return_msg += "_put failed with exception %s" % e
            return {'success': RC.datastore_failure, 'update_result': update_result, 'return_msg': return_msg,
                    'debug_data': debug_data}

        if replicate == True and issubclass(self.__class__, ReplicateToFirebaseFlag):
            self.replicateEntityToFirebase()

        if replicate == True and issubclass(self.__class__, ReplicateToDatastoreFlag):
            self.replicateUpdateEntityToDatastore()

        return {'success': RC.success, 'update_result': update_result, 'return_msg': return_msg,
                'debug_data': debug_data}

    @staticmethod
    def kget(key):
        return_msg  = 'DatastoreFunctions:kget '
        call_result = {}
        debug_data =[]
        get_result = None

        try:
            get_result = key.get()
        except Exception as e:
            return_msg += "get failed with exception %s" % e
            return {'success': RC.datastore_failure, 'get_result': get_result,'return_msg': return_msg, 'debug_data': debug_data }

        return {'success': RC.success, 'get_result': get_result,'return_msg': return_msg, 'debug_data': debug_data }

    @staticmethod
    def kget_no_caching(key):
        return_msg  = 'DatastoreFunctions:kget_no_caching '
        call_result = {}
        debug_data =[]
        get_result = None

        try:
            get_result = key.get(use_cache=False, use_memcache=False)
        except Exception as e:
            return_msg += "get failed with exception %s" % e
            return {'success': RC.datastore_failure, 'get_result': get_result,'return_msg': return_msg, 'debug_data': debug_data }

        return {'success': RC.success, 'get_result': get_result,'return_msg': return_msg, 'debug_data': debug_data }

    @staticmethod
    def kdelete(user_uid=None,key=None,backup=True,replicate=False):
        return_msg  = 'DatastoreFunctions:kdelete '
        debug_data =[]
        delete_result = None

    ## input validation
        DV = DataValidation()
        call_result = DV.checkValues([[user_uid,True,long,"bigint","greater0"],
                                      [key,True,ndb.key.Key],
                                      [backup,True,bool],
                                      [replicate,True,bool]
                                      ])
        debug_data.append(call_result)
        if call_result['success'] != True:
            return_msg += "initial input validation failure"
            return {'success': RC.input_validation_failed, 'delete_result': delete_result,'return_msg': return_msg, 'debug_data': debug_data }
    ##</end> input validation

    ## get the complete entity if we'll need it
        if backup == True or replicate == True:
            try:
                    entity = key.get()
            except Exception as e:
                return_msg += "get  of entity failed with exception %s" % e
                return {'success': RC.datastore_failure, 'delete_result': delete_result,'return_msg': return_msg, 'debug_data': debug_data }
    ##</end> get the complete entity

        if namespace_manager:
            normal_namespace = namespace_manager.get_namespace()
    ### backup the entity into the deleted namespace
        if backup == True:
            if namespace_manager:
                ##change namespaces to keep data separate and put the copy of the entity
                try:
                    namespace_manager.set_namespace("deleted_data")
                except Exception as e:
                    return_msg += "switching namespace to deleted_data failed with exception %s" % e
                    namespace_manager.set_namespace(normal_namespace)
                    return {'success': RC.datastore_failure, 'delete_result': delete_result,'return_msg': return_msg, 'debug_data': debug_data }

            try:
                new_entity_key = entity.put()
            except Exception as e:
                return_msg += "put of entity into deleted_data namespace failed with exception:%s" %e
                if namespace_manager:
                    namespace_manager.set_namespace(normal_namespace)
                return {'success': RC.datastore_failure, 'delete_result': delete_result,'return_msg': return_msg, 'debug_data': debug_data }

            new_entity_url_key = new_entity_key.urlsafe()
        ##</end>change namespaces to keep data separate and put the copy of the entity

            if namespace_manager:
                # change namespace back to normal one to write the delete reference record
                try:
                        namespace_manager.set_namespace(normal_namespace)
                except Exception as e:
                    return_msg += "switching namespace back to normal namespace failed with exception %s" % e
                    return {'success': RC.datastore_failure, 'delete_result': delete_result,'return_msg': return_msg, 'debug_data': debug_data }

        ## write the delete record reference to normal namespace
            try:
                delete_record = DatastoreDeletedItems(id=new_entity_url_key)
                delete_record.user_uid = user_uid
                delete_record.datastore_name = unicode(entity._get_kind())
                delete_record.delete_date = datetime.now()
                delete_record.put()
            except Exception as e:
                return_msg += "writing delete record failed with exception %s" % e
                return {'success': RC.datastore_failure, 'delete_result': delete_result,'return_msg': return_msg, 'debug_data': debug_data }
        ##</end> write the delete record reference to normal namespace

    ### backup the entity into the deleted namespace

        #safety check to make sure we are in the right namespace
        if namespace_manager and namespace_manager.get_namespace() != normal_namespace:
            try:
                namespace_manager.set_namespace(normal_namespace)
            except Exception as e:
                return_msg += "switching namespace back to normal namespace failed with exception %s" % e
                return {'success': RC.datastore_failure, 'delete_result': delete_result,'return_msg': return_msg, 'debug_data': debug_data }

        try:
            delete_result = key.delete()
        except Exception as e:
            return_msg += "delete failed with exception %s" % e
            return {'success': RC.datastore_failure, 'delete_result': delete_result,'return_msg': return_msg, 'debug_data': debug_data }



        #this should be done if desired before calling kdelete. and only delete upon success of this function
        #this precaution ensures there won't be leftovers in other locations for deleted items.
        #if replicate == True and issubclass(entity.__class__,ReplicateToFirebaseFlag):
        #   entity.replicateEntityToFirebase(delete_flag = True)
        #if replicate == True and issubclass(entity.__class__,ReplicateToDatastoreFlag):
        #    entity.replicateDeleteEntityToDatastore()

        return {'success': RC.success, 'delete_result': delete_result,'return_msg': return_msg, 'debug_data': debug_data }

    @staticmethod
    def kfetch(query= None,limit = None,offset = 0,batch_size = 20,keys_only = False,projection = None,prefetch_size = None,produce_cursors = False,start_cursor = None,end_cursor = None,deadline = 5,read_policy = ndb.EVENTUAL_CONSISTENCY):
        return_msg  = 'DatastoreFunctions:kfetch '
        debug_data =[]
        fetch_result = []

        if query == None or type(query) != ndb.query.Query:
            return_msg += "query input value is not a query object its a %s" % type(query)
            return {'success': RC.input_validation_failed, 'fetch_result': fetch_result,'return_msg': return_msg, 'debug_data': debug_data }

        kwargs = {}
        if six.PY2:
            kwargs.update(dict(
                deadline=deadline,
                read_policy=read_policy,
                batch_size=batch_size,
                prefetch_size=prefetch_size,
            ))
        else:
            kwargs.update(dict(
                timeout=deadline,
                read_consistency=read_policy,

            ))
        if limit is not None:
            kwargs.update(dict(
                limit=limit
            ))

        try:
            fetch_result = query.fetch(
                offset=offset, keys_only=keys_only, projection=projection, produce_cursors=produce_cursors,
                start_cursor=start_cursor, end_cursor=end_cursor,
                **kwargs
            )
        except Exception as e:
            #ensure that even if no results were found we return an empty list prevent exceptions.
            if fetch_result == None:
                fetch_result = []
            return_msg += "query failed with exception %s" % e
            return {'success': RC.datastore_failure, 'fetch_result': fetch_result,'return_msg': return_msg, 'debug_data': debug_data }

        #ensure that even if no results were found we return an empty list prevent exceptions.
        if fetch_result == None:
            fetch_result = []

        return {'success': True, 'fetch_result': fetch_result,'return_msg': return_msg, 'debug_data': debug_data }

    @staticmethod
    def kdelete_multi(user_uid=None,keys=None,backup=True,replicate=False):
        return_msg  = 'DatastoreFunctions:kMultiDelete '
        debug_data =[]
        delete_result = None

        if len(keys) <1:
            return_msg += "nothing to delete"
            return {'success': RC.success, 'delete_result': delete_result,'return_msg': return_msg, 'debug_data': debug_data }

    ## if we need to backup these entities gets their data before deleting it so we can pass it on the deletion replication function
        backup_entitites = []
        if  backup==True:
            for entity_key in keys:
                try:
                        entity = entity_key.get()
                except Exception as e:
                    return_msg += "get failed on entity key:%s with exception %s" % (entity_key.string_id(),e)
                    return {'success': RC.datastore_failure, 'delete_result': delete_result,'return_msg': return_msg, 'debug_data': debug_data }
                backup_entitites.append(entity)
    ##</end> if we need to backup these entities gets their data before deleting it so we can pass it on the deletion replication function

        if namespace_manager:
            normal_namespace = namespace_manager.get_namespace()
    ### backup the entity into the deleted namespace
        if backup == True:
            for entity in backup_entitites:
                if namespace_manager:
                    ##change namespaces to keep data separate and put the copy of the entity
                    try:
                        namespace_manager.set_namespace("deleted_data")
                    except Exception as e:
                        return_msg += "switching namespace to deleted_data failed with exception %s" % e
                        namespace_manager.set_namespace(normal_namespace)
                        return {'success': RC.datastore_failure, 'delete_result': delete_result,'return_msg': return_msg, 'debug_data': debug_data }

                try:
                    new_entity_key = entity.put()
                except Exception as e:
                    return_msg += "put of entity into deleted_data namespace failed with exception:%s" %e
                    if namespace_manager:
                        namespace_manager.set_namespace(normal_namespace)
                    return {'success': RC.datastore_failure, 'delete_result': delete_result,'return_msg': return_msg, 'debug_data': debug_data }

                new_entity_url_key = new_entity_key.urlsafe()
            ##</end>change namespaces to keep data separate and put the copy of the entity

                if namespace_manager:
                    # change namespace back to normal one to write the delete reference record
                    try:
                            namespace_manager.set_namespace(normal_namespace)
                    except Exception as e:
                        return_msg += "switching namespace back to normal namespace failed with exception %s" % e
                        return {'success': RC.datastore_failure, 'delete_result': delete_result,'return_msg': return_msg, 'debug_data': debug_data }

            ## write the delete record reference to normal namespace
                try:
                    delete_record = DatastoreDeletedItems(id=new_entity_url_key)
                    delete_record.user_uid = user_uid
                    delete_record.datastore_name = unicode(entity._get_kind())
                    delete_record.delete_date = datetime.now()
                    delete_record.put()
                except Exception as e:
                    return_msg += "writing delete record failed with exception %s" % e
                    return {'success': RC.datastore_failure, 'delete_result': delete_result,'return_msg': return_msg, 'debug_data': debug_data }
            ##</end> write the delete record reference to normal namespace

    ### backup the entity into the deleted namespace

        #safety check to make sure we are in the right namespace
        if namespace_manager and namespace_manager.get_namespace() != normal_namespace:
            try:
                namespace_manager.set_namespace(normal_namespace)
            except Exception as e:
                return_msg += "switching namespace back to normal namespace failed with exception %s" % e
                return {'success': RC.datastore_failure, 'delete_result': delete_result,'return_msg': return_msg, 'debug_data': debug_data }


        try:
            delete_result = ndb.delete_multi(keys)
        except Exception as e:
            return_msg += "delete_multi failed with exception %s" % e
            return {'success': RC.datastore_failure, 'delete_result': delete_result,'return_msg': return_msg, 'debug_data': debug_data }

        return {'success': RC.success, 'delete_result': delete_result,'return_msg': return_msg, 'debug_data': debug_data }

    @staticmethod
    def kput_multi(entities,replicate=True):
        return_msg  = 'DatastoreFunctions:kput '
        call_result = {}
        debug_data = []
        fail_flag = False
        put_result = None
        fail_entity_indexs = []
        replication_firebase_entities = []
        replication_datastore_entities = []

    ### process each entity in the list
        for entity_index,entity in enumerate(entities):
        ## find each _rule_ variable, its associated data and validate the data
            for key in entity.__class__.__dict__:
                #ignore non rule vars
                if len(key) > 6 and key[0:6] != "_rule_":
                    continue

                #rules to check value against
                args = entity.__class__.__dict__[key][:]
                #value to check against, none is put in if no value is found so datavalidation can check against that
                if key[6:] in entity.__dict__['_values']:
                    args.insert(0,entity.__dict__['_values'][key[6:]])
                else:
                    args.insert(0,None)

                call_result = entity.checkValues([args])
                debug_data.append(call_result)
                if call_result['success'] == False:
                    return_msg += "msg: validation failed for entity index: %d field:%s." % (entity_index, key[6:])
                    fail_flag = True
                    fail_entity_indexs.append(entity_index)
                    continue
        ##</end> find each _rule_ variable, its associated data and validate the data

            #flag if the entity needs to be replicated
            if issubclass(entity.__class__,ReplicateToFirebaseFlag):
                replication_firebase_entities.append(entity)
            if issubclass(entity.__class__,ReplicateToDatastoreFlag):
                replication_datastore_entities.append(entity)

            continue
    ###</end> process each entity in the list

        if fail_flag == True:
            return {'success': RC.input_validation_failed, 'put_result': put_result,'return_msg': return_msg, 'debug_data': debug_data}

        try:
            put_result = ndb.put_multi(entities)
        except Exception as e:
            return_msg += "db.put_multi failed with exception %s" % e
            return {'success': RC.datastore_failure, 'put_result': put_result,'return_msg': return_msg, 'debug_data': debug_data }


        if replicate == True and len(replication_firebase_entities) >0:
            for entity in replication_firebase_entities:
                entity.replicateEntityToFirebase()

        if replicate == True and len(replication_datastore_entities) >0:
            replication_datastore_entities[0].replicateCreateEntityListToDatastore(replication_datastore_entities)


        return {'success': RC.success, 'put_result': put_result,'return_msg': return_msg, 'debug_data': debug_data }

    @staticmethod
    def kget_multi(entities):
        return_msg  = 'DatastoreFunctions:kget_multi '
        call_result = {}
        debug_data =[]
        get_result = None

        try:
            get_result = ndb.get_multi(entities)
        except Exception as e:
            return_msg += "get failed with exception %s" % e
            return {'success': RC.datastore_failure, 'get_result': get_result,'return_msg': return_msg, 'debug_data': debug_data }

        return {'success': RC.success, 'get_result': get_result,'return_msg': return_msg, 'debug_data': debug_data }


