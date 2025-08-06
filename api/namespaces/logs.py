"""Define o namespace de logs para integração com WebSocket e gerenciamento de logs em tempo real."""

from __future__ import annotations

import traceback
from typing import Any

import engineio
import socketio
from quart import request, session
from quart_socketio import Namespace
from tqdm import tqdm

from utils.interfaces import ItemMessageList
from utils.models.logs import MessageLog, MessageLogDict


class ASyncServerType(socketio.AsyncServer):
    """
    Define o tipo de servidor assíncrono para integração com o Socket.IO.

    Args:
        Nenhum argumento específico.

    Returns:
        None: Classe de tipagem para o servidor assíncrono.

    """

    eio: engineio.AsyncServer


class LogsNamespace(Namespace):
    """
    Gerencia eventos de logs em tempo real via WebSocket.

    Args:
        namespace (str): Nome do namespace.
        server (ASyncServerType): Instância do servidor assíncrono.

    Returns:
        None: Classe de namespace para manipulação de logs.

    """

    namespace: str
    server: ASyncServerType

    async def on_connect(self) -> None:
        """
        Manipula o evento de conexão de um cliente ao namespace.

        Args:
            Nenhum argumento.

        Returns:
            None: Apenas executa ações de conexão.

        """
        # Obtém o session id do request
        sid = request.sid
        # Salva a sessão do usuário conectado
        await self.save_session(sid=sid, session=session)

    async def on_disconnect(self) -> None:
        """
        Manipula o evento de desconexão de um cliente.

        Args:
            Nenhum argumento.

        Returns:
            None: Apenas executa ações de desconexão.

        """
        # Evento de desconexão não implementado

    async def on_stopbot(self, *args: Any, **kwargs: Any) -> None:
        """
        Emitissor de sinal de parada para um processo específico.

        Args:
            *args: Argumentos posicionais.
            **kwargs: Argumentos nomeados.

        Returns:
            None: Apenas emite o evento de parada.

        """
        data = await request.form

        await self.emit("stopbot", room=data["pid"])

    async def on_join_room(self) -> None:
        """
        Adiciona o cliente a uma sala específica.

        Args:
            Nenhum argumento.

        Returns:
            None: Apenas adiciona o cliente à sala.

        """
        # Obtém o session id e os dados do formulário
        sid = request.sid
        data = await request.form
        # Adiciona o cliente à sala informada
        await self.enter_room(sid=sid, room=data["room"], namespace=self.namespace)

    async def on_load_cache(self) -> MessageLogDict:
        """
        Carrega o cache de logs para um processo.

        Args:
            Nenhum argumento.

        Returns:
            MessageLogDict: Dicionário com os dados do log carregado.

        """
        # Obtém os dados do formulário e carrega o log do Redis
        _data = dict(list((await request.form).items()))
        message = await self.log_redis(pid=_data["pid"])
        return message, True

    async def on_log_execution(self) -> None:
        """
        Recebe e propaga logs de execução em tempo real.

        Args:
            Nenhum argumento.

        Returns:
            None: Apenas emite o log para a sala correspondente.

        """
        # Obtém os dados do formulário e atualiza o log no Redis
        _data = dict(list((await request.form).items()))

        try:
            message = await self.log_redis(pid=_data["pid"], message=_data)
            # Emite o log atualizado para a sala do processo
            await self.emit("log_execution", data=message, room=_data["pid"])

        except KeyError as e:
            tqdm.write(
                f"Erro ao processar log: {'\n'.join(traceback.format_exception(e))}"
            )

    async def _calc_success_errors(  # noqa: D417
        self, message: MessageLogDict, log: MessageLog = None
    ) -> MessageLogDict:
        """
        Calcula e atualiza os valores de sucesso, erro e restante no log.

        Args:
            message (MessageLogDict): Dicionário com informações do log.
            log

        Returns:
            MessageLogDict: Dicionário atualizado com contadores de sucesso e erro.

        """
        # Inicializa os contadores se não existirem

        if log:
            count_success = len(
                list(filter(lambda x: x["type"] == "success", log.messages))
            )
            count_error = len(
                list(filter(lambda x: x["type"] == "error", log.messages))
            )
            remaining = count_success + count_error

            message["success"] = count_success
            message["errors"] = count_error
            message["remaining"] = remaining

        return message

    async def log_redis(
        self, pid: str, message: MessageLogDict = None
    ) -> MessageLogDict:
        """
        Carrega ou atualiza o log de um processo no Redis.

        Args:
            pid (str): Identificador do processo.
            message (MessageLogDict, opcional): Dados do log a serem atualizados.

        Returns:
            MessageLogDict: Dicionário com o log atualizado.

        Raises:
            Exception: Em caso de falha ao salvar ou atualizar o log.

        """
        # Consulta o log existente pelo pid
        log = MessageLog.query_logs(pid)

        # # Prepara a mensagem base
        # _message: MessageLogDict = (
        #     dict(message)
        #     if message
        #     else MessageLogDict(
        #         message="CARREGANDO",
        #         type="LOG",
        #         pid=pid,
        #         status="Em Execução",
        #         row=0,
        #         total=0,
        #         errors=0,
        #         success=0,
        #         remaining=0,
        #         start_time="01/01/2023 - 00:00:00",
        #     )
        # )
        #

        _message = (
            message or log.model_dump()
            if log
            else MessageLogDict(
                message="CARREGANDO",
                pid=pid,
                status="Em Execução",
                row=0,
                total=0,
                errors=0,
                success=0,
                remaining=0,
                type="info",
                start_time="01/01/2023 - 00:00:00",
            )
        )

        msg = _message.pop("message", "Mensagem não informada")

        # Atualiza os contadores de sucesso e erro
        updated_msg = await self._calc_success_errors(_message, log)
        type_log = updated_msg.pop("type", "info")
        if not log:
            # Cria novo log se não existir
            updated_msg["messages"] = [
                ItemMessageList(
                    id_log=int(updated_msg.pop("id_log", 0)) + 1,
                    message=msg,
                    type=type_log,
                )
            ]
            log = MessageLog(**updated_msg)
            log.save()

        elif log:
            if updated_msg.get("pk"):
                updated_msg.pop("pk")

            updated_msg["messages"] = log.messages or []
            updated_msg["messages"].append(
                ItemMessageList(
                    id_log=int(updated_msg.pop("id_log", 0)) + 1,
                    message=msg,
                    type=type_log,
                )
            )

        # Atualiza o log no banco de dados
        log.update(**updated_msg)

        updated_msg["message"] = msg
        updated_msg["type"] = type_log
        return updated_msg
