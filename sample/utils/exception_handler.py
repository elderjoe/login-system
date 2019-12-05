"""
CUSTOM EXCEPTION HANDLER
This serves as a one point of entry for 
all known exceptions that are catchable by this handler.
"""
import json
import logging
from datetime import datetime
from collections import OrderedDict
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import InvalidToken
from .client_ip import client_ip
from authentication.models import User

logger = logging.getLogger(__name__)

def custom_errlog(exc, context, detail):
    logInfo = OrderedDict()
    logInfo['timestamp'] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S")
    if 'request' in context:
        if str(context['request'].user) != 'AnonymousUser':
            logInfo['email'] = context['request'].user.email
        # Get the email address from the exception arguments
        elif len(exc.args) >= 2 and isinstance(exc.args[1], User):
            logInfo['email'] = str(exc.args[1])
        else:
            logInfo['email'] = ''
        logInfo['ip'] = client_ip(context['request'])
    else:
        logInfo['email'] = ''
        logInfo['ip'] = ''
    logInfo['app_name'] = detail['path']
    logInfo['err_code'] = detail['status']
    logInfo['message'] = detail['message']
    logInfo['err_detail'] = None
    # output unexpected error's detail
    if len(exc.args) >= 2 and not isinstance(exc.args[1], User):
        logInfo['err_detail'] = str(exc.args[1])
    if 'errors' in detail:
        logInfo['errors'] = detail['errors']
    logData = json.dumps(logInfo)
    logger.info(logData)

def _extract_errors(exc):
    """
        Extract the errors from the exception object

        Parameters:
            exc: (obj) exception object
        Returns:
            dict
    """
    def _get_errors(errors):
        """
        This retrieves all errors from the error dict

        :Parameters:
            errors: (dict) error dictionary
        :Returns:
            dict
        """
        err = []
        for _, value in errors.items():
            if value[0] not in err:
                err.append(value[0])
        return err
    err = []
    errors = json.loads(json.dumps(exc.__dict__))
    for _, value in errors.items():
        if isinstance(value, dict):
            err.extend(_get_errors(value))
        elif isinstance(value, list):
            err.extend(value)
    return err if len(err) > 1 else err[0]

def _build_error_response(response, exc, context):
    """
    Populates the response object with the error details

    Parameters:
        response: (obj) response to return
        exc: (obj) exception object containing error info
        context: (obj) request object

    Returns:
        dict (OrderDict)
    """
    response.data = OrderedDict()
    if isinstance(exc, ValidationError):
        response.data['errors'] = _extract_errors(exc)
    elif isinstance(exc, InvalidToken):
        if 'messages' in exc.detail:
            response.data['errors'] = exc.detail['messages'][0]['message']
        else:
            response.data['errors'] = exc.detail['detail']
    else:
        response.data['errors'] = exc.detail
    response.data['path'] = context['view'].__class__.__name__
    response.data['time'] = datetime.now()
    response.data['status'] = exc.status_code
    response.data['message'] = exc.__class__.__name__
    return response
    
        
def custom_exception_handler(exc, context):
    """
    Main function for handling errors
    Parameters are set and being called by the rest framework
    itself. Devs does not need to use this function.
    """
    response = exception_handler(exc, context)
    response = _build_error_response(response, exc, context)
    custom_errlog(exc, context, response.data)
    return response
