import inspect
import subprocess
import sys
import threading
import traceback
import dill as pickle
from pathlib import Path
import ast

last_check: str = None


class Dummy(object): ...


p = sys.exec_prefix


def _desspicklable_me(PATH_FILE: Path):
    with PATH_FILE.open("rb") as f:
        readed = pickle.load(f)
        if readed:
            return readed

        return "2.1.0"


def call_func(*args, **kwargs) -> None:
    global last_check
    filename = f"{last_check}.pkl"
    PATH_FILE = Path(__file__).parent.joinpath(filename)
    if PATH_FILE.exists():
        return _desspicklable_me(PATH_FILE)

    subprocess.run(
        [
            str(Path(p).joinpath("python").as_posix()),  # Caminho para o Python
            str(
                Path(__file__).parent.joinpath("run_numpy.py")
            ),  # Arquivo que vai rodar o código no subprocesso
            "--function",
            last_check,  # Função que será chamada
        ],
        capture_output=True,
        text=True,
    )

    return _desspicklable_me(PATH_FILE)


# O objetivo de fazer isso é que, ao chamar qualquer função do NumPy, ela será redirecionada para um subprocesso.
class ModCall[T]:
    def __getattribute__(self, attr):
        filename = f"{attr}.pkl"
        PATHFILE = Path(__file__).parent.joinpath(filename)
        try:
            if PATHFILE.exists():
                return _desspicklable_me(PATHFILE)

            p = sys.exec_prefix
            subprocess.run(
                [
                    str(
                        Path(p).joinpath("python").as_posix()
                    ),  # Caminho para o Python
                    str(
                        Path(__file__).parent.joinpath("run_numpy.py")
                    ),  # Arquivo que vai rodar o código no subprocesso
                    "--function",
                    attr,  # Função que será chamada
                ],
                capture_output=True,
                text=True,
            )

            return _desspicklable_me(PATHFILE)

        except Exception as e:
            global last_check
            last_check = attr

            print(e)

            return call_func


class NumPy:
    name = "numpy"
    __name__ = "numpy"

    def __getattribute__(self, arg=None):
        return self

    def __call__(self, *args, **kwds):
        return ModCall()


# Hook para interceptar o carregamento do módulo numpy
class NumpyImportHook:
    def find_spec(self, fullname, path, target=None):
        if fullname == "numpy":
            print(fullname)
            print(path)
            print(target)
            return (
                NumPy()
            )  # Intercepta a importação do numpy e retorna nossa versão modificada
        return None


# Registrar o import hook
sys.meta_path.insert(0, NumpyImportHook())
