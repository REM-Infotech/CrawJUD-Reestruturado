"""Exception classes for mail-related errors."""

from celery_app.exceptions import BaseExceptionCeleryAppError


class MailError(BaseExceptionCeleryAppError):
    """Exception class for mail-related errors."""

    def __init__(self, **kwargs: str) -> None:
        """Excepts mail error."""
        super().__init__(**kwargs)
