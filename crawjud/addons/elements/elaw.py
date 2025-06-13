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
    botao_andamento = 'button[id="tabViewProcesso:j_id_i1_4_1_3_ae:novoAndamentoPrimeiraBtn"]'
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
    tableprazos = 'tbody[id="tabViewProcesso:j_id_i1_4_1_3_d:dtAgendamentoResults_data"]'

    tipo_polo = "".join((
        'select[id="j_id_3k_1:j_id_3k_4_2_2_t_9_44_2:j_id_3k_4_2_2_t_9_44_3_1_',
        '2_2_1_1:fieldid_13755typeSelectField1CombosCombo_input"]',
    ))

    # CADASTRO
    botao_novo = 'button[id="btnNovo"]'
    css_label_area = 'div[id="comboArea"]'
    elemento = 'div[id="comboArea_panel"]'
    comboareasub_css = 'div[id="comboAreaSub"]'
    elemento_comboareasub = 'div[id="comboAreaSub_panel"]'
    css_button = 'button[id="btnContinuar"]'

    label_esfera = 'label[id="j_id_3k_1:j_id_3k_4_2_2_1_9_u_1:comboRito_label"]'

    css_esfera_judge = 'select[id="j_id_3k_1:j_id_3k_4_2_2_1_9_u_1:comboRito_input"]'
    combo_rito = 'div[id="j_id_3k_1:j_id_3k_4_2_2_1_9_u_1:comboRito_panel"]'
    estado_input = "select[id='j_id_3k_1:j_id_3k_4_2_2_1_9_u_1:comboEstadoVara_input']"
    comarca_input = "select[id='j_id_3k_1:j_id_3k_4_2_2_1_9_u_1:comboComarcaVara_input']"
    foro_input = "select[id='j_id_3k_1:j_id_3k_4_2_2_1_9_u_1:comboForoTribunal_input']"
    vara_input = "select[id='j_id_3k_1:j_id_3k_4_2_2_1_9_u_1:comboVara_input']"
    numero_processo = "input[id='j_id_3k_1:j_id_3k_4_2_2_2_9_f_2:txtNumeroMask']"
    empresa_input = "select[id='j_id_3k_1:comboClientProcessoParte_input']"
    tipo_empresa_input = "select[id='j_id_3k_1:j_id_3k_4_2_2_4_9_2_5_input']"
    tipo_parte_contraria_input = "select[id='j_id_3k_1:j_id_3k_4_2_2_5_9_9_1:j_id_3k_4_2_2_5_9_9_4_2_m_input']"
    css_table_tipo_doc = 'table[id="j_id_3k_1:j_id_3k_4_2_2_5_9_9_1:tipoDocumentoInput"]'
    css_campo_doc = 'input[id="j_id_3k_1:j_id_3k_4_2_2_5_9_9_1:cpfCnpjInput"]'
    css_search_button = 'button[id="j_id_3k_1:j_id_3k_4_2_2_5_9_9_1:j_id_3k_4_2_2_5_9_9_4_2_f"]'
    css_div_select_opt = "".join(
        (
            'div[id="j_id_3k_1:j_id_3k_4_2_2_9_9_44_2:j_id_3k_4',
            '_2_2_9_9_44_3_1_2_2_2_1:fieldid_9240pgTypeSelectField1CombosCombo"]',
        ),
    )
    select_field = "".join(
        (
            'div[id="j_id_3k_1:j_id_3k_4_2_2_9_9_44_2:j_id_3k_4_2_2_9_9_44',
            '_3_1_2_2_2_1:fieldid_9240pgTypeSelectField1CombosCombo_panel"]',
        ),
    )
    css_other_location = "".join(
        (
            'input[id="j_id_3k_1:j_id_3k_4_2_2_9_9_44_2:j_id_3k_4_2_2_9_9_44_3_1_2_2_2_1:',
            "j_id_3k_4_2_2_9_9_44_3_1_2_2_2_2_1_c:j_id_3k_4_2_2_9_9_44_3_1_2_2_2_2_1_f:0:j",
            '_id_3k_4_2_2_9_9_44_3_1_2_2_2_2_1_1f:fieldText"]',
        ),
    )
    comboProcessoTipo = 'div[id="j_id_3k_1:comboProcessoTipo"]'  # noqa: N815
    filtro_processo = 'input[id="j_id_3k_1:comboProcessoTipo_filter"]'
    css_data_distribuicao = 'input[id="j_id_3k_1:dataDistribuicao_input"]'
    css_adv_responsavel = 'input[id="j_id_3k_1:autoCompleteLawyer_input"]'
    css_div_select_Adv = 'div[id="j_id_3k_1:comboAdvogadoResponsavelProcesso"]'  # noqa: N815
    css_input_select_Adv = 'input[id="j_id_3k_1:comboAdvogadoResponsavelProcesso_filter"]'  # noqa: N815
    css_input_adv = 'input[id="j_id_3k_1:autoCompleteLawyerOutraParte_input"]'
    css_check_adv = "".join(
        (
            r"#j_id_3k_1\:autoCompleteLawyerOutraParte_panel > ul > li.ui-autocomplete-item.",
            "ui-autocomplete-list-item.ui-corner-all.ui-state-highlight",
        ),
    )
    css_valor_causa = 'input[id="j_id_3k_1:amountCase_input"]'
    escritrorio_externo = 'div[id="j_id_3k_1:comboEscritorio"]'
    combo_escritorio = 'div[id="j_id_3k_1:comboEscritorio_panel"]'
    contingencia = "select[id='j_id_3k_1:j_id_3k_4_2_2_s_9_n_1:processoContingenciaTipoCombo_input']"
    contigencia_panel = 'div[id="j_id_3k_1:j_id_3k_4_2_2_s_9_n_1:processoContingenciaTipoCombo_panel"]'
    css_add_adv = 'button[id="j_id_3k_1:lawyerOutraParteNovoButtom"]'
    xpath = '//*[@id="j_id_3k_1:lawyerOutraParteNovoButtom_dlg"]/div[2]/iframe'
    css_naoinfomadoc = "".join(
        (
            "#cpfCnpjNoGrid-lawyerOutraParte > tbody > tr > td:nth-child(1) > div >",
            " div.ui-radiobutton-box.ui-widget.ui-corner-all.ui-state-default",
        ),
    )
    botao_continuar = 'button[id="j_id_1e"]'
    css_input_nomeadv = 'input[id="j_id_1h:j_id_1k_2_5"]'
    salvarcss = 'button[id="lawyerOutraParteButtom"]'
    parte_contraria = 'button[id="j_id_3k_1:j_id_3k_4_2_2_5_9_9_1:parteContrariaMainGridBtnNovo"]'
    xpath_iframe = '//*[@id="j_id_3k_1:j_id_3k_4_2_2_5_9_9_1:parteContrariaMainGridBtnNovo_dlg"]/div[2]/iframe'
    cpf_cnpj = 'table[id="registrationCpfCnpjChooseGrid-"]'
    botao_radio_widget = 'div[class="ui-radiobutton ui-widget"]'
    tipo_cpf_cnpj = 'table[id="cpfCnpjTipoNoGrid-"]'
    tipo_cpf = 'input[id="j_id_19"]'
    tipo_cnpj = 'input[id="j_id_1a"]'
    botao_parte_contraria = 'button[id="j_id_1d"]'
    css_name_parte = 'input[id="j_id_1k"]'
    css_save_button = 'button[id="parteContrariaButtom"]'
    css_salvar_proc = 'button[id="btnSalvarOpen"]'
    css_t_found = 'table[id="j_id_3k_1:j_id_3k_4_2_2_5_9_9_1:parteContrariaSearchDisplayGrid"]'
    div_messageerro_css = 'div[id="messages"]'

    # COMPLEMENTAR
    botao_editar_complementar = 'button[id="dtProcessoResults:0:btnEditar"]'
    css_input_uc = "".join(
        (
            'textarea[id="j_id_3k_1:j_id_3k_4_2_2_6_9_44_2:j_id_3k_4_2_2_6_9_4',
            '4_3_1_2_2_1_1:j_id_3k_4_2_2_6_9_44_3_1_2_2_1_13"]',
        ),
    )
    element_select = "".join(
        (
            'select[id="j_id_3k_1:j_id_3k_4_2_2_a_9_44_2:j_id_3k_4_2_2_a_9_44_3',
            '_1_2_2_1_1:fieldid_9241typeSelectField1CombosCombo_input"]',
        ),
    )
    css_data_citacao = 'input[id="j_id_3k_1:dataRecebimento_input"]'
    fase_input = 'select[id="j_id_3k_1:processoFaseCombo_input"]'
    provimento_input = "".join(
        (
            'select[id="j_id_3k_1:j_id_3k_4_2_2_g_9_44_2:j_id_3k_4_2_2',
            '_g_9_44_3_1_2_2_1_1:fieldid_8401typeSelectField1CombosCombo_input"]',
        ),
    )
    fato_gerador_input = "".join(
        (
            'select[id="j_id_3k_1:j_id_3k_4_2_2_m_9_44_2:j_id_3k_4_2_2_m_',
            '9_44_3_1_2_2_1_1:fieldid_9239typeSelectField1CombosCombo_input"]',
        ),
    )
    input_descobjeto_css = "".join(
        (
            'textarea[id="j_id_3k_1:j_id_3k_4_2_2_l_9_44_2:j_id_3k_4_2_2_',
            'l_9_44_3_1_2_2_1_1:j_id_3k_4_2_2_l_9_44_3_1_2_2_1_13"]',
        ),
    )
    objeto_input = "".join(
        (
            'select[id="j_id_3k_1:j_id_3k_4_2_2_n_9_44_2:j_id_3k_4_2_2_n_9_44',
            '_3_1_2_2_1_1:fieldid_8405typeSelectField1CombosCombo_input"]',
        ),
    )

    # DOWNLOAD
    anexosbutton_css = 'a[href="#tabViewProcesso:files"]'
    css_table_doc = 'tbody[id="tabViewProcesso:gedEFileDataTable:GedEFileViewDt_data"]'
    botao_baixar = 'button[title="Baixar"]'

    # PAGAMENTOS
    valor_pagamento = 'a[href="#tabViewProcesso:processoValorPagamento"]'
    botao_novo_pagamento = 'button[id="tabViewProcesso:pvp-pgBotoesValoresPagamentoBtnNovo"]'
    css_typeitens = 'div[id="processoValorPagamentoEditForm:pvp:processoValorPagamentoTipoCombo"]'
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
    css_div_condenacao_type = (
        'div[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_3_1_9_28_1_1_1:pvpEFBtypeSelectField1CombosCombo"]'
    )
    valor_sentenca = (
        'li[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_3_1_9_28_1_1_1:pvpEFBtypeSelectField1CombosCombo_3"]'
    )
    valor_acordao = (
        'li[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_3_1_9_28_1_1_1:pvpEFBtypeSelectField1CombosCombo_1"]'
    )
    css_desc_pgto = 'textarea[id="processoValorPagamentoEditForm:pvp:processoValorPagamentoDescription"]'
    css_data = 'input[id="processoValorPagamentoEditForm:pvp:processoValorPagamentoVencData_input"]'
    css_inputfavorecido = 'input[id="processoValorPagamentoEditForm:pvp:processoValorFavorecido_input"]'
    resultado_favorecido = 'li[class="ui-autocomplete-item ui-autocomplete-list-item ui-corner-all ui-state-highlight"]'
    valor_processo = (
        'div[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_8_1_9_28_1_2_1:pvpEFSpgTypeSelectField1CombosCombo"]'
    )
    boleto = (
        'li[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_8_1_9_28_1_2_1:pvpEFSpgTypeSelectField1CombosCombo_1"]'
    )
    css_cod_bars = "".join(
        (
            'input[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_8_1_9_28_1_2_1:j_id_30_1_i_8_1_9_28_1_2_c_2:j_id_30_',
            '1_i_8_1_9_28_1_2_c_5:0:j_id_30_1_i_8_1_9_28_1_2_c_16:j_id_30_1_i_8_1_9_28_1_2_c_1w"]',
        ),
    )
    css_centro_custas = 'input[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_9_1_9_28_1_1_1:pvpEFBfieldText"]'
    css_div_conta_debito = (
        'div[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_a_1_9_28_1_1_1:pvpEFBtypeSelectField1CombosCombo"]'
    )
    valor_guia = 'input[id="processoValorPagamentoEditForm:pvp:valorField_input"]'
    css_gru = 'li[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_2_1_9_g_1:eFileTipoCombo_35"]'
    editar_pagamentofile = 'div[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_2_1_9_g_1:gedEFileDataTable"]'
    css_tipocusta = (
        'div[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_4_1_9_28_1_1_1:pvpEFBtypeSelectField1CombosCombo"]'
    )
    css_listcusta = (
        'ul[id="processoValorPagamentoEditForm:pvp:j_id_30_1_i_4_1_9_28_1_1_1:pvpEFBtypeSelectField1CombosCombo_items"]'
    )
    custas_civis = 'li[data-label="CUSTAS JUDICIAIS CIVEIS"]'
    custas_monitorias = 'li[data-label="CUSTAS JUDICIAIS - MONITORIAS"]'
    botao_salvar_pagamento = 'button[id="processoValorPagamentoEditForm:btnSalvarProcessoValorPagamento"]'

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
    css_btn_edit = 'button[id="tabViewProcesso:j_id_i1_c_1_6_2:processoValoresEditarBtn"]'
    ver_valores = 'a[href="#tabViewProcesso:valores"]'

    # table_valores_css = 'tbody[id="tabViewProcesso:j_id_i1_c_1_5_2:j_id_i1_c_1_5_70:viewValoresCustomeDt_data"]'
    table_valores_css = 'tbody[id="tabViewProcesso:j_id_i1_c_1_6_2:j_id_i1_c_1_6_4x:viewValoresCustomeDt_data"]'
    value_provcss = 'div[id*="viewValoresCustomeDt:0"]'
    div_tipo_obj_css = 'div[id="selectManyObjetoAdicionarList"]'
    itens_obj_div_css = 'div[id="selectManyObjetoAdicionarList_panel"]'
    checkbox = 'div[class="ui-chkbox ui-widget"]'
    botao_adicionar = 'button[id="adicionarObjetoBtn"]'
    botao_editar = 'button[id*="editarFasePedidoBtn"]'
    css_val_inpt = 'input[id*="processoAmountObjetoDt:0:amountValor_input"][type="text"]'
    css_risk = "".join((
        "/html/body/div[1]/div[4]/div[1]/div/div[2]/form[2]/table/tbody/tr[2]/td/div/div/table",
        "[2]/tbody/tr[2]/td/span/div/div/div/div[1]/div/table/tbody/tr[1]/td[7]/div",
    ))
    processo_objt = 'ul[id="j_id_2z:j_id_32_2e:processoAmountObjetoDt:0:j_id_32_2j_4_1_6_3_k_2_2_1_items"]'
    botao_salvar_id = 'button[id="salvarBtn"]'
    data_correcaoCss = 'input[id="j_id_2z:j_id_32_2e:processoAmountObjetoDt:dataBaseCorrecaoTodosField_input"]'  # noqa: N815
    data_jurosCss = 'input[id="j_id_2z:j_id_32_2e:processoAmountObjetoDt:dataBaseJurosTodosField_input"]'  # noqa: N815
    texto_motivo = 'textarea[id="j_id_2z:j_id_32_2e:j_id_32_2j_7:j_id_32_2j_i"]'

    type_risk_label = 'span[id="j_id_2z:provisaoTipoPedidoCombo_label"]'
    type_risk_select = 'select[id="j_id_2z:provisaoTipoPedidoCombo_input"]'

    tb_advs_resp = 'tbody[id="j_id_3k_1:lawyerOwnersDataTable_data"]'
    tr_not_adv = "tr.ui-datatable-empty-message"

    dict_campos_validar = {
        "estado": 'select[id="j_id_3k_1:j_id_3k_4_2_2_1_9_u_1:comboEstadoVara_input"] > option:selected',
        "comarca": 'select[id="j_id_3k_1:j_id_3k_4_2_2_1_9_u_1:comboComarcaVara_input"] > option:selected',
        "foro": 'select[id="j_id_3k_1:j_id_3k_4_2_2_1_9_u_1:comboForoTribunal_input"] > option:selected',
        "vara": 'select[id="j_id_3k_1:j_id_3k_4_2_2_1_9_u_1:comboVara_input"] > option:selected',
        "fase": 'select[id="j_id_3k_1:processoFaseCombo_input"] > option:selected',
        "tipo_empresa": 'select[id="j_id_3k_1:j_id_3k_4_2_2_4_9_2_5_input"] > option:selected',
        "escritorio": 'select[id="j_id_3k_1:comboEscritorio_input"] > option:selected',
        "advogado_interno": "".join(
            ['select[id="j_id_3k_1:comboAdvoga', 'doResponsavelProcesso_input"] > option:selected'],
        ),
        "divisao": "".join(
            [
                'select[id="j_id_3k_1:j_id_3k_4_2_2_a_9_44_2:j_id_3k_4_2_2_',
                'a_9_44_3_1_2_2_1_1:fieldid_9241typeSelectField1CombosCombo_input"] > option:selected',
            ],
        ),
        "classificacao": "".join(
            ['select[id="j_id_3k_1:j_id_3k_4_2_2_p_9_16_1:', 'processoClassificacaoCombo_input"] > option:selected'],
        ),
        "toi_criado": "".join(
            [
                'select[id="j_id_3k_1:j_id_3k_4_2_2_v_9_44_2:j_id_3k_4_2_2_v_',
                '9_44_3_1_2_2_2_1:fieldid_9243pgTypeSelectField1CombosCombo_input"] > option:selected',
            ],
        ),
        "nota_tecnica": "".join(
            [
                'select[id="j_id_3k_1:j_id_3k_4_2_2_w_9_44_2:j_id_3k_4_2_2_w_9_44_3_1_2',
                '_2_1_1:fieldid_9244typeSelectField1CombosCombo_input"] > option:selected',
            ],
        ),
        "liminar": "".join(
            [
                'select[id="j_id_3k_1:j_id_3k_4_2_2_y_9_44_2:j_id_3k_4_2_2_y_9',
                '_44_3_1_2_2_1_1:fieldid_9830typeSelectField1CombosCombo_input"] > option:selected',
            ],
        ),
        "provimento": "".join(
            [
                'select[id="j_id_3k_1:j_id_3k_4_2_2_g_9_44_2:j_id_3k_4_2_2_g_9_',
                '44_3_1_2_2_1_1:fieldid_8401typeSelectField1CombosCombo_input"] > option:selected',
            ],
        ),
        "fato_gerador": "".join(
            [
                'select[id="j_id_3k_1:j_id_3k_4_2_2_m_9_44_2:j_id_3k_4_2_2_m_9_44_3_1_2',
                '_2_1_1:fieldid_9239typeSelectField1CombosCombo_input"] > option:selected',
            ],
        ),
        "acao": "".join(
            [
                'select[id="j_id_3k_1:j_id_3k_4_2_2_n_9_44_2:j_id_3k_4_2_2_n_9_44_3_1',
                '_2_2_1_1:fieldid_8405typeSelectField1CombosCombo_input"] > option:selected',
            ],
        ),
        "tipo_entrada": "".join(
            [
                'select[id="j_id_3k_1:j_id_3k_4_2_2_e_9_44_2:j_id_3k_4_2_2_e_',
                '9_44_3_1_2_2_1_1:fieldid_9242typeSelectField1CombosCombo_input"] > option:selected',
            ],
        ),
        "objeto": "".join(
            [
                'select[id="j_id_3k_1:j_id_3k_4_2_2_n_9_44_2:j_id_3k_4_2_2_n_9_44_3_1',
                '_2_2_1_1:fieldid_8405typeSelectField1CombosCombo_input"] > option:selected',
            ],
        ),
    }
