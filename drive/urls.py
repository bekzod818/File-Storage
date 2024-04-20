from django.urls import path

from .views import FileDeleteAPIView, FileShareAPIView, FileUploadAPIView

urlpatterns = [
    path("upload/", FileUploadAPIView.as_view(), name="file-upload"),
    path("delete/<int:file_id>/", FileDeleteAPIView.as_view(), name="file-delete"),
    path("share/<int:file_id>/", FileShareAPIView.as_view(), name="file-share"),
]
