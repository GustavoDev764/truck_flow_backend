"""
Modelo base para tabelas customizadas (sem prefixo django).
Todas as tabelas de domínio devem herdar de UUIDModel para usar UUID como id.
"""

import uuid

from django.db import models


class UUIDModel(models.Model):
    """
    Modelo abstrato que define id como UUID.
    Use como base para todos os models que representam tabelas customizadas
    (tabelas sem prefixo auth_*, django_*).
    """

    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
    )

    class Meta:
        abstract = True
