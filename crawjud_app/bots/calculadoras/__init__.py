"""Module: calculadoras.

This module initializes and manages the Calculadoras bot within the CrawJUD-Bots application.
"""

import logging
import traceback
from collections.abc import Callable
from typing import Union

from crawjud.common.exceptions.bot import StartError
from crawjud_app.bots.calculadoras.tjdft import Tjdft

__all__ = ["Tjdft"]
logger_ = logging.getLogger(__name__)
ClassBots = Union[Tjdft]


class Calculadoras:
    """calculadoras class.

    Initializes and executes the Calculadoras bot based on provided configurations.
    """

    def __init__(
        self,
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Initialize Bot instance.

        Sets up the bot and executes the bot module based on the system type.

        Args:
            *args (tuple[str | any]): Additional positional arguments.
            **kwargs (dict[str | any]): Additional keyword arguments.
            path_args (str): Path to the bot's arguments file.
            display_name (str): The display name for the bot.
            system (str): The system for the bot (e.g., projudi).
            typebot (str): The type of bot (e.g., capa).
            logger (logging.Logger, optional): The logger instance.

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
        """Bot property.

        Dynamically imports and returns an instance of the specified bot type.

        Returns:
            any: An instance of the specified bot.

        Raises:
            AttributeError: If the specified bot type is not found.

        """
        bot_call: Callable[[], None] = globals().get(self.typebot_.capitalize())

        if not bot_call:
            raise AttributeError("Robô não encontrado!!")

        return bot_call
