"""
Configurações para ambiente de produção.
"""

from .base import *

DEBUG = False


CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = []


ALLOWED_HOSTS = ["*"]
