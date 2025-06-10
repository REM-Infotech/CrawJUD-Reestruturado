"""Entrypoint for the server application."""

import asyncio

from clear import clear

from api._main import main_app

if __name__ == "__main__":
    clear()

    asyncio.run(main_app())
