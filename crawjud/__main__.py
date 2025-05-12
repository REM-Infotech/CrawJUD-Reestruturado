"""Main entry do módulo CrawJUD."""

import argparse
from importlib import import_module
from pathlib import Path
from sys import argv


def main(bot_name: str, bot_system: str, path_config: Path) -> None:
    """Função de inicialização do robô."""
    bot = import_module(f"crawjud.bots.{bot_system}.{bot_name}", __package__)
    class_bot = getattr(bot, bot_name.capitalize(), None)
    class_bot(bot_name, bot_system, path_config)


if __name__ == "__main__":
    args = argv[1:]
    parser = argparse.ArgumentParser(prog="CrawJUD", description="CrawJUD Automatização")
    parser.add_argument("--bot_system", type=str, required=True)
    parser.add_argument("--bot_name", type=str, required=True)
    parser.add_argument("--path_config", type=str, required=True)

    namespace = parser.parse_args(args)

    main(namespace.bot_name, namespace.bot_system, Path(namespace.path_config))
