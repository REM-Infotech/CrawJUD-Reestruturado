"""Módulo de recursos do celery app."""

from contextlib import suppress

import psutil
from tqdm import tqdm

from . import manage_files

__all__ = ["manage_files"]


def _kill_browsermob() -> None:
    """Finaliza processos relacionados ao BrowserMob Proxy."""
    keyword = "browsermob"
    matching_procs = []

    # Primeira fase: coleta segura dos processos
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        with suppress(
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
            Exception,
        ):
            if any(keyword in part for part in proc.info["cmdline"]):
                matching_procs.append(proc)

    # Segunda fase: finalização dos processos encontrados
    for proc in matching_procs:
        with suppress(psutil.NoSuchProcess, psutil.AccessDenied, Exception):
            tqdm.write(f"Matando PID {proc.pid} ({' '.join(proc.info['cmdline'])})")
            proc.kill()
