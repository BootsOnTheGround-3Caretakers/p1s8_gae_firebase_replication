
#function return codes
class RC():
    success= True
    port_failure = 1001
    input_validation = 1002
    parsing_failure = 1003
    command_failure = 1004
    browser_failure = 1005
    instance_not_ready = 1006
    query_failure = 1007
    threading_failure = 1008
    api_failure = 1009
    state_engine_error = 1010
    subprocess_nonzero_termination = 1011
    
    
#function return dictionary normal keys
class RDK():
    success = 'success'
    debug_data = 'debug_data'
    return_msg = 'return_msg'

class ErrorFunctions():
    @staticmethod
    def parseException(action_description=None,exception_object=None,variables=None):
        variables_string = ''
        e_str = ''
        
        if type(action_description) != str:
            action_description = "Not Specified"
        
        
        if variables != None:
            try:
                variables_string = ' . variables:' +  str(variables) + '.'
            except:
                variables_string = ' . Could not convert variables to strings.'
                
        try:
            e_str = str(exception_object)
        except:
            e_str = "could not convert exception to string"
        
        output_string = 'expection occured while trying to: ' + action_description + ' .exception:' + e_str + variables_string
        return output_string

    @staticmethod    
    def logException(function_name=None,action_description=None,exception_object=None,variables=None):
        
        variables_string = ''
        if type(function_name) != str:
            function_name = "Not Specified"
        if type(action_description) != str:
            action_description = "Not Specified"
        
        if variables != None:
            try:
                variables_string = ' . variables:' +  str(variables) + '.'
            except:
                variables_string = ' . Could not convert variables to strings.'
                
        try:
            e_str = str(exception_object)
        except:
            e_str = "could not convert exception to string"    
        
        output_string = 'expection occured in function: ' + function_name + '. while trying to: ' + action_description + ' .exception: ' + e_str + ' variables: ' + variables_string
        return output_string
        
