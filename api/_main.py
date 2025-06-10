from os import environ

from api import create_app, io


async def main_app() -> None:
    """
    Asynchronously initializes and runs the main application.

    This function performs the following steps:
    1. Creates the application instance using `create_app()`.
    2. Initializes the I/O subsystem with the created app.
    3. Retrieves the host and port from environment variables, defaulting to "0.0.0.0" and 5000 if not set.
    4. Runs the application using the I/O subsystem on the specified host and port.

    """
    app = await create_app()
    await io.init_app(app)

    host = environ.get("host", "0.0.0.0")
    port = environ.get("port", 5000)

    await io.run(app, host=host, port=port)
