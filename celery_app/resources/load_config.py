"""Configuration loader module.

Provides functionality to load configuration from an object.
"""

from ast import TypeVar
from os import environ
from pathlib import Path  # noqa: F401
from typing import AnyStr, Self, Type

from dotenv import load_dotenv

config_dict_model = {
    "broker_url": "",
    "result_backend": "",
    "task_ignore_result": True,
    "broker_connection_retry_on_startup": True,
    "timezone": "",
    "task_create_missing_queues": True,
}

type_config = Type[TypeVar("DictConfig", bound=config_dict_model)]


class Config:
    """Class config para o celery app."""

    celery_config: type_config
    broker_url: str
    result_backend: str
    task_ignore_result: bool
    task_create_missing_queues: bool
    broker_connection_retry_on_startup: bool
    timezone: str

    bool_attributes: list[str] = [
        "task_ignore_result",
        "task_create_missing_queues",
        "broker_connection_retry_on_startup",
    ]
    # CELERY_QUEUES = (  # noqa: N806
    #     Queue("default"),
    #     Queue("caixa_queue", routing_key="crawjud.bot.caixa_launcher"),
    #     Queue("projudi_queue", routing_key="crawjud.bot.projudi_launcher"),
    # )
    # CELERY_ROUTES = {  # noqa: N806
    #     "crawjud.bot.caixa_launcher": {"queue": "caixa_queue"},
    #     "crawjud.bot.projudi_launcher": {"queue": "projudi_queue"},
    # }

    @classmethod
    def load_config(cls, **kwrgs: AnyStr) -> Self:
        """Load Config."""
        return cls(**kwrgs)

    def __init__(self, **kwrgs: AnyStr) -> None:
        """Load Config."""
        self.celery_config = {}
        if len(kwrgs) == 0:
            load_dotenv(str(Path(__file__).cwd().joinpath("celery_app", ".env")))
            kwrgs = environ

        for key, val in list(kwrgs.items()):
            if key in self.bool_attributes:
                val = kwrgs.get(key, "false").lower() == "true"

            self.celery_config[key] = val

            setattr(self, key, val)
