"""Defina modelos e utilitários para manipulação de logs e cache de execução.

Este módulo fornece:
- Modelos para armazenamento de logs no Redis;
- Estruturas para manipulação de mensagens de log;
- Funções utilitárias para consulta e serialização dos dados.

"""

from __future__ import annotations

from collections.abc import Callable, Generator, Mapping
from contextlib import suppress
from typing import (
    Any,
    Literal,
    ParamSpec,
    Self,
    TypedDict,
)

from redis_om import Field, HashModel, JsonModel, NotFoundError

from crawjud.interfaces.types.pje import Processo
from crawjud.utils.interfaces import ItemMessageList

description_message = (
    "e.g. '[(C3K7H5, log, 15, 19:37:15)> Salvando arquivos na pasta...]'"
)

description_pid = "e.g. 'C3K7H5' (identificador do processo)"


P = ParamSpec("RedisQuerySpecs")
type IncEx = (
    set[int] | set[str] | Mapping[int, IncEx | bool] | Mapping[str, IncEx | bool]
)


class ModelRedisHandler(HashModel):
    """Defina o modelo ModelRedisHandler para armazenar logs no Redis.

    Args:
        level (str): Nível do log (ex: 'INFO', 'ERROR').
        message (str): Mensagem do log.
        time (str): Data e hora do log.
        module (str): Nome do módulo do sistema.
        module_name (str): Nome específico do módulo.

    Returns:
        ModelRedisHandler: Instância do modelo de log.

    """

    level: str
    message: str
    time: str
    module: str
    module_name: str


class CachedExecutionDict(TypedDict):
    """Defina o dicionário TypedDict para armazenar execuções em cache no Redis.

    Args:
        processo (str): Identificador do processo jurídico.
        pid (str): Identificador do processo (ex: 'C3K7H5').
        data (dict[str, Any] | list[Any]): Dados do processo armazenados em cache.

    Returns:
        CachedExecutionDict: Dicionário representando a execução em cache.

    """

    processo: str = Field(description="Processo Juridico", primary_key=True)
    pid: str = Field(
        default="desconhecido",
        description=description_pid,
    )
    data: dict[str, Any] | list[Any] = Field()


class MessageLogDict(TypedDict):
    """Model for message logs.

    Attributes:
        id_log (int):
            Unique identifier for the log entry (e.g., 1).

        pid (str):
            Process identifier (e.g., 'C3K7H5').

        message (str):
            Log message content.

        type (str):
            Type of log entry (e.g., 'log', 'error', 'success').

        status (str):
            Status of the process (e.g., 'Em Execução', 'Concluído', 'Erro').

        start_time (str):
            Timestamp of when the log entry
            was created (e.g., '01/01/2023 - 19:37:15').

        row (int):
            Current row number being processed (e.g., 15).

        total (int):
            Total number of rows to be processed (e.g., 100).

        errors (int):
            Number of errors encountered (e.g., 2).

        success (int):
            Number of successful operations (e.g., 98).

        remaining (int):
            Number of rows remaining to be processed (e.g., 85).

    """

    """Model for message logs."""

    pid: str
    type: str
    messages: list[ItemMessageList]
    status: str
    start_time: str
    row: int
    total: int
    errors: int
    success: int
    remaining: int


class MessageLog(JsonModel):
    """Model for message logs.

    Attributes:
        id_log (int):
            Unique identifier for the log entry (e.g., 1).

        pid (str):
            Process identifier (e.g., 'C3K7H5').

        message (str):
            Log message content.

        type (str):
            Type of log entry (e.g., 'log', 'error', 'success').

        status (str):
            Status of the process (e.g., 'Em Execução', 'Concluído', 'Erro').

        start_time (str):
            Timestamp of when the log entry was created
                (e.g., '01/01/2023 - 19:37:15').

        row (int):
            Current row number being processed (e.g., 15).

        total (int):
            Total number of rows to be processed (e.g., 100).

        errors (int):
            Number of errors encountered (e.g., 2).

        success (int):
            Number of successful operations (e.g., 98).

        remaining (int):
            Number of rows remaining to be processed (e.g., 85).


    """

    """Model for message logs."""

    pid: str = Field(
        default="desconhecido",
        description=description_pid,
        primary_key=True,
    )

    messages: list[ItemMessageList] = Field(
        default=[
            ItemMessageList(message="Mensagem não informada", id_log=0, type="info"),
        ],
        description=description_message,
    )
    status: str = Field(
        default="Desconhecido",
        description="e.g. 'Em Execução', 'Concluído', 'Erro' (status do processo)",
    )
    start_time: str = Field(
        default="00/00/0000 - 00:00:00",
        description="e.g. '01/01/2023 - 19:37:15' (data/hora de início)",
    )
    row: int = Field(description="e.g. 15 (linha atual sendo processada)")
    total: int = Field(description="e.g. 100 (total de linhas a serem processadas)")
    errors: int = Field(description="e.g. 2 (quantidade de erros encontrados)")
    success: int = Field(
        description="e.g. 98 (quantidade de operações bem-sucedidas)",
    )
    remaining: int = Field(description="e.g. 85 (linhas restantes para processar)")

    @classmethod
    def query_logs(cls, pid: str) -> Self | None:
        """Recupere o log associado ao identificador de processo (pid).

        Args:
            pid (str): Identificador do processo.

        Returns:
            Self | None: Instância do log correspondente ou None se não encontrado.

        """
        with suppress(NotFoundError, Exception):
            log_pks = cls.all_pks()

            for pk in log_pks:
                if pk == pid:
                    return cls.get(pk)
        return None

    @classmethod
    def all_data(cls) -> list[Self]:
        """Recupere todos os registros do modelo MessageLog do Redis.

        Args:
            cls (type[Self]): Classe do modelo MessageLog a ser consultado.

        Returns:
            list[Self]: Lista de instâncias do modelo MessageLog recuperadas.

        """
        return all_data(cls)

    def model_dump(
        self,
        mode: Literal["json", "python"] = "python",
        include: IncEx | None = None,
        exclude: IncEx | None = None,
        context: dict | None = None,
        warnings: Literal["none", "warn", "error"] = "warn",
        fallback: Callable[..., Any] | None = None,
        *args: P.args,
        by_alias: bool | None = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        **kwargs: P.kwargs,
    ) -> MessageLogDict:
        """Realize o dump do modelo MessageLog convertendo para dicionário.

        Args:
            mode (Literal["json", "python"], opcional): Modo de serialização.
            include (IncEx | None, opcional): Campos a incluir.
            exclude (IncEx | None, opcional): Campos a excluir.
            context (dict | None, opcional): Contexto adicional.
            warnings (Literal["none", "warn", "error"], opcional): Controle de avisos.
            fallback (Callable[..., Any] | None, opcional): Função de fallback.
            *args: Argumentos posicionais adicionais.
            by_alias (bool | None, opcional): Usar aliases dos campos.
            exclude_unset (bool, opcional): Excluir campos não definidos.
            exclude_defaults (bool, opcional): Excluir valores padrão.
            exclude_none (bool, opcional): Excluir campos None.
            round_trip (bool, opcional): Preservar informações para round-trip.
            **kwargs: Argumentos nomeados adicionais.

        Returns:
            MessageLogDict: Dicionário serializado do modelo MessageLog.

        """
        # Realiza o dump do modelo, convertendo para dict
        return MessageLogDict(
            **super().model_dump(
                mode=mode,
                include=include,
                exclude=exclude,
                context=context,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
                round_trip=round_trip,
                warnings=warnings,
                fallback=fallback,
                *args,
                **kwargs,
            ),
        )


class CachedExecution(JsonModel):
    """Defina modelo CachedExecution para armazenar execuções em cache no Redis.

    Args:
        processo (str): Identificador do processo jurídico.
        pid (str): Identificador do processo (ex: 'C3K7H5').
        data (Processo | Any): Dados do processo armazenados em cache.

    Returns:
        CachedExecution: Instância do modelo de execução em cache.

    """

    processo: str = Field(
        description="Processo Juridico",
        primary_key=True,
        default=Processo(),
    )
    pid: str = Field(
        default="desconhecido",
        description="e.g. 'C3K7H5' (identificador do processo)",
    )
    data: Processo | Any = Field()

    @classmethod
    def all_data(cls) -> list[Self]:  # pragma: no cover
        """Recupere todos os registros do modelo CachedExecution do Redis.

        Args:
            cls (type[Self]): Classe do modelo CachedExecution a ser consultado.

        Returns:
            list[Self]: Lista de instâncias do modelo CachedExecution recuperadas.

        """
        return all_data(cls)

    def model_dump(
        self,
        mode: Literal["json", "python"] = "python",
        include: IncEx | None = None,
        exclude: IncEx | None = None,
        context: dict | None = None,
        fallback: Callable[..., Any] | None = None,
        *args: P.args,
        by_alias: bool | None = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal["none", "warn", "error"] = True,
        **kwargs: P.kwargs,
    ) -> CachedExecutionDict:  # pragma: no cover
        """Realize o dump do modelo CachedExecution convertendo para dict.

        Args:
            mode (Literal["json", "python"], opcional): Modo de serialização.
            include (IncEx | None, opcional): Campos a incluir.
            exclude (IncEx | None, opcional): Campos a excluir.
            context (dict | None, opcional): Contexto adicional.
            fallback (Callable[..., Any] | None, opcional): Função de fallback.
            *args: Argumentos posicionais adicionais.
            by_alias (bool | None, opcional): Usar aliases dos campos.
            exclude_unset (bool, opcional): Excluir campos não definidos.
            exclude_defaults (bool, opcional): Excluir valores padrão.
            exclude_none (bool, opcional): Excluir campos None.
            round_trip (bool, opcional): Preservar informações para round-trip.
            warnings (bool | Literal["none", "warn", "error"], opcional):
                Controle de avisos.
            **kwargs: Argumentos nomeados adicionais.

        Returns:
            CachedExecutionDict: Dicionário serializado do modelo.

        """
        return CachedExecutionDict(
            **super().model_dump(
                mode=mode,
                include=include,
                exclude=exclude,
                context=context,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
                round_trip=round_trip,
                warnings=warnings,
                fallback=fallback,
                *args,
                **kwargs,
            ),
        )


def all_data[T](cls: type[T]) -> Generator[T, Any, None]:  # pragma: no cover
    """Recupere todos os registros do modelo informado do Redis de forma iterativa.

    Args:
        cls (type[T]): Classe do modelo Redis a ser consultado.

    Yields:
        Generator[T, Any, None]: Gerador que itera sobre as instâncias do modelo.

    """
    pks = list(cls.all_pks())
    cls.total_pks = len(pks)
    for pk in pks:
        yield cls.get(pk)
