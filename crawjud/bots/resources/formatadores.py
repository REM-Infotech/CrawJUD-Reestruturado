"""Fornece funções utilitárias para formatação dados."""

import re
from datetime import datetime

from crawjud.types import ReturnFormataTempo


def formata_tempo(item: str | bool) -> ReturnFormataTempo:  # noqa: D103
    if isinstance(item, str):
        if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$", item):
            return datetime.strptime(item.split(".")[0], "%Y-%m-%dT%H:%M:%S")

        elif re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}$", item):
            return datetime.strptime(item, "%Y-%m-%dT%H:%M:%S.%f")

    return item
