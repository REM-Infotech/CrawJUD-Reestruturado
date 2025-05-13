"""Módulo de Addons do SocketIO Server."""

import re
from platform import node


def check_allowed_origin(origin: str = "https://google.com") -> bool:
    """Check if the origin is allowed based on predefined patterns.

    Args:
        origin (str, optional): The origin to check. Defaults to "https://google.com".

    Returns:
        bool: True if origin is allowed, False otherwise.

    """
    allowed_origins = [
        r"http\:\/\/127\.0\.0\.1:*\d*"
        r"https:\/\/.*\.reminfotech\.net\.br",
        r"http:\/\/localhost*",
        r"https:\/\/.*\.nicholas\.dev\.br",
        r"https:\/\/.*\.robotz\.dev",
        r"https:\/\/.*\.rhsolutions\.info",
        r"https:\/\/.*\.rhsolut\.com\.br",
    ]
    if not origin:
        origin = f"https://{node()}"

    for orig in allowed_origins:
        pattern = orig
        matchs = re.match(pattern, origin)
        if matchs:
            return True

    return False
