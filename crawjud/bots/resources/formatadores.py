"""Fornece funções utilitárias para formatação dados."""

from __future__ import annotations

import io
import re
from datetime import datetime
from typing import (
    Generic,
    TypeVar,
)

import base91
import pandas as pd

from celery_app._wrapper import shared_task
from crawjud.types import ReturnFormataTempo
from crawjud.types.bot import BotData

T = TypeVar("AnyValue", bound=ReturnFormataTempo)


def formata_tempo(item: str | bool) -> Generic[T]:  # noqa: D103
    if isinstance(item, str):
        if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$", item.split(".")[0]):
            return datetime.strptime(item.split(".")[0], "%Y-%m-%dT%H:%M:%S")

        elif re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}$", item):
            return datetime.strptime(item, "%Y-%m-%dT%H:%M:%S.%f")

    return item


@shared_task(name="crawjud.dataFrame")
def dataframe(  # noqa: N802
    base91_planilha: str, *args: Generic[T], **kwargs: Generic[T]
) -> list[BotData]:
    """Convert an Excel file to a list of dictionaries with formatted data.

    Reads an Excel file, processes the data by formatting dates and floats,
    and returns the data as a list of dictionaries.

    Returns:
        list[BotData]: A record list from the processed Excel file.

    Raises:
        FileNotFoundError: If the target file does not exist.
        ValueError: For problems reading the file.

    """
    buffer_planilha = io.BytesIO(base91.decode(base91_planilha))
    df = pd.read_excel(buffer_planilha)
    df.columns = df.columns.str.upper()

    def format_data(x: Generic[T]) -> str:
        if str(x) == "NaT" or str(x) == "nan":
            return ""

        if isinstance(x, (datetime, pd.Timestamp)):
            return x.strftime("%d/%m/%Y")

        return x

    def format_float(x: Generic[T]) -> str:
        return f"{x:.2f}".replace(".", ",")

    for col in df.columns:
        df[col] = df[col].apply(format_data)

    for col in df.select_dtypes(include=["float"]).columns:
        df[col] = df[col].apply(format_float)

    to_list = [BotData(list(item.items())) for item in df.to_dict(orient="records")]

    return to_list
