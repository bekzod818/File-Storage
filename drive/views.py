from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import File, Sharing
from .serializers import FileSerializer, UserSerializer


class FileUploadAPIView(APIView):
    def post(self, request, format=None):
        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)  # Assign the owner as the current user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileDeleteAPIView(APIView):
    def delete(self, request, file_id, format=None):
        try:
            file_obj = File.objects.get(id=file_id)
            # Check permissions if needed
            if file_obj.owner == request.user:  # Check if the user owns the file
                file_obj.delete()
                return Response(
                    "File deleted successfully", status=status.HTTP_204_NO_CONTENT
                )
            else:
                return Response(
                    "You do not have permission to delete this file",
                    status=status.HTTP_403_FORBIDDEN,
                )
        except File.DoesNotExist:
            return Response("File not found", status=status.HTTP_404_NOT_FOUND)


class FileShareAPIView(APIView):
    def post(self, request, file_id, format=None):
        try:
            file_obj = File.objects.get(id=file_id)
            shared_with_users = request.data.getlist(
                "shared_with_users"
            )  # Assuming you receive a list of user IDs to share with
            for user_id in shared_with_users:
                shared_user = User.objects.get(id=user_id)
                Sharing.objects.create(
                    file=file_obj, shared_with=shared_user, shared_by=request.user
                )
            return Response("File shared successfully", status=status.HTTP_201_CREATED)
        except File.DoesNotExist:
            return Response("File not found", status=status.HTTP_404_NOT_FOUND)


class UserRegistrationAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = (
        UserSerializer  # Assuming you have a serializer for user registration
    )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response


class UserLoginAPIView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
