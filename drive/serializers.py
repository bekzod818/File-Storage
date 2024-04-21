from django.contrib.auth.models import User
from rest_framework import serializers

from .models import File, Sharing


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError("Passwords must match")
        return attrs

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
