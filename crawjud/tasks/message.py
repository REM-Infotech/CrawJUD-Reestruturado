"""Tarefas relacionadas ao envio de mensagens de log para o sistema de monitoramento.

Este módulo contém a classe PrintMessage, responsável por enviar mensagens de log
assíncronas via Socket.IO, permitindo a comunicação em tempo real com o sistema de
monitoramento.
"""

from __future__ import annotations

from contextlib import suppress
from pathlib import Path

from dotenv import dotenv_values

from crawjud.decorators import shared_task
from crawjud_app.custom.task import ContextTask

environ = dotenv_values()
workdir_path = Path(__file__).cwd()


@shared_task(name="print_message", bind=True, base=ContextTask)
class PrintMessage[T](ContextTask):
    """Classe responsável por enviar mensagens de log para o sistema de monitoramento.

    Esta classe utiliza o Socket.IO para enviar mensagens de log assíncronas,
    permitindo a comunicação em tempo real com o sistema de monitoramento.
    """

    def __init__(  # noqa: D107
        self,
        event: str = "log_execution",
        data: dict[str, str] | str | None = None,
        room: str | None = None,
        *args: T,
        **kwargs: T,
    ) -> None:
        self.print_msg(event=event, data=data, room=room, *args, **kwargs)

    def print_msg(
        self,
        event: str = "log_execution",
        data: dict[str, str] | str | None = None,
        room: str | None = None,
        *args: T,
        **kwargs: T,
    ) -> None:
        """Envia mensagem assíncrona para o sistema de monitoramento via Socket.IO.

        Args:
            event (str): Evento a ser emitido (padrão: "log_execution").
            data (dict[str, str] | str): Dados da mensagem a ser enviada.
            room (str): Sala para envio da mensagem (opcional).
            *args: Argumentos posicionais adicionais.
            **kwargs: Argumentos nomeados adicionais.



        """
        current_task: ContextTask = kwargs.get("current_task")
        sio = current_task.sio if current_task else self.sio
        if data:
            with suppress(Exception):
                # Cria uma instância do cliente Socket.IO e conecta ao servidor
                # com o namespace e cabeçalhos especificados.
                # Se uma sala for especificada, o cliente se juntará a ela.
                # Em seguida, emite o evento com os dados fornecidos.

                # Se uma sala for especificada, o cliente se juntará a ela.
                if room:
                    join_data = {"data": {"room": room}}
                    sio.emit("join_room", data=join_data)

                # Emite o evento com os dados fornecidos.
                sio.emit("log_execution", data={"data": data})
