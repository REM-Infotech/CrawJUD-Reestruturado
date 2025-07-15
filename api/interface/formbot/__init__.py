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
    },
    "ADMINISTRATIVO": {
        "file_auth": AdministrativoFormFileAuth,
        "multipe_files": AdministrativoFormMultipleFiles,
    },
}


class FormDict(  # noqa: D101
    JuridicoFormFileAuth,
    JuridicoFormMultipleFiles,
    JuridicoFormOnlyAuth,
    JuridicoFormOnlyFile,
    JuridicoFormPautas,
    JuridicoFormProcParte,
    AdministrativoFormFileAuth,
    AdministrativoFormMultipleFiles,
):
    @classmethod
    async def constructor(cls, bot: BotsCrawJUD, data: dict[str, AnyStr]) -> Self:  # noqa: D102
        classification = bot.classification.upper()
        config = bot.form_cfg.lower()
        return FORM_CONFIG[classification][config](**data)

    @classmethod
    def get_annotations(cls, classification: str, config: str) -> dict[str, Any]:  # noqa: D102
        return FORM_CONFIG[classification][config].__annotations__
