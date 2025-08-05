"""Module: projudi.

Manage initialization and execution of various Projudi bot types within CrawJUD-Bots.
"""

from __future__ import annotations

import logging
import traceback
from typing import Callable, Union

from crawjud.bot.common.exceptions import StartError
from crawjud.bot.scripts.projudi.capa import Capa
from crawjud.bot.scripts.projudi.intimacoes import Intimacoes
from crawjud.bot.scripts.projudi.movimentacao import Movimentacao
from crawjud.bot.scripts.projudi.proc_parte import ProcParte as Proc_parte
from crawjud.bot.scripts.projudi.protocolo import Protocolo

ClassBots = Union[Capa, Intimacoes, Movimentacao, Proc_parte, Protocolo]
logger_ = logging.getLogger(__name__)


class Projudi:
    """Initialize and execute the specified Projudi bot type with detailed configuration.

    Reads parameters such as system, typebot, and display_name and launches the corresponding bot.
    """

    def __init__(self, *args: str | int, **kwargs: str | int) -> None:
        """Initialize the Projudi instance and start execution of the selected bot.

        Args:
            *args (tuple[str | int]): Additional positional arguments.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments (including system and typebot).

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
        """Retrieve the bot class corresponding to the chosen type.

        Returns:
            ClassBots: An instance of the selected bot type.

        Raises:
            AttributeError: If the specified bot type is not found.

        """
        bot_call: Callable[[], None] = globals().get(self.typebot_.capitalize())

        # rb = self.bots.get(self.typebot)
        if not bot_call:
            raise AttributeError("Robô não encontrado!!")

        return bot_call
