"""Quart application package."""

import re
from importlib import import_module
from pathlib import Path

import quart_flask_patch  # noqa: F401
import socketio
from dotenv import dotenv_values
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from quart import Quart
from quart_cors import cors
from quart_jwt_extended import JWTManager
from quart_socketio import SocketIO
from quart_socketio.config.python_socketio import AsyncSocketIOConfig

from api.middleware import ProxyFixMiddleware as ProxyHeadersMiddleware
from crawjud_app import make_celery


def check_cors_allowed_origins(*args) -> bool:  # noqa: ANN002, D103
    return True


environ = dotenv_values()
sess = Session()
app = Quart(__name__)
jwt = JWTManager()
db = SQLAlchemy()

config = AsyncSocketIOConfig(
    client_manager=socketio.RedisManager(
        url=environ.get("SOCKETIO_REDIS", "redis://localhost:6379/0")
    )
)


io = SocketIO(
    async_mode="asgi",
    launch_mode="uvicorn",
    cookie="access",
    socket_config=config,
)


async def create_app() -> Quart:
    """
    Create and configure the Quart application instance.

    Args:
        confg (object): The configuration object to load settings from.

    Returns:
        ASGIApp: The ASGI application instance with CORS and middleware applied.

    """
    app.config.from_pyfile(Path(__file__).parent.resolve().joinpath("quartconf.py"))

    async with app.app_context():
        await init_extensions(app)
        await register_routes(app)

    app.asgi_app = ProxyHeadersMiddleware(app.asgi_app)
    return cors(
        app,
        allow_origin=[re.compile(r"^https?:\/\/[^\/]+")],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "x-xsrf-token",
            "X-Xsrf-Token",
        ],
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_credentials=True,
    )


async def database_start(app: Quart) -> None:
    """
    Initialize and configure the application database.

    This function performs the following tasks:
    1. Checks if the current server exists in the database
    2. Creates a new server entry if it doesn't exist
    3. Initializes all database tables

    Args:
        app (Quart): The Quart application instance

    Note:
        This function requires the following environment variables:
        - NAMESERVER: The name of the server
        - HOSTNAME: The address of the server

    """
    from api.models import init_database

    await init_database()


async def register_routes(app: Quart) -> None:
    """
    Register application's blueprints and error handlers with the Quart instance.

    This function manages the application's routing configuration by:
    1. Dynamically importing required route modules
    2. Registering blueprints for bot and webhook endpoints
    3. Setting up application-wide error handlers

    Args:
        app (Quart): The Quart application instance to configure

    Note:
        Currently registers 'bot' and 'webhook' blueprints, and imports
        logs routes automatically.

    """
    async with app.app_context():
        # Dynamically import additional route modules as needed.
        import_module("api.routes", package=__package__)

    from api.routes.auth import auth
    from api.routes.bot import bot
    from api.routes.config import admin
    from api.routes.credentials import cred
    from api.routes.dashboard import dash
    from api.routes.execution import exe

    listBlueprints = [bot, auth, exe, dash, cred, admin]  # noqa: N806

    for bp in listBlueprints:
        app.register_blueprint(bp)


async def init_extensions(app: Quart) -> None:
    """
    Initialize and configure the application extensions.

    Args:
        app (Quart): The Quart application instance

    Returns:
        AsyncServer: The SocketIO server instance

    """
    db.init_app(app)
    jwt.init_app(app)
    sess.init_app(app)

    app.extensions["celery"] = make_celery()

    async with app.app_context():
        await database_start(app)
