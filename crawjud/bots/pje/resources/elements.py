"""Defina constantes de elementos e URLs utilizados para automação no sistema PJE.

Este módulo fornece:
- URLs de login, consulta e busca do sistema PJE;
- Seletores de elementos para automação de login e busca.

"""

url_login: str = "https://pje.trt11.jus.br/primeirograu/login.seam"
chk_login: str = "https://pje.trt11.jus.br/pjekz/painel/usuario-externo"
login_input: str = 'input[id="username"]'
password_input: str = 'input[id="password"]'  # noqa: S105
btn_entrar: str = 'button[id="btnEntrar"]'
url_pautas: str = "https://pje.trt11.jus.br/consultaprocessual/pautas"
url_busca: str = "url_de_busca_AC"
btn_busca: str = "btn_busca_AC"
