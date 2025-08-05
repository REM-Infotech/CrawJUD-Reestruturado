# noqa: D100

import re
from contextlib import suppress
from datetime import datetime
from typing import Generic, TypeVar, cast

from celery import shared_task

from celery_app.custom._canvas import subtask
from crawjud.bots.resources.formatadores import formata_tempo
from crawjud.types import ReturnFormataTempo
from crawjud.types.bot import BotData
from crawjud.types.pje import DictSeparaRegiao

DictData = dict[str, str | datetime]
ListData = list[DictData]

T = TypeVar("AnyValue", bound=ReturnFormataTempo)


class PJeFormatadores:  # noqa: D101
    @staticmethod
    @shared_task(name="pje.separar_regiao")
    async def separar_regiao(  # noqa: D417
        frame: list[BotData], *args: Generic[T], **kwargs: Generic[T]
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

        def formata_trt(numero_processo: str) -> None | tuple[str, str]:  # noqa: D102
            # Remove letras, símbolos e pontuações, mantendo apenas números

            # Verifica se o número do processo está no formato CNJ (NNNNNNN-DD.AAAA.J.TR.NNNN)
            padrao_cnj = r"^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$"
            # Remove caracteres especiais e letras, mantendo apenas números, pontuação, "-" e "_"
            numero_processo = re.sub(r"[^\d\-\._]", "", numero_processo)

            if not re.match(padrao_cnj, numero_processo):
                return

            numero_processo = re.sub(
                r"(\d{7})(\d{2})(\d{4})(\d)(\d{2})(\d{4})",
                r"\1-\2.\3.\4.\5.\6",
                numero_processo,
            )
            with suppress(Exception):
                trt_id = re.search(r"(?<=5\.)\d{2}", numero_processo).group()
                if trt_id.startswith("0"):
                    trt_id = trt_id.replace("0", "")

                return trt_id, numero_processo

        for item in frame:
            numero_processo = item["NUMERO_PROCESSO"]
            format_item = formata_trt(numero_processo)

            if not format_item:
                continue

            # Extrai a região e o número do processo formatado
            regiao = format_item[0]
            numero_processo = format_item[1]

            # Atualiza o número do processo no item
            item["NUMERO_PROCESSO"] = numero_processo

            # Adiciona a posição do processo na lista original no dicionário de posições
            position_process[numero_processo] = len(position_process)

            # Caso a região não exista no dicionário, cria uma nova lista
            if not regioes_dict.get(regiao):
                regioes_dict[regiao] = [item]
                continue

            # Caso a região já exista, adiciona o item à lista correspondente
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
    async def formata_url_pje(  # noqa: D102, D103
        regiao: str,
        type_format: str = "login",
        *args: Generic[T],
        **kwargs: Generic[T],
    ) -> str:
        formats = {
            "login": f"https://pje.trt{regiao}.jus.br/primeirograu/login.seam",
            "validate_login": f"https://pje.trt{regiao}.jus.br/pjekz/",
            "search": f"https://pje.trt{regiao}.jus.br/consultaprocessual/",
        }

        return formats[type_format]

    @staticmethod
    @shared_task(name="pje.formata_geral")
    def formata_geral(  # noqa: D102
        lista: ListData, *args: Generic[T], **kwargs: Generic[T]
    ) -> ListData:
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
    def formata_assuntos(  # noqa: D102
        lista: ListData, *args: Generic[T], **kwargs: Generic[T]
    ) -> ListData:
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
    def formata_endereco(  # noqa: D102
        endr_dict: DictData, *args: Generic[T], **kwargs: Generic[T]
    ) -> str:
        return " | ".join([
            f"{endr_k.upper()}: {endr_v.strip()}"
            for endr_k, endr_v in list(endr_dict.items())
        ])

    @staticmethod
    @shared_task(name="pje.formata_representantes")
    def formata_representantes(  # noqa: D102
        lista: ListData, *args: Generic[T], **kwargs: Generic[T]
    ) -> ListData:
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
        lista: ListData, *args: Generic[T], **kwargs: Generic[T]
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
        lista: ListData, *args: Generic[T], **kwargs: Generic[T]
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
    def formata_anexos(  # noqa: D102
        lista: ListData, *args: Generic[T], **kwargs: Generic[T]
    ) -> ListData:
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
    def formata_movimentacao(  # noqa: D102
        lista: ListData, *args: Generic[T], **kwargs: Generic[T]
    ) -> ListData:
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
    def formata_trt(  # noqa: D102
        numero_processo: str, *args: Generic[T], **kwargs: Generic[T]
    ) -> str:
        trt_id = None
        with suppress(Exception):
            trt_id = re.search(r"(?<=5\.)\d{2}", numero_processo).group()
            if trt_id.startswith("0"):
                trt_id = trt_id.replace("0", "")

        return trt_id
