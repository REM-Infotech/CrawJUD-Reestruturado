"""Entrypoint for the server application."""

import asyncio
import logging  # noqa: F401
from pathlib import Path  # noqa: F401
from platform import node  # noqa: F401

import hypercorn  # noqa: F401
import hypercorn.asyncio  # noqa: F401
import hypercorn.run  # noqa: F401
import uvicorn
from clear import clear
from socketio import ASGIApp

from socketio_server import create_socketioserver
from socketio_server.addons.logger import dict_config  # noqa: F401


async def main(log_config: dict, app: ASGIApp) -> None:
    """Run socketio server."""
    config = uvicorn.Config(app, host="0.0.0.0", port=7000, log_level="info", log_config=log_config)  # noqa: S104
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    clear()

    log_folder = Path(__file__).cwd().joinpath("temp", "logs")
    log_folder.mkdir(exist_ok=True, parents=True)
    log_file = str(log_folder.joinpath(f"{__package__}.log"))
    cfg, _ = dict_config(LOG_LEVEL=logging.INFO, LOGGER_NAME=__package__, FILELOG_PATH=log_file)
    app = asyncio.run(create_socketioserver())
    asyncio.run(main(log_config=cfg, app=app))
    # config = hypercorn.Config()

    # hostname = node()

    # config.bind = ["0.0.0.0:7002"]
    # config.loglevel = "info"
    # config.use_reloader = True

    # config.logconfig_dict = cfg

    # asyncio.run(hypercorn.asyncio.serve(app, config, mode="asgi"))
