"""Módulo de controle de envio de email."""

from __future__ import annotations

import mimetypes
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from os import environ
from pathlib import Path
from smtplib import SMTP, SMTP_SSL
from typing import TYPE_CHECKING

from dotenv import load_dotenv

from crawjud_app.common.exceptions.mail import MailError

if TYPE_CHECKING:
    from typing import Self


class Mail:
    """Class to handle mail configuration.

    This class is used to configure the mail server settings for sending emails.

    Attributes:
        server (smtplib.SMTP): Server object.
        MAIL_SERVER (str): The mail server address.
        MAIL_PORT (int): The mail server port.
        MAIL_USERNAME (str): The username for the mail server.
        MAIL_PASSWORD (str): The password for the mail server.
        MAIL_USE_TLS (bool): Whether to use TLS for the mail server.
        MAIL_USE_SSL (bool): Whether to use SSL for the mail server.
        MAIL_DEFAULT_SENDER (str): The default sender email address.
        MAIL_SUBTYPE (str): E-mail message subtype.

    """

    server: SMTP | SMTP_SSL

    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_USE_TLS: bool
    MAIL_USE_SSL: bool
    MAIL_DEFAULT_SENDER: str
    MAIL_SUBTYPE: str

    def __init__(self, **kwrgs: str | bool | int) -> None:
        """Inicializes the Mail class with the given keyword arguments."""
        if len(kwrgs) == 0:
            load_dotenv(str(Path(__file__).cwd().joinpath("crawjud_app", ".env")))
            kwrgs = environ

        self.MAIL_SERVER = kwrgs["MAIL_SERVER"]
        self.MAIL_PORT = int(kwrgs["MAIL_PORT"])
        self.MAIL_USERNAME = kwrgs["MAIL_USERNAME"]
        self.MAIL_PASSWORD = kwrgs["MAIL_PASSWORD"]
        self.MAIL_USE_TLS = kwrgs.get("MAIL_USE_TLS", "false").lower() == "true"
        self.MAIL_USE_SSL = kwrgs.get("MAIL_USE_SSL", "false").lower() == "true"
        self.MAIL_DEFAULT_SENDER = kwrgs["MAIL_DEFAULT_SENDER"]
        self.MAIL_SUBTYPE = kwrgs.get("MAIL_SUBTYPE", "mixed")
        self.initialize_server()

        if not self.MAIL_SUBTYPE:
            self.MAIL_SUBTYPE = "mixed"

        self._message = MIMEMultipart(self.MAIL_SUBTYPE)

    @classmethod
    def construct(cls, **kwrgs: str | bool | int) -> Self:
        """Construct a Mail object with the given keyword arguments."""
        return cls(**kwrgs)

    @property
    def message(self) -> MIMEMultipart:
        """Message constructor.

        Returns:
            MIMEMultipart: Multipart class message.

        """
        return self._message

    def attach_file(self, file_path: str | Path) -> None:
        """Anexa um arquivo ao corpo da mensagem.

        Args:
            file_path (str | Path): Caminho do arquivo a ser anexado.



        Raises:
            FileNotFoundError: Caso o arquivo não seja encontrado.

        """
        # Resolve o caminho do arquivo e obtém o nome
        file = Path(file_path).resolve()
        filename = file.name
        mime_type, _ = mimetypes.guess_type(file)
        # Cria a parte MIME do arquivo
        part = MIMEBase(mime_type.split("/")[0], mime_type.split("/")[1])
        with file.open("rb") as file_:
            part.set_payload(file_.read())

        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        self.message.attach(part)

        return "File attached"

    def initialize_server(self) -> None:
        """Initialize SMTP server."""
        self.server = SMTP(self.MAIL_SERVER, self.MAIL_PORT)

        if self.MAIL_USE_SSL:
            self.server = SMTP_SSL(
                self.MAIL_SERVER,
                self.MAIL_PORT,
                context=ssl.create_default_context(),
            )

        elif self.MAIL_USE_TLS:
            self.server = SMTP(self.MAIL_SERVER, self.MAIL_PORT)
            self.server.starttls(context=ssl.create_default_context())

    def login(self) -> None:
        """Server authentication."""
        self.server.login(self.MAIL_USERNAME, self.MAIL_PASSWORD)

    def send_message(self, to: str) -> None:
        """Send message to recipient.

        Arguments:
            message_object (MIMEMultipart): Message object.
            to (str): Recipient email address.

        """
        try:
            self.login()

            self.message["From"] = self.MAIL_DEFAULT_SENDER
            self.server.sendmail(
                self.MAIL_DEFAULT_SENDER,
                to,
                self.message.as_string(),
            )
            self.server.quit()

            return "Message sent successfully"

        except Exception as e:
            self.server.quit()
            raise MailError(f"Error sending email: {e}") from e
