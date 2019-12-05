import re, requests, json
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, Serializer
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ObjectDoesNotExist
from utils.messages import ERR

User = get_user_model()
STRONG_PASS = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})"
VALID_EMAIL = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
# alphabets, space, dash, period only
NAME_PASS = r"^[a-zA-Z \-\.]*$"
USERNAME_VALID = r"^[a-zA-Z0-9-_]+$"


class UserRegisterSerializer(Serializer):

    email = serializers.EmailField(
        error_messages = {
            'null': ERR.EMAIL_PASS_NULL,
            'blank': ERR.EMAIL_PASS_NULL,
            'required': ERR.EMAIL_FIELD_MISSING,
        }
    )
    password = serializers.CharField(
        error_messages = {
            'null': ERR.EMAIL_PASS_NULL,
            'blank': ERR.EMAIL_PASS_NULL,
            'required': ERR.PASS_FIELD_MISSING,
        }
    )
    confirm_password = serializers.CharField(
        error_messages = {
            'null': ERR.EMAIL_PASS_NULL,
            'blank': ERR.EMAIL_PASS_NULL,
            'required': ERR.PASS_FIELD_MISSING,
        }
    )
    role = serializers.CharField()

    class Meta:
        model = User
        fields = ('email', 'password', 'role', 'confirm_password')

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise ValidationError(ERR.EMAIL_EXIST)
        if not re.match(VALID_EMAIL, email):
            raise ValidationError(ERR.EMAIL_INVALID)
        return email
    
    def validate_password(self, password):
        confirm_password = self.context
        if len(password) < 8:
            raise ValidationError(ERR.PASS_LEN_INVALID)
        if not re.match(STRONG_PASS, password):
            raise ValidationError(ERR.PASS_STR_INVALID)
        if password != confirm_password:
            raise ValidationError(ERR.PASS_NOT_MATCH)
        return password

    def validate_role(self, role):
        if role != User.R_USER and role != User.R_ADMIN \
            and role != User.R_SUPER:
            raise ValidationError(ERR.ROLE_INVALID)
        return role


class UserLoginSerializer(ModelSerializer):
    
    verify_email = None

    email = serializers.EmailField(
        error_messages = {
            'null': ERR.EMAIL_PASS_NULL,
            'blank': ERR.EMAIL_PASS_NULL,
            'required': ERR.EMAIL_FIELD_MISSING,
        }
    )
    password = serializers.CharField(
        error_messages = {
            'null': ERR.EMAIL_PASS_NULL,
            'blank': ERR.EMAIL_PASS_NULL,
            'required': ERR.PASS_FIELD_MISSING,
        }
    )

    class Meta:
        model = User
        fields = ('email', 'password',)

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise ValidationError(ERR.USER_NOT_EXIST)
        if not email:
            raise ValidationError(ERR.EMAIL_PASS_NULL)
        if not re.match(VALID_EMAIL, email):
            raise ValidationError(ERR.EMAIL_PASS_NULL)
        self.verify_email = email
        return email

    def validate_password(self, password):
        if not password:
            raise ValidationError(ERR.EMAIL_PASS_NULL)
        try:
            user = User.objects.get(email=self.verify_email)
            if not user.check_password(password):
                raise ValidationError(ERR.LOGIN_INVALID)
        except ObjectDoesNotExist:
            # Already raised in validate_email, no need to raise again
            pass
        return password

    def _validate_email(self, email, password):
        user = None
        if email and password:
            user = authenticate(
                self.context, email=email, password=password)
        return user

    def validate(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')

        user = None
        email = self.validate_email(email)
        password = self.validate_password(password)
        if email and password:
            user = self._validate_email(email, password)
        if not user:
            if not User.objects.get(email=email).is_active:
                raise ValidationError(ERR.USER_INACTIVE)
        validated_data['user'] = user
        return validated_data


class EmailSerializer(Serializer):
    
    email = serializers.EmailField(
        error_messages = {
            'null': ERR.EMAIL_INVALID,
            'blank': ERR.EMAIL_INVALID,
            'required': ERR.EMAIL_FIELD_MISSING,
        }
    )

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise ValidationError(ERR.USER_NOT_EXIST)
        if not email:
            raise ValidationError(ERR.EMAIL_PASS_NULL)
        if not re.match(VALID_EMAIL, email):
            raise ValidationError(ERR.EMAIL_PASS_NULL)
        return email


class PasswordChangeSerializer(ModelSerializer):
    password = serializers.CharField(
        error_messages = {
            'blank': ERR.PASS_INVALID,
            'null': ERR.PASS_INVALID,
            'required': ERR.PASS_FIELD_MISSING,
        }
    )
    confirm_password = serializers.CharField(
        error_messages = {
            'blank': ERR.PASS_INVALID,
            'null': ERR.PASS_INVALID,
            'required': ERR.PASS_FIELD_MISSING,
        }
    )

    class Meta:
        model = User
        fields = ('password', 'confirm_password',)

    def validate_password(self, password):
        confirm_password = self.context
        if len(password) < 8:
            raise ValidationError(ERR.PASS_LEN_INVALID)
        if not re.match(STRONG_PASS, password):
            raise ValidationError(ERR.PASS_STR_INVALID)
        if password != confirm_password:
            raise ValidationError(ERR.PASS_NOT_MATCH)
        return password


class ChangeRoleSerializer(Serializer):
    role = serializers.CharField(
        error_messages = {
            'blank': ERR.ROLE_INVALID,
            'null': ERR.ROLE_INVALID,
            'required': ERR.ROLE_INVALID,
        }
    )

    def validate_role(self, role):
        roles = [User.R_ADMIN, User.R_SUPER, User.R_USER]
        if not role in roles:
            raise ValidationError(ERR.ROLE_INVALID)
        return role
