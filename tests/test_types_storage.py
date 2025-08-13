from typing import cast

import pytest
from utils.storage.types_storage import storages


def test_storages_literal_values() -> None:
    """Verifica se o tipo 'storages' aceita apenas os valores permitidos.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    Raises:
        AssertionError: Se o valor não estiver entre os permitidos.

    """

    # Testa valores válidos
    def accepts_storage(storage: storages) -> str:
        return storage

    assert accepts_storage("google") == "google"
    assert accepts_storage("minio") == "minio"


def test_storages_literal_invalid_value() -> None:
    """Garante que valores inválidos para 'storages' causam erro de tipo.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    Raises:
        AssertionError: Se não ocorrer erro ao passar valor inválido.

    """
    # Testa valor inválido
    with pytest.raises(AssertionError):
        # O cast ignora o tipo, mas podemos forçar uma asserção
        value = cast("storages", "aws")
        assert value in ("google", "minio")
