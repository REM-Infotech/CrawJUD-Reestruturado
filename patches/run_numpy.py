import argparse
import ast
from io import BytesIO
import pickle
import sys
from contextlib import suppress

import numpy as np

if __name__ == "__main__":

    def main():
        args = sys.argv[1:]
        parser = argparse.ArgumentParser("Celery App CrawJUD.")
        parser.add_argument(
            "--function",
            default="worker",
            help="Tipo de inicialização do celery (ex.: beat, worker, etc.)",
        )

        parser.add_argument(
            "--args",
            default="worker",
            help="Tipo de inicialização do celery (ex.: beat, worker, etc.)",
        )

        parser.add_argument(
            "--kwargs",
            default="worker",
            help="Tipo de inicialização do celery (ex.: beat, worker, etc.)",
        )

        namespaces = parser.parse_args(args)

        with suppress(Exception):
            function_name = namespaces.function
            func = getattr(np, function_name)
            if callable(func):
                _args = ast.literal_eval(namespaces.args)
                _kwargs = ast.literal_eval(namespaces.kwargs)
                result = func(*_args, **_kwargs)
                # Converte arrays numpy para listas Python padrão
                if isinstance(result, np.ndarray):
                    result = result.tolist()
                # Converte outros tipos numpy para tipos Python nativos
                elif hasattr(result, "item"):
                    result = result.item()
                with open(f"{function_name}.pkl", "wb") as f:
                    pickle.dump(result, f)
                print(f"{function_name}.pkl")

    main()
