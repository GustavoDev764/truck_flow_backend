"""Permissões: cliente (CRUD trucks) e manage (CRUD trucks + CRUD users)."""

from rest_framework import permissions


def _user_in_group(user, group_name: str) -> bool:
    return user.is_authenticated and user.groups.filter(name=group_name).exists()


class IsClienteOrManage(permissions.BasePermission):
    """Permite cliente e manage: ambos fazem CRUD de trucks."""

    def has_permission(self, request, view):
        return _user_in_group(request.user, "cliente") or _user_in_group(request.user, "manage")


class IsManage(permissions.BasePermission):
    """Permite apenas o grupo manage: CRUD de usuários."""

    def has_permission(self, request, view):
        return _user_in_group(request.user, "manage")
