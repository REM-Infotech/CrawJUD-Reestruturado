"""Fornece funções utilitárias para formatação dados."""

from __future__ import annotations

import re
from datetime import datetime
from zoneinfo import ZoneInfo


def formata_tempo[T](item: T) -> T | datetime:  # noqa: D103
    if isinstance(item, str):
        if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$", item.split(".")[0]):
            return datetime.strptime(item.split(".")[0], "%Y-%m-%dT%H:%M:%S").replace(
                tzinfo=ZoneInfo("America/Manaus"),
            )

        if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}$", item):
            return datetime.strptime(item, "%Y-%m-%dT%H:%M:%S.%f").replace(
                tzinfo=ZoneInfo("America/Manaus"),
            )

    return item
