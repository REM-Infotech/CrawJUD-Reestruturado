from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    AnyStr,
    Generic,
    ParamSpec,
    TypeVar,
    cast,
)

from celery.canvas import Signature as __Signature
from celery.result import AsyncResult as __AsyncResult
from celery.result import states

if TYPE_CHECKING:
    from celery_app.custom._celery import AsyncCelery

P = ParamSpec("P")
R = TypeVar("R")
TClassBot = TypeVar("TClassBot", bound=object)
TBotSpec = ParamSpec("TBotSpec", bound=AnyStr)

class_set = set()


class AsyncResult(__AsyncResult):
    """Celery AsyncResult.

    Class that wraps the result of a task execution.

    Used to check the status of a task, retrieve its result,
    and perform other operations related to task results.

    See Also:
        :ref:`guide-results` for the complete guide.

    """

    _app: AsyncCelery = None

    def get(
        self,
        timeout: int = None,
        propagate: bool = True,
        interval: float = 0.5,
        no_ack: bool = True,
        follow_parents: bool = True,
        callback: Any = None,
        on_message: Any = None,
        on_interval: Any = None,
        disable_sync_subtasks: bool = True,
        EXCEPTION_STATES: Exception = states.EXCEPTION_STATES,  # noqa: N803
        PROPAGATE_STATES: Exception = states.PROPAGATE_STATES,  # noqa: N803
    ) -> Generic[R]:
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
            EXCEPTION_STATES,
            PROPAGATE_STATES,
        )

    def __getattr__(self, item: str) -> Any:
        """Get attribute from AsyncResult."""
        if item == "_app" and not hasattr(self, "_app"):
            from celery import current_app

            self._app = current_app

        return super().__getattr__(item)

    def wait_ready(self, timeout: float = None) -> Generic[R]:
        """Wait until the result is ready."""
        while not self.ready():
            if timeout is not None:
                timeout -= 0.5
                if timeout <= 0:
                    return None
            self._app.control.ping(timeout=0.5)

        if self.failed():
            return None

        return self.result


class Signature(__Signature):
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

    _app: AsyncCelery = None

    def __init__(
        self,
        task: Any = None,
        args: Any = None,
        kwargs: Any = None,
        options: Any = None,
        type: Any = None,  # noqa: A002
        subtask_type: Any = None,
        immutable: Any = False,
        app: AsyncCelery = None,
        **ex: Any,
    ) -> None:
        if isinstance(task, str):
            task = app.tasks[task]

        super().__init__(
            task, args, kwargs, options, type, subtask_type, immutable, app, **ex
        )

    @classmethod
    def from_dict(cls, d, app=None):  # noqa: ANN001, ANN206
        """Create a new signature from a dict.
        Subclasses can override this method to customize how are
        they created from a dict.
        """  # noqa: D205
        typ = d.get("subtask_type")
        if typ:
            target_cls = cls.TYPES[typ]
            if target_cls is not cls:
                return target_cls.from_dict(d, app=app)
        return Signature(d, app=app)

    def apply_async(
        self,
        args: AnyStr = None,
        kwargs: AnyStr = None,
        route_name: str = None,
        **options: AnyStr,
    ) -> AsyncResult | None:
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
            AsyncResult,
            super().apply_async(args, kwargs, route_name=route_name, **options),
        )
        async_result._app = self._app  # noqa: SLF001
        async_result.wait_ready = AsyncResult.wait_ready.__get__(async_result)
        if async_result:
            return async_result
