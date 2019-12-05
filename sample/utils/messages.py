class ERR():
    # USER RELATED
    EMAIL_PASS_NULL = 'Email or password is invalid. Please check your credentials.'
    EMAIL_EXIST = 'Email already exists.'
    EMAIL_INVALID = 'Email is invalid.'
    PASS_INVALID = 'Password is invalid.'
    PASS_LEN_INVALID = 'Password length should be at least 8 characters.'
    PASS_STR_INVALID = 'Please choose a more secure password. Password should be at least 8 characters, mix with special characters, upper and lower case letters and numbers.'
    PASS_NOT_MATCH = 'Password did not match. Please check you inputs and try again.'
    EMAIL_FIELD_MISSING = 'Email is required.'
    PASS_FIELD_MISSING = 'Password is required.'
    ROLE_INVALID = 'Role is invalid.'
    USER_INACTIVE = 'User is inactive. Please verify your email first.'
    USER_NOT_EXIST = 'The email provided does not exist. Please create an account first.'
    LOGIN_INVALID = 'Email or password is incorrect. Please check your credentials.'
    PERMISSION_DENIED = 'Permission denied.'
    USER_BLOCKED = 'This account has been locked due to multiple number of failed attempts.'
    ROLE_USER_INVALID = 'Role is not set to \'user\' or missing.'
    ROLE_ADMIN_INVALID = 'Role is not set to \'admin\' or missing.'
    ROLE_SUPER_INVALID = 'Role is not set to \'superadmin\' or missing.'
    RST_PSW_INVALID = 'Link provided is invalid. Please try again.'
    RST_PSW_EXPIRED = 'Link already expired. Please try reseting your password again.'
    ACTIVATION_INVALID = 'Activation link is invalid. Please try again or contact support.'
    ACTIVATION_EXPIRED = 'Link has already expired. Please request again for a new activation link.'
    LINK_USED = 'Link has been used already. Please request again for another.'
    # ROLES
    ROLE_INVALID = 'Role does not exists. Please contact support.'
    # SERVER RELATED
    SERVER_ERROR = 'Server error. Please try again or contact support.'


class SCS():
    REGISTER = 'User created.'
    LOGIN = 'Successfully login.'
    LOGOUT = 'Successfully logout.'
    PSW_RESET = 'Password reset success.'
    ACTIVATE = 'Email has been activated. You may login in now.'
    ROLE_UPDATED = 'Role successfully updated.'
    ACTV_SENT = 'Activation link sent.'


class EMAIL():
    messages = {
        'REGISTER': {
            'TITLE': 'Activation email',
            'MSG': 'Welcome to Sample Project.',
            'TEMPLATE': 'activation.html'
        },
        'RESET': {
            'TITLE': 'Reset Password Request',
            'MSG': 'You have requested a change password.',
            'TEMPLATE': 'reset_password.html'
        },
        'ACTV_RESEND': {
            'TITLE': 'Activation Email Request',
            'MSG': 'Requested for activation email.',
            'TEMPLATE': 'activation.html'
        }
    }
    
    TITLE = None
    MSG = None
    TEMPLATE = None

    def __init__(self, event):
        if event in self.messages:
            self.TITLE = self.messages[event]['TITLE']
            self.MSG = self.messages[event]['MSG']
            self.TEMPLATE = self.messages[event]['TEMPLATE']
