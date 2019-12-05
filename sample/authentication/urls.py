from django.conf.urls import url
from .views import (
    APILogin,
    APIRegister,
    APIUserDetail,
)

urlpatterns = [
    url(r'^login/$', APILogin.as_view(), name='login'),
    url(r'^register/$', APIRegister.as_view(), name='register'),
    url(r'^user-detail/$', APIUserDetail.as_view(), name='user-detail'),
]