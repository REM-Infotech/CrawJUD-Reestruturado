"""Update PROJUDI_AM module docstring to Google style.

This module provides selectors for the PROJUDI_AM system.
"""

from crawjud.addons.elements.properties import Configuracao


class PROJUDI_AM(Configuracao):  # noqa: N801
    """Configure PROJUDI_AM selectors and properties.

    This class inherits from Configuracao and defines the CSS selectors and URL
    properties for automating the PROJUDI_AM system.

    Class Attributes:
        url_login (str): Login URL.
        campo_username (str): Selector for username field.
        campo_passwd (str): Selector for password field.
        btn_entrar (str): Selector for the login button.
        chk_login (str): Selector to verify successful login.
        url_busca (str): URL for search functionality.
        url_mesa_adv (str): URL for the lawyer's desk.
        btn_busca (str): Selector for the search button.
        btn_aba_intimacoes (str): Selector for the notifications tab.
        select_page_size_intimacoes (str): Selector for the page size dropdown.
        tab_intimacoes_script (str): Script to select the notifications tab.
        btn_partes (str): Selector for the parties tab.
        btn_infogeral (str): Selector for the general information tab.
        includecontent_capa (str): Selector for the cover content.
        infoproc (str): Selector for the process information table.


    """

    url_login = (
        "https://projudi.tjam.jus.br/projudi/usuario/logon.do?actionType=inicio"
    )
    campo_username = "#login"
    campo_passwd = "#senha"  # noqa: S105 # nosec: B105
    btn_entrar = "#btEntrar"
    chk_login = 'iframe[name="userMainFrame"]'

    url_busca = "".join(
        (
            "https://projudi.tjam.jus.br/projudi/processo/",
            "buscaProcessosQualquerInstancia.do?actionType=pesquisar",
        ),
    )

    url_mesa_adv = "".join((
        "https://projudi.tjam.jus.br/projudi/usuario/",
        "mesaAdvogado.do?actionType=listaInicio&pageNumber=1",
    ))

    btn_busca = ""
    btn_aba_intimacoes = 'li[id="tabItemprefix1"]'
    select_page_size_intimacoes = 'select[name="pagerConfigPageSize"]'

    tab_intimacoes_script = "".join((
        "setTab('/projudi/usuario/mesaAdvogado.do?actionType=",
        "listaInicio&pageNumber=1', 'tabIntimacoes', 'prefix', 1, true)",
    ))

    btn_partes = "#tabItemprefix2"
    btn_infogeral = "#tabItemprefix0"
    includecontent_capa = "includeContent"

    infoproc = 'table[id="informacoesProcessuais"]'
    assunto_proc = 'a[class="definitionAssuntoPrincipal"]'
    resulttable = "resultTable"

    select_page_size = 'select[name="pagerConfigPageSize"]'
    data_inicio = 'input[id="dataInicialMovimentacaoFiltro"]'
    data_fim = 'input[id="dataFinalMovimentacaoFiltro"]'
    filtro = 'input[id="editButton"]'
    expand_btn_projudi = 'a[href="javascript://nop/"]'
    table_moves = './/tr[contains(@class, "odd") or contains(@class, "even")][not(@style="display:none")]'

    primeira_instform1 = "#informacoesProcessuais"
    primeira_instform2 = "#tabprefix0 > #container > #includeContent > fieldset"

    segunda_instform = "#recursoForm > fieldset"

    exception_arrow = './/a[@class="arrowNextOn"]'

    input_radio = "input[type='radio']"

    tipo_documento = 'input[name="descricaoTipoDocumento"]'
    descricao_documento = "div#ajaxAuto_descricaoTipoDocumento > ul > li:nth-child(1)"
    includeContent = 'input#editButton[value="Adicionar"]'  # noqa: N815
    border = 'iframe[frameborder="0"][id]'
    conteudo = '//*[@id="conteudo"]'
    botao_assinar = 'input[name="assinarButton"]'
    botao_confirmar = 'input#closeButton[value="Confirmar Inclusão"]'
    botao_concluir = 'input#editButton[value="Concluir Movimento"]'
    botao_deletar = 'input[type="button"][name="deleteButton"]'
    css_containerprogressbar = 'div[id="divProgressBarContainerAssinado"]'
    css_divprogressbar = 'div[id="divProgressBarAssinado"]'
