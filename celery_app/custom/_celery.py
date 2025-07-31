from typing import AnyStr

from celery import Celery

from celery_app.custom._task import ContextTask


class AsyncCelery(Celery):
    def __init__(self, *args: AnyStr, **kwargs: AnyStr) -> None:
        super().__init__(*args, **kwargs)
        self.patch_task()

        if "app" in kwargs:
            self.init_app(kwargs["app"])

    def patch_task(self) -> None:
        _TaskBase = self.Task  # noqa: N806
        self.Task = ContextTask

    def init_app(self, app: AnyStr) -> None:
        self.app = app

        conf = {}
        for key in app.config.keys():
            if key[0:7] == "CELERY_":
                conf[key[7:].lower()] = app.config[key]

        if (
            "broker_transport_options" not in conf
            and conf.get("broker_url", "")[0:4] == "sqs:"
        ):
            conf["broker_transport_options"] = {"region": "eu-west-1"}

        self.config_from_object(conf)
