"""Update PJE_AM module docstring to Google style.

This module provides an automation interface for the PJE-AM system.
"""

from crawjud_app.addons.elements.properties import Configuracao


class PJE_AM(Configuracao):  # noqa: N801
    """Configure PJE-AM operations and selectors.

    This class manages login, navigation, and other interactions with the PJE-AM system.

    Attributes:
        url_login (str): The login URL for PJE-AM.
        chk_login (str): URL to confirm a successful login.
        login_input (str): CSS selector for the username input.
        password_input (str): CSS selector for the password input.
        btn_entrar (str): CSS selector for the login button.
        url_pautas (str): URL for accessing the pautas page.
        url_busca (str): Placeholder URL for search operations.
        btn_busca (str): CSS selector for the search button.

    """

    url_login: str = "https://pje.trt11.jus.br/primeirograu/login.seam"
    chk_login: str = "https://pje.trt11.jus.br/pjekz/painel/usuario-externo"
    login_input: str = 'input[id="username"]'
    password_input: str = 'input[id="password"]'  # noqa: S105
    btn_entrar: str = 'button[id="btnEntrar"]'
    url_pautas: str = "https://pje.trt11.jus.br/consultaprocessual/pautas"
    url_busca: str = "url_de_busca_AC"
    btn_busca: str = "btn_busca_AC"
