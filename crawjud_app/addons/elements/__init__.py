"""Inicialize o pacote de elementos dos addons.

Este módulo importa e expõe os submódulos principais do pacote 'elements',
permitindo o acesso centralizado às funcionalidades de caixa, calculadoras,
elaw, esaj, pje e projudi.
"""

from . import caixa, calculadoras, elaw, esaj, pje, projudi

__all__ = [
    "caixa",
    "calculadoras",
    "elaw",
    "esaj",
    "pje",
    "projudi",
]
