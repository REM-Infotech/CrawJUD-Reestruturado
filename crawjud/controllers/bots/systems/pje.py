"""Módulo para a classe de controle dos robôs PJe."""

from __future__ import annotations

import importlib
import secrets
import traceback
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from threading import Semaphore
from time import sleep
from typing import TYPE_CHECKING, ClassVar, cast
from uuid import uuid4

from tqdm import tqdm

from crawjud.common.exceptions.bot import ExecutionError, FileUploadError
from crawjud.common.exceptions.validacao import ValidacaoStringError
from crawjud.controllers.bots.master.cnj_bots import CNJBots as ClassBot
from crawjud.interface.dict.bot import BotData
from crawjud.interface.types.custom import StrProcessoCNJ
from crawjud.interface.types.pje import (
    DictDesafio,
    DictResults,
    DictSeparaRegiao,
    Processo,
)
from crawjud.utils.models.logs import CachedExecution
from crawjud.utils.recaptcha import captcha_to_image
from crawjud.utils.storage import Storage
from crawjud_app.iterators import RegioesIterator

if TYPE_CHECKING:
    from httpx import Client, Response

    from crawjud.interface.dict.bot import BotData

DictData = dict[str, str | datetime]
ListData = list[DictData]

workdir = Path(__file__).cwd()

HTTP_STATUS_FORBIDDEN = 403  # Constante para status HTTP Forbidden
COUNT_TRYS = 15


class PjeBot[T](ClassBot):
    """Classe de controle para robôs do PJe."""

    pje_classes: ClassVar[dict[str, type[PjeBot]]] = {}
    subclasses_search: ClassVar[dict[str, type[PjeBot]]] = {}

    semaforo_save = Semaphore(1)
    _storage = Storage("minio")

    @property
    def list_posicao_processo(self) -> dict[str, int]:
        return self.posicoes_processos

    @property
    def data_regiao(self) -> list[BotData]:
        return self._data_regiao

    @data_regiao.setter
    def data_regiao(self, _data_regiao: str) -> None:
        self._data_regiao = _data_regiao

    @property
    def regiao(self) -> str:
        return self._regiao

    @property
    def cookies(self) -> dict[str, str]:
        """Dicionário de Cookies."""
        return self._cookies

    @property
    def headers(self) -> dict[str, str]:
        """Dicionário de Headers."""
        return self._headers

    @property
    def base_url(self) -> str:
        """Dicionário de Cookies."""
        return self._base_url

    @regiao.setter
    def regiao(self, _regiao: str) -> None:
        self._regiao = _regiao

    def buscar_processo(self, data: BotData, row: int, client: Client) -> DictResults:
        """Busca o processo no PJe.

        Returns:
            DictResults: dicionário com os resultados da busca.

        """
        return self.pje_classes["pjesearch"].search(
            self,
            data=data,
            row=row,
            client=client,
        )

    def autenticar(self) -> bool:
        """Autenticação do PJE.

        Returns:
            bool: Booleano para identificar se autenicação foi realizada.

        """
        return self.pje_classes["pjeauth"].auth(self)

    def regioes(self) -> RegioesIterator:
        """Listagem das regiões do PJe.

        Returns:
            RegioesIterator:
                Iterator das Regiões do PJe.

        """
        return RegioesIterator(self)

    def save_file_downloaded(
        self,
        file_name: str,
        response_data: Response,
        data_bot: BotData,
        row: int,
    ) -> None:
        """Envia o `arquivo baixado` no processo para o `storage`.

        Arguments:
            file_name (str): Nome do arquivo.
            response_data (Response): response da request httpx.
            data_bot (BotData): Mapping dos dados da planilha de input.
            row (int): row do loop.

        """
        try:
            path_temp = workdir.joinpath("temp", uuid4().hex)

            chunk = 8 * 1024 * 1024
            file_path = path_temp.joinpath(file_name)
            # Salva arquivo em chunks no storage
            size: int = response_data.headers.get("Content-Length")
            dest_name = str(Path(self.pid.upper()) / file_name)
            upload_file = False
            with file_path.open("wb") as f:
                for _bytes in response_data.iter_bytes(chunk):
                    f.write(_bytes)
                    try:
                        upload_file = True
                        self.storage.append_object(dest_name, _bytes, chunk, size)
                    except (FileUploadError, Exception) as e:
                        tqdm.write("\n".join(traceback.format_exception(e)))

            if not upload_file:
                file_size = file_path.stat().st_size
                with file_path.open("rb") as file:
                    self.storage.put_object(
                        object_name=dest_name,
                        data=file,
                        length=file_size,
                    )

            with suppress(Exception):
                file_path.unlink()

        except (FileUploadError, Exception) as e:
            str_exc = "\n".join(traceback.format_exception_only(e))
            message = "Não foi possível baixar o arquivo. " + str_exc
            self.print_msg(
                row=row,
                message=message,
                type_log="warning",
            )

        finally:
            message = "Arquivo do processo n.{proc} baixado com sucesso!".format(
                proc=data_bot["NUMERO_PROCESSO"],
            )
            self.print_msg(
                row=row,
                message=message,
                type_log="info",
            )

    def save_success_cache(
        self,
        data: Processo,
        processo: StrProcessoCNJ | None = None,
    ) -> None:
        """Salva os resultados em cache Redis.

        Arguments:
            data (Processo): Mapping com as informações extraídas do processo
            processo (StrProcessoCNJ): Número do Processo


        """
        with suppress(Exception):
            cache = CachedExecution(processo=processo, data=data, pid=self.pid)
            cache.save()

    def desafio_captcha(
        self,
        row: int,
        data: BotData,
        id_processo: str,
        client: Client,
    ) -> DictResults:
        """Resolve o desafio captcha para acessar informações do processo no PJe.

        Returns:
            Resultados: Dicionário contendo headers, cookies e resultados do processo.

        Raises:
            ExecutionError: Caso não seja possível obter informações do processo
            após 15 tentativas.

        """
        count_try: int = 0
        response_desafio = None
        data_request: DictDesafio = {}

        def formata_data_result() -> DictDesafio:
            request_json = response_desafio.json()

            if isinstance(request_json, list):
                request_json = request_json[-1]

            return cast("DictDesafio", request_json)

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

        while count_try <= COUNT_TRYS:
            with suppress(Exception):
                img, token_desafio = args_desafio()
                text = captcha_to_image(img)

                link = (
                    f"/processos/{id_processo}"
                    f"?tokenDesafio={token_desafio}"
                    f"&resposta={text}"
                )
                response_desafio = client.get(url=link, timeout=60)

                sleep_time = secrets.randbelow(5) + 3

                if response_desafio.status_code == HTTP_STATUS_FORBIDDEN:
                    raise ExecutionError(
                        message="Erro ao obter informações do processo",
                    )

                data_request = response_desafio.json()
                imagem = data_request.get("imagem")

                if imagem:
                    count_try += 1
                    sleep(sleep_time)
                    continue

                msg = (
                    f"Processo {data['NUMERO_PROCESSO']} encontrado! "
                    "Salvando dados..."
                )
                self.print_msg(
                    message=msg,
                    row=row,
                    type_log="info",
                )

                captcha_token = response_desafio.headers.get("captchatoken", "")
                return DictResults(
                    id_processo=id_processo,
                    captchatoken=str(captcha_token),
                    text=text,
                    data_request=cast("Processo", data_request),
                )

        if count_try > COUNT_TRYS:
            self.print_msg(
                message="Erro ao obter informações do processo",
                row=row,
                type_log="error",
            )
            return None

        return None

    def separar_regiao(self) -> DictSeparaRegiao:
        """Separa os processos por região a partir do número do processo.

        Returns:
            dict[str, list[BotData] | dict[str, int]]: Dicionário com as regiões e a
            posição de cada processo.

        """
        regioes_dict: dict[str, list[BotData]] = {}
        position_process: dict[str, int] = {}

        for item in self.bot_data:
            try:
                numero_processo = StrProcessoCNJ(item["NUMERO_PROCESSO"])

                regiao = numero_processo.tj
                # Atualiza o número do processo no item
                item["NUMERO_PROCESSO"] = numero_processo

                # Adiciona a posição do processo na
                # lista original no dicionário de posições
                position_process[numero_processo] = len(position_process)

                # Caso a região não exista no dicionário, cria uma nova lista
                if not regioes_dict.get(regiao):
                    regioes_dict[regiao] = [item]
                    continue

                # Caso a região já exista, adiciona o item à lista correspondente
                regioes_dict[regiao].append(item)

            except ValidacaoStringError:
                continue

        return {"regioes": regioes_dict, "position_process": position_process}

    def formata_url_pje(
        self,
        _format: str = "login",
    ) -> str:
        """Formata a URL no padrão esperado pelo PJe.

        Returns:
            str: URL formatada.

        """
        formats = {
            "login": f"https://pje.trt{self.regiao}.jus.br/primeirograu/login.seam",
            "validate_login": f"https://pje.trt{self.regiao}.jus.br/pjekz/",
            "search": f"https://pje.trt{self.regiao}.jus.br/consultaprocessual/",
        }

        return formats[_format]

    def __init_subclass__(cls) -> None:
        """Empty."""
        cls.pje_classes[cls.__name__.lower()] = cls


importlib.import_module("crawjud.utils.auth.pje")
importlib.import_module("crawjud.utils.search.pje")
