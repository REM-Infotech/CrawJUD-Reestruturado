import inspect
import subprocess
import sys
import threading
import dill as pickle
from pathlib import Path
import ast

last_check = None


class Dummy(object): ...


# O objetivo de fazer isso é que, ao chamar qualquer função do NumPy, ela será redirecionada para um subprocesso.
class ModCall[T]:
    def __getattribute__(self, attr):
        global last_check
        try:
            last_check = attr

            p = sys.exec_prefix
            result = subprocess.run(
                [
                    str(
                        Path(p).joinpath("python").as_posix()
                    ),  # Caminho para o Python
                    str(
                        Path(__file__).parent.joinpath("run_numpy.py")
                    ),  # Arquivo que vai rodar o código no subprocesso
                    "--function",
                    last_check,  # Função que será chamada
                ],
                capture_output=True,
                text=True,
            )

            filename = f"{last_check}.pkl"
            try:
                with open(filename, "rb") as f:
                    return pickle.load(f)
            except EOFError:
                # Arquivo está vazio ou corrompido
                print(f"Erro: arquivo {filename} está vazio ou corrompido.")
                return Dummy
            return result
        except Exception:
            last_check = attr

            def call_func(*args, **kwargs) -> None:
                p = sys.exec_prefix
                result = subprocess.run(
                    [
                        str(
                            Path(p).joinpath("python").as_posix()
                        ),  # Caminho para o Python
                        str(
                            Path(__file__).parent.joinpath("run_numpy.py")
                        ),  # Arquivo que vai rodar o código no subprocesso
                        "--function",
                        last_check,  # Função que será chamada
                    ],
                    capture_output=True,
                    text=True,
                )

                filename = f"{last_check}.pkl"
                try:
                    with open(filename, "rb") as f:
                        return pickle.load(f)
                except EOFError:
                    # Arquivo está vazio ou corrompido
                    print(f"Erro: arquivo {filename} está vazio ou corrompido.")
                    return Dummy
                return result

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
            return (
                NumPy()
            )  # Intercepta a importação do numpy e retorna nossa versão modificada
        return None


# Registrar o import hook
sys.meta_path.insert(0, NumpyImportHook())

# Teste simples: Ao importar numpy, ele já será patchado automaticamente
if __name__ == "__main__":
    import numpy as np

    # Testando a execução de múltiplas threads com numpy
    arr = np.array([1, 2, 3, 4, 5])

    # Função exemplo que utiliza o numpy
    def func():
        print(
            np.sum(arr)
        )  # A chamada a np.sum será automaticamente redirecionada para subprocesso

    # Criando threads para testar
    threads = []
    for _ in range(5):  # Criando 5 threads
        thread = threading.Thread(target=func)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
