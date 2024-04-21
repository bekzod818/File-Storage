from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import File


class FileUploadAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test_user", password="test_password"
        )
        self.client.force_authenticate(user=self.user)

    def test_file_upload(self):
        url = reverse("file-upload")
        file_content = open(f"{settings.BASE_DIR}/requirements.txt", "rb")
        data = {"name": "test_file", "file": file_content}
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class FileRetrieveUpdateDeleteAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test_user", password="test_password"
        )
        self.file = File.objects.create(name="test_file", file=None, owner=self.user)
        self.client.force_authenticate(user=self.user)

    def test_file_retrieve(self):
        url = reverse("file-delete", kwargs={"file_id": self.file.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.file.id)

    def test_file_update(self):
        url = reverse("file-delete", kwargs={"file_id": self.file.id})
        data = {"name": "updated_file_name"}
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "updated_file_name")

    def test_file_delete(self):
        url = reverse("file-delete", kwargs={"file_id": self.file.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class FileShareAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username="test_user1", password="test_password1"
        )
        self.user2 = User.objects.create_user(
            username="test_user2", password="test_password2"
        )
        self.file = File.objects.create(name="test_file", file=None, owner=self.user1)
        self.client.force_authenticate(user=self.user1)

    def test_file_share(self):
        url = reverse("file-share", kwargs={"file_id": self.file.id})
        data = {"user_ids": [self.user2.id]}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AuthenticatedAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test_user", password="test_password"
        )
        self.client.force_authenticate(user=self.user)

    def test_authenticated_access(self):
        # Test accessing an authenticated endpoint
        url = reverse("file-upload")  # Example endpoint that requires authentication
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_access(self):
        # Test accessing an unauthenticated endpoint
        self.client.force_authenticate(user=None)  # Force authentication to None
        url = reverse("file-upload")  # Example endpoint that requires authentication
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
