from django.conf.urls import url, include
from rest_framework_simplejwt.views import TokenRefreshView
from authentication.views import (
    APIChangePassword,
    APIResetPassword,
    APIResendActivation,
    ResetTokenURL,
    UserActivationUrl,
    APILogout,
)


urlpatterns = [
    url(r'^logout/$', APILogout.as_view(), name='logout'),
    url(r'^resend_activation/$', APIResendActivation.as_view(), name='resend-activation'),
    url(r'^reset_password/$', APIResetPassword.as_view(), name='reset-password'),
    url(r'^change_password/(?P<token>[0-9A-Za-z]{1,250})/$', APIChangePassword.as_view(), name='change-password'),
    url(r'^activate/(?P<token_A>[0-9A-Za-z]{1,350})/(?P<token_B>[0-9A-Za-z]{1,250})/$', UserActivationUrl.as_view(), name='activate-token-check'),
    url(r'^reset/(?P<token_A>[0-9A-Za-z]{1,350})/(?P<token_B>[0-9A-Za-z]{1,250})/$', ResetTokenURL.as_view(), name='reset-token-check'),
    url(r'^api/token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
    url(r'^api/users/', include(('authentication.urls', 'authentication'), namespace='users-api')),
]
