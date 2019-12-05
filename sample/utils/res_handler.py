"""
Purpose of this module is to unify the return formats of the
responses and create the logs.
"""
import logging
import simplejson as json
from collections import OrderedDict
from datetime import datetime
from .client_ip import client_ip

logger = logging.getLogger(__name__)


class CustomResponseLog():
    """
    Single entry point of response back to the web/api
    Will log selected values before returning the response
    """

    def __init__(self, app_name=None, request=None,
                params={}, email=None):
        """
        :Parameters:
            app_name: (str) class name
            request: (obj) request object
            params: (dict) dictionary of additional info
        
        :Returns:
            dict
        """
        self.app_name = app_name.__class__.__name__
        self.request = request
        self.params = params
        self.email = email
        self.logInfo = OrderedDict()

    def custom_response(self):
        self.logInfo['timestamp'] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S")
        if hasattr(self, 'request') and self.request:
            if str(self.request.user) != 'AnonymousUser':
                self.logInfo['email'] = self.request.user.email
            else:
                # This is for the scenario of email was provided but it
                # was a JSON payload. Mostly will be used by the reset-
                # password API.
                if 'email' in self.request.data:
                    self.logInfo['email'] = self.request.data['email']
                elif self.email:
                    self.logInfo['email'] = self.email
                else:
                    self.logInfo['email'] = ''
            self.logInfo['ip'] = client_ip(self.request)
        else:
            self.logInfo['email'] = ''
            self.logInfo['ip'] = ''
        self.logInfo['message'] = 'OK'
        self.logInfo['success'] = True
        self.logInfo['app_name'] = self.app_name
        log_data = json.dumps(self.logInfo)
        logger.info(log_data)
        # Delete keys which are not to be shown in response
        del self.logInfo['timestamp']
        del self.logInfo['email']
        del self.logInfo['ip']
        del self.logInfo['app_name']
        if len(self.params) != 0:
            self.logInfo['data'] = self.params
        return json.loads(
                json.dumps(self.logInfo),
                object_pairs_hook=OrderedDict
        )
