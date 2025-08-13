"""Fornece funções utilitárias para formatação dados."""

from __future__ import annotations

import io
import re
from datetime import datetime
from zoneinfo import ZoneInfo

import base91
import pandas as pd

from crawjud_app.decorators import shared_task
from interface.dict.bot import BotData


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


@shared_task(name="crawjud.dataFrame")
def dataframe[T](
    base91_planilha: str,
) -> list[BotData]:
    """Convert an Excel file to a list of dictionaries with formatted data.

    Reads an Excel file, processes the data by formatting dates and floats,
    and returns the data as a list of dictionaries.

    Returns:
        list[BotData]: A record list from the processed Excel file.

    """
    buffer_planilha = io.BytesIO(base91.decode(base91_planilha))
    df = pd.read_excel(buffer_planilha)
    df.columns = df.columns.str.upper()

    def format_data(x: T) -> str:
        if str(x) == "NaT" or str(x) == "nan":
            return ""

        if isinstance(x, (datetime, pd.Timestamp)):
            return x.strftime("%d/%m/%Y")

        return x

    def format_float(x: T) -> str:
        return f"{x:.2f}".replace(".", ",")

    for col in df.columns:
        df[col] = df[col].apply(format_data)

    for col in df.select_dtypes(include=["float"]).columns:
        df[col] = df[col].apply(format_float)

    return [BotData(list(item.items())) for item in df.to_dict(orient="records")]
