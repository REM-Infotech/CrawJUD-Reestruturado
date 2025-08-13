import pytest
from multiprocessing import Process
from collections.abc import Callable
import time

"""Testa funções principais do módulo main.py do CrawJUD.

Testa inicialização, reinício e parada dos serviços Celery Worker e Beat.

"""


import crawjud_app.main as main


def dummy_func() -> None:
    """Função dummy para testes de processos."""
    time.sleep(0.1)


def test_start_service_returns_process() -> None:
    """Verifica se start_service retorna um objeto Process ativo."""
    proc = main.start_service(dummy_func)
    assert isinstance(proc, Process)
    assert proc.is_alive()
    main.stop_service(proc)


def test_stop_service_returns_false() -> None:
    """Verifica se stop_service retorna False após matar o processo."""
    proc = main.start_service(dummy_func)
    result = main.stop_service(proc)
    assert result is False
    assert not proc.is_alive()


def test_restart_service_starts_new_process() -> None:
    """Verifica se restart_service reinicia o processo corretamente."""
    proc = main.start_service(dummy_func)
    new_proc = main.restart_service(dummy_func, proc)
    assert isinstance(new_proc, Process)
    assert new_proc.is_alive()
    main.stop_service(new_proc)


def test_start_worker_and_start_beat_do_not_raise(monkeypatch) -> None:
    """Testa se start_worker e start_beat não levantam exceções.

    Usa monkeypatch para evitar execução real do Celery.
    """
    monkeypatch.setattr(main, "make_celery", lambda: None)
    class DummyWorker:
        def __init__(self, **kwargs) -> None: pass
        def start(self) -> None: pass
        def stop(self) -> None: pass
    class DummyBeat:
        def __init__(self, **kwargs) -> None: pass
        def run(self) -> None: pass

    monkeypatch.setattr(main, "Worker", DummyWorker)
    monkeypatch.setattr(main, "Beat", DummyBeat)

    main.start_worker()
    main.start_beat()
