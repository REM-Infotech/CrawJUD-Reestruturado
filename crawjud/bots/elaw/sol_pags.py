"""Module for managing payment solution processes within the ELAW system.

This module provides functionality to handle payment management and solution creation within
the ELAW system. It enables automated payment processing, validations, and record-keeping.

Classes:
    SolPags: Handles payment solutions by extending the CrawJUD base class

Attributes:
    type_doc (dict): Maps document lengths to document types (CPF/CNPJ)

"""

import os
import time
import traceback
from contextlib import suppress
from datetime import datetime
from time import sleep
from typing import Self

from pytz import timezone
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.bot import ClassBot
from crawjud.common.exceptions.bot import ExecutionError

type_doc = {11: "cpf", 14: "cnpj"}


class SolPags(ClassBot):
    """The SolPags class extends CrawJUD to manage page solutions within the application.

    Attributes:
        attribute_name (type): Description of the attribute.


    """

    @classmethod
    def initialize(
        cls,
        *args: str | int,
        **kwargs: str | int,
    ) -> Self:
        """
        Initialize bot instance.

        Args:
            *args (tuple[str | int]): Variable length argument list.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.

        """
        return cls(*args, **kwargs)

    def __init__(
        self,
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Initialize the SolPags instance.

        Args:
            *args (tuple[str | int]): Variable length argument list.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.

        """
        super().__init__()
        self.module_bot = __name__

        super().setup(*args, **kwargs)
        super().auth_bot()
        self.start_time = time.perf_counter()

    def execution(self) -> None:
        """Execute the main processing loop for page solutions."""
        frame = self.dataFrame()
        self.max_rows = len(frame)
        self.driver.maximize_window()
        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = self.elawFormats(value)
            if self.isStoped:
                break

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth_bot()

            try:
                self.queue()

            except Exception as e:
                old_message = None
                windows = self.driver.window_handles

                if len(windows) == 0:
                    with suppress(Exception):
                        self.driver_launch(
                            message="Webdriver encerrado inesperadamente, reinicializando..."
                        )

                    old_message = self.message

                    self.auth_bot()

                if old_message is None:
                    old_message = self.message
                message_error = str(e)

                self.type_log = "error"
                self.message_error = f"{message_error}. | Operação: {old_message}"
                self.prt()

                self.bot_data.update({"MOTIVO_ERRO": self.message_error})
                self.append_error(self.bot_data)

                self.message_error = None

        self.finalize_execution()

    def queue(self) -> None:
        """Handle the solution queue processing.

        Raises:
            ExecutionError: If an error occurs during execution.

        """
        try:
            search = self.search_bot()

            if search is True:
                namedef = self.format_string(self.bot_data.get("TIPO_PAGAMENTO"))
                self.new_payment()
                self.set_pgto(namedef)
                pgto = getattr(self, namedef.lower())
                pgto()

                self.save_changes()
                self.append_success(self.confirm_save())

            elif search is not True:
                raise ExecutionError(message="Processo não encontrado!")

        except Exception as e:
            self.logger.exception("".join(traceback.format_exception(e)))
            raise ExecutionError(e=e) from e

    def new_payment(self) -> None:
        """Create a new payment entry.

        Raises:
            ExecutionError: If an error occurs during payment creation.

        """
        try:
            tab_pagamentos: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.valor_pagamento,
                )),
            )
            tab_pagamentos.click()

            novo_pgto: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.botao_novo_pagamento,
                )),
            )
            novo_pgto.click()

        except Exception as e:
            self.logger.exception("".join(traceback.format_exception(e)))
            raise ExecutionError(e=e) from e

    def set_pgto(self, namedef: str) -> None:
        """Set the payment type.

        Args:
            namedef (str): The name definition for the payment type.

        Raises:
            ExecutionError: If the payment type is not found.

        """
        try:
            self.message = "Informando tipo de pagamento"
            self.type_log = "log"
            self.prt()

            type_itens: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.css_typeitens,
                )),
            )
            type_itens.click()

            sleep(0.5)

            list_itens: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.listitens_css,
                )),
            )
            list_itens = list_itens.find_elements(By.TAG_NAME, "li")

            for item in list_itens:
                item: WebElement = item

                normalizado_text = self.format_string(item.text)

                if normalizado_text.lower() == namedef.lower():
                    item.click()
                    return

                if "_" in normalizado_text:
                    normalizado_text = normalizado_text.split("_")
                    for norm in normalizado_text:
                        if norm.lower() == namedef.lower():
                            item.click()
                            return

            raise ExecutionError(message="Tipo de Pagamento não encontrado")

        except Exception as e:
            self.logger.exception("".join(traceback.format_exception(e)))
            raise ExecutionError(e=e) from e

    def condenacao(self) -> None:
        """Handle condemnation details.

        Raises:
            ExecutionError: If an error occurs during condemnation handling.

        """
        try:
            self.message = "Informando o valor da guia"
            self.type_log = "log"
            self.prt()

            text = self.bot_data.get("VALOR_GUIA")
            element: WebElement = self.wait.until(
                ec.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.elements.css_element,
                )),
            )

            sleep(0.5)
            element.send_keys(Keys.CONTROL, "a")
            element.send_keys(Keys.BACKSPACE)
            self.interact.send_key(element, text)
            self.driver.execute_script(
                f"document.querySelector('{self.elements.css_element}').blur()"
            )

            self.interact.sleep_load('div[id="j_id_2x"]')

            div_type_doc: WebElement = self.wait.until(
                ec.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.elements.type_doc_css,
                )),
            )
            div_type_doc.click()
            sleep(0.5)

            list_type_doc: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.list_type_doc_css,
                )),
            )
            list_type_doc = list_type_doc.find_elements(By.TAG_NAME, "li")

            for item in list_type_doc:
                item: WebElement = item
                if item.text.lower() == "guia de pagamento":
                    item.click()
                    break

            self.interact.sleep_load('div[id="j_id_2x"]')
            self.message = "Enviando guia"
            self.type_log = "log"
            self.prt()

            docs = [self.bot_data.get("DOC_GUIA")]
            calculo = self.bot_data.get("DOC_CALCULO", None)

            if calculo:
                calculos = [str(calculo)]

                if "," in str(calculo):
                    calculos = str(calculo).split(",")

                docs.extend(calculos)

            for doc in docs:
                doc = self.format_string(doc.upper())
                insert_doc: WebElement = self.wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        self.elements.editar_pagamento,
                    )),
                )
                path_doc = os.path.join(self.output_dir_path, doc)
                insert_doc.send_keys(path_doc)

                self.interact.wait_fileupload()
                sleep(0.5)

            self.message = "Informando tipo de condenação"
            self.type_log = "log"
            self.prt()
            div_condenacao_type: WebElement = self.wait.until(
                ec.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.elements.css_div_condenacao_type,
                )),
            )
            div_condenacao_type.click()

            tipo_condenacao = str(self.bot_data.get("TIPO_CONDENACAO"))
            if tipo_condenacao.lower() == "sentença":
                sleep(0.5)
                sentenca = self.driver.find_element(
                    By.CSS_SELECTOR, self.elements.valor_sentenca
                )
                sentenca.click()

            elif tipo_condenacao.lower() == "acórdão":
                sleep(0.5)
                acordao = self.driver.find_element(
                    By.CSS_SELECTOR, self.elements.valor_acordao
                )
                acordao.click()

            self.message = "Informando descrição do pagamento"
            self.type_log = "log"
            self.prt()

            desc_pagamento = str(self.bot_data.get("DESC_PAGAMENTO"))

            desc_pgto: WebElement = self.wait.until(
                ec.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.elements.css_desc_pgto,
                )),
            )
            desc_pgto.click()
            if "\n" in desc_pagamento:
                desc_pagamento = desc_pagamento.replace("\n", "")

            elif "\t" in desc_pagamento:
                desc_pagamento = desc_pagamento.replace("\t", "")
            desc_pgto.send_keys(desc_pagamento)
            sleep(0.5)

            self.driver.execute_script(
                f"document.querySelector('{self.elements.css_desc_pgto}').blur()"
            )

            self.message = "Informando data para pagamento"
            self.type_log = "log"
            self.prt()

            data_lancamento: WebElement = self.wait.until(
                ec.element_to_be_clickable((By.CSS_SELECTOR, self.elements.css_data)),
            )
            data_lancamento.click()
            data_lancamento.send_keys(self.bot_data.get("DATA_LANCAMENTO"))
            data_lancamento.send_keys(Keys.TAB)
            self.driver.execute_script(
                f"document.querySelector('{self.elements.css_data}').blur()"
            )

            self.interact.sleep_load('div[id="j_id_2x"]')
            self.message = "Informando favorecido"
            self.type_log = "log"
            self.prt()

            input_favorecido: WebElement = WebDriverWait(self.driver, 10).until(
                ec.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.elements.css_inputfavorecido,
                )),
            )
            input_favorecido.click()
            input_favorecido.clear()
            sleep(2)

            input_favorecido.send_keys(
                self.bot_data.get("CNPJ_FAVORECIDO", "00.360.305/0001-04")
            )

            result_favorecido: WebElement = WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.resultado_favorecido,
                )),
            )
            result_favorecido.click()

            self.interact.sleep_load('div[id="j_id_2x"]')
            self.message = "Informando forma de pagamento"
            self.type_log = "log"
            self.prt()

            label_forma_pgto = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.valor_processo
            )
            label_forma_pgto.click()

            sleep(1)
            boleto = self.driver.find_element(By.CSS_SELECTOR, self.elements.boleto)
            boleto.click()

            self.interact.sleep_load('div[id="j_id_2x"]')

            campo_cod_barras: WebElement = self.wait.until(
                ec.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.elements.css_cod_bars,
                )),
            )
            campo_cod_barras.click()
            sleep(0.5)

            cod_barras = str(self.bot_data.get("COD_BARRAS"))
            campo_cod_barras.send_keys(cod_barras.replace("\t", "").replace("\n", ""))
            self.driver.execute_script(
                f"document.querySelector('{self.elements.css_cod_bars}').blur()"
            )

            self.interact.sleep_load('div[id="j_id_2x"]')
            self.message = "Informando centro de custas"
            self.type_log = "log"
            self.prt()

            centro_custas: WebElement = self.wait.until(
                ec.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.elements.css_centro_custas,
                )),
            )
            centro_custas.click()
            centro_custas.send_keys("A906030100")

            self.driver.execute_script(
                f"document.querySelector('{self.elements.css_centro_custas}').blur()"
            )

            sleep(1)
            self.message = "Informando conta para débito"
            self.type_log = "log"
            self.prt()

            div_conta_debito: WebElement = self.wait.until(
                ec.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.elements.css_div_conta_debito,
                )),
            )
            div_conta_debito.click()
            sleep(1)
            conta_debito = self.driver.find_element(
                By.CSS_SELECTOR,
                'li[data-label="AMAZONAS - PAGTO CONDENAÇÕES DE LITÍGIOS CÍVEIS CONTRAPARTIDA"]',
            )
            conta_debito.click()

        except Exception as e:
            self.logger.exception("".join(traceback.format_exception(e)))
            raise ExecutionError(e=e) from e

    def custas(self) -> None:
        """Manage cost-related operations.

        Raises:
            ExecutionError: If an error occurs during cost management.

        """
        try:
            self.message = "Informando valor da guia"
            self.type_log = "log"
            self.prt()

            valor_doc = self.bot_data.get("VALOR_GUIA").replace(".", ",")

            element: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.valor_guia,
                )),
            )
            element.click()
            element.send_keys(Keys.CONTROL, "a")
            sleep(0.5)
            element.send_keys(Keys.BACK_SPACE)
            sleep(0.5)
            element.send_keys(valor_doc)

            self.driver.execute_script(
                f"document.querySelector('{self.elements.valor_guia}').blur()"
            )

            sleep(0.5)

            list_tipo_doc: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.type_doc_css,
                )),
            )
            list_tipo_doc.click()
            sleep(1)

            set_gru = self.driver.find_element(By.CSS_SELECTOR, self.elements.css_gru)
            set_gru.click()

            sleep(2)
            self.message = "Inserindo documento"
            self.type_log = "log"
            self.prt()

            docs = [self.bot_data.get("DOC_GUIA")]

            for doc in docs:
                doc = self.format_string(doc)
                insert_doc: WebElement = self.wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        self.elements.editar_pagamento,
                    )),
                )
                insert_doc.send_keys(f"{self.output_dir_path}/{doc}")

                wait_upload: WebElement = (
                    WebDriverWait(self.driver, 20)
                    .until(
                        ec.presence_of_element_located((
                            By.CSS_SELECTOR,
                            self.elements.editar_pagamentofile,
                        ))
                    )
                    .find_element(By.TAG_NAME, "table")
                    .find_element(By.TAG_NAME, "tbody")
                    .find_elements(By.TAG_NAME, "tr")
                )

                if len(wait_upload) == len(docs):
                    break

            solicitante = str(self.bot_data.get("SOLICITANTE")).lower()
            if solicitante == "monitoria" or solicitante.lower() == "monitória":
                desc_pgto: WebElement = self.wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        self.elements.css_desc_pgto,
                    )),
                )
                desc_pgto.send_keys(self.bot_data.get("DESC_PAGAMENTO"))
                self.driver.execute_script(
                    f"document.querySelector('{self.elements.css_desc_pgto}').blur()"
                )

            self.message = "Informando tipo de guia"
            self.type_log = "log"
            self.prt()

            div_tipo_custa = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.css_tipocusta
            )
            div_tipo_custa.click()
            sleep(1)

            tipo_guia = str(self.bot_data.get("TIPO_GUIA"))
            list_tipo_custa: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.css_listcusta,
                )),
            )
            list_tipo_custa = list_tipo_custa.find_elements(By.TAG_NAME, "li")
            for item in list_tipo_custa:
                item: WebElement = item
                if tipo_guia.lower() == item.text.lower():
                    sleep(0.5)
                    item.click()
                    break

            sleep(1)
            self.message = "Informando data para pagamento"
            self.type_log = "log"
            self.prt()

            data_vencimento = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.css_data
            )
            data_vencimento.click()
            data_vencimento.send_keys(self.bot_data.get("DATA_LANCAMENTO"))
            self.driver.execute_script(
                f"document.querySelector('{self.elements.css_data}').blur()"
            )
            self.interact.sleep_load('div[id="j_id_2x"]')

            label_forma_pgto = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.valor_processo
            )
            label_forma_pgto.click()

            sleep(1)
            boleto = self.driver.find_element(By.CSS_SELECTOR, self.elements.boleto)
            boleto.click()

            self.interact.sleep_load('div[id="j_id_2x"]')

            campo_cod_barras: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.css_cod_bars,
                )),
            )
            campo_cod_barras.click()
            sleep(0.5)
            campo_cod_barras.send_keys(self.bot_data.get("COD_BARRAS"))
            self.driver.execute_script(
                f"document.querySelector('{self.elements.css_cod_bars}').blur()"
            )

            self.message = "Informando favorecido"
            self.type_log = "log"
            self.prt()

            sleep(2)
            input_favorecido: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.css_inputfavorecido,
                )),
            )
            input_favorecido.click()
            sleep(1)
            input_favorecido.clear()

            input_favorecido.send_keys(
                self.bot_data.get("CNPJ_FAVORECIDO", "04.812.509/0001-90")
            )

            result_favorecido: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.resultado_favorecido,
                )),
            )
            result_favorecido.click()
            self.driver.execute_script(
                f"document.querySelector('{self.elements.css_inputfavorecido}').blur()"
            )

            self.message = "Informando centro de custas"
            self.type_log = "log"
            self.prt()

            sleep(1)

            centro_custas: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.css_centro_custas,
                )),
            )
            centro_custas.click()
            centro_custas.send_keys("A906030100")

            # self.driver.execute_script(f"document.querySelector('{self.elements.css_centro_custas}').blur()")

            self.message = "Informando conta débito"
            self.type_log = "log"
            self.prt()

            div_conta_debito: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.css_div_conta_debito,
                )),
            )
            div_conta_debito.click()
            sleep(1)

            if solicitante == "jec":
                conta_debito = self.driver.find_element(
                    By.CSS_SELECTOR, self.elements.custas_civis
                )
                conta_debito.click()

            elif solicitante == "monitoria" or solicitante == "monitória":
                conta_debito = self.driver.find_element(
                    By.CSS_SELECTOR, self.elements.custas_monitorias
                )
                conta_debito.click()

        except Exception as e:
            self.logger.exception("".join(traceback.format_exception(e)))
            raise ExecutionError(e=e) from e

    def save_changes(self) -> None:
        """Save all changes made during the payment process."""
        try:
            self.message = "Salvando alterações"
            self.type_log = "log"
            self.prt()
            save: WebElement = self.wait.until(
                ec.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.elements.botao_salvar_pagamento,
                )),
            )
            save.click()

        except Exception as e:
            self.logger.exception("".join(traceback.format_exception(e)))
            raise ExecutionError(e=e) from e

    def confirm_save(self) -> None:
        """Confirm the saving of payment details.

        Raises:
            ExecutionError: If the save operation fails.

        """
        try:
            tab_pagamentos: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.valor_pagamento,
                )),
            )
            tab_pagamentos.click()

            enter_table: WebElement = (
                self.wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        self.elements.valor_resultado,
                    ))
                )
                .find_element(By.TAG_NAME, "table")
                .find_element(By.TAG_NAME, "tbody")
            )
            check_solicitacoes = enter_table.find_elements(By.TAG_NAME, "tr")
            info_sucesso = [
                self.bot_data.get("NUMERO_PROCESSO"),
                "Pagamento solicitado com sucesso!!",
            ]
            current_handle = self.driver.current_window_handle

            for pos, item in enumerate(check_solicitacoes):
                if item.text == "Nenhum registro encontrado!":
                    raise ExecutionError(message="Pagamento não solicitado")

                sleep(2)
                open_details = item.find_element(
                    By.CSS_SELECTOR, self.elements.botao_ver
                )
                open_details.click()

                sleep(1)
                id_task = item.find_elements(By.TAG_NAME, "td")[2].text
                closeContext = self.wait.until(  # noqa: N806
                    ec.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            f'div[id="tabViewProcesso:pvp-dtProcessoValorResults:{pos}:pvp-pgBotoesValoresPagamentoBtnVer_dlg"]',
                        ),
                    ),
                ).find_element(By.TAG_NAME, "a")

                WaitFrame = WebDriverWait(self.driver, 5).until(  # noqa: N806
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        self.elements.valor,
                    )),
                )
                self.driver.switch_to.frame(WaitFrame)
                sleep(1)

                tipoCusta = ""  # noqa: N806
                cod_bars = ""
                tipoCondenacao = ""  # noqa: N806
                now = datetime.now(timezone("America/Manaus")).strftime(
                    "%d-%m-%Y %H.%M.%S"
                )
                Name_Comprovante1 = f"COMPROVANTE 1 {self.bot_data.get('NUMERO_PROCESSO')} - {self.pid} - {now}.png"  # noqa: N806
                cod_bars_xls = str(
                    self.bot_data.get("COD_BARRAS").replace(".", "").replace(" ", "")
                )

                with suppress(TimeoutException):
                    tipoCusta = str(  # noqa: N806
                        self.wait.until(
                            ec.presence_of_element_located((
                                By.CSS_SELECTOR,
                                self.elements.visualizar_tipo_custas,
                            )),
                        )
                        .text.split(":")[-1]
                        .replace("\n", ""),
                    )

                with suppress(TimeoutException):
                    cod_bars = str(
                        self.wait.until(
                            ec.presence_of_element_located((
                                By.CSS_SELECTOR,
                                self.elements.visualizar_cod_barras,
                            )),
                        )
                        .text.split(":")[-1]
                        .replace("\n", ""),
                    )

                with suppress(TimeoutException):
                    tipoCondenacao = (  # noqa: N806
                        self.wait.until(
                            ec.presence_of_element_located((
                                By.CSS_SELECTOR,
                                self.elements.visualizar_tipoCondenacao,
                            )),
                        )
                        .text.split(":")[-1]
                        .replace("\n", "")
                    )

                namedef = self.format_string(
                    self.bot_data.get("TIPO_PAGAMENTO")
                ).lower()

                chk_bars = cod_bars == cod_bars_xls

                if namedef == "condenacao":
                    tipo_condenacao_xls = str(
                        self.bot_data.get("TIPO_CONDENACAO", "")
                    )
                    match_condenacao = (
                        tipo_condenacao_xls.lower() == tipoCondenacao.lower()
                    )
                    matchs = all([match_condenacao, chk_bars])

                elif namedef == "custas":
                    tipo_custa_xls = str(self.bot_data.get("TIPO_GUIA", ""))
                    match_custa = tipo_custa_xls.lower() == tipoCusta.lower()
                    matchs = all([match_custa, chk_bars])

                if matchs:
                    self.driver.switch_to.default_content()
                    url_page = WaitFrame.get_attribute("src")
                    self.getScreenShot(url_page, Name_Comprovante1)
                    self.driver.switch_to.window(current_handle)

                    closeContext.click()
                    Name_Comprovante2 = f"COMPROVANTE 2 {self.bot_data.get('NUMERO_PROCESSO')} - {self.pid} - {now}.png"  # noqa: N806
                    item.screenshot(
                        os.path.join(self.output_dir_path, Name_Comprovante2)
                    )

                    info_sucesso.extend([
                        tipoCondenacao,
                        Name_Comprovante1,
                        id_task,
                        Name_Comprovante2,
                    ])
                    return info_sucesso

                self.driver.switch_to.default_content()
                closeContext.click()
                sleep(0.25)

            raise ExecutionError(message="Pagamento não solicitado")

        except Exception as e:
            self.logger.exception("".join(traceback.format_exception(e)))
            return [
                self.bot_data.get("NUMERO_PROCESSO"),
                "Pagamento solicitado com sucesso!!",
            ]

    def getScreenShot(self, url_page: str, Name_Comprovante1: str) -> None:  # noqa: N802, N803
        """Capture a screenshot of the specified page.

        Args:
            url_page (str): The URL of the page to capture.
            Name_Comprovante1 (str): The name for the screenshot file.

        """
        self.driver.switch_to.new_window("tab")
        self.driver.get(url_page)
        self.driver.save_screenshot(
            os.path.join(self.output_dir_path, Name_Comprovante1)
        )
        self.driver.close()
