from rest_framework.exceptions import APIException


class InternalError(APIException):

    status_code = 503
    res_detail = 'Server error. Please try again or contact support.'
    error = None
    code = 'InternalServerError'

    def __init__(self, message, error):
        self.detail = message
        self.error = error
        