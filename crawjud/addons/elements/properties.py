"""Update configuration properties module docstring to Google style.

This module manages configuration properties for web elements.
It defines the Configuracao class that encapsulates element property data.
"""


class Configuracao:
    """Initialize configuration for web element properties.

    This class handles element data retrieval as properties. If a property is not
    found, it raises an AttributeError.

    Attributes:
        element_data (dict): The dictionary containing element properties.

    """

    def __init__(self, dados: object) -> None:
        """Initialize instance with element data.

        Args:
            dados (object): Data containing element properties.

        """
        self.element_data = dados

    def __getattr__(self, name: str) -> str:
        """Retrieve a property value for a given element name.

        Args:
            name (str): Name of the element property.

        Returns:
            str: The property value.

        Raises:
            AttributeError: If the property for the given name is not found.

        """
        element = self.element_data.get(name)
        if not element:
            raise AttributeError(f"Elemento {name} não encontrado")

        return element
