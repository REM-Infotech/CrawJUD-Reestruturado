import pytest
from crawjud_app.common.exceptions.elaw import ElawError, AdvogadoError

# python
"""Teste unitário para classes de exceção ElawError e AdvogadoError do módulo elaw.

Testa a criação, mensagem e herança das exceções ElawError e AdvogadoError.

"""



def test_elaw_error_mensagem_padrao() -> None:
    """Verifique a mensagem padrão ao instanciar ElawError com exceção.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    """
    # Cria exceção simulada
    exc = RuntimeError("erro simulado")
    bot_execution_id = "exec-001"
    error = ElawError(exc, bot_execution_id)
    # Verifica se mensagem padrão e nome da exceção estão presentes
    assert "Erro ao executar operaçao" in str(error)
    assert "RuntimeError" in str(error)
    assert "erro simulado" in str(error)
    assert isinstance(error, ElawError)

def test_elaw_error_mensagem_customizada() -> None:
    """Verifique mensagem customizada ao instanciar ElawError.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    """
    exc = ValueError("valor inválido")
    bot_execution_id = "exec-002"
    mensagem = "Erro customizado"
    error = ElawError(exc, bot_execution_id, message=mensagem)
    assert mensagem in str(error)
    assert "ValueError" in str(error)

def test_elaw_error_heranca_base() -> None:
    """Verifique se ElawError é subclasse de BaseCrawJUDError.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    """
    exc = Exception("erro base")
    bot_execution_id = "exec-003"
    with pytest.raises(ElawError):
        raise ElawError(exc, bot_execution_id)

def test_advogado_error_mensagem_padrao() -> None:
    """Verifique a mensagem padrão ao instanciar AdvogadoError.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    """
    bot_execution_id = "exec-004"
    error = AdvogadoError(bot_execution_id)
    assert "Erro ao executar operaçao" in str(error)
    assert isinstance(error, AdvogadoError)

def test_advogado_error_com_excecao() -> None:
    """Verifique mensagem ao instanciar AdvogadoError com exceção.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    """
    bot_execution_id = "exec-005"
    exc = KeyError("chave ausente")
    error = AdvogadoError(bot_execution_id, exception=exc)
    assert "KeyError" in str(error)
    assert "chave ausente" in str(error)

def test_advogado_error_mensagem_customizada() -> None:
    """Verifique mensagem customizada ao instanciar AdvogadoError.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    """
    bot_execution_id = "exec-006"
    mensagem = "Erro customizado advogado"
    error = AdvogadoError(bot_execution_id, message=mensagem)
    assert mensagem in str(error)

def test_advogado_error_heranca_base() -> None:
    """Verifique se AdvogadoError é subclasse de BaseCrawJUDError.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    """
    bot_execution_id = "exec-007"
    with pytest.raises(AdvogadoError):
        raise AdvogadoError(bot_execution_id)
