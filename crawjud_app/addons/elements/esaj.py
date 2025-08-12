"""Fornece seletores CSS e URLs para automação de processos judiciais no ESAJ.

Este módulo contém:
- Seletores CSS e XPath para elementos de interface do ESAJ.
- URLs de acesso para funcionalidades específicas do sistema.
- Dicionários e variáveis para facilitar a navegação e extração de dados.

"""

css_val_doc_custas_ini = (
    "body > table:nth-child(4) > tbody > tr > td > table:nth-child(10)"
    " > tbody > tr:nth-child(5) > td:nth-child(3) > strong"
)

url_preparo_esaj = (
    "https://consultasaj.tjam.jus.br/ccpweb/iniciarCalculoDeCustas.do?cd"
    "TipoCusta=9&flTipoCusta=1&&cdServicoCalculoCusta=690019"
)

url_preparo_projudi = (
    "https://consultasaj.tjam.jus.br/ccpweb/iniciarCalculoDeCustas.do?"
    "cdTipoCusta=21&flTipoCusta=5&&cdServicoCalculoCusta=690007"
)

get_page_custas_pagas = 'button[class="btn btn-secondary btn-space linkConsultaSG"]'

consultaproc_grau1 = "https://consultasaj.tjam.jus.br/cpopg/open.do"
consultaproc_grau2 = "https://consultasaj.tjam.jus.br/cposgcr/open.do"
url_login = "https://consultasaj.tjam.jus.br/sajcas/login"
url_login_cert = "https://consultasaj.tjam.jus.br/sajcas/login#aba-certificado"

campo_username = 'input[id="usernameForm"]'
campo_2_login = 'input[id="passwordForm"]'  # nosec: B105
btn_entrar = 'input[name="pbEntrar"]'
chk_login = (
    "#esajConteudoHome > table:nth-child(4) > tbody > tr > "
    "td.esajCelulaDescricaoServicos"
)

url_busca = ""
btn_busca = ""

acao = 'span[id="classeProcesso"]'
vara_processual = 'span[id="varaProcesso"]'
area_selecao = "tablePartesPrincipais"
id_valor = "valorAcaoProcesso"
data_processual = "dataHoraDistribuicaoProcesso"
classe_processual = '//*[@id="classeProcesso"]/span'

sumary_header_1 = (
    'div[class="unj-entity-header__summary"] > '
    'div[class="container"] > '
    'div[class="row"]'
)
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
value2_itemsumary: dict[str, str] = {
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
selecionar_classe = 'div.ui-select-container[input-id="selectClasseIntermediaria"]'
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
