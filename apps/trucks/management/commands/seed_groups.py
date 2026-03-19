"""
Seed para auth_group: cria os grupos 'cliente' e 'manage'.

- cliente: CRUD de caminhões
- manage: CRUD de caminhões + CRUD de usuários (criar, editar, desativar, trocar senha)

Opcionalmente cria usuários de exemplo: manage@truckflow.com e cliente@truckflow.com (senha: truckflow123).
"""

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

GROUPS = ["cliente", "manage"]


SEED_USERS = [
    {
        "username": "manage@truckflow.com",
        "email": "manage@truckflow.com",
        "password": "truckflow123",
        "groups": ["manage"],
    },
    {
        "username": "cliente@truckflow.com",
        "email": "cliente@truckflow.com",
        "password": "truckflow123",
        "groups": ["cliente"],
    },
]


class Command(BaseCommand):
    help = "Cria os grupos padrão: cliente e manage. Use --create-users para criar usuários de exemplo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--create-users",
            action="store_true",
            help="Cria usuários de exemplo (manage@truckflow.com e cliente@truckflow.com, senha: truckflow123).",
        )

    def handle(self, *args, **options):
        created_grps = 0
        for name in GROUPS:
            _, created = Group.objects.get_or_create(name=name)
            if created:
                created_grps += 1
        self.stdout.write(self.style.SUCCESS(f"Grupos: {created_grps} novos de {len(GROUPS)}."))

        if options.get("create_users"):
            for u in SEED_USERS:
                user, created = User.objects.get_or_create(
                    username=u["username"],
                    defaults={"email": u["email"], "is_active": True},
                )
                if created:
                    user.set_password(u["password"])
                    user.save()
                    for gname in u["groups"]:
                        g = Group.objects.get(name=gname)
                        user.groups.add(g)
                    self.stdout.write(self.style.SUCCESS(f"Usuário criado: {u['username']}"))
                else:
                    self.stdout.write(f"Usuário já existe: {u['username']}")
