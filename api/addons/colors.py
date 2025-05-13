"""Módulo de funcionalidade de cores."""

import secrets


def gerar_cor_base() -> tuple[int, int, int]:
    """Gera uma cor base."""
    r = secrets.randbelow(256)
    g = secrets.randbelow(256)
    b = secrets.randbelow(256)
    return r, g, b


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convensor RGB para Hexadecimal."""
    return f"#{r:02x}{g:02x}{b:02x}"


def escurecer_cor(r: int, g: int, b: int, fator: int = 0.85) -> tuple[int, int, int]:
    """Escurece a cor."""
    return int(r * fator), int(g * fator), int(b * fator)
