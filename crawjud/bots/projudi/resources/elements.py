"""Define elementos e seletores utilizados para automação no sistema Projudi.

Este módulo contém variáveis com URLs, seletores CSS e XPath para facilitar
operações automatizadas de login, busca de processos, navegação e manipulação
de documentos no Projudi.

"""

url_login = "https://projudi.tjam.jus.br/projudi/usuario/logon.do?actionType=inicio"
campo_username = "#login"
campo_2_login = "#senha"  # nosec: B105
btn_entrar = "#btEntrar"
chk_login = 'iframe[name="userMainFrame"]'

url_busca = (
    "https://projudi.tjam.jus.br/projudi/processo/"
    "buscaProcessosQualquerInstancia.do?actionType=pesquisar"
)

url_mesa_adv = "https://projudi.tjam.jus.br/projudi/usuario/mesaAdvogado.do?actionType=listaInicio&pageNumber=1"

btn_busca = ""
btn_aba_intimacoes = 'li[id="tabItemprefix1"]'
select_page_size_intimacoes = 'select[name="pagerConfigPageSize"]'

tab_intimacoes_script = (
    "setTab("
    "'/projudi/usuario/mesaAdvogado.do?actionType=listaInicio&pageNumber=1', "
    "'tabIntimacoes', 'prefix', 1, true)"
)

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
table_moves = (
    './/tr[contains(@class, "odd") or contains(@class, "even")]'
    '[not(@style="display:none")]'
)

primeira_instform1 = "#informacoesProcessuais"
primeira_instform2 = "#tabprefix0 > #container > #includeContent > fieldset"

segunda_instform = "#recursoForm > fieldset"

exception_arrow = './/a[@class="arrowNextOn"]'

input_radio = "input[type='radio']"

tipo_documento = 'input[name="descricaoTipoDocumento"]'
descricao_documento = "div#ajaxAuto_descricaoTipoDocumento > ul > li:nth-child(1)"
include_content = 'input#editButton[value="Adicionar"]'
border = 'iframe[frameborder="0"][id]'
conteudo = '//*[@id="conteudo"]'
botao_assinar = 'input[name="assinarButton"]'
botao_confirmar = 'input#closeButton[value="Confirmar Inclusão"]'
botao_concluir = 'input#editButton[value="Concluir Movimento"]'
botao_deletar = 'input[type="button"][name="deleteButton"]'
css_containerprogressbar = 'div[id="divProgressBarContainerAssinado"]'
css_divprogressbar = 'div[id="divProgressBarAssinado"]'
