"""Initialize and manage the Caixa bot for the CrawJUD-Bots with docstrings up to standard.

Provide a class interface to run the Emissor bot, handle exceptions, and
configure logging. This file follows Google/PEP 257 docstring guidelines.
"""

import logging
import traceback
from collections.abc import Callable
from typing import Union

from crawjud.bots.caixa.emissor import Emissor
from crawjud.common.exceptions.bot import StartError

logger_ = logging.getLogger(__name__)
ClassBots = Union[Emissor]


class Caixa:
    """Set up and run the Emissor bot for deposit operations in the Caixa system effectively.

    Capture logging and system parameters, handle initialization errors,
    and pass arguments to the selected bot class.
    """

    def __init__(
        self,
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Initialize the Caixa bot and handle any startup exceptions thoroughly.

        Args:
            *args (str|int): Positional parameters for bot setup and environment.
            **kwargs (str|int): Contains relevant configuration and logging info.

        Raises:
            StartError: If an error occurs during the bot startup or initialization.

        """
        try:
            display_name = kwargs.get("display_name")
            system = kwargs.get("system")
            typebot = kwargs.get("typebot")
            logger = kwargs.get("logger", logger_)
            logger.info(
                "Starting bot %s with system %s and type %s",
                display_name,
                system,
                typebot,
            )

            self.typebot_ = typebot

            self.bot_call.initialize(*args, **kwargs).execution()

        except Exception as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
            self.logger.exception("".join(traceback.format_exception(e)))
            err = traceback.format_exc()
            logger.exception(err)
            raise StartError(traceback.format_exc()) from e

    @property
    def bot_call(self) -> ClassBots:
        """Retrieve the bot class reference dynamically based on the chosen type.

        Returns:
            ClassBots: Either the Emissor class or another specialized bot class.

        Raises:
            AttributeError: If the bot type does not exist in the current environment.

        """
        bot_call: Callable[[], None] = globals().get(self.typebot_.capitalize())

        if not bot_call:
            raise AttributeError("Robô não encontrado!!")

        return bot_call
