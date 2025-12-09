from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Пользователь имеет доступ на чтение, если привычка публичная (is_public=True).
    Пользователь имеет полный доступ (CRUD) только к своим привычкам.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешить GET, HEAD или OPTIONS (доступ на чтение) для всех,
        # если привычка публичная.
        if request.method in permissions.SAFE_METHODS:
            return obj.is_public

        # Разрешить полный доступ (изменение/удаление) только владельцу привычки.
        return obj.user == request.user

class IsOwner(permissions.BasePermission):
    """
    Разрешает полный доступ (CRUD) только владельцу объекта.
    Используется для списка привычек пользователя.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

    def has_permission(self, request, view):
        # На уровне списка (list) проверяем, что пользователь аутентифицирован.
        return request.user.is_authenticated
