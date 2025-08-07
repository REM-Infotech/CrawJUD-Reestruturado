# noqa: D104
from __future__ import annotations

import secrets
import traceback
from contextlib import suppress
from os import path, remove
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING, Any, Generator, cast
from uuid import uuid4

from httpx import Client
from tqdm import tqdm

from celery_app.custom._canvas import subtask
from celery_app.custom._task import ContextTask
from crawjud.abstract._head import HeadBot
from crawjud.common.exceptions.bot import ExecutionError
from crawjud.types.pje import DictDesafio, DictResults, DictSeparaRegiao, Processo
from utils.recaptcha import captcha_to_image
from utils.storage import Storage

if TYPE_CHECKING:
    from httpx import Response

    from crawjud.types.bot import BotData


workdir = Path(__file__).cwd()
path_temp = workdir.joinpath("temp", uuid4().hex)


class PjeBot[T](HeadBot, ContextTask):
    def buscar_processo(self, data: BotData, row: int, client: Client) -> DictResults:
        cls_search = self.subclasses_search[f"{self.system.lower()}search"]
        return cls_search.search(self, data=data, row=row, client=client)

    def autenticar(self, system: str) -> bool:
        return self.subclasses_auth[f"auth{system.lower()}"].auth(self)

    def regioes(self) -> Generator[tuple[str, str], Any, None]:
        self.carregar_arquivos()

        task_separa_regiao = subtask("pje.separar_regiao")

        dict_processo_separado: DictSeparaRegiao = task_separa_regiao.apply_async(
            kwargs={"frame": self.bot_data}
        ).wait_ready()

        posicoes_processos_planilha = dict_processo_separado["position_process"]
        regioes = dict_processo_separado["regioes"]

        self._posicoes_processos = posicoes_processos_planilha
        self.total_rows = len(posicoes_processos_planilha.values())

        for regiao, data_regiao in list(regioes.items()):
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
            chunk = 8 * 1024 * 1024
            storage = Storage("minio")
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
                        storage.append_object(dest_name, _bytes, chunk, size)
                    except Exception as e:
                        tqdm.write("\n".join(traceback.format_exception(e)))

            if not upload_file:
                file_size = path.getsize(file_path)
                with file_path.open("rb") as file:
                    storage.put_object(
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
