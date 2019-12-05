from os import urandom
from datetime import timedelta
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from django.utils.http import (
    int_to_base36, urlsafe_base64_encode, urlsafe_base64_decode
)
from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils.crypto import salted_hmac
from django.utils.encoding import force_bytes, force_text
from django.core.signing import TimestampSigner
from rest_framework.exceptions import ValidationError

from sample.settings.settings import SECRET_SALT
from authentication.models import User


class TokenGenerator(PasswordResetTokenGenerator):
    """ Creates hash for user authentication """
    def _make_hash_value(self, user, timestamp):
        """
        Encrypts user and timestamp to be use in the authentication link
        """
        return (
            six.text_type(user.uuid) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )

    def _make_token_with_timestamp(self, user, timestamp):
        # timestamp is number of days since 2001-1-1.  Converted to
        # base 36, this gives us a 3 digit string until about 2121
        ts_b36 = int_to_base36(timestamp)
        hash = salted_hmac(
            self.key_salt,
            self._make_hash_value(user, timestamp),
        ).hexdigest()[:100]
        return "%s-%s" % (ts_b36, hash)


generate_token = TokenGenerator()


def token_generator(user):
    """
    custom token generator
    :Parameters:
        user : User
    :Returns:
        token_A : (str)
        token_B : (str)
    """
    _hash = generate_token.make_token(user)
    RANDOM_CODE = urandom(32).hex()
    signer = TimestampSigner(salt=SECRET_SALT)
    tokenHash = urlsafe_base64_encode(
                force_bytes(
                    str(user.uuid) + ':' + RANDOM_CODE + '|' + _hash))
    tokenHash = signer.sign(tokenHash)
    token_A = urlsafe_base64_encode(
                force_bytes(tokenHash))
    tokenB_Hash = signer.sign(_hash)
    token_B = urlsafe_base64_encode(
                force_bytes(':'.join([str(user.uuid), tokenB_Hash])))

    return token_A, token_B


def token_decoder(token_A, _err_code=None):
    """
    decoder for token_A
    :Parameters:
        token_A : (str)
        _err_code : (str)
    :Returns:
        user : User object
        token : (str)
    """
    signer = TimestampSigner(salt=SECRET_SALT)
    try:
        tokenHash = force_text(
                    urlsafe_base64_decode(token_A))
    except DjangoUnicodeDecodeError:
        raise ValidationError(_err_code)
    except(ValueError):
        # This is for the unhandled exceptions
        raise ValidationError(_err_code)
    tokenHash = signer.unsign(tokenHash, max_age=timedelta(days=1))
    uid = force_text(urlsafe_base64_decode(tokenHash))
    _id = uid.split(':')[0]
    token = uid.split('|')[1]
    user = User.objects.get(uuid=_id)
    return user, token


def token_decoder2(token_B, _err_code=None):
    """
    decoder for token_B
    :Parameters:
        token_B : (str)
        _err_code : (str)
    :Returns:
        user : User object
        token : (str)
    """
    signer = TimestampSigner(salt=SECRET_SALT)
    try:
        uid = force_text(urlsafe_base64_decode(token_B))
    except DjangoUnicodeDecodeError:
        raise ValidationError(_err_code)
    except(ValueError):
        # This is for the unhandled exceptions
        raise ValidationError(_err_code)
    _id = uid.split(':')[0]
    _hash = ':'.join(uid.split(':')[1:])
    token = signer.unsign(_hash, max_age=timedelta(days=1))
    user = User.objects.get(uuid=_id)
    return user, token
