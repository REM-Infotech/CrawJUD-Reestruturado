"""Entrypoint for the server application."""

import asyncio

from tqdm import tqdm

from api._main import main_app

if __name__ == "__main__":
    try:
        asyncio.run(main_app())
    except KeyboardInterrupt:
        tqdm.write("Server stopped by user.")
