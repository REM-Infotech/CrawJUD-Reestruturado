"""Module for creating XLSX templates from list templates."""


class MakeModels:
    """Class to generate XLSX files based on a model and header lists."""

    def __init__(self, model_name: str, display_name: str) -> None:
        """Initialize a MakeModels instance.

        Args:
            model_name (str): The model or key identifier.
            display_name (str): The display name for the file.

        """
        self.model_name = model_name
        self.displayname = display_name
