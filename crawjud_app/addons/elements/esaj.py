"""Update ESAJ_AM module docstring to Google style.

This module configures selectors for automating ESAJ operations.
"""

from crawjud_app.addons.elements.properties import Configuracao


class ESAJ_AM(Configuracao):  # noqa: N801
    """Configure ESAJ automation selectors and URLs.

    This class defines CSS selectors and URLs used for ESAJ system automation,
    including login, search functionality, and process details access.

    Attributes:
        css_val_doc_custas_ini (str): Selector for document value element.
        url_preparo_esaj (str): URL to prepare ESAJ calculations.
        url_preparo_projudi (str): URL to prepare PROJUDI calculations.
        get_page_custas_pagas (str): Selector for the custas pagas button.
        consultaproc_grau1 (str): URL for first-degree process consultation.
        consultaproc_grau2 (str): URL for second-degree process consultation.
        url_login (str): URL for the login page.
        url_login_cert (str): URL for the certificate-based login page.
        campo_username (str): CSS selector for the username input field.
        campo_passwd (str): CSS selector for the password input field.
        btn_entrar (str): CSS selector for the login button.
        chk_login (str): CSS selector to verify successful login.
        url_busca (str): URL for search functionality.
        btn_busca (str): CSS selector for the search button.
        acao (str): CSS selector for the action span.
        vara_processual (str): CSS selector for the process court span.
        area_selecao (str): ID for the main parts table.
        id_valor (str): ID for the action value.
        data_processual (str): ID for the distribution date and time.
        classe_processual (str): XPath selector for the process class.
        sumary_header_1 (str): CSS selector for the first summary header.
        rows_sumary_ (str): CSS selector for summary rows.
        sumary_header_2 (str): CSS selector for the second summary header.
        selecao_processual (str): XPath selector for process selection.
        orgao_processual (str): XPath selector for the judicial body of the process.
        status_processual (str): CSS selector for the process status.
        relator (str): XPath selector for the process reporter.
        nome_foro (str): CSS selector for the forum name input.
        tree_selection (str): CSS selector for the class selection tree input.
        civil_selector (str): CSS selector for the civil area selector.
        valor_acao (str): CSS selector for the action value input.
        botao_avancar (str): CSS selector for the advance button.
        interessado (str): CSS selector for the interested party input.
        check (str): CSS selector for checkboxes.
        botao_avancar_dois (str): CSS selector for the second advance button.
        boleto (str): CSS selector for the boleto link.
        mensagem_retorno (str): CSS selector for the return message.
        movimentacoes (str): CSS selector for all movements table body.
        ultimas_movimentacoes (str): CSS selector for the latest movements table.
        editar_classificacao (str): CSS selector for the classification edit button.
        selecionar_classe (str): CSS selector for the intermediate class selection container.
        toggle (str): CSS selector for the toggle button.
        input_classe (str): CSS selector for the intermediate class input.
        select_categoria (str): CSS selector for the category selection container.
        input_categoria (str): CSS selector for the category input.
        selecionar_grupo (str): XPath selector for selecting a group.
        input_documento (str): CSS selector for the document input file.
        documento (str): XPath selector for the document button.
        processo_view (str): CSS selector for the process view container.
        nome (str): CSS selector for the party name span.
        botao_incluir_peticao (str): CSS selector for the petition inclusion button.
        botao_incluir_partecontraria (str): CSS selector for the opposing party inclusion button.
        parte_view (str): CSS selector for the party view container.
        botao_protocolar (str): XPath selector for the protocol button.
        botao_confirmar (str): CSS selector for the confirm button in popover content.
        botao_recibo (str): CSS selector for the receipt consultation button.

    """

    css_val_doc_custas_ini = "".join(
        (
            "body > table:nth-child(4) > tbody > tr > td > table:nth-child(10)",
            " > tbody > tr:nth-child(5) > td:nth-child(3) > strong",
        ),
    )

    url_preparo_esaj = "".join(
        (
            "https://consultasaj.tjam.jus.br/ccpweb/iniciarCalculoDeCustas.do?cd",
            "TipoCusta=9&flTipoCusta=1&&cdServicoCalculoCusta=690019",
        ),
    )

    url_preparo_projudi = "".join(
        (
            "https://consultasaj.tjam.jus.br/ccpweb/iniciarCalculoDeCustas.do?",
            "cdTipoCusta=21&flTipoCusta=5&&cdServicoCalculoCusta=690007",
        ),
    )

    get_page_custas_pagas = (
        'button[class="btn btn-secondary btn-space linkConsultaSG"]'
    )

    consultaproc_grau1 = "https://consultasaj.tjam.jus.br/cpopg/open.do"
    consultaproc_grau2 = "https://consultasaj.tjam.jus.br/cposgcr/open.do"
    url_login = "https://consultasaj.tjam.jus.br/sajcas/login"
    url_login_cert = "https://consultasaj.tjam.jus.br/sajcas/login#aba-certificado"

    campo_username = 'input[id="usernameForm"]'
    campo_passwd = 'input[id="passwordForm"]'  # noqa: S105 # nosec: B105
    btn_entrar = 'input[name="pbEntrar"]'
    chk_login = "#esajConteudoHome > table:nth-child(4) > tbody > tr > td.esajCelulaDescricaoServicos"

    url_busca = ""
    btn_busca = ""

    acao = 'span[id="classeProcesso"]'
    vara_processual = 'span[id="varaProcesso"]'
    area_selecao = "tablePartesPrincipais"
    id_valor = "valorAcaoProcesso"
    data_processual = "dataHoraDistribuicaoProcesso"
    classe_processual = '//*[@id="classeProcesso"]/span'

    sumary_header_1 = 'div[class="unj-entity-header__summary"] > div[class="container"] > div[class="row"]'
    rows_sumary_ = 'div[class^="col-"]'

    sumary_header_2 = "div#maisDetalhes > div.row"

    selecao_processual = '//*[@id="secaoProcesso"]/span'
    orgao_processual = '//*[@id="orgaoJulgadorProcesso"]'
    status_processual = 'span[id="situacaoProcesso"]'
    relator = '//*[@id="relatorProcesso"]'
    numproc = "unj-larger-1"
    statusproc = "unj-tag"

    nameitemsumary = "unj-label"
    valueitemsumary = 'div[class="lh-1-1 line-clamp__2"]'

    value2_itemsumary = {
        "CLASSE": "#classeProcesso",
        "DISTRIBUIÇÃO": "#dataHoraDistribuicaoProcesso",
        "CONTROLE": "#numeroControleProcesso",
        "VALOR_DA_AÇÃO": "#valorAcaoProcesso",
        "JUIZ": "#juizProcesso",
        "OUTROS_ASSUNTOS": 'div[class="line-clamp__2"]',
    }

    nome_foro = 'input[name="entity.nmForo"]'
    tree_selection = 'input[name="classesTreeSelection.text"]'
    civil_selector = 'input[name="entity.flArea"][value="1"]'
    valor_acao = 'input[name="entity.vlAcao"]'
    botao_avancar = 'input[name="pbAvancar"]'
    interessado = 'input[name="entity.nmInteressado"]'
    check = 'input[class="checkg0r0"]'
    botao_avancar_dois = 'input[value="Avançar"]'
    boleto = 'a[id="linkBoleto"]'
    mensagem_retorno = 'td[id="mensagemRetorno"]'
    movimentacoes = 'tbody[id="tabelaTodasMovimentacoes"]'
    ultimas_movimentacoes = "tabelaUltimasMovimentacoes"
    editar_classificacao = "botaoEditarClassificacao"
    selecionar_classe = (
        'div.ui-select-container[input-id="selectClasseIntermediaria"]'
    )
    toggle = "span.btn.btn-default.form-control.ui-select-toggle"
    input_classe = "input#selectClasseIntermediaria"
    select_categoria = 'div.ui-select-container[input-id="selectCategoria"]'
    input_categoria = "input#selectCategoria"
    selecionar_grupo = './/li[@class="ui-select-choices-group"]/ul/li/span'
    input_documento = "#botaoAdicionarDocumento > input[type=file]"
    documento = '//nav[@class="document-data__nav"]/div/ul/li[5]/button[2]'
    processo_view = 'div[ui-view="parteProcessoView"]'
    nome = 'span[ng-bind="parte.nome"]'
    botao_incluir_peticao = (
        'button[ng-click="incluirParteDoProcessoPeticaoDiversa(parte)"]'
    )
    botao_incluir_partecontraria = (
        'button[ng-click="incluirParteDoProcessoNoPoloContrario(parte)"]'
    )
    parte_view = 'div[ui-view="parteView"]'
    botao_protocolar = '//*[@id="botaoProtocolar"]'
    botao_confirmar = "div.popover-content button.confirm-button"
    botao_recibo = 'button[ng-click="consultarReciboPeticao(peticao)"]'

    table_moves = (
        './/tr[contains(@class, "fundoClaro") or contains(@class, "fundoEscuro")]'
    )
