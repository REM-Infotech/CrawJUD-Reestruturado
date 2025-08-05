"""Update ELAW_AME module docstring to Google style.

This module provides selectors for automating ELAW operations.
"""

from crawjud.addons.elements.properties import Configuracao


class ELAW_AME(Configuracao):  # noqa: N801
    """Configure ELAW automation selectors and operations.

    This class stores selectors and URLs required for ELAW automation tasks,
    such as login and search operations.

    """

    # Login Elaw
    url_login = ""
    campo_username = ""
    campo_passwd = ""  # nosec: B105
    btn_entrar = ""
    chk_login = ""

    # Busca Elaw
    url_busca = ""
    btn_busca = ""

    # ANDAMENTOS
    botao_andamento = (
        'button[id="tabViewProcesso:j_id_i1_4_1_3_ae:novoAndamentoPrimeiraBtn"]'
    )
    input_data = 'input[id="j_id_2n:j_id_2r_2_9_input"]'
    inpt_ocorrencia = 'textarea[id="j_id_2n:txtOcorrenciaAndamento"]'
    inpt_obs = 'textarea[id="j_id_2n:txtObsAndamento"]'
    botao_salvar_andamento = "btnSalvarAndamentoProcesso"

    # Robô Lançar Audiências
    switch_pautaandamento = 'a[href="#tabViewProcesso:agendamentosAndamentos"]'
    btn_novaaudiencia = 'button[id="tabViewProcesso:novaAudienciaBtn"]'
    selectortipoaudiencia = 'select[id="j_id_2l:comboTipoAudiencia_input"]'
    DataAudiencia = 'input[id="j_id_2l:j_id_2p_2_8_8:dataAudienciaField_input"]'
    btn_salvar = 'button[id="btnSalvarNovaAudiencia"]'
    tableprazos = (
        'tbody[id="tabViewProcesso:j_id_i1_4_1_3_d:dtAgendamentoResults_data"]'
    )

    tipo_polo = "//*[contains(@id, 'fieldid_13755typeSelectField1CombosCombo_input')]"

    # CADASTRO
    input_localidade = "//input[contains(@id, 'fieldid_13351fieldText')]"
    botao_novo = 'button[id="btnNovo"]'
    css_label_area = '//select[contains(@id, "comboArea_input")]'
    comboareasub_css = '//select[contains(@id, "comboAreaSub_input")]'
    css_button = 'button[id="btnContinuar"]'
    xpath_checkadvinterno = "//*[contains(@id, 'j_id_3y_1:autoCompleteLawyer_item')]"
    label_esfera = 'span[id="j_id_3y_1:j_id_3y_4_2_2_1_9_u_1:comboRito_label"]'

    css_esfera_judge = '//select[contains(@id, "comboRito_input")]'
    estado_input = "//select[contains(@id, 'comboEstadoVara_input')]"
    comarca_input = "//select[contains(@id, 'comboComarcaVara_input')]"
    foro_input = "//select[contains(@id, 'comboForoTribunal_input')]"
    vara_input = "//select[contains(@id, 'comboVara_input')]"
    empresa_input = "//select[contains(@id, 'comboClientProcessoParte_input')]"
    tipo_empresa_input = '//select[contains(@id, "j_id_3y_4_2_2_4_9_2_5_input")]'
    tipo_parte_contraria_input = (
        "//select[contains(@id, 'j_id_3y_4_2_2_5_9_9_4_2_m_input')]"
    )
    select_tipo_doc = "//select[contains(@id, 'tipoDocumentoInput_input')]"
    combo_rito = '//select[contains(@id, "comboRito_input")]'

    numero_processo = "input[id='j_id_3y_1:j_id_3y_4_2_2_2_9_f_2:txtNumeroMask']"
    css_campo_doc = 'input[id="j_id_3y_1:j_id_3y_4_2_2_5_9_9_1:cpfCnpjInput"]'
    css_search_button = (
        'button[id="j_id_3y_1:j_id_3y_4_2_2_5_9_9_1:j_id_3y_4_2_2_5_9_9_4_2_f"]'
    )

    select_uf_proc = (
        "//select[contains(@id, 'fieldid_9240pgTypeSelectField1CombosCombo_input')]"
    )
    select_field = "".join(
        (
            'div[id="j_id_3y_1:j_id_3y_4_2_2_9_9_44_2:j_id_3y_4_2_2_9_9_44',
            '_3_1_2_2_2_1:fieldid_9240pgTypeSelectField1CombosCombo_panel"]',
        ),
    )
    css_other_location = "".join(
        (
            'input[id="j_id_3y_1:j_id_3y_4_2_2_9_9_46_2:j_id_3y_4_2_2_9_9_46_3_1_2_2_2_1:',
            "j_id_3y_4_2_2_9_9_46_3_1_2_2_2_2_1_c:j_id_3y_4_2_2_9_9_46_3_1_2_2_2_2_1_f:0:j",
            '_id_3y_4_2_2_9_9_46_3_1_2_2_2_2_1_1g:fieldText"]',
        ),
    )
    comboProcessoTipo = 'div[id="j_id_3y_1:comboProcessoTipo"]'  # noqa: N815
    filtro_processo = 'input[id="j_id_3y_1:comboProcessoTipo_filter"]'
    css_data_distribuicao = 'input[id="j_id_3y_1:dataDistribuicao_input"]'
    adv_responsavel = "//input[contains(@id, 'autoCompleteLawyer_input')]"
    select_advogado_responsavel = (
        "//select[contains(@id, 'comboAdvogadoResponsavelProcesso_input')]"  # noqa: N815
    )
    css_input_select_adv = (
        'input[id="j_id_3y_1:comboAdvogadoResponsavelProcesso_filter"]'  # noqa: N815
    )
    css_input_adv = 'input[id="j_id_3y_1:autoCompleteLawyerOutraParte_input"]'
    css_check_adv = (
        '//*[contains(@id, "j_id_3y_1:autoCompleteLawyerOutraParte_item")]'
    )
    valor_causa = "//input[contains(@id, 'amountCase_input')]"
    escritrorio_externo = '//div[contains(@id, "comboEscritorio")]'
    select_escritorio = "//select[contains(@id, 'comboEscritorio_input')]"
    contingencia = "//*[contains(@id, 'processoContingenciaTipoCombo_input')]"
    contigencia_panel = 'div[id="j_id_3y_1:j_id_3y_4_2_2_s_9_n_1:processoContingenciaTipoCombo_panel"]'
    css_add_adv = 'button[id="j_id_3y_1:lawyerOutraParteNovoButtom"]'
    iframe_cadastro_parte_contraria = (
        'div[id*=":parteContrariaMainGridBtnNovo_dlg"] > div > iframe'
    )
    iframe_cadastro_parte_close_dnv = (
        'div[id*=":parteContrariaMainGridBtnNovo_dlg"] > div > a'
    )

    iframe_cadastro_advogado_close_dnv = (
        'div[id="j_id_3y_1:lawyerOutraParteNovoButtom_dlg"] > div > a'
    )
    iframe_cadastro_advogado_contra = (
        'div[id="j_id_3y_1:lawyerOutraParteNovoButtom_dlg"] > div > iframe'
    )
    btn_novo_advogado_contra = '//button[contains(@id, "lawyerOutraParteNovoButtom")]'
    css_naoinfomadoc = "".join(
        (
            "#cpfCnpjNoGrid-lawyerOutraParte > tbody > tr > td:nth-child(1) > div >",
            " div.ui-radiobutton-box.ui-widget.ui-corner-all.ui-state-default",
        ),
    )
    botao_continuar = 'button[id="j_id_1e"]'
    css_input_nomeadv = 'input[id="j_id_1h:j_id_1k_2_5"]'
    salvarcss = 'button[id="lawyerOutraParteButtom"]'
    parte_contraria = "//button[contains(@id, 'parteContrariaMainGridBtnNovo')]"

    cpf_cnpj = 'table[id="registrationCpfCnpjChooseGrid-"]'
    botao_radio_widget = 'div[class="ui-radiobutton ui-widget"]'
    tipo_cpf_cnpj = "//select[contains(@id, 'cpfCnpjTipoNoGrid-_input')]"
    tipo_cpf = 'input[id="j_id_1a"]'
    tipo_cnpj = 'input[id="j_id_1b"]'
    botao_parte_contraria = 'button[id="j_id_1e"]'
    css_name_parte = 'input[id="j_id_1k"]'
    css_save_button = 'button[id="parteContrariaButtom"]'
    css_salvar_proc = 'button[id="btnSalvarOpen"]'
    css_t_found = (
        'table[id="j_id_3y_1:j_id_3y_4_2_2_5_9_9_1:parteContrariaSearchDisplayGrid"]'
    )
    div_messageerro_css = 'div[id="messages"]'

    # COMPLEMENTAR
    botao_editar_complementar = 'button[id="dtProcessoResults:0:btnEditar"]'
    css_input_uc = "//textarea[contains(@id, 'fieldid_9236fieldTextarea')]"
    divisao_select = (
        "//*[contains(@id, 'fieldid_9241typeSelectField1CombosCombo_input')]"
    )
    data_citacao = "//input[contains(@id, 'dataRecebimento_input')]"
    bairro_input = "//input[contains(@id, 'fieldid_9237fieldText')]"
    fase_input = '//select[contains(@id, "processoFaseCombo_input")]'
    provimento_input = (
        '//select[contains(@id, "fieldid_8401typeSelectField1CombosCombo_input")]'
    )
    fato_gerador_input = (
        '//select[contains(@id, "fieldid_9239typeSelectField1CombosCombo_input")]'
    )

    input_descobjeto = "//*[contains(@id, 'fieldid_9844fieldTextarea')]"
    objeto_input = (
        "//select[contains(@id, 'fieldid_8405typeSelectField1CombosCombo_input')]"
    )

    # DOWNLOAD
    anexosbutton_css = 'a[href="#tabViewProcesso:files"]'
    css_table_doc = (
        'tbody[id="tabViewProcesso:gedEFileDataTable:GedEFileViewDt_data"]'
    )
    botao_baixar = 'button[title="Baixar"]'

    # PAGAMENTOS
    valor_pagamento = 'a[href="#tabViewProcesso:processoValorPagamento"]'
    botao_novo_pagamento = (
        'button[id="tabViewProcesso:pvp-pgBotoesValoresPagamentoBtnNovo"]'
    )
    css_typeitens = (
        'div[id="processoValorPagamentoEditForm:pvp:processoValorPagamentoTipoCombo"]'
    )
    listitens_css = 'ul[id="processoValorPagamentoEditForm:pvp:processoValorPagamentoTipoCombo_items"]'

    # Input informa valor de pagamento
    css_element = "".join((
        'input[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_1_1_9_1g_1:',
        'processoValorRateioAmountAllDt:0:j_id_30_1_i_1_1_9_1g_2_2_q_input"]',
    ))

    # Div do tipo de documento
    type_doc_css = 'div[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_2_1_9_g_1:eFileTipoCombo"]'
    list_type_doc_css = 'ul[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_2_1_9_g_1:eFileTipoCombo_items"]'
    editar_pagamento = 'input[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_2_1_9_g_1:uploadGedEFile_input"]'
    css_div_condenacao_type = 'div[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_3_1_9_28_1_1_1:pvpEFBtypeSelectField1CombosCombo"]'
    valor_sentenca = 'li[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_3_1_9_28_1_1_1:pvpEFBtypeSelectField1CombosCombo_3"]'
    valor_acordao = 'li[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_3_1_9_28_1_1_1:pvpEFBtypeSelectField1CombosCombo_1"]'
    css_desc_pgto = 'textarea[id="processoValorPagamentoEditForm:pvp:processoValorPagamentoDescription"]'
    css_data = 'input[id="processoValorPagamentoEditForm:pvp:processoValorPagamentoVencData_input"]'
    css_inputfavorecido = (
        'input[id="processoValorPagamentoEditForm:pvp:processoValorFavorecido_input"]'
    )
    resultado_favorecido = 'li[class="ui-autocomplete-item ui-autocomplete-list-item ui-corner-all ui-state-highlight"]'
    valor_processo = 'div[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_8_1_9_28_1_2_1:pvpEFSpgTypeSelectField1CombosCombo"]'
    boleto = 'li[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_8_1_9_28_1_2_1:pvpEFSpgTypeSelectField1CombosCombo_1"]'
    css_cod_bars = "".join(
        (
            'input[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_8_1_9_28_1_2_1:j_id_30_1_i_8_1_9_28_1_2_c_2:j_id_30_',
            '1_i_8_1_9_28_1_2_c_5:0:j_id_30_1_i_8_1_9_28_1_2_c_16:j_id_30_1_i_8_1_9_28_1_2_c_1w"]',
        ),
    )
    css_centro_custas = 'input[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_9_1_9_28_1_1_1:pvpEFBfieldText"]'
    css_div_conta_debito = 'div[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_a_1_9_28_1_1_1:pvpEFBtypeSelectField1CombosCombo"]'
    valor_guia = 'input[id="processoValorPagamentoEditForm:pvp:valorField_input"]'
    css_gru = 'li[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_2_1_9_g_1:eFileTipoCombo_35"]'
    editar_pagamentofile = 'div[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_2_1_9_g_1:gedEFileDataTable"]'
    css_tipocusta = 'div[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_4_1_9_28_1_1_1:pvpEFBtypeSelectField1CombosCombo"]'
    css_listcusta = 'ul[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_4_1_9_28_1_1_1:pvpEFBtypeSelectField1CombosCombo_items"]'
    custas_civis = 'li[data-label="CUSTAS JUDICIAIS CIVEIS"]'
    custas_monitorias = 'li[data-label="CUSTAS JUDICIAIS - MONITORIAS"]'
    botao_salvar_pagamento = (
        'button[id="processoValorPagamentoEditForm:btnSalvarProcessoValorPagamento"]'
    )

    # Validar resultados Solicitação de Pagamento
    valor_resultado = 'div[id="tabViewProcesso:pvp-dtProcessoValorResults"]'
    botao_ver = 'button[title="Ver"]'
    valor = 'iframe[title="Valor"]'
    visualizar_tipo_custas = r"#processoValorPagamentoView\:j_id_p_1_2_1_2_1 > table > tbody > tr:nth-child(5)"
    visualizar_cod_barras = "".join(
        (
            r"#processoValorPagamentoView\:j_id_p_1_2_1_2_7_8_4_23_1\:j_id_p_1_2_1_",
            r"2_7_8_4_23_2_1_2_1\:j_id_p_1_2_1_2_7_8_4_23_2_1_2_2_1_3 > table > tbody > tr:nth-child(3)",
        ),
    )
    visualizar_tipoCondenacao = r"#processoValorPagamentoView\:j_id_p_1_2_1_2_1 > table > tbody > tr:nth-child(4)"  # noqa: N815

    # PROVISIONAMENTO
    css_btn_edit = (
        'button[id="tabViewProcesso:j_id_i1_c_1_6_2:processoValoresEditarBtn"]'
    )
    ver_valores = 'a[href="#tabViewProcesso:valores"]'

    # table_valores_css = 'tbody[id="tabViewProcesso:j_id_i1_c_1_5_2:j_id_i1_c_1_5_70:viewValoresCustomeDt_data"]'
    table_valores_css = 'tbody[id="tabViewProcesso:j_id_i1_c_1_6_2:j_id_i1_c_1_6_4x:viewValoresCustomeDt_data"]'
    value_provcss = 'div[id*="viewValoresCustomeDt:0"]'
    div_tipo_obj_css = 'div[id="selectManyObjetoAdicionarList"]'
    itens_obj_div_css = 'div[id="selectManyObjetoAdicionarList_panel"]'
    checkbox = 'div[class="ui-chkbox ui-widget"]'
    botao_adicionar = 'button[id="adicionarObjetoBtn"]'
    botao_editar = 'button[id*="editarFasePedidoBtn"]'
    css_val_inpt = (
        'input[id*="processoAmountObjetoDt:0:amountValor_input"][type="text"]'
    )
    css_risk = "".join((
        "/html/body/div[1]/div[4]/div[1]/div/div[2]/form[2]/table/tbody/tr[2]/td/div/div/table[2]",
        "/tbody/tr[2]/td/span/div/div/div/div[1]/div/table/tbody/tr[1]/td[7]/div",
    ))
    processo_objt = 'ul[id="j_id_2z:j_id_32_2e:processoAmountObjetoDt:0:j_id_32_2j_4_1_6_3_k_2_2_1_items"]'
    botao_salvar_id = 'button[id="salvarBtn"]'
    data_correcaoCss = 'input[id="j_id_2z:j_id_32_2e:processoAmountObjetoDt:dataBaseCorrecaoTodosField_input"]'  # noqa: N815
    data_jurosCss = 'input[id="j_id_2z:j_id_32_2e:processoAmountObjetoDt:dataBaseJurosTodosField_input"]'  # noqa: N815
    texto_motivo = 'textarea[id="j_id_2z:j_id_32_2e:j_id_32_2j_7:j_id_32_2j_i"]'

    type_risk_label = 'span[id="j_id_2z:provisaoTipoPedidoCombo_label"]'
    type_risk_select = 'select[id="j_id_2z:provisaoTipoPedidoCombo_input"]'

    tabela_advogados_resp = 'tbody[id*="lawyerOwnersDataTable_data"]'
    tr_not_adv = "tr.ui-datatable-empty-message"

    dict_campos_validar = {
        "estado": 'select[id*="comboEstadoVara_input"] > option:selected',
        "comarca": 'select[id*="comboComarcaVara_input"] > option:selected',
        "foro": 'select[id*="comboForoTribunal_input"] > option:selected',
        "vara": 'select[id*="comboVara_input"] > option:selected',
        "fase": 'select[id*="processoFaseCombo_input"] > option:selected',
        "tipo_empresa": 'select[id*="j_id_3y_4_2_2_4_9_2_5_input"] > option:selected',
        "escritorio": 'select[id*="comboEscritorio_input"] > option:selected',
        "advogado_interno": 'select[id*="comboAdvogadoResponsavelProcesso_input"] > option:selected',
        "divisao": 'select[id*="fieldid_9241typeSelectField1CombosCombo_input"] > option:selected',
        "classificacao": 'select[id*="processoClassificacaoCombo_input"] > option:selected',
        "toi_criado": 'select[id=*"fieldid_9243pgTypeSelectField1CombosCombo_input"] > option:selected',
        "nota_tecnica": 'select[id=*"fieldid_9244typeSelectField1CombosCombo_input"] > option:selected',
        "liminar": 'select[id=*"fieldid_9830typeSelectField1CombosCombo_input"] > option:selected',
        "provimento": 'select[id=*"fieldid_8401typeSelectField1CombosCombo_input"] > option:selected',
        "fato_gerador": 'select[id*="fieldid_9239typeSelectField1CombosCombo_input"] > option:selected',
        "acao": 'select[id*="fieldid_8405typeSelectField1CombosCombo_input"] > option:selected',
        "tipo_entrada": 'select[id*="fieldid_9242typeSelectField1CombosCombo_input"] > option:selected',
        "objeto": 'select[id=*"fieldid_8405typeSelectField1CombosCombo_input"] > option:selected',
    }
