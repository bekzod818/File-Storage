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
from .serializers import FileSerializer, SharingUserSerializer, UserSerializer


class FileUploadAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FileSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FileDeleteAPIView(APIView):
    permission_classes = (
        IsAuthenticated,
        IsOwnerOrReadOnly,
    )
    serializer_class = FileSerializer

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
    serializer_class = SharingUserSerializer

    def post(self, request, file_id, *args, **kwargs):
        file_obj = get_object_or_404(File, id=file_id)
        self.check_object_permissions(request, file_obj)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        users = User.objects.filter(id__in=serializer.validated_data["user_ids"])
        for user in users:
            Sharing.objects.create(
                file=file_obj, shared_with=user, shared_by=request.user
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
