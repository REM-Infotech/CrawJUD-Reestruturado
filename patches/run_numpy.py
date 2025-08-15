import argparse
import ast
from pathlib import Path
import dill as pickle
import numpy as np
import sys
from contextlib import suppress

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--function", help="Função do NumPy a ser chamada", default="__name__"
    )
    parser.add_argument("--args", help="Argumentos para a função", default="()")
    parser.add_argument(
        "--kwargs", help="Argumentos nomeados para a função", default="{}"
    )

    args = parser.parse_args()

    result = None

    function_name = args.function
    func = getattr(np, function_name)

    _args = ast.literal_eval(
        args.args
    )  # Convertendo os argumentos de string para tupla/lista
    _kwargs = ast.literal_eval(
        args.kwargs
    )  # Convertendo os kwargs para um dicionário

    if callable(func):
        try:
            result = func(*_args, **_kwargs)  # Chama a função com os argumentos
        except Exception:
            result = func

    else:
        result = func

    with Path(__file__).parent.joinpath(f"{function_name}.pkl").open("wb") as f:
        pickle.dump(result, f)

    print(f"{function_name}.pkl")
