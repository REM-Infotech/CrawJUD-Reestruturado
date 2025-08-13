"""Módulo Celery App do CrawJUD Automatização."""

import argparse
import platform
from collections.abc import Callable
from contextlib import suppress
from multiprocessing import Process
from os import environ
from pathlib import Path
from platform import node
from sys import argv
from time import sleep

from celery.apps.beat import Beat
from celery.apps.worker import Worker
from clear import clear
from dotenv import dotenv_values
from inquirer import List, prompt
from inquirer.themes import GreenPassion
from tqdm import tqdm

from crawjud_app import app as app
from crawjud_app import make_celery
from crawjud_app.addons import worker_name_generator

clear()
envdot = dotenv_values()
environ["WORKER_NAME"] = f"{worker_name_generator()}@{node()}"

work_dir = Path(__file__).cwd()


def start_worker() -> None:
    """Start the Celery Worker."""
    environ.update({"APPLICATION_APP": "worker"})
    worker_name = environ["WORKER_NAME"]

    debug = envdot.get("DEBUG", "false").lower() == "true"
    pool_ = "prefork"
    if debug or platform.system() == "Windows":
        pool_ = "threads"

    celery = make_celery()
    worker = Worker(
        app=celery,
        hostname=worker_name,
        task_events=True,
        loglevel="DEBUG",
        concurrency=int(environ.get("CELERY_CONCURRENCY", "16")),
        pool=pool_,
    )
    with suppress(KeyboardInterrupt):
        worker.start()

    worker.stop()


def start_beat() -> None:
    """Start the Celery beat scheduler."""
    celery = make_celery()
    environ.update({"APPLICATION_APP": "beat"})
    scheduler = "crawjud_app.addons.scheduler:DatabaseScheduler"
    beat = Beat(
        app=celery,
        scheduler=scheduler,
        max_interval=5,
        loglevel="INFO",
        logfile=work_dir.joinpath(
            "temp",
            "logs",
            f"{environ['WORKER_NAME']}_beat.log",
        ),
        no_color=False,
    )
    beat.run()


def start_service(call: Callable) -> Process:  # noqa: D103
    proc = Process(target=call)
    proc.start()
    return proc


def restart_service(call: Callable, proc: Process) -> Process:  # noqa: D103
    stop_service(proc)
    sleep(5)

    return start_service(call)


def stop_service(proc: Process) -> bool:
    """Pare o serviço passado como processo.

    Args:
        proc (Process): Processo a ser parado.

    Returns:
        bool: True se o processo foi parado com sucesso, False caso contrário.

    """
    proc.terminate()
    proc.join()
    # Retorna True se o processo foi parado com sucesso, False caso contrário.
    return proc.is_alive()


def main() -> None:  # pragma: no cover
    """Entrada main."""
    with suppress(KeyboardInterrupt, Exception):
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
        process_celery = start_service(callable_obj)

        process_running = True

        opt_1 = f"Reiniciar {str(namespaces.type).capitalize()}"
        opt_2 = f"Encerrar {str(namespaces.type).capitalize()}"

        while process_running:
            clear()
            questions = [
                List(
                    "option_server",
                    "Selecione o que fazer",
                    choices=[
                        opt_1,
                        opt_2,
                    ],
                    default=opt_1,
                ),
            ]

            result = prompt(questions, theme=GreenPassion())

            if not result:
                process_running = stop_service(process_celery)
                break

            if result.get("option_server") == opt_1:
                process_celery = restart_service(callable_obj, process_celery)

            elif result.get("option_server") == opt_2:
                process_running = stop_service(process_celery)

    clear()
    tqdm.write("Serviço encerrado!")
