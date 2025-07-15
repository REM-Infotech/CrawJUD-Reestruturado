"""Módulo de tipos do celery app."""

from os import PathLike
from typing import Literal, Union

# Definição do tipo "StrPath"
StrPath = Union[str, PathLike]


TReturnMessageMail = Literal["E-mail enviado com sucesso!"]
TReturnMessageExecutBot = Literal["Execução encerrada com sucesso!"]
TReturnMessageUploadFile = Literal["Arquivo enviado com sucesso!"]
