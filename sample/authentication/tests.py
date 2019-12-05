"""
Test cases for the whole authentication module
"""
import json
from django.urls.exceptions import NoReverseMatch
from django.test import TestCase
from django.urls import reverse
from django.core import mail
from rest_framework.authtoken.models import Token

from .models import User
from lib._test_utils import get_code, req_post, req_get


class AuthenticationTest(TestCase):
    REG_URL = reverse('users-api:register')
    LOGIN_URL = reverse('users-api:login')
    PASS_RESET_URL = reverse('reset-password')
    RESEND_ACT_URL = reverse('resend-activation')

    def setUp(self):
        # Control data for the test to be made
        User.objects._create('test@mail.com', 'Abcd123@')

    def test_register(self):
        user = User.objects.get(email='test@mail.com')
        # check test db for user
        self.assertIsNotNone(user)
        # check if user email is test@mail.com
        self.assertEqual('test@mail.com', 'test@mail.com')
        # test json body
        _info = {
            'email': None,
            'password': None,
            'confirm_password': None
        }
        # Post request
        response = req_post(self, {}, self.REG_URL)
        # Post request without passing any json data
        self.assertEqual(503, response.status_code)

        # Post request with empty values
        response = req_post(self, _info, self.REG_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code
        # Email already exist, password is required
        self.assertEqual(400, get_code(response))

        # Post request with email but without password
        _info['email'] = 'test@mail.com'
        response = req_post(self, _info, self.REG_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, Email already exist
        # or password is required
        self.assertEqual(400, get_code(response))

        # Post request with email with one password
        _info['email'] = 'test_1@mail.com'
        _info['password'] = 'abcd123'
        response = req_post(self, _info, self.REG_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, password length error
        # or password is required
        self.assertEqual(400, get_code(response))

        # Post request with email with 2 password, length < 8
        _info['password'] = 'abcd123'
        _info['confirm_password'] = 'abcd123'
        response = req_post(self, _info, self.REG_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, password length error
        self.assertEqual(400, get_code(response))

        # Post request with email with 2 password
        # password length < 8, confirm_password length == 8
        _info['password'] = 'abcd123'
        _info['confirm_password'] = 'abcd123@'
        response = req_post(self, _info, self.REG_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, password complexity error
        self.assertEqual(400, get_code(response))

        # Post request with email with 2 password
        # password length == 8, confirm_password length < 8
        _info['password'] = 'abcd123@'
        _info['confirm_password'] = 'abcd123'
        response = req_post(self, _info, self.REG_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, password complexity error
        self.assertEqual(400, get_code(response))

        # Post request with email with 2 password, 2 length = 8
        # no uppercase
        _info['password'] = 'abcd123@'
        _info['confirm_password'] = 'abcd123@'
        response = req_post(self, _info, self.REG_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, password complexity error
        self.assertEqual(400, get_code(response))

        # Post request with email with 2 password, 2 length = 8
        # all uppercase
        _info['password'] = 'ABCD123@'
        _info['confirm_password'] = 'ABCD123@'
        response = req_post(self, _info, self.REG_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, password complexity error
        self.assertEqual(400, get_code(response))

        # Post request with email with 2 password, 2 length = 8
        # no special characters
        _info['password'] = 'ABCD1234'
        _info['confirm_password'] = 'ABCD1234'
        response = req_post(self, _info, self.REG_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, password complexity error
        self.assertEqual(400, get_code(response))

        # Post request with incorrect email (comma separated emails)
        # matching password
        # 2 length = 8, correct password complexity
        _info['email'] = 'test_1@mail.com,test_2@mail.com'
        _info['password'] = 'Abcd123@'
        _info['confirm_password'] = 'Abcd123@'
        response = req_post(self, _info, self.REG_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, invalid email address
        self.assertEqual(400, get_code(response))

        # Post request with incorrect email (regex) and 2 matching password
        # 2 length = 8, correct password complexity
        _info['email'] = 'test_1@mail'
        _info['password'] = 'Abcd123@'
        _info['confirm_password'] = 'Abcd123@'
        response = req_post(self, _info, self.REG_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, invalid email address
        self.assertEqual(400, get_code(response))

        # Post request with incorrect email (XSS) and 2 matching password
        # 2 length = 8, correct password complexity
        _info['email'] = '\"<script>alert(\'foo\')</script>\"@example.com\"@example.com'
        _info['password'] = 'Abcd123@'
        _info['confirm_password'] = 'Abcd123@'
        response = req_post(self, _info, self.REG_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, invalid email address
        self.assertEqual(400, get_code(response))

        # Post request with incorrect email (XSS) and 2 matching password
        # 2 length = 8, correct password complexity
        _info['email'] = 'foo\'onclick=\'alert\'foo=\'@kk.com'
        _info['password'] = 'Abcd123@'
        _info['confirm_password'] = 'Abcd123@'
        response = req_post(self, _info, self.REG_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, invalid email address
        self.assertEqual(400, get_code(response))

        # Post request with correct email (regex) and 2 matching password
        # 2 length = 8, correct password complexity
        _info['email'] = 'test_1@mail.com'
        _info['password'] = 'Abcd123@'
        _info['confirm_password'] = 'Abcd123@'
        _info['role'] = 'user'
        response = req_post(self, _info, self.REG_URL)
        # Verify if response if 201
        self.assertEqual(201, response.status_code)

        # Check mail if sent
        self.assertEqual(len(mail.outbox), 1)
        # Get token from email
        emailBody = mail.outbox[0].message().get_payload()[1].as_string()
        token = emailBody.split('activate/')[1]
        # Removing other text as we need only the token from url
        token = token.split('/" ')[0]
        token_A, token_B, _ = token.split('/')
        # Verify title
        self.assertEqual('Activation email', mail.outbox[0].subject)
        # Verify to email address
        self.assertEqual(_info['email'], mail.outbox[0].to[0])
        # Verify from email address
        self.assertEqual('Sample <sample@gmail.com>', mail.outbox[0].from_email)

        # Get request without tokens
        with self.assertRaises(NoReverseMatch):
            self.client.get(reverse('activate-token-check', args=[]))
        # Get request with token_A only
        with self.assertRaises(NoReverseMatch):
            self.client.get(reverse('activate-token-check', args=[token_A]))
        # Get request with token_B only
        with self.assertRaises(NoReverseMatch):
            self.client.get(reverse('activate-token-check', args=[token_B]))

        # Get request invalid token_A
        invalid_A = token_A
        invalid_A += 'Abcd123'
        response = self.client.get(
                reverse('activate-token-check', args=[invalid_A, token_B]))
        # Verify status code 400
        self.assertEqual(400, response.status_code)
        # Verify err code, invalid token
        self.assertEqual(400, get_code(response))

        # Get request invalid token_B
        invalid_B = token_B
        invalid_B += 'Abcd123'
        response = self.client.get(
                reverse('activate-token-check', args=[token_A, invalid_B]))
        # Verify status code 400
        self.assertEqual(400, response.status_code)
        # Verify err code, invalid token
        self.assertEqual(400, get_code(response))

        # Get request invalid tokens
        response = self.client.get(
                reverse('activate-token-check', args=[invalid_A, invalid_B]))
        # Verify status code 400
        self.assertEqual(400, response.status_code)
        # Verify err code, invalid token
        self.assertEqual(400, get_code(response))

        # Get request to token check
        response = self.client.get(
                reverse('activate-token-check', args=[token_A, token_B]))
        # Verify status code 200
        self.assertEqual(200, response.status_code)
        # check if user is active
        user = User.objects.get(email=_info['email'])
        self.assertEqual(user.is_active, True)

        # check if login successfully
        _info = {
            'email': 'test_1@mail.com',
            'password': 'Abcd123@',
        }
        response = req_post(self, _info, self.LOGIN_URL)
        # Verify status code, 200
        self.assertEqual(200, response.status_code)
        self.token = response.data['data']['access']

        # check if token has changed on multiple logins
        response = req_post(self, _info, self.LOGIN_URL)
        token_A = response.data['data']['access']
        response = req_post(self, _info, self.LOGIN_URL)
        token_B = response.data['data']['access']
        self.assertNotEqual(token_A, token_B)

    def test_reset_password(self):
        _info = {
            'email': None
        }
        # request with get command
        response = self.client.get(self.PASS_RESET_URL)
        # verify status code, get not allowed
        self.assertEqual(405, response.status_code)

        # post with no email supplied
        response = req_post(self, _info, self.PASS_RESET_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, email not supplied
        self.assertEqual(400, get_code(response))

        # post with invalid email (regex)
        _info['email'] = 'test_1@mail'
        response = req_post(self, _info, self.PASS_RESET_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, invalid email
        self.assertEqual(400, get_code(response))

        # post with invalid email (csv)
        _info['email'] = 'test_1@mail.com,test_2@mail.com'
        response = req_post(self, _info, self.PASS_RESET_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, invalid email
        self.assertEqual(400, get_code(response))

        # post with email does not exist
        _info['email'] = 'test_1@mail.com'
        response = req_post(self, _info, self.PASS_RESET_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, email not supplied
        self.assertEqual(400, get_code(response))

        # post with registered email
        _info['email'] = 'test@mail.com'
        response = req_post(self, _info, self.PASS_RESET_URL)
        # Verify if response if 200
        self.assertEqual(200, response.status_code)
        # Check mail if sent
        self.assertEqual(len(mail.outbox), 1)
        # Get token from email
        emailBody = mail.outbox[0].message().get_payload()[1].as_string()
        token = emailBody.split('reset/')[1]
        # Removing other text as we need only the token from url
        token = token.split('/" ')[0]
        token_A, token_B, _ = token.split('/')
        # Verify title
        self.assertEqual('Reset Password Request', mail.outbox[0].subject)
        # Verify to email address
        self.assertEqual(_info['email'], mail.outbox[0].to[0])
        # Verify from email address
        self.assertEqual(
            'Sample <sample@gmail.com>', mail.outbox[0].from_email)

        # Get request without tokens
        with self.assertRaises(NoReverseMatch):
            self.client.get(reverse('reset-token-check', args=[]))

        # Get request with token_A only
        with self.assertRaises(NoReverseMatch):
            self.client.get(reverse('reset-token-check', args=[token_A]))

        # Get request with token_B only
        with self.assertRaises(NoReverseMatch):
            self.client.get(reverse('reset-token-check', args=[token_B]))

        # Get request invalid token_A
        invalid_A = token_A
        invalid_A += 'Abcd123'
        response = self.client.get(
                reverse('reset-token-check', args=[invalid_A, token_B]))
        # Verify status code 400
        self.assertEqual(400, response.status_code)
        # Verify err code, invalid token
        self.assertEqual(400, get_code(response))

        # # Get request invalid token_B
        invalid_B = token_B
        invalid_B += 'Abcd123'
        response = self.client.get(
                reverse('reset-token-check', args=[token_A, invalid_B]))
        # Verify status code 400
        self.assertEqual(400, response.status_code)
        # Verify err code, invalid token
        self.assertEqual(400, get_code(response))

        # Get request invalid tokens
        response = self.client.get(
                reverse('reset-token-check', args=[invalid_A, invalid_B]))
        # Verify status code 400
        self.assertEqual(400, response.status_code)
        # Verify err code, invalid token
        self.assertEqual(400, get_code(response))

        # Get request to token check
        response = self.client.get(
                reverse('reset-token-check', args=[token_A, token_B]))
        # Verify status code 200
        self.assertEqual(200, response.status_code)
        # Verify if token key is present
        self.assertIn('token', response.data['data'])
        # Verify return if equal to token_B
        self.assertEqual(token_B, response.data['data']['token'])

        # Change password json body
        _info = {
            'password': None,
            'confirm_password': None
        }

        # Change password post request without token
        with self.assertRaises(NoReverseMatch):
            req_post(self, {}, reverse('change-password', args=[]))

        # Post request with token, no password and confirm_password supplied
        response = req_post(
            self, _info, reverse('change-password', args=[token_B]))
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, no password supplied
        self.assertEqual(400, get_code(response))

        # Post with 1 password supplied only
        # length = 7, violates password complexity
        _info['password'] = 'abcd123'
        response = req_post(
            self, _info, reverse('change-password', args=[token_B]))
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, password length error
        # or password is required
        self.assertEqual(400, get_code(response))

        # Post with 1 password supplied only
        # length = 8, violates password complexity
        _info['password'] = 'abcd1234'
        response = req_post(
            self, _info, reverse('change-password', args=[token_B]))
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, password complexity error
        # or password is required
        self.assertEqual(400, get_code(response))

        # Post with 1 password supplied only
        # length = 8, password complexity
        _info['password'] = 'Abcd123@'
        response = req_post(
            self, _info, reverse('change-password', args=[token_B]))
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, password did not match
        # or password is required
        self.assertEqual(400, get_code(response))

        # Post with 2 password supplied
        # 1 length = 8, password complexity
        # 2 length < 8, violates password complexity
        _info['password'] = 'Abcd123@'
        _info['confirm_password'] = 'abcd123'
        response = req_post(
            self, _info, reverse('change-password', args=[token_B]))
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, password did not match
        self.assertEqual(400, get_code(response))

        # Post with 2 password supplied
        # 1 length = 8, password complexity
        # 2 length = 8, violates password complexity
        _info['password'] = 'Abcd123@'
        _info['confirm_password'] = 'abcd1234'
        response = req_post(
            self, _info, reverse('change-password', args=[token_B]))
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, password did not match
        self.assertEqual(400, get_code(response))

        # Post with 1 password supplied, confirm_password only
        # 1 none
        # 2 length = 8, violates password complexity
        _info['password'] = None
        _info['confirm_password'] = 'abcd1234'
        response = req_post(
            self, _info, reverse('change-password', args=[token_B]))
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, password is required
        self.assertEqual(400, get_code(response))

        # Post with 2 password supplied
        # 1 length = 8, password complexity
        # 2 length = 8, password complexity
        _info['password'] = 'Abcd123!'
        _info['confirm_password'] = 'Abcd123!'
        response = req_post(
            self, _info, reverse('change-password', args=[token_B]))
        # Verify if response if 400
        self.assertEqual(200, response.status_code)

        # Login json body
        _info = {
            'email': 'test@mail.com',
            'password': _info['password']
        }

        # TODO remove after activation function is done
        user = User.objects.get(email='test@mail.com')
        user.is_active = True
        user.save()
        # Login with new password
        response = req_post(self, _info, self.LOGIN_URL)
        # Verify status code, 200
        self.assertEqual(200, response.status_code)
        # Verify if token key is returned
        self.assertIn('access', response.data['data'])
        # Verify if token is not empty
        self.assertIsNotNone(json.dumps(response.data['data']['access']))

    def test_resend_activation(self):
        _info = {
            'email': None
        }
        # request with get command
        response = self.client.get(self.RESEND_ACT_URL)
        # verify status code, get not allowed
        self.assertEqual(405, response.status_code)

        # post with no email supplied
        response = req_post(self, _info, self.RESEND_ACT_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, email not supplied
        self.assertEqual(400, get_code(response))

        # post with invalid email (regex)
        _info['email'] = 'test_1@mail'
        response = req_post(self, _info, self.RESEND_ACT_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, invalid email
        self.assertEqual(400, get_code(response))

        # post with invalid email (csv)
        _info['email'] = 'test_1@mail.com,test_2@mail.com'
        response = req_post(self, _info, self.RESEND_ACT_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, invalid email
        self.assertEqual(400, get_code(response))

        # post with email does not exist
        _info['email'] = 'test_1@mail.com'
        response = req_post(self, _info, self.RESEND_ACT_URL)
        # Verify if response if 400
        self.assertEqual(400, response.status_code)
        # Verify error code, email not supplied
        self.assertEqual(400, get_code(response))

        # post with registered email
        _info['email'] = 'test@mail.com'
        response = req_post(self, _info, self.RESEND_ACT_URL)
        # Verify if response if 200
        self.assertEqual(200, response.status_code)
        # Check mail if sent
        self.assertEqual(len(mail.outbox), 1)
        # Get token from email
        emailBody = mail.outbox[0].message().get_payload()[1].as_string()
        token = emailBody.split('activate/')[1]
        # Removing other text as we need only the token from url
        token = token.split('/" ')[0]
        token_A, token_B, _ = token.split('/')
        # Verify title
        self.assertEqual('Activation Email Request', mail.outbox[0].subject)
        # Verify to email address
        self.assertEqual(_info['email'], mail.outbox[0].to[0])
        # Verify from email address
        self.assertEqual(
            'Sample <sample@gmail.com>', mail.outbox[0].from_email)

