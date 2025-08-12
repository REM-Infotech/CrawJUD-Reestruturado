from typing import Generic, TypeVar
import logging
import pytest
from utils.logger.handlers import ColorFormatter

T = TypeVar("T")


def test_colorformatter_format_info_message() -> None:
    """Teste se ColorFormatter formata mensagem de nível INFO com cor.

    Returns:
        None: Não retorna valor.

    """
    formatter = ColorFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Mensagem de teste INFO",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    assert "Mensagem de teste INFO" in formatted
    # Verifica se contém código de cor ANSI para INFO (cinza)
    assert "\x1b[" in formatted


def test_colorformatter_format_warning_message() -> None:
    """Teste se ColorFormatter formata mensagem de nível WARNING com cor.

    Returns:
        None: Não retorna valor.

    """
    formatter = ColorFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.WARNING,
        pathname=__file__,
        lineno=20,
        msg="Mensagem de teste WARNING",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    assert "Mensagem de teste WARNING" in formatted
    # Verifica se contém código de cor ANSI para WARNING (amarelo)
    assert "\x1b[" in formatted


def test_colorformatter_format_error_message() -> None:
    """Teste se ColorFormatter formata mensagem de nível ERROR com cor.

    Returns:
        None: Não retorna valor.

    """
    formatter = ColorFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.ERROR,
        pathname=__file__,
        lineno=30,
        msg="Mensagem de teste ERROR",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    assert "Mensagem de teste ERROR" in formatted
    # Verifica se contém código de cor ANSI para ERROR (vermelho)
    assert "\x1b[" in formatted


def test_colorformatter_format_critical_message() -> None:
    """Teste se ColorFormatter formata mensagem de nível CRITICAL com cor.

    Returns:
        None: Não retorna valor.

    """
    formatter = ColorFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.CRITICAL,
        pathname=__file__,
        lineno=40,
        msg="Mensagem de teste CRITICAL",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    assert "Mensagem de teste CRITICAL" in formatted
    # Verifica se contém código de cor ANSI para CRITICAL (vermelho negrito)
    assert "\x1b[" in formatted


def test_colorformatter_format_with_color_message_attribute() -> None:
    """Teste se ColorFormatter utiliza atributo color_message se presente.

    Returns:
        None: Não retorna valor.

    """
    formatter = ColorFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=50,
        msg="Mensagem original",
        args=(),
        exc_info=None,
    )
    record.color_message = "Mensagem colorida"
    formatted = formatter.format(record)
    assert "Mensagem colorida" in formatted
