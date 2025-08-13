from __future__ import annotations

import re
import secrets
import traceback
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from threading import Semaphore
from time import sleep
from typing import TYPE_CHECKING, Any, cast
from uuid import uuid4

from tqdm import tqdm

from crawjud_app.abstract._head import HeadBot
from crawjud_app.common.exceptions.bot import ExecutionError, FileUploadError
from crawjud_app.custom.task import ContextTask
from crawjud_app.types.bot import BotData
from crawjud_app.types.pje import DictDesafio, DictResults, DictSeparaRegiao, Processo
from utils.models.logs import CachedExecution
from utils.recaptcha import captcha_to_image
from utils.storage import Storage

if TYPE_CHECKING:
    from collections.abc import Generator

    from httpx import Client, Response

    from crawjud_app.types.bot import BotData

DictData = dict[str, str | datetime]
ListData = list[DictData]

workdir = Path(__file__).cwd()

HTTP_STATUS_FORBIDDEN = 403  # Constante para status HTTP Forbidden
COUNT_TRYS = 15


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
            dest_name = str(Path(self.pid.upper()) / file_name)
            upload_file = False
            with file_path.open("wb") as f:
                for _bytes in response.iter_bytes(chunk):
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
                proc=data["NUMERO_PROCESSO"],
            )
            self.print_msg(
                row=row,
                message=message,
                type_log="info",
            )

    def save_success_cache(self, data: Processo, processo: str | None = None) -> None:
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

    def formata_trt(self, numero_processo: str) -> tuple[str, str] | None:
        # Remove letras, símbolos e pontuações, mantendo apenas números

        # Verifica se o número do processo está no formato CNJ
        # Formato CNJ: (NNNNNNN-DD.AAAA.J.TR.NNNN)
        padrao_cnj = r"^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$"
        # Remove caracteres especiais e letras, mantendo apenas números, pontuação,
        # "-" e "_"
        numero_processo = re.sub(r"[^\d\-\._]", "", numero_processo)

        if not re.match(padrao_cnj, numero_processo):
            return None

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
        """Separa os processos por região a partir do número do processo.

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

            # Adiciona a posição do processo na
            # lista original no dicionário de posições
            position_process[numero_processo] = len(position_process)

            # Caso a região não exista no dicionário, cria uma nova lista
            if not regioes_dict.get(regiao):
                regioes_dict[regiao] = [item]
                continue

            # Caso a região já exista, adiciona o item à lista correspondente
            regioes_dict[regiao].append(item)

        return {"regioes": regioes_dict, "position_process": position_process}
