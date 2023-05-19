from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    '''Разрешения для Администратора или только чтение.'''

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser)


class IsAuthorOrReadOnly(permissions.BasePermission):
    '''Разрешение для автора или только на чтение.'''

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
