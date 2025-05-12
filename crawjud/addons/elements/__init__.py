"""Module for ElementsBot.

Configure and retrieve an elements bot instance based on system attributes.

Classes:
    ElementsBot: A class that configures and retrieves an elements bot instance.

Methods:
    __init__: Initializes the ElementsBot instance.
    Config: Configures the elements_bot attribute by dynamically importing a module based on the system and state_or_client attributes.
    bot_elements: Retrieves the elements bot instance.

Attributes:
    elements_bot: Stores the elements bot instance.

"""  # noqa: E501

from __future__ import annotations

from importlib import import_module
from typing import Self

from crawjud.addons.elements.elaw import ELAW_AME
from crawjud.addons.elements.esaj import ESAJ_AM
from crawjud.addons.elements.pje import PJE_AM
from crawjud.addons.elements.projudi import PROJUDI_AM


class ElementsBot:
    """Configure and retrieve elements bot instance.

    Inherit from CrawJUD and dynamically set the elements bot based on system
    and state_or_client attributes.

    Attributes:
        elements_bot (Optional[Union[ELAW_AME, ESAJ_AM, PJE_AM, PROJUDI_AM]):
            The current elements bot instance.

    """

    elements_bot = None

    def __init__(self) -> None:
        """Initialize the ElementsBot instance.

        Call the parent initialization if required.
        """

    def config(self) -> Self:
        """Configure the elements_bot attribute.

        Dynamically import the module based on `system` and `state_or_client`,
        and assign the corresponding class to elements_bot.

        Returns:
            Self: The configured ElementsBot instance.

        """
        if self.elements_bot is None:
            self.elements_bot = getattr(
                import_module(f".{self.system.lower()}", __package__),
                f"{self.system.upper()}_{self.state_or_client.upper()}",
            )
        return self

    @property
    def bot_elements(self) -> ELAW_AME | ESAJ_AM | PJE_AM | PROJUDI_AM:
        """Retrieve the configured elements bot instance.

        Returns:
            Union[ELAW_AME, ESAJ_AM, PJE_AM, PROJUDI_AM]: The active elements bot.

        """
        return self.elements_bot
