from pathlib import Path
import subprocess
import sys
import threading

obj = None

dict_attrs = {}


class ModCall[T]:
    def __getattribute__(self, arg: T = None):
        last_check = arg

        def call_func(*args, **kwargs) -> None:
            p = sys.exec_prefix
            result = subprocess.run(
                [
                    str(Path(p).joinpath("python").as_posix()),
                    str(Path(__file__).parent.joinpath("run_numpy.py")),
                    "--function",
                    last_check,
                    "--args",
                    f"{args}",
                    "--kwargs",
                    f"{kwargs}",
                ],
                capture_output=True,
                text=True,
            )

            if result.stdout:
                import pickle

                with open(f"{last_check}.pkl", "rb") as f:
                    r_pickle = pickle.load(f)
                    return r_pickle
            return result

        return call_func

    def __call__(self, *args, **kwds):
        pass


class NumPy[T]:
    name = "numpy"
    __name__ = "numpy"

    def __getattribute__(self, arg: T = None):
        return self

    def __call__(self, *args, **kwds):
        return ModCall()


# Import Hook para interceptar o carregamento do módulo numpy
class NumpyImportHook[T]:
    def find_spec(self, fullname, path, target=None):
        # Quando o numpy for importado, aplicamos o patch
        if fullname == "numpy":
            return NumPy()
        return None

    def pega_atributo(self, *args, **kwargs) -> None:
        print("ok")


# Registrar o import hook para intercepção
sys.meta_path.insert(0, NumpyImportHook())

# Teste simples: Ao importar numpy, ele já será patchado automaticamente
if __name__ == "__main__":
    import numpy as np

    np.__getattribute__ = NumpyImportHook.pega_atributo.__get__(np)
    # Testando a execução de múltiplas threads com numpy
    arr = np.array([1, 2, 3, 4, 5])

    # Função exemplo que utiliza o numpy
    def func():
        print(
            np.sum(arr),
        )  # A chamada a np.sum será automaticamente redirecionada para subprocesso se necessário

    # Criando threads para testar
    threads = []
    for _ in range(5):  # Criando 5 threads
        thread = threading.Thread(target=func)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
