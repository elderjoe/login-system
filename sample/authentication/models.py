from uuid import uuid4
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from rest_framework.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from utils.messages import ERR


class UserManager(BaseUserManager):

    def _create(self, email, password, **kwargs):
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def _get_email_password(self, **kwargs):
        email = kwargs.get('email')
        password = kwargs.get('password')
        del kwargs['email']
        del kwargs['password']
        if not email or not password:
            raise ValidationError(_(ERR.EMAIL_PASS_NULL))
        return email, password, kwargs

    def save_user(self, **kwargs):
        del kwargs['confirm_password']
        if kwargs.get('role') != 'user':
            raise ValidationError(_(ERR.ROLE_USER_INVALID))
        email, password, userInfo = self._get_email_password(**kwargs)
        return self._create(email, password, **userInfo)
    
    def save_admin(self, **kwargs):
        if kwargs.get('role') != 'admin':
            raise ValidationError(_(ERR.ROLE_ADMIN_INVALID))
        email, password, userInfo = self._get_email_password(**kwargs)
        return self._create(email, password, **userInfo)
    
    def save_superuser(self, **kwargs):
        if kwargs.get('role') != 'superadmin':
            raise ValidationError(_(ERR.ROLE_SUPER_INVALID))
        email, password, userInfo = self._get_email_password(**kwargs)
        return self._create(email, password, **userInfo)

    def update_role(self, _model, role):
        _model.role = role
        _model.save()
        return _model


class User(AbstractBaseUser):

    R_USER, R_ADMIN, R_SUPER = ['user', 'admin', 'superadmin']
    ROLES = (
        (R_USER, 'USER'),
        (R_ADMIN, 'ADMIN'),
        (R_SUPER, 'SUPERADMIN'),
    )
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(null=False, blank=False, unique=True)
    password = models.CharField(max_length=256, null=False, blank=False)
    is_active = models.BooleanField(default=False)
    role = models.CharField(max_length=12, choices=ROLES, default=R_USER)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)

    USERNAME_FIELD = 'email'

    class META:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    objects = UserManager()


class ActivationResetManager(models.Manager):

    def save_tokens(self, **kwargs):
        tokenInfo = self.model(**kwargs)
        tokenInfo.save()

    def update_used(self, user, token, event):
        try:
            tokenInfo = self.model.objects.get(
                            uuid=user, used=False, event=event)
            tokenInfo.used = True
            tokenInfo.save()
        except ObjectDoesNotExist:
            # Special case, have to pass the user object to get
            # the email address.
            raise ValidationError(ERR.LINK_USED, user)
    
    def invalidate_token(self, user, event):
        tokenInfo = self.model.objects.filter(
                        uuid=user, used=False, event=event)
        if len(tokenInfo) >= 1:
            for tokens in tokenInfo:
                tokens.used = True
                tokens.save()


class UserActivationResetToken(models.Model):
    """
        To record the tokens created in registration and reset password.
        This will invalidate the tokens once used. Using the default
        functionality, token is still usable even it has been used so doing
        this will prevent that events.
    """    
    RESETPASS, ACTIVATE = ['resetpassword', 'activate']
    EVENTS = (
        (RESETPASS, 'RESETPASSWORD'),
        (ACTIVATE, 'ACTIVATE'),
    )
    uuid = models.ForeignKey(User, on_delete=models.CASCADE)
    token_a = models.TextField(null=True, blank=True)
    token_b = models.TextField(null=True, blank=True)
    event = models.CharField(max_length=15, choices=EVENTS, default=RESETPASS)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)

    objects = ActivationResetManager()

    class Meta:
        db_table = 'useractivationresettoken'
