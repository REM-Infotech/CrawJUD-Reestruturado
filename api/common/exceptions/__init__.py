"""Fornece exceções personalizadas para o módulo de API.

Este pacote contém definições de exceções específicas utilizadas
para tratamento de erros na camada comum da API.
"""

from ._form import LoadFormError

__all__ = ["LoadFormError"]
