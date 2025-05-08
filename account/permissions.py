from rest_framework import permissions


class IsNotBanned(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and not user.is_banned