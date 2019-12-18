"""
This module can be use for test control data.
Web and API can also use this for setting up the user,
saving images for test evidences. 
"""
from datetime import datetime
from django.contrib.auth.hashers import make_password
# import pyotp --- FOR OTP FUNCTIONALITIES
import os


class TestController():
    user_email = 'CREDENTIALS HERE'
    user_password = 'CREDENTIALS HERE'

    def create_dummy(self):
        """
        For dummy testing
        
        For every testcases, it creates a new user so might as well
        implement a method so the code does not repeat.
        """
        pass
        # Create user first
        # This should be implemented if ever this testcase is connected to
        # the model or db. Change the code accordingly.
        # 
        # user = <MODEL>.objects.create_user(self.user_email, self.user_password)
        # user.is_active = True
        # user.save()

        # If 2FA is implemented in the website use this one
        # Change accordingly to where is the table for 2FA is located
        # 
        # settings = <MODEL>(
        #     two_fa=False,
        #     two_fa_key=pyotp.random_base32(),
        #     user=user
        # )
        # settings.save()
    
    def save_image(self, method_name, test_folder, selenium):
        """
        Saves the images based on the method name/unit test name

        :Parameters:
            method_name: (str)
            folder: (str)
            selenium: (obj)
        """
        # Windows OS does not allow to use colon(:) for file names
        if os.name == 'nt':
            TIME = datetime.utcnow().strftime("_%Y-%m-%d-%H%M%S")
        else:
            TIME = datetime.utcnow().strftime("_%Y-%m-%d-%H:%M:%S")
        selenium.save_screenshot(
            '/'.join([test_folder, method_name+TIME+'.png']))
