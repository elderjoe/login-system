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
Install the webdrivers first before running the selenium testing
`sudo apt-get install chromium-chromedriver`

To test the APIs, use `manage.py test`
For the selenium, use `manage.py test authentication.test_web`

## Test Notes
- Although this repo does not have any Frontend (could be added in the future), the selenium script
shows my implementation. There are other ways to implement the code so this just serves as reference.
- The `test_web.py` was used to test a certain domain so elements should be edited to support the other websites.
- The Selenium part was done in WSL (Ubuntu).