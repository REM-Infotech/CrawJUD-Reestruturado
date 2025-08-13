import pytest
import logging
import time
from utils.logger.handlers import _format_time

# language: python



class DummyRecord(logging.LogRecord):
    """Classe auxiliar para criar LogRecord customizado para testes."""
    def __init__(self, created: float, msecs: float = 123.0):
        super().__init__(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="mensagem",
            args=(),
            exc_info=None
        )
        self.created = created
        self.msecs = msecs

def test_format_time_default_format(monkeypatch) -> None:
    """Testa formatação padrão sem datefmt.

    Args:
        monkeypatch (pytest.MonkeyPatch): Utilizado para mockar funções.

    Returns:
        None: Não retorna valor.

    Raises:
        AssertionError: Se o formato não corresponder ao esperado.

    """
    # Mocka time.localtime e time.strftime para retorno previsível
    monkeypatch.setattr(time, "localtime", lambda ts: time.struct_time((2024, 6, 1, 12, 34, 56, 0, 0, 0)))
    monkeypatch.setattr(time, "strftime", lambda fmt, ct: "2024-06-01 12:34:56" if fmt == "%Y-%m-%d %H:%M:%S" else "mocked")
    record = DummyRecord(created=1717246496.123, msecs=123.0)
    result = _format_time(record)
    # Espera incluir milissegundos
    assert result == "2024-06-01 12:34:56.123"
    assert isinstance(result, str)

def test_format_time_with_datefmt(monkeypatch) -> None:
    """Testa formatação com datefmt customizado.

    Args:
        monkeypatch (pytest.MonkeyPatch): Utilizado para mockar funções.

    Returns:
        None: Não retorna valor.

    Raises:
        AssertionError: Se o formato não corresponder ao esperado.

    """
    monkeypatch.setattr(time, "localtime", lambda ts: time.struct_time((2024, 6, 1, 8, 0, 0, 0, 0, 0)))
    monkeypatch.setattr(time, "strftime", lambda fmt, ct: "01/06/2024 08:00:00" if fmt == "%d/%m/%Y %H:%M:%S" else "mocked")
    record = DummyRecord(created=1717228800.0, msecs=0.0)
    result = _format_time(record, "%d/%m/%Y %H:%M:%S")
    assert result == "01/06/2024 08:00:00"
    assert isinstance(result, str)

def test_format_time_msecs_zero(monkeypatch) -> None:
    """Testa formatação quando msecs é zero.

    Args:
        monkeypatch (pytest.MonkeyPatch): Utilizado para mockar funções.

    Returns:
        None: Não retorna valor.

    Raises:
        AssertionError: Se o formato não corresponder ao esperado.

    """
    monkeypatch.setattr(time, "localtime", lambda ts: time.struct_time((2024, 6, 1, 0, 0, 0, 0, 0, 0)))
    monkeypatch.setattr(time, "strftime", lambda fmt, ct: "2024-06-01 00:00:00" if fmt == "%Y-%m-%d %H:%M:%S" else "mocked")
    record = DummyRecord(created=1717200000.0, msecs=0.0)
    result = _format_time(record)
    assert result == "2024-06-01 00:00:00.000"
    assert isinstance(result, str)

def test_format_time_different_created(monkeypatch) -> None:
    """Testa formatação para diferentes valores de created.

    Args:
        monkeypatch (pytest.MonkeyPatch): Utilizado para mockar funções.

    Returns:
        None: Não retorna valor.

    Raises:
        AssertionError: Se o formato não corresponder ao esperado.

    """
    monkeypatch.setattr(time, "localtime", lambda ts: time.struct_time((2023, 12, 31, 23, 59, 59, 0, 0, 0)))
    monkeypatch.setattr(time, "strftime", lambda fmt, ct: "2023-12-31 23:59:59" if fmt == "%Y-%m-%d %H:%M:%S" else "mocked")
    record = DummyRecord(created=1704067199.999, msecs=999.0)
    result = _format_time(record)
    assert result == "2023-12-31 23:59:59.999"
    assert isinstance(result, str)

def test_format_time_return_type(monkeypatch) -> None:
    """Testa se o retorno da função é sempre uma string.

    Args:
        monkeypatch (pytest.MonkeyPatch): Utilizado para mockar funções.

    Returns:
        None: Não retorna valor.

    Raises:
        AssertionError: Se o tipo de retorno não for string.

    """
    monkeypatch.setattr(time, "localtime", lambda ts: time.struct_time((2024, 1, 1, 0, 0, 0, 0, 0, 0)))
    monkeypatch.setattr(time, "strftime", lambda fmt, ct: "2024-01-01 00:00:00")
    record = DummyRecord(created=1704067200.0, msecs=0.0)
    result = _format_time(record)
    assert isinstance(result, str)
