from api.common.exceptions._form import LoadFormError
import pytest

def test_loadformerror_message() -> None:
    """Verifique se LoadFormError armazena e retorna a mensagem corretamente.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    Raises:
        AssertionError: Se a mensagem não for armazenada corretamente.

    """
    mensagem = "Erro ao carregar formulário"
    erro = LoadFormError(mensagem)
    assert str(erro) == mensagem

def test_loadformerror_is_exception() -> None:
    """Verifique se LoadFormError é uma subclasse de Exception.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    Raises:
        AssertionError: Se LoadFormError não for subclasse de Exception.

    """
    erro = LoadFormError("mensagem")
    assert isinstance(erro, Exception)

def test_loadformerror_raise() -> None:
    """Teste se LoadFormError é levantada corretamente com pytest.raises.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    Raises:
        AssertionError: Se a exceção não for levantada corretamente.

    """
    with pytest.raises(LoadFormError) as excinfo:
        raise LoadFormError("Falha no formulário")
    assert str(excinfo.value) == "Falha no formulário"
