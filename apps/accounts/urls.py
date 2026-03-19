from django.urls import path

from apps.accounts.presentation.views import (
    UserChangePasswordAPIView,
    UserDeactivateAPIView,
    UserDetailAPIView,
    UserListCreateAPIView,
)

urlpatterns = [
    path("users/", UserListCreateAPIView.as_view(), name="user-list-create"),
    path("users/<int:user_id>/", UserDetailAPIView.as_view(), name="user-detail"),
    path(
        "users/<int:user_id>/deactivate/", UserDeactivateAPIView.as_view(), name="user-deactivate"
    ),
    path(
        "users/<int:user_id>/change-password/",
        UserChangePasswordAPIView.as_view(),
        name="user-change-password",
    ),
]
