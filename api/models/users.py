"""Module for user-related models and authentication utilities."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import bcrypt
import pytz
from quart_jwt_extended import get_current_user

from api import db, jwt

salt = bcrypt.gensalt()


@jwt.user_identity_loader
def user_identity_lookup(*args: str, **kwargs: object) -> int:
    """
    Get the user's identity.

    Returns:
        int: The user's ID.

    """
    user: Users = args[0]

    return user.id


@jwt.token_in_blacklist_loader
def check_if_token_revoked(jwt_data: dict, *args: str, **kwargs: object) -> bool:
    """
    Check if the token is in the blocklist.

    Returns:
        bool: True if the token is revoked, False otherwise.

    """
    arg = args  # noqa: F841
    kw = kwargs  # noqa: F841

    jti = jwt_data["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None


@jwt.user_loader_callback_loader
def user_lookup_callback(*args: str, **kwargs: object) -> Users | None:
    """
    Get the user from the JWT data.

    Returns:
        Users | None: The user object or None if not found.

    """
    id_: int = args[0]

    return db.session.query(Users).filter_by(id=id_).one_or_none()


class TokenBlocklist(db.Model):
    """Database model for token blocklist."""

    id: int = db.Column(db.Integer, primary_key=True)
    jti: str = db.Column(db.String(36), nullable=False, index=True)
    type: str = db.Column(db.String(16), nullable=False)
    user_id = db.Column(
        db.ForeignKey("users.id"),
        default=lambda: get_current_user().id,
        nullable=False,
    )
    created_at = db.Column(
        db.DateTime,
        server_default=datetime.now(pytz.timezone("America/Manaus")).isoformat(),
        nullable=False,
    )


class SuperUser(db.Model):
    """Database model for a super user."""

    __tablename__ = "superuser"
    id: int = db.Column(db.Integer, primary_key=True)
    users_id: int = db.Column(db.Integer, db.ForeignKey("users.id"))
    users = db.relationship("Users", backref=db.backref("supersu", lazy=True))


class Users(db.Model):
    """Database model for application users."""

    __tablename__ = "users"
    id: int = db.Column(db.Integer, primary_key=True)
    login: str = db.Column(db.String(length=30), nullable=False, unique=True)
    nome_usuario: str = db.Column(db.String(length=64), nullable=False, unique=True)
    email: str = db.Column(db.String(length=50), nullable=False, unique=True)
    password: str = db.Column(db.String(length=60), nullable=False)
    login_time = db.Column(
        db.DateTime, default=datetime.now(pytz.timezone("Etc/GMT+4"))
    )
    verification_code: str = db.Column(db.String(length=45), unique=True)
    login_id: str = db.Column(
        db.String(length=64), nullable=False, default=str(uuid4())
    )
    filename: str = db.Column(db.String(length=128))
    blob_doc = db.Column(db.LargeBinary(length=(2**32) - 1))

    licenseus_id: int = db.Column(db.Integer, db.ForeignKey("licenses_users.id"))
    licenseusr = db.relationship("LicensesUsers", backref="user")

    def __init__(
        self, login: str = None, nome_usuario: str = None, email: str = None
    ) -> None:
        """
        Initialize a new user instance.

        Args:
            login (str, optional): The user's login name.
            nome_usuario (str, optional): The full name.
            email (str, optional): The user's email.

        """
        self.login = login
        self.nome_usuario = nome_usuario
        self.email = email

    @property
    def senhacrip(self) -> any:
        """
        Get the encrypted password.

        Returns:
            str: The encrypted password.

        """
        return self.senhacrip

    @senhacrip.setter
    def senhacrip(self, senha_texto: str) -> None:
        """
        Encrypt and set the user’s password.

        Args:
            senha_texto (str): Plain text password.

        """
        self.password = bcrypt.hashpw(senha_texto.encode(), salt).decode("utf-8")

    def check_password(self, senha_texto_claro: str) -> bool:
        """
        Check if the provided password matches the stored encrypted password.

        Args:
            senha_texto_claro (str): Plain text password.

        Returns:
            bool: True if valid, False otherwise.

        """
        return bcrypt.checkpw(
            senha_texto_claro.encode("utf-8"), self.password.encode("utf-8")
        )

    @property
    def dict_query(self) -> dict[str, str | int]:
        """
        Return a dictionary representation of selected user attributes.

        Returns:
            dict: Dictionary of user attributes.

        """
        data = {
            "id": self.id,
            "login": self.login,
            "nome_usuario": self.nome_usuario,
            "email": self.email,
        }

        if len(self.admin) > 0:
            data.update({"tipo_user": "admin"})

        if len(self.supersu) > 0:
            data.update({"tipo_user": "supersu"})
            data.update({"licenses": self.licenseusr.license_token})

        return data


class LicensesUsers(db.Model):
    """Database model representing license users."""

    __tablename__ = "licenses_users"
    id: int = db.Column(db.Integer, primary_key=True)
    name_client: str = db.Column(db.String(length=60), nullable=False, unique=True)
    cpf_cnpj: str = db.Column(db.String(length=30), nullable=False, unique=True)
    license_token: str = db.Column(db.String(length=512), nullable=False, unique=True)

    # Relacionamento de muitos para muitos com users
    admins = db.relationship("Users", secondary="admins", backref="admin")
    bots = db.relationship(
        "BotsCrawJUD",
        secondary="execution_bots",
        backref=db.backref("license", lazy=True),
    )
