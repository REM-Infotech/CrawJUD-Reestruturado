"""Módulo de tipos do celery app."""

from os import PathLike
from typing import Literal

# Definição do tipo "StrPath"
StrPath = str | PathLike


TReturnMessageMail = Literal["E-mail enviado com sucesso!"]
TReturnMessageExecutBot = Literal["Execução encerrada com sucesso!"]
TReturnMessageUploadFile = Literal["Arquivo enviado com sucesso!"]
