"""Integração e configuração de formulários para bots jurídicos e administrativos.

Define tipos de formulários, mapeamento de configurações e u
tilitários para construção dinâmica de dicionários de formulário.
"""

from typing import Any, AnyStr, Self

from api.models.bots import BotsCrawJUD
from crawjud.interfaces.formbot.administrativo import (
    AdministrativoFormFileAuth,
    AdministrativoFormMultipleFiles,
)
from crawjud.interfaces.formbot.juridico import (
    JuridicoFormFileAuth,
    JuridicoFormMultipleFiles,
    JuridicoFormOnlyAuth,
    JuridicoFormOnlyFile,
    JuridicoFormPautas,
    JuridicoFormPJE,
    JuridicoFormProcParte,
)

type ClassFormDict = (
    JuridicoFormFileAuth
    | JuridicoFormMultipleFiles
    | JuridicoFormOnlyAuth
    | JuridicoFormOnlyFile
    | JuridicoFormPautas
    | JuridicoFormProcParte
    | AdministrativoFormFileAuth
    | AdministrativoFormMultipleFiles
)

FORM_CONFIG: dict[str, dict[str, ClassFormDict]] = {
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
        """Construa dinamicamente um formulário baseado na configuração do bot.

        Args:
            bot (BotsCrawJUD): Instância do bot contendo configuração.
            data (dict[str, AnyStr]): Dados para inicializar o formulário.

        Returns:
            Self: Instância do formulário apropriado preenchida com os dados.

        """
        classification = bot.classification.upper()
        config = bot.form_cfg.lower()
        return FORM_CONFIG[classification][config](**data)

    @classmethod
    def get_annotations(cls, classification: str, config: str) -> dict[str, Any]:
        """Recupere as anotações de tipo do formulário conforme configuração.

        Args:
            classification (str): Classificação do formulário (ex: 'JURIDICO').
            config (str): Configuração do formulário (ex: 'file_auth').

        Returns:
            dict[str, Any]: Dicionário de anotações de tipo do formulário.

        """
        return FORM_CONFIG[classification][config].__annotations__
