"""
Defines database models for CrawJUD bots and their execution details.

Provides structures for bot configurations, credentials, and execution logging.
"""

from collections.abc import Buffer
from datetime import datetime
from typing import ClassVar

import pytz
from sqlalchemy.orm.relationships import RelationshipProperty

from api import db


class BotsCrawJUD(db.Model):
    """
    Represents a CrawJUD bot entity.

    Attributes:
        id (int): Primary key for the bot.
        display_name (str): Display name of the bot.
        system (str): System type or identifier.
        state (str): Operational status of the bot.
        client (str): Client identifier.
        type (str): Type classification of the bot.
        form_cfg (str): Configuration form reference.
        classification (str): Classification of the bot's purpose.
        text (str): Descriptive text or notes.

    """

    __tablename__ = "bots"
    id: int = db.Column(db.Integer, primary_key=True)
    display_name: str = db.Column(db.String(length=45), nullable=False)
    system: str = db.Column(db.String(length=45), nullable=False)
    state: str = db.Column(db.String(length=45), nullable=False)
    client: str = db.Column(db.String(length=45), nullable=False)
    type: str = db.Column(db.String(length=45), nullable=False)
    form_cfg: str = db.Column(db.String(length=45), nullable=False)
    classification: str = db.Column(db.String(length=45), nullable=False)
    text: str = db.Column(db.String(length=512), nullable=False)


class Credentials(db.Model):
    """
    Represents stored credentials for a user or system.

    Attributes:
        id (int): Primary key for the credential.
        nome_credencial (str): Descriptive name for the credential.
        system (str): System type or identifier.
        login_method (str): Authentication method used.
        login (str): Username or login identifier.
        password (str): Password stored for the credential.
        key (str): Optional key used in authentication.
        certficate (str): Optional certificate name.
        certficate_blob (bytes): Binary certificate data.
        license_id (int): Foreign key referencing the license.

    """

    __tablename__ = "credentials"
    id: int = db.Column(db.Integer, primary_key=True)
    nome_credencial: str = db.Column(db.String(length=45), nullable=False)
    system: str = db.Column(db.String(length=45), nullable=False)
    login_method: str = db.Column(db.String(length=45), nullable=False)
    login: str = db.Column(db.String(length=45), nullable=False)
    password: str = db.Column(db.String(length=45))
    key: str = db.Column(db.String(length=45))
    certficate: str = db.Column(db.String(length=45))
    certficate_blob: Buffer = db.Column(db.LargeBinary(length=(2**32) - 1))

    license_id: int = db.Column(db.Integer, db.ForeignKey("licenses_users.id"))
    license_usr = db.relationship(
        "LicensesUsers", backref=db.backref("credentials", lazy=True)
    )


class Executions(db.Model):
    """
    Represents bot execution records.

    Attributes:
        pid (str): Process identifier for the execution.
        id (int): Primary key for the execution record.
        status (str): Current status of the execution.
        file_output (str): Path or reference to output file.
        total_rows (str): Row count for processed data.
        url_socket (str): Socket address for communication.
        data_execucao (datetime): Execution start timestamp.
        data_finalizacao (datetime): Execution end timestamp.
        arquivo_xlsx (str): Reference to the exported .xlsx file.
        bot_id (int): Foreign key referencing the bot.
        user_id (int): Foreign key referencing the user.
        license_id (int): Foreign key referencing the license.

    """

    __tablename__ = "executions"
    pid: str = db.Column(db.String(length=12), nullable=False)
    id: int = db.Column(db.Integer, primary_key=True)
    status: str = db.Column(db.String(length=45), nullable=False)
    file_output: str = db.Column(db.String(length=512))
    total_rows: str = db.Column(db.String(length=45))
    url_socket: str = db.Column(db.String(length=64))
    data_execucao: datetime = db.Column(
        db.DateTime, default=datetime.now(pytz.timezone("America/Manaus"))
    )
    data_finalizacao: datetime = db.Column(
        db.DateTime, default=datetime.now(pytz.timezone("America/Manaus"))
    )
    arquivo_xlsx: str = db.Column(db.String(length=64))

    bot_id: int = db.Column(db.Integer, db.ForeignKey("bots.id"))
    bot: ClassVar[RelationshipProperty[BotsCrawJUD]] = db.relationship(
        BotsCrawJUD,
        backref=db.backref("executions", lazy=True),
    )

    user_id: int = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("Users", backref=db.backref("executions", lazy=True))

    license_id: int = db.Column(db.Integer, db.ForeignKey("licenses_users.id"))
    license_usr = db.relationship(
        "LicensesUsers", backref=db.backref("executions", lazy=True)
    )


class ThreadBots(db.Model):
    """
    Manages thread references linked to bot processes.

    Attributes:
        id (int): Primary key for the thread reference.
        pid (str): Process identifier for the thread.
        processID (str): Unique ID referencing the system process.

    """

    __tablename__ = "thread_bots"
    id = db.Column(db.Integer, primary_key=True)
    pid: str = db.Column(db.String(length=12), nullable=False)
    processID: str = db.Column(db.String(length=64), nullable=False)  # noqa: N815
