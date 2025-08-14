"""Exception classes for mail-related errors."""

from crawjud.common.exceptions import BaseExceptionCeleryAppError


class MailError(BaseExceptionCeleryAppError):
    """Exception class for mail-related errors."""

    def __init__(self, **kwargs: str) -> None:
        """Excepts mail error."""
        super().__init__(**kwargs)
