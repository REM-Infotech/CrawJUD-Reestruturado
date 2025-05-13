"""Quart Config Module."""

import logging
import secrets
from datetime import timedelta
from pathlib import Path

workdir = Path(__file__).cwd()

WITH_REDIS = False
LOG_LEVEL = logging.INFO
DEBUG: type[bool] = False
TESTING: type[bool] = False
JWT_SECRET_KEY: type[str] = secrets.token_hex()
SECRET_KEY: type[str] = secrets.token_hex()
TEMPLATES_AUTO_RELOAD: type[bool] = False

# FLASK-MAIL CONFIG
MAIL_SERVER: type[str] = ""
MAIL_PORT: type[int] = 587
MAIL_USE_TLS: type[bool] = False
MAIL_USE_SSL: type[bool] = False
MAIL_USERNAME: type[str] = ""
MAIL_PASSWORD: type[str] = ""
MAIL_DEFAULT_SENDER: type[str] = ""

# SQLALCHEMY CONFIG
SQLALCHEMY_POOL_SIZE: type[int] = 30  # Número de conexões na pool

# Número de conexões extras além da pool_size
SQLALCHEMY_MAX_OVERFLOW: type[int] = 10

# Tempo de espera para obter uma conexão
SQLALCHEMY_POOL_TIMEOUT: type[int] = 30

# Tempo (em segundos) para reciclar as conexões ociosas
SQLALCHEMY_POOL_RECYCLE: type[int] = 1800

# Verificar a saúde da conexão antes de usá-la
SQLALCHEMY_POOL_PRE_PING: type[bool] = True

SQLALCHEMY_DATABASE_URI: type[str] = "sqlite:///local.db"
SQLALCHEMY_ENGINE_OPTIONS: dict[str, str | bool] = {"pool_pre_ping": True}
SQLALCHEMY_TRACK_MODIFICATIONS: type[bool] = False

PERMANENT_SESSION_LIFETIME: type[int] = timedelta(days=31).max.seconds

REDIS_HOST: type[str] = ""
REDIS_PORT: type[int] = 6379
REDIS_DB: type[str] = ""
REDIS_PASSWORD: type[str] = ""

BROKER_DATABASE: type[int] = 1
RESULT_BACKEND_DATABASE: type[int] = 2
