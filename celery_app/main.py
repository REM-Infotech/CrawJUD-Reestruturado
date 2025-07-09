"""Módulo Celery App do CrawJUD Automatização."""

import argparse
import asyncio
from multiprocessing import Process
from os import environ
from pathlib import Path
from platform import node
from sys import argv

import tqdm
from celery.apps.beat import Beat  # noqa: F401
from celery.apps.worker import Worker

from celery_app import make_celery
from celery_app.addons import worker_name_generator


def start_worker() -> None:
    """Start the Celery Worker."""
    environ.update({"APPLICATION_APP": "worker"})
    worker_name = f"{worker_name_generator()}@{node()}"

    celery = make_celery()
    worker = Worker(
        app=celery,
        hostname=worker_name,
        task_events=True,
        loglevel="INFO",
        concurrency=50.0,
        pool="threads",
    )
    worker = worker

    try:
        worker.start()

    except Exception as e:
        if isinstance(e, KeyboardInterrupt):
            worker.stop()

        else:
            tqdm.write("[bold red]Error starting worker.")

    asyncio.run(start_worker())


def start_beat() -> None:
    """Start the Celery beat scheduler."""
    celery = make_celery()
    environ.update({"APPLICATION_APP": "beat"})
    scheduler = "celery_app.addons.scheduler:DatabaseScheduler"
    worker_name = f"{worker_name_generator()}_celery"
    beat = Beat(
        app=celery,
        scheduler=scheduler,
        max_interval=5,
        loglevel="INFO",
        logfile=Path().cwd().joinpath("temp", "logs", f"{worker_name}.log"),
        no_color=False,
    )
    beat.run()


def main() -> None:
    """Entrada main."""
    calls = {"worker": start_worker, "beat": start_beat}
    args = argv[1:]
    parser = argparse.ArgumentParser("Celery App CrawJUD.")
    parser.add_argument(
        "--type",
        default="worker",
        help="Tipo de inicialização do celery (ex.: beat, worker, etc.)",
    )
    namespaces = parser.parse_args(args)

    callable_obj = calls[namespaces.type]
    process_celery = Process(target=callable_obj, daemon=True)
    process_celery.start()
    input("Pressione Enter para encerrar")
    process_celery.kill()
