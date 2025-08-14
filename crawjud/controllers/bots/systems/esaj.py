"""Módulo para a classe de controle dos robôs ESaj."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from crawjud.controllers.bots.master.cnj_bots import CNJBots as ClassBot

DictData = dict[str, str | datetime]
ListData = list[DictData]

workdir = Path(__file__).cwd()

HTTP_STATUS_FORBIDDEN = 403  # Constante para status HTTP Forbidden
COUNT_TRYS = 15


class ESajBot[T](ClassBot):
    """Classe de controle para robôs do ESaj."""
