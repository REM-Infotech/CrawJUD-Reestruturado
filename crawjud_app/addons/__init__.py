"""Módulo de Addons do celery app."""

import secrets
import string


def worker_name_generator(prefix: str = "worker") -> str:
    """Generate a unique worker name with specific format.

    Creates a worker name by combining a prefix with random uppercase letters and digits
    in the format: 'worker_XXXX_YYYY' where X are letters and Y are digits.

    Returns:
        str: A unique worker identifier in format 'worker_ABCD_1234'.

    Example:
        >>> worker_name_generator()
        'worker_KRTM_5289'

    """
    letters = "".join(secrets.choice(string.ascii_uppercase) for _ in range(4))
    digits = "".join(secrets.choice(string.digits) for _ in range(4))

    return f"{prefix}_{letters}_{digits}"
