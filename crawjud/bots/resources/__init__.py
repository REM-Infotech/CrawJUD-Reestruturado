"""
Fornece recursos e utilitários para os bots do sistema CrawJUD.

Este pacote contém módulos e funções auxiliares utilizados pelos bots
para realizar operações específicas no contexto do projeto CrawJUD.
"""

from contextlib import suppress

import psutil

from . import files_manage

__all__ = ["files_manage"]


def _kill_browsermob() -> None:
    """
    Finaliza processos relacionados ao BrowserMob Proxy.

    Args:
        None

    Returns:
        None: Não retorna valor.

    """
    keyword = "browsermob"
    matching_procs = []

    # Primeira fase: coleta segura dos processos
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        with suppress(
            psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, Exception
        ):
            if any(keyword in part for part in proc.info["cmdline"]):
                matching_procs.append(proc)

    # Segunda fase: finalização dos processos encontrados
    for proc in matching_procs:
        with suppress(psutil.NoSuchProcess, psutil.AccessDenied, Exception):
            print(f"Matando PID {proc.pid} ({' '.join(proc.info['cmdline'])})")
            proc.kill()
