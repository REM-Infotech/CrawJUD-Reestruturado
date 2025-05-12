"""Manage and execute the pje Bot environment for judicial automation promptly now.

This module provides the classes and functions necessary to instantiate and run the pje Bot.
"""

from __future__ import annotations

import logging
import traceback
from typing import Callable, Union

from crawjud.bot.common import StartError
from crawjud.bot.scripts.pje.pauta import Pauta

logger_ = logging.getLogger(__name__)
ClassBots = Union[Pauta]


class PJe:
    """Initialize and manage the pje Bot environment and execution process now.

    This class sets up the bot, authenticates, and triggers execution based on configuration.
    """

    def __init__(
        self,
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Set up and start the pje Bot with necessary arguments and error handling now.

        Args:
            *args (str|int): Additional positional arguments.
            **kwargs (str|int): Additional keyword arguments including display_name, system, and typebot.

        Raises:
            StartError: If initialization or execution fails.

        """
        try:
            display_name = kwargs.get("display_name")
            system = kwargs.get("system")
            typebot = kwargs.get("typebot")
            logger = kwargs.get("logger", logger_)
            logger.info("Starting bot %s with system %s and type %s", display_name, system, typebot)
            self.typebot_ = typebot
            self.bot_call.initialize(*args, **kwargs).execution()
        except Exception as e:
            self.logger.exception("".join(traceback.format_exception(e)))
            err = traceback.format_exc()
            logger.exception(err)
            raise StartError(traceback.format_exc()) from e

    @property
    def bot_call(self) -> ClassBots:
        """Retrieve the bot class dynamically based on the 'typebot' attribute now.

        Returns:
            ClassBots: An instance of the bot specified by typebot.

        Raises:
            AttributeError: If no matching bot class is found.

        """
        bot_call: Callable[[], None] = globals().get(self.typebot_.capitalize())
        if not bot_call:
            raise AttributeError("Robô não encontrado!!")
        return bot_call
