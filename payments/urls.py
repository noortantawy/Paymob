from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import *

urlpatterns = [
    path("auth/token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("pay", PayView.as_view(), name="pay"),
    path("pay/tcp", PayTcpView.as_view(), name="pay_tcp"),  # same as /pay but over TCP
]
