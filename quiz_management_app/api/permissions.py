from rest_framework.permissions import BasePermission

class IsQuizOwner(BasePermission):
    """Custom permission to only allow owners of a quiz to edit or delete it."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user