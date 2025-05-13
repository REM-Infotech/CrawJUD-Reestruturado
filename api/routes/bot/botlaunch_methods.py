"""Módulo de gerenciamento da inicialização dos bots."""

from __future__ import annotations

from typing import TYPE_CHECKING

from api.models import BotsCrawJUD, LicensesUsers
from api.models.users import Users

if TYPE_CHECKING:
    from flask_sqlalchemy import SQLAlchemy


async def license_user(usr: int, db: SQLAlchemy) -> str:
    """
    Return license token.

    Returns:
        str: License token of the user.

    """
    return (
        db.session.query(LicensesUsers)
        .select_from(Users)
        .join(Users, LicensesUsers.user)
        .filter(Users.id == usr)
        .first()
        .license_token
    )


async def get_bot_info(db: SQLAlchemy, id_: int) -> BotsCrawJUD | None:
    """
    Retrieve bot information from the database.

    Returns:
        BotsCrawJUD | None: Bot information or None if not found.

    """
    return db.session.query(BotsCrawJUD).filter(BotsCrawJUD.id == id_).first()
