# noqa: D100
async def formata_url_pje(regiao: str, type_format: str = "login") -> str:  # noqa: D102, D103
    formats = {
        "login": f"https://pje.trt{regiao}.jus.br/primeirograu/login.seam",
        "validate_login": f"https://pje.trt{regiao}.jus.br/pjekz/",
        "search": f"https://pje.trt{regiao}.jus.br/consultaprocessual/",
    }

    return formats[type_format]
