from crawjud.common.exceptions.bot import ExecutionError


def raise_execution_error(msg: str) -> None:
    raise ExecutionError(message=msg)
