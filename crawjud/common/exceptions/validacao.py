"""Módulo para controle de exceptions de validações de valores."""


class ValidacaoStringError(ValueError):
    """Exception de erro de validação de string."""

    message: str
    exception: Exception

    def __init__(self, message: str, *args) -> None:
        """Inicializa exception de validação."""
        self.message = message
        super().__init__(*args)
        self.exception = self
