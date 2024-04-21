from rest_framework import permissions

from .models import Permission


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsOwnerOrCheckPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        if (
            request.method in permissions.SAFE_METHODS
            and Permission.objects.filter(
                file=obj,
                user=request.user,
                permission__in=[Permission.READ, Permission.CHANGE],
            ).exists()
        ):
            return True
        if (
            request.method == "PUT"
            and Permission.objects.filter(
                file=obj, user=request.user, permission=Permission.CHANGE
            ).exists()
        ):
            return True
