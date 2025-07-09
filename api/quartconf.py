"""Quart Config Module."""

import json
import logging
from datetime import timedelta
from os import environ
from pathlib import Path

from dotenv import load_dotenv
from redis import Redis

load_dotenv(str(Path(__file__).cwd().joinpath("api", ".env")))

env = environ

WITH_REDIS = env.get("WITH_REDIS", "false").lower() == "true"
LOG_LEVEL = logging.INFO
DEBUG = env.get("DEBUG", "false").lower() == "true"
TESTING = env.get("TESTING", "false").lower() == "true"

SECRET_KEY = env.get("APP_SECRET")
TEMPLATES_AUTO_RELOAD = env.get("TEMPLATES_AUTO_RELOAD", "false").lower() == "true"

# FLASK-MAIL CONFIG
MAIL_SERVER = env.get("MAIL_SERVER", "localhost")
MAIL_PORT = int(env.get("MAIL_PORT", 587))
MAIL_USE_TLS = env.get("MAIL_USE_TLS", "false").lower() == "true"
MAIL_USE_SSL = env.get("MAIL_USE_SSL", "false").lower() == "true"
MAIL_USERNAME = env.get("MAIL_USERNAME", "")
MAIL_PASSWORD = env.get("MAIL_PASSWORD", "")
MAIL_DEFAULT_SENDER = env.get("MAIL_DEFAULT_SENDER", "")

# SQLALCHEMY CONFIG
SQLALCHEMY_POOL_SIZE = int(env.get("SQLALCHEMY_POOL_SIZE", 30))  # Número de conexões na pool

# Número de conexões extras além da pool_size
SQLALCHEMY_MAX_OVERFLOW = int(env.get("SQLALCHEMY_MAX_OVERFLOW", 10))

# Tempo de espera para obter uma conexão
SQLALCHEMY_POOL_TIMEOUT = int(env.get("SQLALCHEMY_POOL_TIMEOUT", 30))

# Tempo (em segundos) para reciclar as conexões ociosas
SQLALCHEMY_POOL_RECYCLE = int(env.get("SQLALCHEMY_POOL_RECYCLE", 1800))

# Verificar a saúde da conexão antes de usá-la
SQLALCHEMY_POOL_PRE_PING = env.get("SQLALCHEMY_POOL_PRE_PING", "true").lower() == "true"

SQLALCHEMY_DATABASE_URI = env.get("SQLALCHEMY_DATABASE_URI", "sqlite:///local.db")

SQLALCHEMY_ENGINE_OPTIONS = json.loads(env.get("SQLALCHEMY_ENGINE_OPTIONS", '{"pool_pre_ping": "True"}'))
SQLALCHEMY_TRACK_MODIFICATIONS = env.get("WITH_REDIS", "false").lower() == "true"

PERMANENT_SESSION_LIFETIME = timedelta(days=31).max.seconds

REDIS_HOST = env.get("REDIS_HOST", "localhost")
REDIS_PORT = int(env.get("REDIS_PORT", 6379))
REDIS_DB = int(env.get("REDIS_DB", 0))
REDIS_PASSWORD = env.get("REDIS_PASSWORD", "")

BROKER_DATABASE = 1
RESULT_BACKEND_DATABASE = 2

# JWT CONFIG
JWT_SECRET_KEY = env.get("JWT_APP_SECRET")
JWT_TOKEN_LOCATION = ["cookies"]
JWT_COOKIE_CSRF_PROTECT = True
JWT_CSRF_IN_COOKIES = True
JWT_ACCESS_CSRF_HEADER_NAME = "X-Xsrf-Token"
JWT_ACCESS_CSRF_COOKIE_NAME = "X-Xsrf-Token"

SESSION_TYPE = "redis"
SESSION_REDIS = Redis.from_url(env.get("REDIS_URI"))
