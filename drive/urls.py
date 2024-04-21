from django.urls import path

from .views import (
    FileDeleteAPIView,
    FileShareAPIView,
    FileUploadAPIView,
    UserLoginAPIView,
    UserRegistrationAPIView,
)

urlpatterns = [
    path("register/", UserRegistrationAPIView.as_view(), name="user-register"),
    path("login/", UserLoginAPIView.as_view(), name="user-login"),
    path("upload/", FileUploadAPIView.as_view(), name="file-upload"),
    path("delete/<int:file_id>/", FileDeleteAPIView.as_view(), name="file-delete"),
    path("share/<int:file_id>/", FileShareAPIView.as_view(), name="file-share"),
]
