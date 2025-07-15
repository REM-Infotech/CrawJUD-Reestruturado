"""Módulo de gestão de Models do banco de dados."""

import pathlib
from os import environ
from typing import TypedDict
from uuid import uuid4

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


class DatabaseInitEnvDict(TypedDict):
    ROOT_USERNAME: str
    ROOT_PASSWORD: str
    ROOT_EMAIL: str
    ROOT_CLIENT: str
    ROOT_CPF_CNPJ_CLIENT: str


async def init_database() -> None:
    """Inicializa o banco de dados."""
    async with app.app_context():
        db.create_all()

        env = DatabaseInitEnvDict(**environ)

        with db.session.no_autoflush:
            bot_toadd = []
            user = Users.query.filter(Users.login == env["ROOT_USERNAME"]).first()
            if not user:
                user = Users(
                    login=env["ROOT_USERNAME"],
                    email=env["ROOT_EMAIL"],
                    nome_usuario=env["ROOT_USERNAME"],
                )

                user.senhacrip = env["ROOT_PASSWORD"]

                bot_toadd.append(user)

            name_client = env["ROOT_CLIENT"]
            cpf_cnpj_client = env["ROOT_CPF_CNPJ_CLIENT"]
            license_user = LicensesUsers.query.filter(
                LicensesUsers.name_client == name_client
            ).first()

            if not license_user:
                license_user = LicensesUsers(
                    name_client=name_client,
                    cpf_cnpj=cpf_cnpj_client,
                    license_token=uuid4().hex,
                )

                license_user.admins = [user]

                bot_toadd.append(license_user)

            if not user.licenseusr:
                user.licenseusr = license_user
                user.licenseus_id = license_user.id

            path_file = (
                pathlib.Path(__file__).parent.resolve().joinpath("export.json")
            )
            excel = pd.read_json(path_file).to_dict(orient="records")

            for row in excel:
                bot = (
                    db.session.query(BotsCrawJUD)
                    .filter(BotsCrawJUD.display_name == row["display_name"])
                    .first()
                )

                if not bot:
                    bot = BotsCrawJUD(**row)
                    bot_toadd.append(bot)

            if bot_toadd:
                db.session.add_all(bot_toadd)

            license_user.bots.extend(bot_toadd)

            db.session.commit()

        tqdm.write("Database initialized successfully.")
