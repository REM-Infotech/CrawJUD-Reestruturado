"""Módulo de gestão de Models do banco de dados."""

import pathlib
from os import environ

import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

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

load_dotenv()


async def init_database() -> None:
    """Inicializa o banco de dados."""
    async with app.app_context():
        db.create_all()

        env = environ
        user = Users.query.filter(Users.login == env.get("ROOT_USERNAME")).first()
        if not user:
            user = Users(
                login=env.get("ROOT_USERNAME"), email=env.get("ROOT_EMAIL"), nome_usuario=env.get("ROOT_USERNAME")
            )

            user.senhacrip = env.get("ROOT_PASSWORD")

            db.session.add(user)
            db.session.commit()

        path_file = pathlib.Path(__file__).parent.resolve().joinpath("export.json")
        excel = pd.read_json(path_file).to_dict(orient="records")

        bot_toadd = []
        for row in excel:
            bot = db.session.query(BotsCrawJUD).filter(BotsCrawJUD.display_name == row["display_name"]).first()

            if not bot:
                bot = BotsCrawJUD(**row)
                bot_toadd.append(bot)
        if bot_toadd:
            db.session.add_all(bot_toadd)
            db.session.commit()
        tqdm.write("Database initialized successfully.")
