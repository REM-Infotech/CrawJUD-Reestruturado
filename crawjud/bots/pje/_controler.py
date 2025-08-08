# noqa: D104
from __future__ import annotations

import re
import secrets
import traceback
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from datetime import datetime
from os import path, remove
from pathlib import Path
from threading import Semaphore
from time import sleep
from typing import TYPE_CHECKING, Any, Generator, cast
from uuid import uuid4

import pandas as pd
from httpx import Client
from pytz import timezone
from tqdm import tqdm

from celery_app.custom._task import ContextTask
from crawjud.abstract._head import HeadBot
from crawjud.common.exceptions.bot import ExecutionError
from crawjud.types.bot import BotData
from crawjud.types.pje import DictDesafio, DictResults, DictSeparaRegiao, Processo
from utils.models.logs import CachedExecution
from utils.recaptcha import captcha_to_image
from utils.storage import Storage

if TYPE_CHECKING:
    from httpx import Response

    from crawjud.types.bot import BotData

DictData = dict[str, str | datetime]
ListData = list[DictData]

workdir = Path(__file__).cwd()


class PjeBot[T](HeadBot, ContextTask):
    semaforo_save = Semaphore(1)
    _storage = Storage("minio")

    @property
    def storage(self) -> Storage:
        return self._storage

    def buscar_processo(self, data: BotData, row: int, client: Client) -> DictResults:
        cls_search = self.subclasses_search[f"{self.system.lower()}search"]
        return cls_search.search(self, data=data, row=row, client=client)

    def autenticar(self, system: str) -> bool:
        return self.subclasses_auth[f"auth{system.lower()}"].auth(self)

    def regioes(self) -> Generator[tuple[str, str], Any, None]:
        self.carregar_arquivos()

        dict_processo_separado: DictSeparaRegiao = self.separar_regiao()

        posicoes_processos_planilha = dict_processo_separado["position_process"]
        regioes = dict_processo_separado["regioes"]

        self._posicoes_processos = posicoes_processos_planilha
        self.total_rows = len(posicoes_processos_planilha.values())

        for regiao, data_regiao in regioes.items():
            self.regiao = regiao
            self.data_regiao = data_regiao

            yield regiao, data_regiao

    def save_file_downloaded(
        self,
        file_name: str,
        response: Response,
        data: BotData,
        row: int,
    ) -> None:
        try:
            path_temp = workdir.joinpath("temp", uuid4().hex)

            chunk = 8 * 1024 * 1024
            file_path = path_temp.joinpath(file_name)
            # Salva arquivo em chunks no storage
            size: int = response.headers.get("Content-Length")
            dest_name = path.join(self.pid.upper(), file_name)
            upload_file = False
            with file_path.open("wb") as f:
                for _bytes in response.iter_bytes(chunk):
                    f.write(_bytes)
                    try:
                        upload_file = True
                        self.storage.append_object(dest_name, _bytes, chunk, size)
                    except Exception as e:
                        tqdm.write("\n".join(traceback.format_exception(e)))

            if not upload_file:
                file_size = path.getsize(file_path)
                with file_path.open("rb") as file:
                    self.storage.put_object(
                        object_name=dest_name,
                        data=file,
                        length=file_size,
                    )

            with suppress(Exception):
                remove(file_path)

        except Exception as e:
            str_exc = "\n".join(traceback.format_exception_only(e))
            message = "Não foi possível baixar o arquivo. " + str_exc
            self.print_msg(
                row=row,
                message=message,
                type_log="warning",
            )

        finally:
            message = "Arquivo do processo n.{proc} baixado com sucesso!".format(
                proc=data["NUMERO_PROCESSO"]
            )
            self.print_msg(
                row=row,
                message=message,
                type_log="info",
            )

    def save_success_cache(self, data: Processo, processo: str) -> None:
        with suppress(Exception):
            _cache = CachedExecution(processo=processo, data=data, pid=self.pid)
            _cache.save()

    def desafio_captcha(
        self,
        row: int,
        data: BotData,
        id_processo: str,
        client: Client,
    ) -> DictResults:
        """
        Resolve o desafio captcha para acessar informações do processo no sistema PJe.

        Returns:
            Resultados: Dicionário contendo headers, cookies e resultados do processo.

        Raises:
            ExecutionError: Caso não seja possível obter informações do processo após 15 tentativas.

        """
        count_try: int = 0
        response_desafio = None
        data_request: DictDesafio = {}

        def formata_data_result() -> DictDesafio:
            _request_json = response_desafio.json()

            if isinstance(_request_json, list):
                _request_json = _request_json[-1]

            return cast(DictDesafio, _request_json)

        def args_desafio() -> tuple[str, str]:
            if count_try == 0:
                link = f"/captcha?idProcesso={id_processo}"

                nonlocal response_desafio
                response_desafio = client.get(url=link, timeout=60)

                nonlocal data_request
                data_request = formata_data_result()

            img = data_request.get("imagem")
            token_desafio = data_request.get("tokenDesafio")

            return img, token_desafio

        while count_try <= 15:
            with suppress(Exception):
                img, token_desafio = args_desafio()
                text = captcha_to_image(img)

                link = f"/processos/{id_processo}?tokenDesafio={token_desafio}&resposta={text}"
                response_desafio = client.get(url=link, timeout=60)

                _sleep = secrets.randbelow(5) + 3

                if response_desafio.status_code == 403:
                    raise ExecutionError(
                        message="Erro ao obter informações do processo"
                    )

                data_request = response_desafio.json()
                imagem = data_request.get("imagem")

                if imagem:
                    count_try += 1
                    sleep(_sleep)
                    continue

                msg = f"Processo {data['NUMERO_PROCESSO']} encontrado! Salvando dados..."
                self.print_msg(message=msg, row=row, type_log="info")

                captcha_token = response_desafio.headers.get("captchatoken", "")
                return DictResults(
                    id_processo=id_processo,
                    captchatoken=str(captcha_token),
                    text=text,
                    data_request=cast(Processo, data_request),
                )

        if count_try > 15:
            self.print_msg(
                message="Erro ao obter informações do processo",
                row=row,
                type_log="error",
            )
            return

        return None

    def formata_trt(self, numero_processo: str) -> None | tuple[str, str]:  # noqa: D102
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

    def separar_regiao(self) -> DictSeparaRegiao:
        """
        Separa os processos por região a partir do número do processo.

        Returns:
            dict[str, list[BotData] | dict[str, int]]: Dicionário com as regiões e a
            posição de cada processo.

        """
        regioes_dict: dict[str, list[BotData]] = {}
        position_process: dict[str, int] = {}

        for item in self.bot_data:
            numero_processo = item["NUMERO_PROCESSO"]
            format_item = self.formata_trt(numero_processo)

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

        return {"regioes": regioes_dict, "position_process": position_process}

    def salva_sucesso(self) -> None:
        try:
            path_temp = workdir.joinpath("temp", uuid4().hex)

            path_temp.mkdir(parents=True, exist_ok=True)

            _data = datetime.now(timezone("America/Manaus")).strftime(
                "%d-%m-%Y_%H-%M-%S"
            )
            path_planilha = path_temp.parent.joinpath(
                f"EXECUÇÃO {self.pid.upper()} - {_data}.xlsx"
            )

            xlsx_writer = pd.ExcelWriter(str(path_planilha), "openpyxl", mode="w")
            with self.semaforo_save:
                with ThreadPoolExecutor(max_workers=5) as pool:
                    with xlsx_writer as writer:
                        semaforo_planilha = Semaphore(1)
                        data_query = CachedExecution.all_data()

                        list_dict_representantes: list[dict[str, str]] = []

                        def formata_assuntos(
                            lista: list[dict[str, str]],
                        ) -> Generator[dict[str, datetime | str], Any, None]:
                            for item in lista:
                                formated_data = {
                                    f"{k}".upper(): formata_tempo(v)
                                    for k, v in dict(item).items()
                                    if not isinstance(v, list) or k.lower() != "id"
                                }

                                yield formated_data

                        def formata_endereco(endr_dict: dict[str, str]) -> str:
                            return " | ".join([
                                f"{endr_k.upper()}: {endr_v.strip()}"
                                for endr_k, endr_v in endr_dict.items()
                            ])

                        def formata_representantes(
                            lista: list[dict[str, str]],
                        ) -> Generator[dict[str, datetime | str], Any, None]:
                            for item in lista:
                                tipo_parte = item.pop("tipo")
                                if item.get("endereco"):
                                    item.update({
                                        "endereco".upper(): formata_endereco(
                                            item.get("endereco")
                                        )
                                    })

                                formated_data = {
                                    f"{k}_{tipo_parte}".upper(): formata_tempo(v)
                                    for k, v in item.items()
                                    if not isinstance(v, list)
                                    and all([
                                        k.lower() != "utilizaLoginSenha".lower(),
                                        k.lower() != "situacao".lower(),
                                        k.lower() != "login".lower(),
                                        k.lower() != "idPessoa".lower(),
                                    ])
                                }

                                yield formated_data

                        def formata_partes(
                            lista: list[dict[str, str]],
                        ) -> Generator[dict[str, datetime | str], Any, None]:
                            for item in lista:
                                polo_parte = item.pop("polo")
                                representantes: list[dict[str, str]] = []

                                if item.get("endereco"):
                                    item.update({
                                        "endereco".upper(): formata_endereco(
                                            item.get("endereco")
                                        )
                                    })

                                if item.get("representantes"):
                                    representantes = item.pop("representantes")

                                if item.get("papeis"):
                                    item.pop("papeis")

                                formated_data = {
                                    f"{k}_polo_{polo_parte}".upper(): formata_tempo(v)
                                    for k, v in item.items()
                                    if not isinstance(v, list)
                                    and all([
                                        k.lower() != "utilizaLoginSenha".lower(),
                                        k.lower() != "situacao".lower(),
                                        k.lower() != "login".lower(),
                                        k.lower() != "idPessoa".lower(),
                                    ])
                                }

                                for adv in formata_representantes(representantes):
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
                                    item.update({
                                        "endereco".upper(): formata_endereco(
                                            item.get("endereco")
                                        )
                                    })

                                if item.get("representantes"):
                                    representantes = item.pop("representantes")

                                if item.get("papeis"):
                                    item.pop("papeis")

                                formated_data = {
                                    f"{k}_{polo_parte}".upper(): formata_tempo(v)
                                    for k, v in item.items()
                                    if not isinstance(v, list)
                                    and all([
                                        k.lower() != "id".lower(),
                                        k.lower() != "nome".lower(),
                                        k.lower() != "tipo".lower(),
                                        k.lower() != "endereco".lower(),
                                    ])
                                }

                                for adv in formata_representantes(representantes):
                                    _new_data = {"REPRESENTADO": item.get("nome")}
                                    _new_data.update(adv)
                                    list_dict_representantes.append(_new_data)

                                yield formated_data

                        def formata_tempo(
                            item: str | bool,
                        ) -> datetime | float | int | bool | str:
                            if isinstance(item, str):
                                if re.match(
                                    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$", item
                                ):
                                    return datetime.strptime(
                                        item.split(".")[0], "%Y-%m-%dT%H:%M:%S"
                                    )

                                elif re.match(
                                    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}$",
                                    item,
                                ):
                                    return datetime.strptime(
                                        item, "%Y-%m-%dT%H:%M:%S.%f"
                                    )

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
                                    for k, v in item.items()
                                    if not isinstance(v, list)
                                    and any(
                                        k.lower() == x.lower()
                                        for x in (
                                            "id",
                                            "titulo",
                                            "idUnicoDocumento",
                                            "data",
                                        )
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
                                    for k, v in item.items()
                                    if not isinstance(v, list)
                                    and any(
                                        k.lower() == x.lower()
                                        for x in (
                                            "id",
                                            "titulo",
                                            "idUnicoDocumento",
                                            "data",
                                            "usuarioCriador",
                                            "tipoConteudo",
                                        )
                                    )
                                }

                                yield formated_data

                        def save_in_batches(
                            _data_list: list[dict], _sheet_name: str
                        ) -> None:
                            """
                            Salva os dados em lotes no arquivo Excel para evitar exceder o limite de linhas.

                            Returns:
                                None: Não retorna valor.

                            """
                            with semaforo_planilha:
                                df = pd.DataFrame(_data_list)
                                max_rows = int(writer.book[_sheet_name].max_row)
                                df.to_excel(
                                    writer, _sheet_name, startrow=max_rows + 1
                                )

                        def formata_geral(
                            lista: list[dict[str, str]],
                        ) -> Generator[dict[str, datetime | str], Any, None]:
                            for item in lista:
                                formated_data = {
                                    k.upper(): formata_tempo(v)
                                    for k, v in item.items()
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
                            list_assuntos: list[dict[str, str]] = []
                            list_anexos: list[dict[str, str]] = []
                            list_movimentacoes: list[dict[str, str]] = []
                            list_expedientes: list[dict[str, str]] = []
                            contagem = 0
                            divide_5 = 0

                            for _, _item in pbar:
                                if not pbar.total:
                                    pbar.total = int(_item.total_pks) + 1
                                    pbar.display()
                                    divide_5 = int(pbar.total / 5)

                                _pk = _item.processo
                                _data_item = _item.model_dump()["data"]

                                if not _data_item.get("numero"):
                                    print(_data_item)
                                    continue

                                _data_item.pop("numero")

                                if _data_item.get("expedientes"):
                                    list_expedientes.extend([
                                        {"NUMERO_PROCESSO": _pk, **item}
                                        for item in formata_geral(
                                            list(_data_item.pop("expedientes"))
                                        )
                                    ])

                                if _data_item.get("itensProcesso"):
                                    itens_processo: list[dict[str, str]] = (
                                        _data_item.pop("itensProcesso")
                                    )
                                    list_anexos.extend([
                                        {"NUMERO_PROCESSO": _pk, **item}
                                        for item in formata_anexos(
                                            list(
                                                filter(
                                                    lambda x: x.get("anexos"),
                                                    itens_processo,
                                                )
                                            )
                                        )
                                    ])
                                    list_movimentacoes.extend([
                                        {"NUMERO_PROCESSO": _pk, **item}
                                        for item in formata_movimentacao(
                                            itens_processo
                                        )
                                    ])

                                list_assuntos.extend([
                                    {"NUMERO_PROCESSO": _pk, **item}
                                    for item in formata_assuntos(
                                        _data_item.pop("assuntos")
                                    )
                                ])
                                lista_partes_passivo.extend([
                                    {"NUMERO_PROCESSO": _pk, **item}
                                    for item in formata_partes(
                                        _data_item.pop("poloPassivo")
                                    )
                                ])
                                lista_partes_ativo.extend([
                                    {"NUMERO_PROCESSO": _pk, **item}
                                    for item in formata_partes(
                                        _data_item.pop("poloAtivo")
                                    )
                                ])

                                if _data_item.get("poloOutros"):
                                    outras_partes_list.extend([
                                        {"NUMERO_PROCESSO": _pk, **item}
                                        for item in formata_partes_terceiros(
                                            _data_item.pop("poloOutros")
                                        )
                                    ])

                                global list_dict_representantes
                                advogados.extend([
                                    {"NUMERO_PROCESSO": _pk, **item}
                                    for item in list_dict_representantes
                                ])

                                data_save.extend([
                                    {"NUMERO_PROCESSO": _pk, **item}
                                    for item in formata_geral([_data_item])
                                ])

                                if (
                                    contagem == int(divide_5)
                                    or int(pbar.n) + 1 == pbar.total
                                ):
                                    saves = [
                                        (data_save, "Processos"),
                                        (list_assuntos, "Assuntos"),
                                        (outras_partes_list, "Outras Partes"),
                                        (lista_partes_ativo, "Autores"),
                                        (lista_partes_passivo, "Réus"),
                                        (advogados, "Advogados"),
                                        (list_movimentacoes, "Movimentações"),
                                        (list_anexos, "Anexos Movimentações"),
                                        (list_expedientes, "Expedientes"),
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

                                contagem += 1
                                list_dict_representantes = []

                            if len(data_save) > 0:
                                saves = [
                                    (data_save, "Processos"),
                                    (list_assuntos, "Assuntos"),
                                    (outras_partes_list, "Outras Partes"),
                                    (lista_partes_ativo, "Autores"),
                                    (lista_partes_passivo, "Réus"),
                                    (advogados, "Advogados"),
                                    (list_movimentacoes, "Movimentações"),
                                    (list_anexos, "Anexos Movimentações"),
                                    (list_expedientes, "Expedientes"),
                                ]
                                for save in saves:
                                    pool.submit(
                                        save_in_batches,
                                        _data_item=save[0],
                                        _sheet_name=save[1],
                                    )
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

                        load_data()

                        with suppress(Exception):
                            dest_path = path.join(
                                self.pid.upper(), path_planilha.name
                            )
                            self.storage.fput_object(
                                object_name=dest_path, file_path=str(path_planilha)
                            )

        except Exception as e:
            self.print_msg("\n".join(traceback.format_exception_only(e)))
