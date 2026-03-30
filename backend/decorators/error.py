from flask import jsonify
from functools import wraps
from classes.Error import InputError, AccessError
import traceback

def catch_errors(func):

    @wraps(func)
    def error_wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        
        except (InputError, AccessError) as err:
            print(f"DEBUG - Caught error in function '{func.__name__}': {err}")
            traceback.print_exc()

            response = jsonify({"error": str(err)})
            response.status_code = err.status_code
            
            return response
        
        except Exception as err:
            print(f"DEBUG - Unhandled Exception in function '{func.__name__}': {err}")
            traceback.print_exc()

            response = jsonify({"error": f"Internal Server Error: {str(err)}"})
            response.status_code = 500

            return response
    
    return error_wrapper_func