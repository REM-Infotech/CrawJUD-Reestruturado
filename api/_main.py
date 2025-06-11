import logging
from contextlib import suppress
from os import environ
from pathlib import Path

from api import create_app, io
from api.addons.logger import dict_config
from api.namespaces import register_namespaces


async def main_app() -> None:
    """
    Asynchronously initializes and runs the main application.

    This function performs the following steps:
    1. Creates the application instance using `create_app()`.
    2. Initializes the I/O subsystem with the created app.
    3. Retrieves the host and port from environment variables, defaulting to "0.0.0.0" and 5000 if not set.
    4. Runs the application using the I/O subsystem on the specified host and port.

    """
    with suppress(KeyboardInterrupt):
        app = await create_app()
        await io.init_app(app)
        await register_namespaces(io)
        host = environ.get("host", "0.0.0.0")
        port = environ.get("port", 5000)

        log_folder = Path(__file__).cwd().joinpath("temp", "logs")
        log_folder.mkdir(exist_ok=True, parents=True)
        log_file = str(log_folder.joinpath(f"{__package__}.log"))
        cfg, _ = dict_config(LOG_LEVEL=logging.INFO, LOGGER_NAME=__package__, FILELOG_PATH=log_file)

        await io.run(app, host=host, port=port, log_config=cfg, log_level=logging.INFO)
