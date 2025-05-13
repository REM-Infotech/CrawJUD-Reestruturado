"""Quart Config Module."""

import logging
import secrets
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.resolve().joinpath(".env"))


WITH_REDIS = False
LOG_LEVEL = logging.INFO
DEBUG = False
TESTING = False
JWT_SECRET_KEY = secrets.token_hex()
SECRET_KEY = secrets.token_hex()
TEMPLATES_AUTO_RELOAD = False

# FLASK-MAIL CONFIG
MAIL_SERVER = ""
MAIL_PORT = 587
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = ""
MAIL_PASSWORD = ""
MAIL_DEFAULT_SENDER = ""

# SQLALCHEMY CONFIG
SQLALCHEMY_POOL_SIZE = 30  # Número de conexões na pool

# Número de conexões extras além da pool_size
SQLALCHEMY_MAX_OVERFLOW = 10

# Tempo de espera para obter uma conexão
SQLALCHEMY_POOL_TIMEOUT = 30

# Tempo (em segundos) para reciclar as conexões ociosas
SQLALCHEMY_POOL_RECYCLE = 1800

# Verificar a saúde da conexão antes de usá-la
SQLALCHEMY_POOL_PRE_PING = True

SQLALCHEMY_DATABASE_URI = "sqlite:///local.db"
SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
SQLALCHEMY_TRACK_MODIFICATIONS = False

PERMANENT_SESSION_LIFETIME = timedelta(days=31).max.seconds

REDIS_HOST = ""
REDIS_PORT = 6379
REDIS_DB = ""
REDIS_PASSWORD = ""

BROKER_DATABASE = 1
RESULT_BACKEND_DATABASE = 2
