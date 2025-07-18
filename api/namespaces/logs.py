"""Define o namespace de logs para integração com WebSocket e gerenciamento de logs em tempo real."""

from __future__ import annotations

from typing import Any

import engineio
import socketio
from quart import request, session
from quart_socketio import Namespace

from addons.printlogs._interface import ItemMessageList
from addons.printlogs._interface import MessageLog as MessageLogDict
from models.logs import MessageLog


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

    async def on_stop_signal(self, *args: Any, **kwargs: Any) -> None:
        """
        Emitissor de sinal de parada para um processo específico.

        Args:
            *args: Argumentos posicionais.
            **kwargs: Argumentos nomeados.

        Returns:
            None: Apenas emite o evento de parada.

        """
        # Obtém os dados do formulário da requisição
        message_data = dict(list((await request.form).items()))
        # Emite o sinal de parada para o processo identificado por pid
        await self.emit("stop_signal", data=message_data, room=message_data["pid"])

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
        return message

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
        message = await self.log_redis(pid=_data["pid"], message=_data)
        # Emite o log atualizado para a sala do processo
        await self.emit("log_execution", data=message, room=_data["pid"])

    async def _calc_success_errors(self, message: MessageLogDict) -> MessageLogDict:
        """
        Calcula e atualiza os valores de sucesso, erro e restante no log.

        Args:
            message (MessageLogDict): Dicionário com informações do log.

        Returns:
            MessageLogDict: Dicionário atualizado com contadores de sucesso e erro.

        """
        # Inicializa os contadores se não existirem
        message["success"] = message.get("success", 0)
        message["errors"] = message.get("errors", 0)
        message["remaining"] = message.get("total", 0) - message["success"]

        # Atualiza os contadores conforme o tipo de mensagem
        if message.get("type"):
            if message.get("type") == "error":
                message["errors"] += 1
            elif message["type"] == "success":
                message["success"] += 1

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

        # Prepara a mensagem base
        _message: MessageLogDict = (
            dict(message)
            if message
            else MessageLogDict(
                message="CARREGANDO",
                type="LOG",
                pid=pid,
                status="Em Execução",
                row=1,
                total=1,
                errors=1,
                success=1,
                remaining=1,
                start_time="01/01/2023 - 00:00:00",
            )
        )
        msg = _message.pop("message", "Mensagem não informada")

        if log:
            # Adiciona nova mensagem ao log existente
            log.messages.append(
                ItemMessageList(message=msg, id_log=len(log.messages))
            )
            if not _message:
                _message = log.model_dump()

        elif not log:
            # Cria novo log se não existir
            _message["messages"] = [
                ItemMessageList(
                    id_log=int(_message.pop("id_log", 0)) + 1,
                    message=msg,
                )
            ]
            log = MessageLog(**_message)
            log.save()

        # Atualiza os contadores de sucesso e erro
        updated_msg = await self._calc_success_errors(_message)
        # Atualiza o log no banco de dados
        log.update(**updated_msg)

        updated_msg["message"] = msg
        return updated_msg
