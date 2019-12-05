# Sample Login System
This repository is intentionally created to simulate or be a base code for the generic functionalities implemented in the simplest possible way.  
- Login
- Register
- Reset and Change Password
- Resend Activation Email
- Update User Detail

## Requirements
- Python 3.5.7
- MySQL server

## How to setup
It is best to install a virtual environment for development. You may use
virtualenv or pipenv.
- (USING VIRTUALENV) `pip install -r requirements.txt`
- (USING PIPENV) `pipenv install`

## Notes
- The provided API endpoints `Insomnia-request-api.json` can only be used in Insomnia. Download it
[here](https://insomnia.rest/download/)
- Default database engine is MySQL so just change the configuration in `sample/settings/local.py` to use your own.
- Emails are printed in console unless the configuration is change in `sample/settings/local.py`
- In update user detail, only role can be updated.

## Testing
To test, use `manage.py test`
