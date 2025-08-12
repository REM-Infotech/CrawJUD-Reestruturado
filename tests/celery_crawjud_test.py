from pathlib import Path

import pytest

from crawjud_app import app_celery, make_celery
from crawjud_app.custom import AsyncCelery


@pytest.fixture
def temp_log_dir(tmp_path: Path) -> Path:
    """Crie e forneça um diretório temporário para logs."""
    log_dir = tmp_path / "logs"  # pragma: no cover
    log_dir.mkdir()  # pragma: no cover
    return log_dir  # pragma: no cover


def test_make_celery_retorna_instancia_celery() -> None:
    """Teste se make_celery retorna uma instância de Celery configurada.

    Returns:
        None: Não retorna valor.

    """
    celery_instance = make_celery()
    assert isinstance(celery_instance, AsyncCelery)
    assert hasattr(celery_instance.conf, "update")


def test_app_celery_eh_instancia_de_celery() -> None:
    """Teste se app_celery é uma instância de Celery.

    Returns:
        None: Não retorna valor.

    """
    assert isinstance(app_celery, AsyncCelery)
