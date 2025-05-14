"""Entrypoint for the server application."""

import asyncio
import logging
from pathlib import Path
from platform import node

import hypercorn
import hypercorn.asyncio
import hypercorn.run
from clear import clear
from socketio import ASGIApp

from socketio_server import sio
from socketio_server.addons.logger import dict_config

if __name__ == "__main__":
    clear()

    app = ASGIApp(sio)
    config = hypercorn.Config()

    hostname = node()

    config.bind = ["0.0.0.0:5000"]
    config.loglevel = "info"
    config.use_reloader = True

    log_folder = Path(__file__).cwd().joinpath("temp", "logs")
    log_folder.mkdir(exist_ok=True)
    log_file = str(log_folder.joinpath(f"{__package__}.log"))
    cfg, _ = dict_config(LOG_LEVEL=logging.INFO, LOGGER_NAME=__package__, FILELOG_PATH=log_file)
    config.logconfig_dict = cfg

    asyncio.run(hypercorn.asyncio.serve(app, config, mode="asgi"))
