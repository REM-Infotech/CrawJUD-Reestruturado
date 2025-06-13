"""Quart application package."""

from importlib import import_module
from pathlib import Path

import aiofiles
import quart_flask_patch  # noqa: F401
from flask_sqlalchemy import SQLAlchemy
from quart import Quart
from quart_cors import cors
from quart_jwt_extended import JWTManager
from quart_socketio import SocketIO

from api.middleware import ProxyFixMiddleware as ProxyHeadersMiddleware
from api.namespaces import register_namespaces as register_namespaces


def check_cors_allowed_origins(*args) -> bool:  # noqa: ANN002, D103
    return True


app = Quart(__name__)
jwt = JWTManager()
db = SQLAlchemy()
io = SocketIO(async_mode="asgi", launch_mode="uvicorn", cookie="access")


@io.on("connect", namespace="/")
async def on_connect() -> None:
    """Handle client connection event."""


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
        allow_origin=["http://localhost:5173"],
        allow_headers=["Content-Type", "Authorization"],
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

    if not Path("is_init.txt").exists():
        async with aiofiles.open("is_init.txt", "w") as f:
            await f.write(f"{await init_database()}")

    from api.models import Users

    if not db.engine.dialect.has_table(db.engine.connect(), Users.__tablename__):
        async with aiofiles.open("is_init.txt", "w") as f:
            await f.write(f"{await init_database()}")


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
    async with app.app_context():
        await database_start(app)
