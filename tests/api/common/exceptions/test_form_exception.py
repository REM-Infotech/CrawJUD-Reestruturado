
import importlib
import pytest

class LoadFormErrorDummy(Exception):
    pass


@pytest.fixture(scope="class")
def load_form_error() -> LoadFormErrorDummy:
    """Fixture para criar uma instância de LoadFormError."""

    return importlib.import_module("api.common.exceptions._form", __package__).LoadFormError


def test_loadformerror_message(load_form_error) -> None:
    """Verifique se LoadFormError armazena e retorna a mensagem corretamente.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    Raises:
        AssertionError: Se a mensagem não for armazenada corretamente.

    """
    mensagem = "Erro ao carregar formulário"
    erro = load_form_error(mensagem)
    assert str(erro) == mensagem

def test_loadformerror_is_exception(load_form_error) -> None:
    """Verifique se LoadFormError é uma subclasse de Exception.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    Raises:
        AssertionError: Se LoadFormError não for subclasse de Exception.

    """
    erro = load_form_error("mensagem")
    assert isinstance(erro, Exception)

def test_loadformerror_raise(load_form_error) -> None:
    """Teste se LoadFormError é levantada corretamente com pytest.raises.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    Raises:
        AssertionError: Se a exceção não for levantada corretamente.

    """
    with pytest.raises(load_form_error) as excinfo:
        raise load_form_error("Falha no formulário")
    assert str(excinfo.value) == "Falha no formulário"
