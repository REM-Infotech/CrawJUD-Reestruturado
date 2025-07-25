"""Configuration loader module.

Provides functionality to load configuration from an object.
"""

from os import environ
from pathlib import Path  # noqa: F401
from typing import AnyStr, Self, TypedDict

from dotenv import load_dotenv

load_dotenv()

config_dict_model = {
    "broker_url": "",
    "result_backend": "",
    "task_ignore_result": True,
    "broker_connection_retry_on_startup": True,
    "timezone": "",
    "task_create_missing_queues": True,
}


class CeleryConfig(TypedDict):  # noqa: D101
    broker_url: str
    result_backend: str
    task_ignore_result: bool
    broker_connection_retry_on_startup: bool
    timezone: str
    task_create_missing_queues: bool


class Config:
    """Class config para o celery app."""

    celery_config: CeleryConfig
    broker_url: str
    result_backend: str
    task_ignore_result: bool
    task_create_missing_queues: bool
    broker_connection_retry_on_startup: bool
    timezone: str
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

    def convert_bool(self, v: str) -> bool:  # noqa: D102
        return v.lower() == "true" or v == 1

    def __init__(self, **kwargs: AnyStr) -> None:
        """Load Config."""
        arguments = kwargs.copy()
        arguments.update(environ)
        self.celery_config = CeleryConfig(**{
            k.lower(): v
            for k, v in list(arguments.items())
            if k.lower() in CeleryConfig.__annotations__.keys()
        })

        call_convert = {bool: self.convert_bool}

        for k, v in self.celery_config.items():
            type_key = CeleryConfig.__annotations__.get(k)
            if not isinstance(v, type_key):
                call_ = call_convert.get(type_key)
                if call_:
                    v = call_(v)

            setattr(self, k, v)
