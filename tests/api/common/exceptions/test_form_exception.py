import importlib

import pytest


class LoadFormErrorDummy(Exception):
    """Defina exceção dummy para simular erro de carregamento de formulário."""

    def __init__(self, message: str, *args) -> None:
        """Defina o construtor para LoadFormErrorDummy com mensagem e argumentos.

        Args:
        message (str): Mensagem de erro a ser armazenada na exceção.
            *args (tuple): Argumentos adicionais para a exceção.


        """
        super().__init__(*args)


@pytest.fixture(scope="class")
def load_form_error() -> LoadFormErrorDummy:
    """Fixture para criar uma instância de LoadFormError.

    Returns:
        LoadFormErrorDummy: Classe de exceção LoadFormError importada dinamicamente.

    """
    return importlib.import_module(
        "api.common.exceptions._form",
        __package__,
    ).LoadFormError


def test_loadformerror_message(load_form_error) -> None:
    """Verifique se LoadFormError armazena e retorna a mensagem corretamente.

    Args:
        Nenhum.



    """
    mensagem = "Erro ao carregar formulário"
    erro = load_form_error(mensagem)
    assert str(erro) == mensagem


def test_loadformerror_is_exception(load_form_error) -> None:
    """Verifique se LoadFormError é uma subclasse de Exception."""
    erro = load_form_error("mensagem")
    assert isinstance(erro, Exception)


def test_loadformerror_raise(load_form_error) -> None:
    """Teste se LoadFormError é levantada corretamente com pytest.raises."""
    with pytest.raises(load_form_error) as excinfo:
        raise load_form_error(message="Falha no formulário")
    assert str(excinfo.value) == "Falha no formulário"
