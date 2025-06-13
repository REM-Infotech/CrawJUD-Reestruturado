"""Main entry do módulo CrawJUD."""

import argparse
from importlib import import_module
from pathlib import Path
from sys import argv


def main(bot_name: str, bot_system: str, path_config: Path) -> None:
    """
    Função principal para inicialização do robô.

    Esta função é responsável por carregar dinamicamente o módulo do robô especificado,
        instanciar a classe do robô e executar o método de execução principal.
        O nome do robô e do sistema são usados para localizar o módulo correto
        dentro da estrutura do projeto. O arquivo de configuração é passado para o
        robô durante a inicialização.

    Args:
        bot_name (str): Nome do robô a ser inicializado. Deve corresponder ao nome do módulo do robô.
        bot_system (str): Nome do sistema ao qual o robô pertence. Deve corresponder ao diretório do sistema.
        path_config (Path): Caminho para o arquivo de configuração necessário para inicializar o robô.



    Example:
        ```python
        main(
            bot_name="capa",  # Nome do robô
            bot_system="projudi",  # Sistema ao qual o robô pertence
            path_config=Path(
                "/caminho/para/config.json",
            ),
        )
        ```
    ## Disclaimer:
        Funcionamento do`path_config`
            O arquivo do Json tem que estar junto com a planilha de execução do robô.
            Os parâmetros do Json devem ser:
            ```
                {
                    "pid": "Q6M2N9",
                    "schedule": false,
                    "xlsx": "Provisao_-_02.06.xlsx_CORRETA.xlsx",
                    "username": "paula.melo2",
                    "password": "RoboFMV2024$",
                    "login_method": "pw",
                    "client": "AME - AMAZONAS ENERGIA",
                    "total_rows": 44
                }
            ```

    """
    bot = import_module(f"crawjud.bots.{bot_system}.{bot_name}", __package__)
    class_bot = getattr(bot, bot_name.capitalize(), None)
    bot = class_bot.initialize(bot_name=bot_name, bot_system=bot_system, path_config=path_config)
    bot.execution()


if __name__ == "__main__":
    args = argv[1:]
    parser = argparse.ArgumentParser(prog="CrawJUD", description="CrawJUD Automatização")
    parser.add_argument("--bot_system", type=str, required=True)
    parser.add_argument("--bot_name", type=str, required=True)
    parser.add_argument("--path_config", type=str, required=True)

    namespace = parser.parse_args(args)

    main(bot_name=namespace.bot_name, bot_system=namespace.bot_system, path_config=Path(namespace.path_config))
