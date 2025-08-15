"""Classe de Tarefas customizadas para integração com Celery.

Este módulo implementa a classe ContextTask, que estende funcionalidades da
Task do Celery, permitindo execução de tarefas assíncronas, criação de
assinaturas (signatures) e subtarefas, além de integração com variáveis de
ambiente e suporte a funções corrotina.

"""

from __future__ import annotations

from asyncio import iscoroutinefunction
from asyncio import run as run_async
from typing import TYPE_CHECKING, ClassVar, Generic, ParamSpec

from celery.app.task import Task as TaskBase
from dotenv import dotenv_values

from crawjud_app.custom.canvas import subtask

environ = dotenv_values()
P = ParamSpec("P")

if TYPE_CHECKING:
    from crawjud.interfaces.types.celery.canvas import (
        CeleryResult,
        Signature,
    )


class ContextTask[T](TaskBase):
    """Implementa uma tarefa customizada para integração com Celery.

    Esta classe estende a TaskBase do Celery, permitindo execução de tarefas
    assíncronas, criação de assinaturas (signatures) e subtarefas, além de
    integração com variáveis de ambiente e suporte a funções corrotina.

    Atributos:
        abstract (bool): Indica se a classe é abstrata.
        contains_classmethod (bool): Indica se contém métodos de classe.
        tasks_cls (dict): Dicionário para armazenar classes de tarefas.

    Métodos:
        _run: Executa a tarefa, suportando funções corrotina.
        signature: Cria uma assinatura para a tarefa.
        subtask: Cria uma subtarefa para a tarefa.
        apply_async: Executa a tarefa de forma assíncrona.
        __call__: Permite chamada direta da tarefa.
    """

    abstract = True
    contains_classmethod = False

    tasks_cls: ClassVar[dict] = {}

    def _run(self, *args: Generic[T], **kwargs: Generic[T]) -> None:
        if iscoroutinefunction(self.run):
            return run_async(self.run(*args, **kwargs))

        return self.run(*args, **kwargs)

    def signature(
        self,
        args: T = None,
        *starargs: T,
        **starkwargs: T,
    ) -> Signature:
        """Create signature.

        Returns:
            :class:`~celery.signature`:  object for
                this task, wrapping arguments and execution options
                for a single task invocation.

        """
        starkwargs.setdefault("app", self.app)
        return subtask(self, args, *starargs, **starkwargs)

    def subtask(
        self,
        args: T = None,
        *starargs: T,
        **starkwargs: T,
    ) -> Signature:
        """Create signature.

        Returns:
            :class:`~celery.signature`:  object for
                this task, wrapping arguments and execution options
                for a single task invocation.

        """
        star_arg = starargs
        star_kwarg = starkwargs

        return subtask(self, args, *star_arg, **star_kwarg)

    def apply_async(
        self,
        args: tuple[str, T] | None = None,
        kwargs: dict[str, T] | None = None,
        task_id: str | None = None,
        producer: str | None = None,
        link: str | None = None,
        link_error: str | None = None,
        shadow: str | None = None,
        **options: T,
    ) -> CeleryResult:
        """Apply tasks asynchronously by sending a message.

        Arguments:
            task_id (str): The unique identifier for the task.
            args (Tuple): The positional arguments to pass on to the task.

            kwargs (Dict): The keyword arguments to pass on to the task.

            countdown (float): Number of seconds into the future that the
                task should execute.  Defaults to immediate execution.

            eta (~datetime.datetime): Absolute time and date of when the task
                should be executed.  May not be specified if `countdown`
                is also supplied.

            expires (float, ~datetime.datetime): Datetime or
                seconds in the future for the task should expire.
                The task won't be executed after the expiration time.

            shadow (str): Override task name used in logs/monitoring.
                Default is retrieved from :meth:`shadow_name`.

            connection (kombu.Connection): Reuse existing broker connection
                instead of acquiring one from the connection pool.

            retry (bool): If enabled sending of the task message will be
                retried in the event of connection loss or failure.
                Default is taken from the :setting:`task_publish_retry`
                setting.  Note that you need to handle the
                producer/connection manually for this to work.

            retry_policy (Mapping): Override the retry policy used.
                See the :setting:`task_publish_retry_policy` setting.

            time_limit (int): If set, overrides the default time limit.

            soft_time_limit (int): If set, overrides the default soft
                time limit.

            queue (str, kombu.Queue): The queue to route the task to.
                This must be a key present in :setting:`task_queues`, or
                :setting:`task_create_missing_queues` must be
                enabled.  See :ref:`guide-routing` for more
                information.

            exchange (str, kombu.Exchange): Named custom exchange to send the
                task to.  Usually not used in combination with the ``queue``
                argument.

            routing_key (str): Custom routing key used to route the task to a
                worker server.  If in combination with a ``queue`` argument
                only used to specify custom routing keys to topic exchanges.

            priority (int): The task priority, a number between 0 and 9.
                Defaults to the :attr:`priority` attribute.

            serializer (str): Serialization method to use.
                Can be `pickle`, `json`, `yaml`, `msgpack` or any custom
                serialization method that's been registered
                with :mod:`kombu.serialization.registry`.
                Defaults to the :attr:`serializer` attribute.

            compression (str): Optional compression method
                to use.  Can be one of ``zlib``, ``bzip2``,
                or any custom compression methods registered with
                :func:`kombu.compression.register`.
                Defaults to the :setting:`task_compression` setting.

            link (Signature): A single, or a list of tasks signatures
                to apply if the task returns successfully.

            link_error (Signature): A single, or a list of task signatures
                to apply if an error occurs while executing the task.

            producer (kombu.Producer): custom producer to use when publishing
                the task.

            add_to_parent (bool): If set to True (default) and the task
                is applied while executing another task, then the result
                will be appended to the parent tasks ``request.children``
                attribute.  Trailing can also be disabled by default using the
                :attr:`trail` attribute

            ignore_result (bool): If set to `False` (default) the result
                of a task will be stored in the backend. If set to `True`
                the result will not be stored. This can also be set
                using the :attr:`ignore_result` in the `app.task` decorator.

            publisher (kombu.Producer): Deprecated alias to ``producer``.

            headers (Dict): Message headers to be included in the message.
                The headers can be used as an overlay for custom labeling
                using the :ref:`canvas-stamping` feature.

            **options: Keyword arguments to override task execution options.**

        Returns:
            celery.result.AsyncResult: Promise of future evaluation.

        Note:
            Also supports all keyword arguments supported by
            :meth:`kombu.Producer.publish`.

        """
        return super().apply_async(
            args,
            kwargs,
            task_id,
            producer,
            link,
            link_error,
            shadow,
            **options,
        )

    def __call__(self, *args: T, **kwargs: T) -> None:
        """Executa a tarefa diretamente ao chamar a instância da classe.

        Args:
            *args (T): Argumentos posicionais para a tarefa.
            **kwargs (T): Argumentos nomeados para a tarefa.

        Returns:
            None: Não retorna valor.

        """
        return self._run(*args, **kwargs)
