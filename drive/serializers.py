from django.contrib.auth.models import User
from rest_framework import serializers

from .models import File, Group, Sharing


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ("id", "name", "file")
        read_only_fields = ("id",)


class GroupSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["files"] = FileSerializer(instance.files.all(), many=True).data
        return data

    def create(self, validated_data):
        validated_data["files"] = filter(
            lambda file: file.owner == self.context["request"].user,
            validated_data.get("files"),
        )
        return super().create(validated_data)

    class Meta:
        model = Group
        fields = ("id", "name", "files")
        read_only_fields = ("id",)
        extra_kwargs = {
            "files": {"write_only": True},
        }


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError("Passwords must match")
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get("username"),
            email=validated_data.get("email"),
            password=validated_data.get("password1"),
        )
        return user

    class Meta:
        model = User
        fields = ["id", "username", "email", "password1", "password2"]


class SharingSerializer(serializers.ModelSerializer):
    shared_with = UserSerializer(read_only=True)
    shared_by = UserSerializer(read_only=True)
    shared_file = FileSerializer(read_only=True)

    class Meta:
        model = Sharing
        fields = ["id", "shared_file", "shared_with", "shared_by", "shared_at"]


class SharingUserSerializer(serializers.Serializer):
    user_ids = serializers.ListField(child=serializers.IntegerField())
