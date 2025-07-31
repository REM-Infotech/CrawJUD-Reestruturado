import os
import re
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import Any, Generator

import pandas as pd
from clear import clear
from dotenv import load_dotenv
from termcolor import colored
from tqdm import tqdm

from models.logs import CachedExecution

clear()
load_dotenv()


data_query = CachedExecution.all_data()
path_planilha = Path(__file__).parent.joinpath("Processos.xlsx")

if path_planilha.exists():
    os.remove(path_planilha)

list_dict_representantes: list[dict[str, str]] = []
kw = {
    "path": path_planilha,
    "engine": "openpyxl",
    "mode": "a",
    "if_sheet_exists": "overlay",
}


def formata_assuntos(
    lista: list[dict[str, str]],
) -> Generator[dict[str, datetime | str], Any, None]:
    for item in lista:
        formated_data = {
            f"{k}".upper(): formata_tempo(v)
            for k, v in list(dict(item).items())
            if not isinstance(v, list) or not k.lower() == "id"
        }

        yield formated_data


def formata_endereco(endr_dict: dict[str, str]) -> str:
    return " | ".join([
        f"{endr_k.upper()}: {endr_v.strip()}"
        for endr_k, endr_v in list(endr_dict.items())
    ])


def formata_representantes(
    lista: list[dict[str, str]],
) -> Generator[dict[str, datetime | str], Any, None]:
    for item in lista:
        tipo_parte = item.pop("tipo")
        if item.get("endereco"):
            item.update({"endereco".upper(): formata_endereco(item.get("endereco"))})

        formated_data = {
            f"{k}_{tipo_parte}".upper(): formata_tempo(v)
            for k, v in list(dict(item).items())
            if not isinstance(v, list)
            and not k.lower() == "utilizaLoginSenha".lower()
            and not k.lower() == "situacao".lower()
            and not k.lower() == "login".lower()
            and not k.lower() == "idPessoa".lower()
        }

        yield formated_data


def formata_partes(
    lista: list[dict[str, str]],
) -> Generator[dict[str, datetime | str], Any, None]:
    for item in lista:
        polo_parte = item.pop("polo")
        representantes: list[dict[str, str]] = []

        if item.get("endereco"):
            item.update({"endereco".upper(): formata_endereco(item.get("endereco"))})

        if item.get("representantes"):
            representantes = item.pop("representantes")

        if item.get("papeis"):
            item.pop("papeis")

        formated_data = {
            f"{k}_polo_{polo_parte}".upper(): formata_tempo(v)
            for k, v in list(dict(item).items())
            if not isinstance(v, list)
            and not k.lower() == "utilizaLoginSenha".lower()
            and not k.lower() == "situacao".lower()
            and not k.lower() == "login".lower()
            and not k.lower() == "idPessoa".lower()
        }

        for adv in list(formata_representantes(representantes)):
            _new_data = {"REPRESENTADO": item.get("nome")}
            _new_data.update(adv)
            list_dict_representantes.append(_new_data)

        yield formated_data


def formata_partes_terceiros(
    lista: list[dict[str, str]],
) -> Generator[dict[str, str], Any, None]:
    for item in lista:
        polo_parte = item.pop("polo")
        representantes: list[dict[str, str]] = []

        if item.get("endereco"):
            item.update({"endereco".upper(): formata_endereco(item.get("endereco"))})

        if item.get("representantes"):
            representantes = item.pop("representantes")

        if item.get("papeis"):
            item.pop("papeis")

        formated_data = {
            f"{k}_{polo_parte}".upper(): formata_tempo(v)
            for k, v in list(dict(item).items())
            if not isinstance(v, list)
            and not k.lower() == "utilizaLoginSenha".lower()
            and not k.lower() == "situacao".lower()
            and not k.lower() == "login".lower()
            and not k.lower() == "idPessoa".lower()
        }

        for adv in list(formata_representantes(representantes)):
            _new_data = {"REPRESENTADO": item.get("nome")}
            _new_data.update(adv)
            list_dict_representantes.append(_new_data)

        yield formated_data


def formata_tempo(item: str | bool) -> datetime | float | int | bool | str:
    if isinstance(item, str):
        if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$", item):
            return datetime.strptime(item.split(".")[0], "%Y-%m-%dT%H:%M:%S")

        elif re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}$", item):
            return datetime.strptime(item, "%Y-%m-%dT%H:%M:%S.%f")

    return item


def formata_anexos(
    lista: list[dict[str, str]],
) -> Generator[dict[str, str], Any, None]:
    new_lista: list[dict[str, str]] = []
    for item in lista:
        new_lista.extend(item.pop("anexos"))

    for item in new_lista:
        formated_data = {
            k.upper(): formata_tempo(v)
            for k, v in list(dict(item).items())
            if not isinstance(v, list)
            and (
                k.lower() == "id"
                or k.lower() == "titulo"
                or k.lower() == "idUnicoDocumento".lower()
                or k.lower() == "data"
            )
        }

        yield formated_data


def formata_movimentacao(
    lista: list[dict[str, str]],
) -> Generator[dict[str, str], Any, None]:
    for item in lista:
        if item.get("anexos"):
            item.pop("anexos")

        formated_data = {
            k.upper(): formata_tempo(v)
            for k, v in list(dict(item).items())
            if not isinstance(v, list)
            and (
                k.lower() == "id"
                or k.lower() == "titulo"
                or k.lower() == "idUnicoDocumento".lower()
                or k.lower() == "data"
                or k.lower() == "usuarioCriador".lower()
                or k.lower() == "tipoConteudo".lower()
            )
        }

        yield formated_data


# Salva os dados em lotes para evitar exceder o limite de linhas do Excel
def save_in_batches(
    data: list[dict], sheet_name: str, writer: pd.ExcelWriter, batch_size: int = 5000
) -> None:
    """
    Salva os dados em lotes no arquivo Excel para evitar exceder o limite de linhas.

    Args:
        data (list[dict]): Lista de dicionários com os dados a serem salvos.
        sheet_name (str): Nome da planilha no Excel.
        writer (pd.ExcelWriter): Objeto ExcelWriter para escrita.
        batch_size (int): Tamanho do lote de linhas por escrita.

    Returns:
        None: Não retorna valor.

    """
    df = pd.DataFrame(data)
    try:
        existing_df = pd.read_excel(str(path_planilha), sheet_name=sheet_name)
        df_final = pd.concat([existing_df, df])
        df_final.to_excel(writer, sheet_name=sheet_name, index=False)
    except Exception:
        df.to_excel(writer, sheet_name=sheet_name, index=False)


def formata_geral(
    lista: list[dict[str, str]],
) -> Generator[dict[str, datetime | str], Any, None]:
    for item in lista:
        formated_data = {
            k.upper(): formata_tempo(v)
            for k, v in list(dict(item).items())
            if not isinstance(v, list)
        }

        yield formated_data


def load_data() -> tuple[list, list, list]:
    pbar = tqdm(enumerate(data_query))
    data_save: list[dict[str, str]] = []
    advogados: list[dict[str, str]] = []
    outras_partes_list: list[dict[str, str]] = []
    lista_partes_ativo: list[dict[str, str]] = []
    lista_partes_passivo: list[dict[str, str]] = []
    list_assuntos: list[dict[str, str]] = []  # noqa: N806
    list_anexos: list[dict[str, str]] = []
    list_movimentacoes: list[dict[str, str]] = []
    list_expedientes: list[dict[str, str]] = []
    contagem = 0
    divide_5 = 0
    for _, _item in pbar:
        if not pbar.total:
            pbar.total = int(_item.total_pks)
            pbar.display()
            divide_5 = int(pbar.total / 5)

        _pk = _item.processo
        _data_item = _item.model_dump()["data"]
        _data_item.pop("numero")

        if _data_item.get("expedientes"):
            list_expedientes.extend([
                {"NUMERO_PROCESSO": _pk, **item}
                for item in list(formata_geral(list(_data_item.pop("expedientes"))))
            ])

        if _data_item.get("itensProcesso"):
            itens_processo: list[dict[str, str]] = _data_item.pop("itensProcesso")
            list_anexos.extend([
                {"NUMERO_PROCESSO": _pk, **item}
                for item in list(
                    formata_anexos(
                        list(filter(lambda x: x.get("anexos"), itens_processo))
                    )
                )
            ])
            list_movimentacoes.extend([
                {"NUMERO_PROCESSO": _pk, **item}
                for item in formata_movimentacao(list(itens_processo))
            ])

        list_assuntos.extend([
            {"NUMERO_PROCESSO": _pk, **item}
            for item in list(formata_assuntos(_data_item.pop("assuntos")))
        ])
        lista_partes_passivo.extend([
            {"NUMERO_PROCESSO": _pk, **item}
            for item in list(formata_partes(_data_item.pop("poloPassivo")))
        ])
        lista_partes_ativo.extend([
            {"NUMERO_PROCESSO": _pk, **item}
            for item in list(formata_partes(_data_item.pop("poloAtivo")))
        ])

        if _data_item.get("poloOutros"):
            outras_partes_list.extend([
                {"NUMERO_PROCESSO": _pk, **item}
                for item in list(
                    formata_partes_terceiros(_data_item.pop("poloOutros"))
                )
            ])

        global list_dict_representantes
        advogados.extend([
            {"NUMERO_PROCESSO": _pk, **item} for item in list_dict_representantes
        ])

        data_save.extend([
            {"NUMERO_PROCESSO": _pk, **item}
            for item in list(formata_geral([_data_item]))
        ])

        if contagem == int(divide_5) or int(pbar.n) + 1 == pbar.total:
            with pd.ExcelWriter(**kw) as writer:
                saves = [
                    (data_save, "Processos", writer),
                    (list_assuntos, "Assuntos", writer),
                    (outras_partes_list, "Outras Partes", writer),
                    (lista_partes_ativo, "Autores", writer),
                    (lista_partes_passivo, "Réus", writer),
                    (advogados, "Advogados", writer),
                    (list_movimentacoes, "Movimentações", writer),
                    (list_anexos, "Anexos Movimentações", writer),
                    (list_expedientes, "Expedientes", writer),
                ]
                for save in saves:
                    save_in_batches(*save)
                    save[0].clear()

                data_save: list[dict[str, str]] = []
                advogados = []
                outras_partes_list = []
                lista_partes_ativo = []
                lista_partes_passivo = []
                list_assuntos: list[dict[str, str]] = []
                list_anexos: list[dict[str, str]] = []
                list_movimentacoes: list[dict[str, str]] = []
                list_expedientes: list[dict[str, str]] = []

            contagem = 0

        tqdm.write(
            colored(
                str(int(pbar.n) + 1 == pbar.total),
                color={"False": "red", "True": "green"}[
                    str(int(pbar.n) + 1 == pbar.total)
                ],
            )
        )
        contagem += 1
        list_dict_representantes = []


with suppress(Exception):
    if not path_planilha.exists():
        with pd.ExcelWriter(str(path_planilha), "openpyxl", mode="w") as writer:
            pd.DataFrame().to_excel(excel_writer=writer, sheet_name="Processos")


load_data()
