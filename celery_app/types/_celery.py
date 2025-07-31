from typing import AnyStr, Generic, Optional, ParamSpec, Protocol, TypeVar

from celery.canvas import Signature as __Signature
from celery.result import AsyncResult as __AsyncResult

P = ParamSpec("P")
R = TypeVar("R")
TClassBot = TypeVar("TClassBot", bound=object)
TBotSpec = ParamSpec("TBotSpec", bound=AnyStr)

class_set = set()


class AsyncResult(Protocol, __AsyncResult):
    """Celery AsyncResult.

    Class that wraps the result of a task execution.

    Used to check the status of a task, retrieve its result,
    and perform other operations related to task results.

    See Also:
        :ref:`guide-results` for the complete guide.

    """

    def get(self, timeout: Optional[float] = None) -> Generic[R]:
        """Get the result of the task execution."""


class Signature(Protocol, __Signature):
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

    def apply_async(self, *args: AnyStr, **kwargs: AnyStr) -> AsyncResult:
        """Apply this task asynchronously.

        Arguments:
            args (Tuple): Partial args to be prepended to the existing args.
            kwargs (Dict): Partial kwargs to be merged with existing kwargs.
            options (Dict): Partial options to be merged
                with existing options.

        Returns:
            ~@AsyncResult: promise of future evaluation.


        See Also:
            :meth:`~@Task.apply_async` and the :ref:`guide-calling` guide.

        """
