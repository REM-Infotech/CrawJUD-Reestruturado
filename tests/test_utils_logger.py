from typing import Generic, TypeVar
import pytest
from utils.logger import dict_config

T = TypeVar("T")


def test_dict_config_retorna_tupla_config_e_nome_logger() -> None:
    """Teste se dict_config retorna tupla com config e nome do logger.

    Returns:
        None: Não retorna valor.

    """
    config, logger_name = dict_config(FILELOG_PATH="teste.log")
    assert isinstance(config, dict)
    assert isinstance(logger_name, str)
    assert config["handlers"]["file_handler"]["filename"] == "teste.log"
    assert "version" in config
    assert "handlers" in config
    assert "formatters" in config
    assert "loggers" in config
    assert logger_name in config["loggers"]


def test_dict_config_nome_logger_personalizado() -> None:
    """Teste se dict_config aceita nome de logger personalizado.

    Returns:
        None: Não retorna valor.

    """
    config, logger_name = dict_config(FILELOG_PATH="teste.log", LOGGER_NAME="custom_logger")
    assert logger_name == "custom_logger"
    assert "custom_logger" in config["loggers"]


def test_dict_config_nivel_log_personalizado() -> None:
    """Teste se dict_config aceita nível de log personalizado.

    Returns:
        None: Não retorna valor.

    """
    config, _ = dict_config(FILELOG_PATH="teste.log", LOG_LEVEL=50)
    assert config["root"]["level"] == 20  # logging.INFO é 20
    assert config["handlers"]["file_handler"]["level"] == 20


def test_dict_config_backupcount_e_maxbytes() -> None:
    """Teste se dict_config define backupCount e maxBytes corretamente.

    Returns:
        None: Não retorna valor.

    """
    config, _ = dict_config(FILELOG_PATH="teste.log")
    file_handler = config["handlers"]["file_handler"]
    assert file_handler["maxBytes"] == 40960
    assert file_handler["backupCount"] == 5
