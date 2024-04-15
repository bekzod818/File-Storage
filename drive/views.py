from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import File, Sharing
from .permissions import IsOwnerOrReadOnly
from .serializers import FileSerializer, UserSerializer


class FileUploadAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = FileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FileDeleteAPIView(APIView):
    permission_classes = (
        IsAuthenticated,
        IsOwnerOrReadOnly,
    )

    def delete(self, request, file_id, *args, **kwargs):
        file_obj = get_object_or_404(File, id=file_id)
        # Check permissions if needed
        self.check_object_permissions(request, file_obj)
        file_obj.delete()
        return Response("File deleted successfully", status=status.HTTP_204_NO_CONTENT)


class FileShareAPIView(APIView):
    permission_classes = (
        IsAuthenticated,
        IsOwnerOrReadOnly,
    )

    def post(self, request, file_id, *args, **kwargs):
        file_obj = get_object_or_404(File, id=file_id)
        self.check_object_permissions(request, file_obj)
        shared_with_users = request.data.getlist(
            "shared_with_users"
        )  # Assuming you receive a list of user IDs to share with
        for user_id in shared_with_users:
            shared_user = User.objects.filter(id=user_id).first()
            if shared_user:
                Sharing.objects.create(
                    file=file_obj, shared_with=shared_user, shared_by=request.user
                )
        return Response("File shared successfully", status=status.HTTP_201_CREATED)


class UserRegistrationAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_201_CREATED)


class UserLoginAPIView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_200_OK)
