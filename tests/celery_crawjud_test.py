from typing import Generator
import logging
import os
import pytest
from pathlib import Path
from . import make_celery, config_loggers, app
from crawjud_app.custom import AsyncCelery
from crawjud_app.custom import AsyncCelery
from . import app_celery

@pytest.fixture
def temp_log_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Crie e forneça um diretório temporário para logs."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    yield log_dir

def test_config_loggers_cria_log_file(temp_log_dir: Path) -> None:
    """Teste se config_loggers cria o arquivo de log corretamente.

    Args:
        temp_log_dir (Path): Diretório temporário para logs.

    Returns:
        None: Não retorna valor.

    """
    os.environ["WORKER_NAME"] = "test_worker"
    os.environ["DEBUG"] = "True"
    log_file = temp_log_dir / "test_worker.log"
    logger = logging.getLogger("test_worker")
    config_loggers(logger=logger)
    assert log_file.exists()

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
