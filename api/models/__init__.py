"""Módulo de gestão de Models do banco de dados."""

from api import app, db
from api.models.bots import BotsCrawJUD, Credentials, Executions, ThreadBots
from api.models.schedule import CrontabModel, ScheduleModel
from api.models.secondaries import admins, execution_bots
from api.models.users import LicensesUsers, SuperUser, Users

__all__ = [
    admins,
    execution_bots,
    Users,
    LicensesUsers,
    SuperUser,
    BotsCrawJUD,
    Credentials,
    Executions,
    ScheduleModel,
    CrontabModel,
    ThreadBots,
]


async def init_database() -> None:
    """Inicializa o banco de dados."""
    async with app.app_context():
        db.create_all()
