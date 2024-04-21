from django.urls import path

from .views import (
    FileListUploadAPIView,
    FileRetrieveUpdateDeleteAPIView,
    FileShareAPIView,
    GroupListCreateAPIView,
    GroupRetrieveUpdateDeleteAPIView,
    UserLoginAPIView,
    UserRegistrationAPIView,
)

urlpatterns = [
    path("register/", UserRegistrationAPIView.as_view(), name="user-register"),
    path("login/", UserLoginAPIView.as_view(), name="user-login"),
    path("upload/", FileListUploadAPIView.as_view(), name="file-upload"),
    path("groups/", GroupListCreateAPIView.as_view(), name="groups-list-create"),
    path(
        "group/<int:group_id>/",
        GroupRetrieveUpdateDeleteAPIView.as_view(),
        name="group-retrieve-update-delete",
    ),
    path(
        "file/<int:file_id>/",
        FileRetrieveUpdateDeleteAPIView.as_view(),
        name="file-delete",
    ),
    path("share/<int:file_id>/", FileShareAPIView.as_view(), name="file-share"),
]
