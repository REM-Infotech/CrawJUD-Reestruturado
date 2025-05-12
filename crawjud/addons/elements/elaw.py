"""Update ELAW_AME module docstring to Google style.

This module provides selectors for automating ELAW operations.
"""

from crawjud.addons.elements.properties import Configuracao


class ELAW_AME(Configuracao):  # noqa: N801
    """Configure ELAW automation selectors and operations.

    This class stores selectors and URLs required for ELAW automation tasks,
    such as login and search operations.

    Attributes:
        url_login (str): URL for Elaw login.
        campo_username (str): Selector for the username input.
        campo_passwd (str): Selector for the password input.
        btn_entrar (str): Selector for the login button.
        chk_login (str): Selector to check for successful login.
        url_busca (str): URL for search functionality.
        btn_busca (str): Selector for the search button.
        botao_andamento (str): Selector for the 'Andamento' button.
        input_data (str): Selector for the date input field.
        inpt_ocorrencia (str): Selector for the occurrence textarea.
        inpt_obs (str): Selector for the observation textarea.
        botao_salvar_andamento (str): Selector for the save andamento button.
        switch_pautaandamento (str): Selector to switch pauta andamento.
        btn_novaaudiencia (str): Selector for the new audiência button.
        selectortipoaudiencia (str): Selector for the tipo audiência selector.
        DataAudiencia (str): Selector for the data audiência input.
        btn_salvar (str): Selector for the save button.
        tableprazos (str): Selector for the prazos table.
        tipo_polo (str): Selector for the tipo polo selector.
        botao_novo (str): Selector for the new button.
        css_label_area (str): Selector for the area label.
        elemento (str): Selector for the area element.
        comboareasub_css (str): Selector for the combo area sub.
        elemento_comboareasub (str): Selector for the combo area sub element.
        css_button (str): Selector for the continue button.
        label_esfera (str): Selector for the esfera label.
        css_esfera_judge (str): Selector for the esfera judge selector.
        combo_rito (str): Selector for the rito combo.
        estado_input (str): Selector for the estado input.
        comarca_input (str): Selector for the comarca input.
        foro_input (str): Selector for the foro input.
        vara_input (str): Selector for the vara input.
        numero_processo (str): Selector for the numero processo input.
        empresa_input (str): Selector for the empresa input.
        tipo_empresa_input (str): Selector for the tipo empresa input.
        tipo_parte_contraria_input (str): Selector for the tipo parte contraria input.
        css_table_tipo_doc (str): Selector for the tipo documento table.
        css_campo_doc (str): Selector for the documento campo.
        css_search_button (str): Selector for the search button.
        css_div_select_opt (str): Selector for the select options div.
        select_field (str): Selector for the select field.
        css_other_location (str): Selector for the other location input.
        comboProcessoTipo (str): Selector for the processo tipo combo.
        filtro_processo (str): Selector for the processo filtro input.
        css_data_distribuicao (str): Selector for the data distribuição input.
        css_adv_responsavel (str): Selector for the advogado responsável input.
        css_div_select_Adv (str): Selector for the advogado select div.
        css_input_select_Adv (str): Selector for the advogado select input.
        css_input_adv (str): Selector for the advogado input.
        css_check_adv (str): Selector for the advogado checkbox.
        css_valor_causa (str): Selector for the valor causa input.
        escritrorio_externo (str): Selector for the escritório externo.
        combo_escritorio (str): Selector for the combo escritório.
        contingencia (str): Selector for the contingencia select.
        contigencia_panel (str): Selector for the contingencia panel.
        css_add_adv (str): Selector for the add advogado button.
        xpath (str): Selector for the iframe.
        css_naoinfomadoc (str): Selector for the naoinfomadoc.
        botao_continuar (str): Selector for the continuar button.
        css_input_nomeadv (str): Selector for the nome advogado input.
        salvarcss (str): Selector for the salvar button.
        parte_contraria (str): Selector for the parte contraria button.
        xpath_iframe (str): Selector for the parte contraria iframe.
        cpf_cnpj (str): Selector for the CPF/CNPJ table.
        botao_radio_widget (str): Selector for the radio widget.
        tipo_cpf_cnpj (str): Selector for the tipo CPF/CNPJ table.
        tipo_cpf (str): Selector for the tipo CPF input.
        tipo_cnpj (str): Selector for the tipo CNPJ input.
        botao_parte_contraria (str): Selector for the parte contraria button.
        css_name_parte (str): Selector for the nome parte input.
        css_save_button (str): Selector for the save button.
        css_salvar_proc (str): Selector for the salvar processo button.
        css_t_found (str): Selector for the t found table.
        div_messageerro_css (str): Selector for the error message div.
        botao_editar_complementar (str): Selector for the editar complementar button.
        css_input_uc (str): Selector for the input UC textarea.
        element_select (str): Selector for the element select.
        css_data_citacao (str): Selector for the data citação input.
        fase_input (str): Selector for the fase input.
        provimento_input (str): Selector for the provimento input.
        fato_gerador_input (str): Selector for the fato gerador input.
        input_descobjeto_css (str): Selector for the objeto description textarea.
        objeto_input (str): Selector for the objeto input.
        anexosbutton_css (str): Selector for the anexos button.
        css_table_doc (str): Selector for the documents table.
        botao_baixar (str): Selector for the baixar button.
        valor_pagamento (str): Selector for the valor pagamento.
        botao_novo_pagamento (str): Selector for the novo pagamento button.
        css_typeitens (str): Selector for the type itens.
        listitens_css (str): Selector for the list itens.
        css_element (str): Selector for the element input.
        type_doc_css (str): Selector for the tipo documento.
        list_type_doc_css (str): Selector for the list tipo documento.
        editar_pagamento (str): Selector for the editar pagamento input.
        css_div_condenacao_type (str): Selector for the condenacao type div.
        valor_sentenca (str): Selector for the valor sentenca.
        valor_acordao (str): Selector for the valor acórdão.
        css_desc_pgto (str): Selector for the description pagamento textarea.
        css_data (str): Selector for the pagamento data input.
        css_inputfavorecido (str): Selector for the favorecido input.
        resultado_favorecido (str): Selector for the favorecido result.
        valor_processo (str): Selector for the valor processo.
        boleto (str): Selector for the boleto.
        css_cod_bars (str): Selector for the código de barras input.
        css_centro_custas (str): Selector for the centro custas input.
        css_div_conta_debito (str): Selector for the conta débito div.
        valor_guia (str): Selector for the valor guia input.
        css_gru (str): Selector for the GRU.
        editar_pagamentofile (str): Selector for the editar pagamento file.
        css_tipocusta (str): Selector for the tipo custas.
        css_listcusta (str): Selector for the list custas.
        custas_civis (str): Selector for as custas civis.
        custas_monitorias (str): Selector for as custas monitorias.
        botao_salvar_pagamento (str): Selector for the salvar pagamento button.
        valor_resultado (str): Selector for the valor resultado.
        botao_ver (str): Selector for the ver button.
        valor (str): Selector for the valor iframe.
        visualizar_tipo_custas (str): Selector for visualizar tipo custas.
        visualizar_cod_barras (str): Selector for visualizar código de barras.
        visualizar_tipoCondenacao (str): Selector for visualizar tipo condenação.
        css_btn_edit (str): Selector for the editar button.
        ver_valores (str): Selector for ver valores.
        table_valores_css (str): Selector for the valores table.
        value_provcss (str): Selector for the valor provisão.
        div_tipo_obj_css (str): Selector for the tipo objeto div.
        itens_obj_div_css (str): Selector for the itens objeto div.
        checkbox (str): Selector for the checkbox.
        botao_adicionar (str): Selector for the adicionar botão.
        botao_editar (str): Selector for the editar botão.
        css_val_inpt (str): Selector for the valor input.
        css_risk (str): Selector for the risco div.
        processo_objt (str): Selector for o processo objeto.
        botao_salvar_id (str): Selector para salvar ID botão.
        daata_correcaoCss (str): Selector para data correção.
        data_jurosCss (str): Selector para data juros.
        texto_motivo (str): Selector para texto motivo.
        type_risk_label (str): Selector para o label de risco.
        type_risk_select (str): Selector para o select de risco.
        tb_advs_resp (str): Selector para a tabela de advogados responsáveis.
        tr_not_adv (str): Selector para a mensagem de tabela vazia.

        dict_campos_validar (dict): Dictionary mapping field names to their selectors.

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
    botao_andamento = 'button[id="tabViewProcesso:j_id_i3_4_1_3_ae:novoAndamentoPrimeiraBtn"]'
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
    tableprazos = 'tbody[id="tabViewProcesso:j_id_i3_4_1_3_d:dtAgendamentoResults_data"]'

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
    css_element = "".join((
        'input[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_1_1_9_1f_1:proces',
        'soValorRateioAmountAllDt:0:j_id_2m_1_i_1_1_9_1f_2_2_q_input"]',
    ))
    type_doc_css = 'div[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_2_1_9_g_1:eFileTipoCombo"]'
    list_type_doc_css = 'ul[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_2_1_9_g_1:eFileTipoCombo_items"]'
    editar_pagamento = 'input[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_2_1_9_g_1:uploadGedEFile_input"]'
    css_div_condenacao_type = (
        'div[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_3_1_9_26_1_1_1:pvpEFBtypeSelectField1CombosCombo"]'
    )
    valor_sentenca = (
        'li[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_3_1_9_26_1_1_1:pvpEFBtypeSelectField1CombosCombo_3"]'
    )
    valor_acordao = (
        'li[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_3_1_9_26_1_1_1:pvpEFBtypeSelectField1CombosCombo_1"]'
    )
    css_desc_pgto = 'textarea[id="processoValorPagamentoEditForm:pvp:processoValorPagamentoDescription"]'
    css_data = 'input[id="processoValorPagamentoEditForm:pvp:processoValorPagamentoVencData_input"]'
    css_inputfavorecido = 'input[id="processoValorPagamentoEditForm:pvp:processoValorFavorecido_input"]'
    resultado_favorecido = 'li[class="ui-autocomplete-item ui-autocomplete-list-item ui-corner-all ui-state-highlight"]'
    valor_processo = (
        'div[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_8_1_9_26_1_2_1:pvpEFSpgTypeSelectField1CombosCombo"]'
    )
    boleto = (
        'li[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_8_1_9_26_1_2_1:pvpEFSpgTypeSelectField1CombosCombo_1"]'
    )
    css_cod_bars = "".join(
        (
            'input[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_8_1_9_26_1_2_1:',
            "j_id_2m_1_i_8_1_9_26_1_2_c_2:j_id_2m_1_i_8_1_9_26_1_2_c_5:0:",
            'j_id_2m_1_i_8_1_9_26_1_2_c_15:j_id_2m_1_i_8_1_9_26_1_2_c_1v"]',
        ),
    )
    css_centro_custas = 'input[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_9_1_9_26_1_1_1:pvpEFBfieldText"]'
    css_div_conta_debito = (
        'div[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_a_1_9_26_1_1_1:pvpEFBtypeSelectField1CombosCombo"]'
    )
    valor_guia = 'input[id="processoValorPagamentoEditForm:pvp:valorField_input"]'
    css_gru = 'li[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_2_1_9_g_1:eFileTipoCombo_35"]'
    editar_pagamentofile = 'div[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_2_1_9_g_1:gedEFileDataTable"]'
    css_tipocusta = (
        'div[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_4_1_9_26_1_1_1:pvpEFBtypeSelectField1CombosCombo"]'
    )
    css_listcusta = (
        'ul[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_4_1_9_26_1_1_1:pvpEFBtypeSelectField1CombosCombo_items"]'
    )
    custas_civis = 'li[data-label="CUSTAS JUDICIAIS CIVEIS"]'
    custas_monitorias = 'li[data-label="CUSTAS JUDICIAIS - MONITORIAS"]'
    botao_salvar_pagamento = 'button[id="processoValorPagamentoEditForm:btnSalvarProcessoValorPagamento"]'
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
    css_btn_edit = 'button[id="tabViewProcesso:j_id_i3_c_1_5_2:processoValoresEditarBtn"]'
    ver_valores = 'a[href="#tabViewProcesso:valores"]'
    table_valores_css = 'tbody[id="tabViewProcesso:j_id_i3_c_1_5_2:j_id_i3_c_1_5_70:viewValoresCustomeDt_data"]'
    value_provcss = "".join(
        (
            'div[id="tabViewProcesso:j_id_i3_c_1_5_2:j_id_i3_c_1_5_70',
            ':viewValoresCustomeDt:0:j_id_i3_c_1_5_7e:0:j_id_i3_c_1_5_7m"]',
        ),
    )
    div_tipo_obj_css = 'div[id="selectManyObjetoAdicionarList"]'
    itens_obj_div_css = 'div[id="selectManyObjetoAdicionarList_panel"]'
    checkbox = 'div[class="ui-chkbox ui-widget"]'
    botao_adicionar = 'button[id="adicionarObjetoBtn"]'
    botao_editar = 'button[id="j_id_4w:editarFasePedidoBtn"]'
    css_val_inpt = 'input[id="j_id_2m:j_id_2p_2e:processoAmountObjetoDt:0:amountValor_input"][type="text"]'
    css_risk = 'div[id="j_id_2m:j_id_2p_2e:processoAmountObjetoDt:0:j_id_2p_2i_5_1_6_5_k_2_2_1"]'
    processo_objt = 'ul[id="j_id_2m:j_id_2p_2e:processoAmountObjetoDt:0:j_id_2p_2i_5_1_6_5_k_2_2_1_items"]'
    botao_salvar_id = 'button[id="salvarBtn"]'
    daata_correcaoCss = 'input[id="j_id_2m:j_id_2p_2e:processoAmountObjetoDt:0:amountDataCorrecao_input"]'  # noqa: N815
    data_jurosCss = 'input[id="j_id_2m:j_id_2p_2e:processoAmountObjetoDt:0:amountDataJuros_input"]'  # noqa: N815
    texto_motivo = 'textarea[id="j_id_2m:j_id_2p_2e:j_id_2p_2i_8:j_id_2p_2i_j"]'

    type_risk_label = 'label[id="j_id_2m:provisaoTipoPedidoCombo_label"]'
    type_risk_select = 'select[id="j_id_2m:provisaoTipoPedidoCombo_input"]'

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
