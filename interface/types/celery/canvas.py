"""Fornece tipos e wrappers personalizados para integração com Celery.

Este módulo define classes tipadas para resultados assíncronos,
resultados imediatos (EagerResult) e assinaturas de tarefas (Signature),
facilitando o uso de Celery com tipagem estática e integração com
o sistema de tarefas assíncronas do projeto.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    AnyStr,
    ClassVar,
    Generic,
    ParamSpec,
    Self,
    TypeVar,
    cast,
)

from celery.canvas import Signature as __Signature
from celery.result import AsyncResult as __AsyncResult
from celery.result import EagerResult as __EagerResult
from celery.result import states

if TYPE_CHECKING:
    from crawjud_app.custom.celery import AsyncCelery

P = ParamSpec("P")
R = TypeVar("R")
TClassBot = TypeVar("TClassBot", bound=object)
TBotSpec = ParamSpec("TBotSpec", bound=AnyStr)

class_set = set()


class CeleryResult[T](__AsyncResult, __EagerResult):
    """Celery Results.

    Class that wraps the result of a task execution.

    Used to check the status of a task, retrieve its result,
    and perform other operations related to task results.

    See Also:
        :ref:`guide-results` for the complete guide.

    """

    _app: ClassVar[AsyncCelery] = None

    def get(
        self,
        timeout: int | None = None,
        interval: float = 0.5,
        callback: T = None,
        on_message: T = None,
        on_interval: T = None,
        *,
        propagate: bool = True,
        no_ack: bool = True,
        follow_parents: bool = True,
        disable_sync_subtasks: bool = True,
        exception_states: Exception = states.EXCEPTION_STATES,
        propagate_states: Exception = states.PROPAGATE_STATES,
    ) -> Generic[R]:
        """Wait until task is ready, and return its result.

        Warning:
           Waiting for tasks within a task may lead to deadlocks.
           Please read :ref:`task-synchronous-subtasks`.

        Warning:
           Backends use resources to store and transmit results. To ensure
           that resources are released, you must eventually call
           :meth:`~@AsyncResult.get` or :meth:`~@AsyncResult.forget` on
           EVERY :class:`~@AsyncResult` instance returned after calling
           a task.

        Arguments:
            callback (Callable[[T], None]): A callback function to be called
                with the result of the task when it is ready.
            exception_states (Iterable[Union[str, Type[BaseException]]]): A list of
                exception states that should be propagated to the parent task.
            on_interval (Callable[[float], None]): A callback function to be called
                periodically with the elapsed time since the task was started.
            on_message (Callable[[Any], None]): A callback function to be called
                with the message received from the task when it is ready.
            propagate_states (Iterable[Union[str, Type[BaseException]]]): A list of
                states that should be propagated to the parent task.
            timeout (float): How long to wait, in seconds, before the
                operation times out. This is the setting for the publisher
                (celery client) and is different from `timeout` parameter of
                `@app.task`, which is the setting for the worker. The task
                isn't terminated even if timeout occurs.
            propagate (bool): Re-raise exception if the task failed.
            interval (float): Time to wait (in seconds) before retrying to
                retrieve the result.  Note that this does not have any effect
                when using the RPC/redis result store backends, as they don't
                use polling.
            no_ack (bool): Enable amqp no ack (automatically acknowledge
                message).  If this is :const:`False` then the message will
                **not be acked**.
            follow_parents (bool): Re-raise any exception raised by
                parent tasks.
            disable_sync_subtasks (bool): Disable tasks to wait for sub tasks
                this is the default configuration. CAUTION do not enable this
                unless you must.

        Returns:
            T: Resultado da tarefa, ou lança exceção se falhar.

        """
        return super().get(
            timeout,
            propagate,
            interval,
            no_ack,
            follow_parents,
            callback,
            on_message,
            on_interval,
            disable_sync_subtasks,
            exception_states,
            propagate_states,
        )

    def __getattr__(self, item: str) -> T:
        """Retorne o atributo solicitado ou inicialize '_app' se necessário.

        Args:
            item (str): Nome do atributo a ser acessado.

        Returns:
            T: Valor do atributo solicitado.

        """
        if item == "_app" and not hasattr(self, "_app"):
            from celery import current_app

            self._app = current_app

        return super().__getattr__(item)

    def wait_ready(self, timeout: float | None = None) -> T:
        """Aguarde até que o resultado da tarefa esteja pronto ou o timeout.

        Args:
            timeout (float | None): Tempo máximo de espera em segundos,
                ou None para aguardar indefinidamente.

        Returns:
            T: Resultado da tarefa se concluída com sucesso,
                ou None em caso de falha ou expiração.

        """
        while not self.ready():
            if timeout is not None:
                timeout -= 0.5
                if timeout <= 0:
                    return None
            self._app.control.ping(timeout=0.5)

        if self.failed():
            return None

        return self.result


class Signature[T](__Signature):
    """Task Signature.

    Class that wraps the arguments and execution options
    for a single task invocation.

    Used as the parts in a :class:`group` and other constructs,
    or to pass tasks around as callbacks while being compatible
    with serializers with a strict type subset.

    Signatures can also be created from tasks:

    - Using the ``.signature()`` method that has the same signature
      as ``Task.apply_async``:

        .. code-block:: pycon

            >>> add.signature(args=(1,), kwargs={"kw": 2}, options={})

    - or the ``.s()`` shortcut that works for star arguments:

        .. code-block:: pycon

            >>> add.s(1, kw=2)

    - the ``.s()`` shortcut does not allow you to specify execution options
      but there's a chaining `.set` method that returns the signature:

        .. code-block:: pycon

            >>> add.s(2, 2).set(countdown=10).set(expires=30).delay()

    Note:
        You should use :func:`~celery.signature` to create new signatures.
        The ``Signature`` class is the type returned by that function and
        should be used for ``isinstance`` checks for signatures.

    See Also:
        :ref:`guide-canvas` for the complete guide.

    Arguments:
        task (Union[Type[celery.app.task.Task], str]): Either a task
            class/instance, or the name of a task.
        args (Tuple): Positional arguments to apply.
        kwargs (Dict): Keyword arguments to apply.
        options (Dict): Additional options to :meth:`Task.apply_async`.

    Note:
        If the first argument is a :class:`dict`, the other
        arguments will be ignored and the values in the dict will be used
        instead::

            >>> s = signature('tasks.add', args=(2, 2))
            >>> signature(s)
            {'task': 'tasks.add', args=(2, 2), kwargs={}, options={}}

    """

    _app: ClassVar[AsyncCelery] = None

    def __init__(
        self,
        task: T = None,
        args: T = None,
        kwargs: T = None,
        options: T = None,
        type: T = None,  # noqa: A002
        subtask_type: T = None,
        *,
        immutable: bool = False,
        app: AsyncCelery = None,
        **ex: T,
    ) -> None:
        """Inicialize uma instância de Signature com os parâmetros fornecidos.

        Args:
            task (T): Tarefa ou nome da tarefa a ser associada à assinatura.
            args (T): Argumentos posicionais para a tarefa.
            kwargs (T): Argumentos nomeados para a tarefa.
            options (T): Opções adicionais para execução da tarefa.
            type (T): Tipo da sub-tarefa (opcional).
            subtask_type (T): Tipo específico de sub-tarefa (opcional).
            immutable (bool): Define se a assinatura é imutável.
            app (AsyncCelery): Instância do aplicativo Celery.
            **ex (T): Parâmetros extras para configuração.

        """
        if isinstance(task, str):
            task = app.tasks[task]

        super().__init__(
            task,
            args,
            kwargs,
            options,
            type,
            subtask_type,
            immutable,
            app,
            **ex,
        )

    @classmethod
    def from_dict(cls, d: T, app: T | None = None) -> Self:
        """Crie uma instância de Signature a partir de um dicionário de dados.

        Args:
            d (T): Dicionário contendo os dados da assinatura da tarefa.
            app (T | None): Instância opcional do aplicativo Celery.

        Returns:
            Self: Instância de Signature criada a partir do dicionário.

        """
        typ = d.get("subtask_type")
        if typ:
            target_cls = cls.TYPES[typ]
            if target_cls is not cls:
                return target_cls.from_dict(d, app=app)
        return Signature(d, app=app)

    def apply_async(
        self,
        args: AnyStr | None = None,
        kwargs: AnyStr | None = None,
        route_name: str | None = None,
        **options: AnyStr,
    ) -> CeleryResult | None:
        """Apply this task asynchronously.

        Arguments:
            args (Tuple): Partial args to be prepended to the existing args.
            kwargs (Dict): Partial kwargs to be merged with existing kwargs.
            route_name (str): Name of the route to use for this task.
            **options (Dict): Partial options to be merged
                with existing options.

        Returns:
            ~@AsyncResult: promise of future evaluation.


        See Also:
            :meth:`~@Task.apply_async` and the :ref:`guide-calling` guide.

        """
        async_result = cast(
            "CeleryResult",
            super().apply_async(args, kwargs, route_name=route_name, **options),
        )
        async_result._app = self._app  # noqa: SLF001
        async_result.wait_ready = CeleryResult.wait_ready.__get__(async_result)
        if async_result:
            return async_result
        return None
