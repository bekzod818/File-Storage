from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import File, Group, Sharing
from .permissions import IsOwnerOrCheckPermission, IsOwnerOrReadOnly
from .serializers import (
    FileSerializer,
    GroupSerializer,
    SharingUserSerializer,
    UserSerializer,
)


class FileListUploadAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FileSerializer

    def get(self, request, *args, **kwargs):
        files = File.objects.filter(owner=request.user)
        serializer = self.serializer_class(files, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FileRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = (
        IsAuthenticated,
        IsOwnerOrCheckPermission,
    )
    serializer_class = FileSerializer

    def get(self, request, file_id, *args, **kwargs):
        file_obj = get_object_or_404(File, pk=file_id)
        # Check permissions
        self.check_object_permissions(request, file_obj)
        serializer = self.serializer_class(file_obj)
        return Response(serializer.data)

    def put(self, request, file_id, *args, **kwargs):
        file_obj = get_object_or_404(File, pk=file_id)
        # Check permissions
        self.check_object_permissions(request, file_obj)
        serializer = self.serializer_class(file_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, file_id, *args, **kwargs):
        file_obj = get_object_or_404(File, id=file_id)
        # Check permissions
        self.check_object_permissions(request, file_obj)
        file_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FileShareAPIView(APIView):
    permission_classes = (
        IsAuthenticated,
        IsOwnerOrCheckPermission,
    )
    serializer_class = SharingUserSerializer

    def post(self, request, file_id, *args, **kwargs):
        file_obj = get_object_or_404(File, id=file_id)
        # Check permissions
        self.check_object_permissions(request, file_obj)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        users = User.objects.filter(id__in=serializer.validated_data["user_ids"])
        # Create a list of Sharing objects to be bulk created
        sharing_objects = [
            Sharing(shared_file=file_obj, shared_with=user, shared_by=request.user)
            for user in users
        ]
        # Bulk create Sharing objects
        Sharing.objects.bulk_create(sharing_objects)
        return Response(
            {"message": f"File shared successfully"}, status=status.HTTP_201_CREATED
        )


class GroupListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = GroupSerializer

    def get(self, request, *args, **kwargs):
        groups = Group.objects.filter(owner=request.user)
        serializer = self.serializer_class(groups, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GroupRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = (
        IsAuthenticated,
        IsOwnerOrReadOnly,
    )
    serializer_class = GroupSerializer

    def get(self, request, group_id, *args, **kwargs):
        group = get_object_or_404(Group, pk=group_id)
        # Check permissions
        self.check_object_permissions(request, group)
        serializer = self.serializer_class(group)
        return Response(serializer.data)

    def put(self, request, group_id, *args, **kwargs):
        group = get_object_or_404(Group, pk=group_id)
        # Check permissions
        self.check_object_permissions(request, group)
        serializer = self.serializer_class(group, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, group_id, *args, **kwargs):
        group = get_object_or_404(Group, id=group_id)
        # Check permissions
        self.check_object_permissions(request, group)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
