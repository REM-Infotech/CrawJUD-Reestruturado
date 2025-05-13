"""API De Controle dos robôs crawjud."""

from anyio import Path
from quart import Quart
from quart_jwt_extended import JWTManager

app = Quart(__name__)
jwt = JWTManager()


async def create_app() -> None:
    """Create and configure the Quart application instance.

    Args:
        config_object (str | object): The configuration object to load settings from.

    Returns:
        Quart: Configured Quart application instance.

    """
    resolved_path = await Path(__file__).parent.resolve()
    configfile = resolved_path.joinpath("quartconf.py")
    app.config.from_pyfile(configfile)
