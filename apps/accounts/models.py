"""Modelos de contas - sessões JWT para invalidação."""

import uuid

from django.conf import settings
from django.db import models


class Session(models.Model):
    """Sessão JWT - controla invalidação de tokens após logout."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="jwt_sessions",
    )
    jti = models.UUIDField(unique=True, editable=False, db_index=True)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_session"
        ordering = ["-created_at"]
