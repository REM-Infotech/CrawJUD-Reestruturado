import importlib
from redis import Redis

# Pseudocode
"""
- Test if environment variables are loaded and used correctly for config values.
- Mock `os.environ` to control config values for each test.
- Test boolean conversions for flags like `WITH_REDIS`, `DEBUG`, `TESTING`, etc.
- Test integer conversions for ports and pool sizes.
- Test default values when env vars are missing.
- Test Redis connection string usage for `SESSION_REDIS`.
- Test JSON parsing for `SQLALCHEMY_ENGINE_OPTIONS`.
- Test timedelta calculation for `PERMANENT_SESSION_LIFETIME`.
- Use pytest and monkeypatch for environment mocking."""

# Python

def test_with_redis_true(monkeypatch):
    # Testa se WITH_REDIS é True quando variável de ambiente está "true"
    monkeypatch.setenv("WITH_REDIS", "true")
    conf = importlib.reload(importlib.import_module("api.quartconf"))
    assert conf.WITH_REDIS is True

def test_with_redis_false(monkeypatch):
    # Testa se WITH_REDIS é False quando variável de ambiente está "false"
    monkeypatch.setenv("WITH_REDIS", "false")
    conf = importlib.reload(importlib.import_module("api.quartconf"))
    assert conf.WITH_REDIS is False

def test_debug_flag(monkeypatch):
    # Testa se DEBUG é definido corretamente
    monkeypatch.setenv("DEBUG", "true")
    conf = importlib.reload(importlib.import_module("api.quartconf"))
    assert conf.DEBUG is True

def test_testing_flag(monkeypatch):
    # Testa se TESTING é definido corretamente
    monkeypatch.setenv("TESTING", "true")
    conf = importlib.reload(importlib.import_module("api.quartconf"))
    assert conf.TESTING is True

def test_mail_port_default(monkeypatch):
    # Testa valor padrão de MAIL_PORT
    monkeypatch.delenv("MAIL_PORT", raising=False)
    conf = importlib.reload(importlib.import_module("api.quartconf"))
    assert conf.MAIL_PORT == 587

def test_mail_port_env(monkeypatch):
    # Testa valor de MAIL_PORT vindo da variável de ambiente
    monkeypatch.setenv("MAIL_PORT", "2525")
    conf = importlib.reload(importlib.import_module("api.quartconf"))
    assert conf.MAIL_PORT == 2525

def test_sqlalchemy_pool_size_default(monkeypatch):
    # Testa valor padrão de SQLALCHEMY_POOL_SIZE
    monkeypatch.delenv("SQLALCHEMY_POOL_SIZE", raising=False)
    conf = importlib.reload(importlib.import_module("api.quartconf"))
    assert conf.SQLALCHEMY_POOL_SIZE == 30

def test_sqlalchemy_engine_options_json(monkeypatch):
    # Testa parsing de JSON para SQLALCHEMY_ENGINE_OPTIONS
    monkeypatch.setenv("SQLALCHEMY_ENGINE_OPTIONS", '{"pool_pre_ping": true, "echo": false}')
    conf = importlib.reload(importlib.import_module("api.quartconf"))
    assert conf.SQLALCHEMY_ENGINE_OPTIONS == {"pool_pre_ping": True, "echo": False}

def test_permanent_session_lifetime(monkeypatch):
    # Testa cálculo de PERMANENT_SESSION_LIFETIME
    conf = importlib.reload(importlib.import_module("api.quartconf"))
    # timedelta(days=31).max.seconds deve ser igual a 86399
    assert conf.PERMANENT_SESSION_LIFETIME == 86399

def test_redis_host_default(monkeypatch):
    # Testa valor padrão de REDIS_HOST
    monkeypatch.delenv("REDIS_HOST", raising=False)
    conf = importlib.reload(importlib.import_module("api.quartconf"))
    assert conf.REDIS_HOST == "localhost"

def test_session_redis(monkeypatch):
    # Testa se SESSION_REDIS é instância de Redis
    monkeypatch.setenv("SESSION_REDIS", "redis://localhost:6379/0")
    conf = importlib.reload(importlib.import_module("api.quartconf"))
    assert isinstance(conf.SESSION_REDIS, Redis)
