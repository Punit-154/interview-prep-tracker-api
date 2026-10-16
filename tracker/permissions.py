from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to ensure only owners of an object can view, mutate, or delete it.
    """

    def has_object_permission(self, request, view, obj):
        # The object must have a `user` attribute
        return obj.user == request.user
