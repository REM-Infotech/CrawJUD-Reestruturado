"""Fornece a classe AsyncCelery para integração customizada do Celery.

Este módulo define:
- AsyncCelery: classe que estende Celery para aplicar ContextTask e integração
  com configuração da aplicação.
"""

from typing import AnyStr

from celery import Celery

from crawjud_app.custom.task import ContextTask


class AsyncCelery[T](Celery):
    """Estenda Celery para aplicar ContextTask e integração com configuração.

    Args:
        *args (AnyStr): Argumentos posicionais para inicialização do Celery.
        **kwargs (AnyStr): Argumentos nomeados para inicialização do Celery.

    Returns:
        None: Não retorna valor.

    Raises:
        Exception: Pode lançar exceções do Celery em caso de erro de configuração.

    """

    def __init__(self, *args: AnyStr, **kwargs: AnyStr) -> None:
        """Inicialize AsyncCelery com argumentos e configure integração com app.

        Args:
            *args (AnyStr): Argumentos posicionais para inicialização do Celery.
            **kwargs (AnyStr): Argumentos nomeados para inicialização do Celery.


        """
        super().__init__(*args, **kwargs)
        self.patch_task()

        if "app" in kwargs:
            self.init_app(kwargs["app"])

    def patch_task(self) -> None:
        """Substitua a classe base Task pela ContextTask."""
        self.Task = ContextTask

    def init_app(self, app: T) -> None:
        """Configure integração do Celery com a aplicação fornecida.

        Args:
            app: Instância da aplicação contendo configurações do Celery.

        """
        self.app = app

        conf = {}
        for key in app.config:
            if key[0:7] == "CELERY_":
                conf[key[7:].lower()] = app.config[key]

        if (
            "broker_transport_options" not in conf
            and conf.get("broker_url", "")[0:4] == "sqs:"
        ):
            conf["broker_transport_options"] = {"region": "eu-west-1"}

        self.config_from_object(conf)
