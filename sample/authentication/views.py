import json
from collections import OrderedDict
from django.views.decorators.cache import never_cache
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model, login
from django.core.signing import SignatureExpired, BadSignature
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import (
    APIException,
    ValidationError,
    PermissionDenied
)
from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    EmailSerializer,
    PasswordChangeSerializer,
    ChangeRoleSerializer,
)
from axes.attempts import is_already_locked
from rest_framework_simplejwt.tokens import RefreshToken
from utils.messages import ERR, SCS, EMAIL
from utils.custom_exceptions import InternalError
from utils.res_handler import CustomResponseLog
from utils.create_email import make_email
from .auth_tokens import (
    generate_token,
    token_generator,
    token_decoder,
    token_decoder2
)
from .models import UserActivationResetToken as OTToken

User = get_user_model()


def _save_tokens(user, token_A, token_B, event):
    """
    Saves the tokens generated upon registration
    reset password and resend activation email.

    Parameters:
        user: (obj)
        token_A: (str)
        token_B: (str)
        event: (str) from which event it was generated

    Returns:
        dict
    """
    tokenInfo = OrderedDict()
    tokenInfo['uuid'] = user
    tokenInfo['token_a'] = token_A
    tokenInfo['token_b'] = token_B
    tokenInfo['event'] = event
    OTToken.objects.save_tokens(**tokenInfo)


class APILogin(APIView):

    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def get_jwt_token(self, user):
        authTokens = RefreshToken.for_user(user)
        return authTokens

    def post(self, request):
        try:
            userInfo = self.serializer_class(
                    data=request.data,
                    context=request)
            userInfo.is_valid(raise_exception=True)
            user = userInfo.validated_data['user']
            login(request, user, backend='axes.backends.AxesModelBackend')
            jwtToken = self.get_jwt_token(user)
            res = OrderedDict
            res = {
                'access': str(jwtToken.access_token),
                'refresh': str(jwtToken) 
            }
            res = CustomResponseLog(self, request, res)
            return Response(res.custom_response())
        except ValidationError:
            raise
        except Exception as e:
            if is_already_locked(request):
                raise PermissionDenied(ERR.PERMISSION_DENIED)
            else:
                raise InternalError(ERR.SERVER_ERROR, str(e))


class APILogout(APIView):
    """
    Logout API
    Due to the app uses JWT, only the frontend can delete the
    token to invalidate the users.
    """
    permission_classes = [AllowAny,]

    def logout(self, request):
        if not request.META.get('HTTP_AUTHORIZATION'):
            raise PermissionDenied(ERR.PERMISSION_DENIED)
        res = CustomResponseLog(self, request, SCS.LOGOUT)
        return Response(res.custom_response())

    def post(self, request):
        return self.logout(request)


class APIRegister(APIView):

    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            userInfo = self.serializer_class(data=request.data,
                        context=request.data['confirm_password'])
            userInfo.is_valid(raise_exception=True)
            user = User.objects.save_user(**userInfo.data)
            if user:
                res = SCS.REGISTER
            else:
                raise Exception
            token_A, token_B = token_generator(user)
            tokenInfo = OrderedDict()
            tokenInfo['token_A'] = token_A
            tokenInfo['token_B'] = token_B
            msg = EMAIL('REGISTER')
            _save_tokens(user, token_A, token_B, OTToken.ACTIVATE)
            make_email(msg.TITLE, msg.MSG, user.email,
                        msg.TEMPLATE, tokenInfo, request)
            res = CustomResponseLog(self, request, res)
            return Response(res.custom_response(), status=201)
        except ValidationError:
            raise
        except Exception as e:
            raise InternalError(ERR.SERVER_ERROR, str(e))


class APIResetPassword(APIView):

    serializer_class = EmailSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            userInfo = self.serializer_class(data=request.data)
            userInfo.is_valid(raise_exception=True)
            email = userInfo.data['email']
            user = User.objects.get(email=email)
            OTToken.objects.invalidate_token(user, OTToken.RESETPASS)
            token_A, token_B = token_generator(user)
            tokenInfo = OrderedDict()
            tokenInfo['token_A'] = token_A
            tokenInfo['token_B'] = token_B
            _save_tokens(user, token_A, token_B, OTToken.RESETPASS)
            msg = EMAIL('RESET')
            make_email(msg.TITLE, msg.MSG, user.email,
                        msg.TEMPLATE, tokenInfo, request)
            res = CustomResponseLog(self, request)
            return Response(res.custom_response())
        except ValidationError:
            raise
        except Exception as e:
            raise InternalError(ERR.SERVER_ERROR, str(e))


class APIChangePassword(APIView):

    serializer_class = PasswordChangeSerializer
    permission_classes = [AllowAny,]

    def post(self, request, token):
        try:
            user, token = token_decoder2(token, ERR.RST_PSW_INVALID)
            if not generate_token.check_token(user, token):
                raise ValidationError(ERR.RST_PSW_INVALID)
            if 'confirm_password' not in request.data:
                raise ValidationError(ERR.PASS_NOT_MATCH)
            userInfo = self.serializer_class(data=request.data,
                        context=request.data['confirm_password'])
            userInfo.is_valid(raise_exception=True)
            user.set_password(userInfo.validated_data['confirm_password'])
            user.save()
            OTToken.objects.update_used(user, token, OTToken.RESETPASS)
            res = CustomResponseLog(
                    self, request, SCS.PSW_RESET, user.email)
            return Response(res.custom_response())
        except ValidationError:
            raise
        except SignatureExpired:
            raise ValidationError(ERR.RST_PSW_EXPIRED)
        except BadSignature:
            raise ValidationError(ERR.RST_PSW_INVALID)
        except Exception as e:
            raise InternalError(ERR.SERVER_ERROR, str(e))


class ResetTokenURL(APIView):
    """
    This checks the token from the email reset password if 
    it is correct or existing in the database.
    """
    permission_classes = [AllowAny,]

    @never_cache
    def get(self, request, token_A, token_B):
        try:
            user, token = token_decoder(token_A, ERR.RST_PSW_INVALID)
            if not generate_token.check_token(user, token):
                raise ValidationError(ERR.RST_PSW_INVALID)
            confirm_user, confirm_token = token_decoder2(
                                        token_B, ERR.RST_PSW_INVALID)
            if not generate_token.check_token(confirm_user, confirm_token):
                raise ValidationError(ERR.RST_PSW_INVALID)
            tokenInfo = OrderedDict()
            tokenInfo['token'] = token_B
            res = CustomResponseLog(self, request, tokenInfo, user.email)
            return Response(res.custom_response(), status=200)
        except ValidationError:
            raise
        except SignatureExpired:
            raise ValidationError(ERR.RST_PSW_EXPIRED)
        except BadSignature:
            raise ValidationError(ERR.RST_PSW_INVALID)
        except Exception as e:
            raise InternalError(ERR.SERVER_ERROR, str(e))


class UserActivationUrl(APIView):
    """
    This checks the token from the user acitvation link if 
    it is correct or existing in the database.
    """
    permission_classes = [AllowAny,]

    @never_cache
    def get(self, request, token_A, token_B):
        try:
            user, token = token_decoder(token_A, ERR.ACTIVATION_INVALID)
            if not generate_token.check_token(user, token):
                raise ValidationError(ERR.ACTIVATION_INVALID)
            confirm_user, confirm_token = token_decoder2(
                                        token_B, ERR.ACTIVATION_INVALID)
            if not generate_token.check_token(confirm_user, confirm_token):
                raise ValidationError(ERR.ACTIVATION_INVALID)
            user.is_active = True
            user.save()
            userInfo = OrderedDict()
            userInfo['email'] = user.email
            OTToken.objects.update_used(user, token, OTToken.ACTIVATE)
            res = CustomResponseLog(self, request, {}, user.email)
            return Response(res.custom_response(), status=200)
        except SignatureExpired:
            raise ValidationError(ERR.ACTIVATION_EXPIRED)
        except BadSignature:
            raise ValidationError(ERR.ACTIVATION_INVALID)
        except ValidationError:
            raise
        except Exception as e:
            raise Exception(ERR.SERVER_ERROR, str(e))


class APIResendActivation(APIView):
    """
    Resend Activation Email
    """
    permission_classes = [AllowAny,]
    serializer_class = EmailSerializer

    def post(self, request):
        try:
            # validate email address
            emailInfo = self.serializer_class(data=request.data)
            emailInfo.is_valid(raise_exception=True)
            email = emailInfo.validated_data.get('email', '')
            user = User.objects.get(email=email)
            token_A, token_B = token_generator(user)
            tokenInfo = OrderedDict()
            tokenInfo['token_A'] = token_A
            tokenInfo['token_B'] = token_B
            msg = EMAIL('ACTV_RESEND')
            _save_tokens(user, token_A, token_B, OTToken.ACTIVATE)
            make_email(msg.TITLE, msg.MSG, user.email,
                        msg.TEMPLATE, tokenInfo, request)
            res = CustomResponseLog(self, request, SCS.ACTV_SENT)
            return Response(res.custom_response(), status=200)
        except ValidationError:
            raise
        except Exception as e:
            raise Exception(ERR.SERVER_ERROR, str(e))


class APIUserDetail(APIView):
    """
    To demonstrate if JWT truly works.
    Only authenticated users can see the response of this endpoint
    """
    serializer_class = ChangeRoleSerializer
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        try:
            email = request.user.email
            user = User.objects.get(email=email)
            userInfo = OrderedDict()
            userInfo['email'] = email
            userInfo['role'] = user.role
            userInfo['last_login'] = str(user.last_login)
            res = CustomResponseLog(self, request, userInfo) 
            return Response(res.custom_response(), status=200)
        except ValidationError:
            raise
        except Exception as e:
            raise Exception(ERR.SERVER_ERROR, str(e))

    def post(self, request):
        try:
            userInfo = self.serializer_class(data=request.data)
            userInfo.is_valid(raise_exception=True)
            userObj = User.objects.get(email=request.user.email)
            role = userInfo.validated_data['role']
            User.objects.update_role(userObj, role)
            res = CustomResponseLog(self, request, SCS.ROLE_UPDATED)
            return Response(res.custom_response(), status=200)
        except ValidationError:
            raise
        except Exception as e:
            raise Exception(ERR.SERVER_ERROR, str(e))

