from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to view or edit it.
    Provides defense-in-depth row-level security.
    """

    def has_object_permission(self, request, view, obj):
        # The object must have a `user` attribute
        return obj.user == request.user
