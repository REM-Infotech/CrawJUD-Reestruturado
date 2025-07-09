"""Main entry do módulo CrawJUD."""

import argparse
from pathlib import Path
from sys import argv

from crawjud.main import main

if __name__ == "__main__":
    args = argv[1:]
    parser = argparse.ArgumentParser(
        prog="CrawJUD", description="CrawJUD Automatização"
    )
    parser.add_argument("--bot_system", type=str, required=True)
    parser.add_argument("--bot_name", type=str, required=True)
    parser.add_argument("--path_config", type=str, required=True)

    namespace = parser.parse_args(args)

    main(
        bot_name=namespace.bot_name,
        bot_system=namespace.bot_system,
        path_config=Path(namespace.path_config),
    )
