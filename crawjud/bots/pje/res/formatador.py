# noqa: D100

import re
from contextlib import suppress
from datetime import datetime
from typing import cast

from celery import shared_task

from celery_app.custom._canvas import subtask
from crawjud.bots.resources.formatadores import formata_tempo
from crawjud.types.bot import BotData
from crawjud.types.pje import DictSeparaRegiao

DictData = dict[str, str | datetime]
ListData = list[DictData]


class PJeFormatadores:  # noqa: D101
    @staticmethod
    @shared_task(name="pje.separar_regiao")
    async def separar_regiao(
        frame: list[BotData],
    ) -> DictSeparaRegiao:
        """
        Separa os processos por região a partir do número do processo.

        Args:
            frame (list[BotData]): Lista de dicionários contendo dados dos processos.

        Returns:
            dict[str, list[BotData] | dict[str, int]]: Dicionário com as regiões e a
            posição de cada processo.

        """
        regioes_dict: dict[str, list[BotData]] = {}
        position_process: dict[str, int] = {}

        def formata_trt(numero_processo: str) -> str:  # noqa: D102
            trt_id = None
            with suppress(Exception):
                trt_id = re.search(r"(?<=5\.)\d{2}", numero_processo).group()
                if trt_id.startswith("0"):
                    trt_id = trt_id.replace("0", "")

            return trt_id

        for item in frame:
            numero_processo = item["NUMERO_PROCESSO"]
            regiao: str = formata_trt(numero_processo)

            if not regiao:
                continue

            position_process[numero_processo] = len(position_process)
            if not regioes_dict.get(regiao):
                regioes_dict[regiao] = [item]
                continue

            regioes_dict[regiao].append(item)

        return cast(
            DictSeparaRegiao,
            {
                "regioes": regioes_dict,
                "position_process": position_process,
            },
        )

    @staticmethod
    @shared_task(name="pje.formata_url_pje")
    async def formata_url_pje(regiao: str, type_format: str = "login") -> str:  # noqa: D102, D103
        formats = {
            "login": f"https://pje.trt{regiao}.jus.br/primeirograu/login.seam",
            "validate_login": f"https://pje.trt{regiao}.jus.br/pjekz/",
            "search": f"https://pje.trt{regiao}.jus.br/consultaprocessual/",
        }

        return formats[type_format]

    @staticmethod
    @shared_task(name="pje.formata_geral")
    def formata_geral(lista: ListData) -> ListData:  # noqa: D102
        new_data: ListData = []
        for item in lista:
            formated_data = {
                k.upper(): formata_tempo(v)
                for k, v in list(dict(item).items())
                if not isinstance(v, list)
            }

            new_data.append(formated_data)

        return new_data

    @staticmethod
    @shared_task(name="pje.formata_assuntos")
    def formata_assuntos(lista: ListData) -> ListData:  # noqa: D102
        items_formatados: ListData = []

        for item in lista:
            formated_data = {
                f"{k}".upper(): formata_tempo(v)
                for k, v in list(dict(item).items())
                if not isinstance(v, list) or not k.lower() == "id"
            }

            items_formatados.append(formated_data)

        return items_formatados

    @staticmethod
    @shared_task(name="pje.formata_endereco")
    def formata_endereco(endr_dict: DictData) -> str:  # noqa: D102
        return " | ".join([
            f"{endr_k.upper()}: {endr_v.strip()}"
            for endr_k, endr_v in list(endr_dict.items())
        ])

    @staticmethod
    @shared_task(name="pje.formata_representantes")
    def formata_representantes(lista: ListData) -> ListData:  # noqa: D102
        list_dict_representantes: ListData = []
        task_formata_endereco = subtask("pje.formata_endereco")
        for item in lista:
            tipo_parte = item.pop("tipo")
            if item.get("endereco"):
                formatar_endereco = task_formata_endereco.apply_async(
                    kwargs={"endr_dict": item.get("endereco")}
                )
                result = formatar_endereco.wait_ready()
                item.update({"endereco".upper(): result})

            formated_data = {
                f"{k}_{tipo_parte}".upper(): formata_tempo(v)
                for k, v in list(dict(item).items())
                if not isinstance(v, list)
                and not k.lower() == "utilizaLoginSenha".lower()
                and not k.lower() == "situacao".lower()
                and not k.lower() == "login".lower()
                and not k.lower() == "idPessoa".lower()
            }

            list_dict_representantes.append(formated_data)

        return list_dict_representantes

    @staticmethod
    @shared_task(name="pje.formata_partes")
    def formata_partes(  # noqa: D102
        lista: ListData,
    ) -> tuple[ListData, ListData]:
        new_data: ListData = []
        list_dict_representantes: ListData = []
        task_formata_endereco = subtask("pje.formata_endereco")
        for item in lista:
            polo_parte = item.pop("polo")
            representantes: ListData = []

            if item.get("endereco"):
                formatar_endereco = task_formata_endereco.apply_async(
                    kwargs={"endr_dict": item.get("endereco")}
                )
                result = formatar_endereco.wait_ready()
                item.update({"endereco".upper(): result})

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

            representantes_task = subtask("pje.formata_representantes").apply_async(
                kwargs={"lista": representantes, "representado": item.get("nome")}
            )

            result = representantes_task.wait_ready()

            if not isinstance(result, list):
                raise TypeError(
                    f"Expected list from task 'pje.formata_representantes', got {type(result)}"
                )

            new_data.append(formated_data)

        return new_data, list_dict_representantes

    @staticmethod
    @shared_task(name="pje.formata_partes_terceiros")
    def formata_partes_terceiros(  # noqa: D102
        lista: ListData,
    ) -> tuple[ListData, ListData]:
        list_dict_representantes: ListData = []
        new_data: ListData = []

        task_formata_endereco = subtask("pje.formata_endereco")
        for item in lista:
            polo_parte = item.pop("polo")
            representantes: ListData = []

            if item.get("endereco"):
                formatar_endereco = task_formata_endereco.apply_async(
                    kwargs={"endr_dict": item.get("endereco")}
                )
                result = formatar_endereco.wait_ready()
                item.update({"endereco".upper(): result})

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

            representantes_task = subtask("pje.formata_representantes").apply_async(
                kwargs={"lista": representantes, "representado": item.get("nome")}
            )

            result = representantes_task.wait_ready()

            if not isinstance(result, list):
                raise TypeError(
                    f"Expected list from task 'pje.formata_representantes', got {type(result)}"
                )

            list_dict_representantes.extend(result)

            new_data.append(formated_data)

        return new_data, list_dict_representantes

    @staticmethod
    @shared_task(name="pje.formata_anexos")
    def formata_anexos(lista: ListData) -> ListData:  # noqa: D102
        new_data: ListData = []
        new_lista: ListData = []
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

            new_data.append(formated_data)

        return new_data

    @staticmethod
    @shared_task(name="pje.formata_movimentacao")
    def formata_movimentacao(lista: ListData) -> ListData:  # noqa: D102
        new_data: ListData = []

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

            new_data.append(formated_data)

        return new_data

    @staticmethod
    @shared_task(name="pje.formata_trt")
    def formata_trt(numero_processo: str) -> str:  # noqa: D102
        trt_id = None
        with suppress(Exception):
            trt_id = re.search(r"(?<=5\.)\d{2}", numero_processo).group()
            if trt_id.startswith("0"):
                trt_id = trt_id.replace("0", "")

        return trt_id
