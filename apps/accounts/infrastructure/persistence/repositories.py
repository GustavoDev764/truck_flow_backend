from __future__ import annotations

from django.contrib.auth.models import Group, User as DjangoUser

from apps.accounts.domain.entities import User
from apps.accounts.domain.repositories import UserRepository


class DjangoUserRepository(UserRepository):
    def get_by_id(self, user_id: int) -> User | None:
        try:
            obj = DjangoUser.objects.get(pk=user_id)
        except DjangoUser.DoesNotExist:
            return None
        return self._to_domain(obj)

    def get_by_username(self, username: str) -> User | None:
        obj = DjangoUser.objects.filter(username=username).first()
        if obj is None:
            return None
        return self._to_domain(obj)

    def list(self) -> list[User]:
        qs = DjangoUser.objects.all().order_by("-date_joined")
        return [self._to_domain(obj) for obj in qs]

    def create(
        self,
        *,
        username: str,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        group_names: list[str],
    ) -> User:
        user = DjangoUser(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save()
        for name in group_names:
            try:
                g = Group.objects.get(name=name)
                user.groups.add(g)
            except Group.DoesNotExist:
                pass
        user.refresh_from_db()
        return self._to_domain(user)

    def update(self, user: User) -> User:
        obj = DjangoUser.objects.get(pk=user.id)
        obj.email = user.email
        obj.first_name = user.first_name
        obj.last_name = user.last_name
        obj.is_active = user.is_active
        obj.save()
        obj.groups.clear()
        for name in user.group_names:
            try:
                g = Group.objects.get(name=name)
                obj.groups.add(g)
            except Group.DoesNotExist:
                pass
        obj.refresh_from_db()
        return self._to_domain(obj)

    def update_password(self, *, user_id: int, new_password: str) -> None:
        obj = DjangoUser.objects.get(pk=user_id)
        obj.set_password(new_password)
        obj.save()

    def delete(self, user_id: int) -> None:
        DjangoUser.objects.filter(pk=user_id).delete()

    def _to_domain(self, obj: DjangoUser) -> User:
        group_names = tuple(obj.groups.values_list("name", flat=True))
        return User(
            id=obj.id,
            username=obj.username,
            email=obj.email,
            first_name=obj.first_name,
            last_name=obj.last_name,
            is_active=obj.is_active,
            group_names=group_names,
            date_joined=obj.date_joined,
        )
