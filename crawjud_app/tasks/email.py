"""Envia e gerencia tarefas relacionadas ao envio de e-mails.

Este módulo fornece a função para envio de e-mails com suporte a anexos,
utilizando a integração com o sistema de tarefas assíncronas do projeto.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from crawjud_app.addons.mail import Mail
from crawjud_app.decorators import shared_task

if TYPE_CHECKING:
    from interface.types import TReturnMessageMail


@shared_task(name="send_email")
def send_email(
    subject: str,
    to: str,
    message: str,
    files_path: list[str] | None = None,
) -> TReturnMessageMail:
    """Send an email to the specified recipient.

    Args:
        subject (str): The subject of the email.
        to (str): The recipient email address.
        message (str): The email message content.
        files_path (list[str] | None): A list of file paths to attach to the email.

    Returns:
        TReturnMessageMail: The result of the email sending operation.

    """
    mail = Mail.construct()
    mail.message["Subject"] = subject
    mail.message["To"] = to
    mail.message.attach(message)

    if len(files_path) > 0:
        for file in files_path:
            mail.attach_file(file)

    mail.send_message(to=to)

    return "E-mail enviado com sucesso!"
