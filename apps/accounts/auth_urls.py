from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.auth_views import CurrentUserAPIView, LoginView


class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


urlpatterns = [
    path("token/", LoginView.as_view(), name="token-obtain"),
    path("token/refresh/", RefreshView.as_view(), name="token-refresh"),
    path("me/", CurrentUserAPIView.as_view(), name="current-user"),
]
