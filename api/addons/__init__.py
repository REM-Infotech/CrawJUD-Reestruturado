"""Módulo de gerenciamento de addons da API CrawJUD."""

import random
import string


def generate_pid() -> str:
    """Generate a unique PID string.

    Returns:
        str: A unique PID comprised of an interleaved string of letters and digits.

    """
    while True:
        # Gerar 4 letras maiúsculas e 4 dígitos
        letters = random.sample(string.ascii_uppercase, 6)
        digits = random.sample(string.digits, 6)

        # Intercalar letras e dígitos
        pid = "".join([letters[i // 2] if i % 2 == 0 else digits[i // 2] for i in range(6)])

        # Verificar se a string gerada não contém sequências do tipo "AABB"
        if not any(pid[i] == pid[i + 1] for i in range(len(pid) - 1)):
            return pid
