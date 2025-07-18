"""Fornece integração e configuração de formulários para bots jurídicos e administrativos.

Define tipos de formulários, mapeamento de configurações e utilitários para construção dinâmica de dicionários de formulário.
"""

# noqa: D104
from typing import Any, AnyStr, Self, Union

from api.interface.formbot.administrativo import (
    AdministrativoFormFileAuth,
    AdministrativoFormMultipleFiles,
)
from api.interface.formbot.juridico import (
    JuridicoFormFileAuth,
    JuridicoFormMultipleFiles,
    JuridicoFormOnlyAuth,
    JuridicoFormOnlyFile,
    JuridicoFormPautas,
    JuridicoFormPJE,
    JuridicoFormProcParte,
)
from api.models.bots import BotsCrawJUD

class_form_dict = Union[
    JuridicoFormFileAuth,
    JuridicoFormMultipleFiles,
    JuridicoFormOnlyAuth,
    JuridicoFormOnlyFile,
    JuridicoFormPautas,
    JuridicoFormProcParte,
    AdministrativoFormFileAuth,
    AdministrativoFormMultipleFiles,
]

FORM_CONFIG: dict[str, dict[str, class_form_dict]] = {
    "JURIDICO": {
        "only_auth": JuridicoFormOnlyAuth,
        "file_auth": JuridicoFormFileAuth,
        "multipe_files": JuridicoFormMultipleFiles,
        "only_file": JuridicoFormOnlyFile,
        "pautas": JuridicoFormPautas,
        "proc_parte": JuridicoFormProcParte,
        "pje": JuridicoFormPJE,
    },
    "ADMINISTRATIVO": {
        "file_auth": AdministrativoFormFileAuth,
        "multipe_files": AdministrativoFormMultipleFiles,
    },
}


class FormDict(
    JuridicoFormFileAuth,
    JuridicoFormMultipleFiles,
    JuridicoFormOnlyAuth,
    JuridicoFormOnlyFile,
    JuridicoFormPautas,
    JuridicoFormProcParte,
    AdministrativoFormFileAuth,
    AdministrativoFormMultipleFiles,
):
    """Permite construção dinâmica e acesso a anotações de tipos de formulários.

    Herda todos os TypedDicts de formulários jurídicos e administrativos.
    """

    @classmethod
    async def constructor(cls, bot: BotsCrawJUD, data: dict[str, AnyStr]) -> Self:
        """Construa dinamicamente um formulário baseado na classificação e configuração do bot.

        Args:
            bot (BotsCrawJUD): Instância do bot contendo classificação e configuração.
            data (dict[str, AnyStr]): Dados para inicializar o formulário.

        Returns:
            Self: Instância do formulário apropriado preenchida com os dados.

        """
        classification = bot.classification.upper()
        config = bot.form_cfg.lower()
        return FORM_CONFIG[classification][config](**data)

    @classmethod
    def get_annotations(cls, classification: str, config: str) -> dict[str, Any]:
        """Recupere as anotações de tipo do formulário conforme classificação e configuração.

        Args:
            classification (str): Classificação do formulário (ex: 'JURIDICO').
            config (str): Configuração do formulário (ex: 'file_auth').

        Returns:
            dict[str, Any]: Dicionário de anotações de tipo do formulário.

        """
        return FORM_CONFIG[classification][config].__annotations__
