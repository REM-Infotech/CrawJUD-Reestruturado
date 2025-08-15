class LoadFormError(Exception):
    """Exceção para erros durante o carregamento do formulário."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
