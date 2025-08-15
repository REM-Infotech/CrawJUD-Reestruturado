"""Empty."""

import os
from contextlib import suppress
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING

import dotenv
from PIL import Image
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.common.exceptions.bot import ExecutionError
from crawjud.interfaces.controllers.bots.systems.projudi import ProjudiBot as ClassBot

from .resources import elements as el

dotenv.load_dotenv()


if TYPE_CHECKING:
    from selenium.webdriver.common.alert import Alert
    from selenium.webdriver.remote.webelement import WebElement


def _raise_execution_error(message: str) -> os.NoReturn:
    raise ExecutionError(message=message)


class Protocolo(ClassBot):
    """Empty."""

    def execution(self) -> None:
        """Empty."""
        frame = self.dataFrame()
        self.max_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = value
            if self.isStoped:
                break

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth_bot()

            try:
                self.queue()

            except ExecutionError as e:
                # TODO(Nicholas Silva): Criação de Exceptions
                # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
                old_message = None

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
        """Manage the execution queue for protocol processing.

        Raises:
            ExecutionError: When protocol processing fails.

        """
        try:
            search = self.search_bot()

            if search is not True:
                _raise_execution_error(message="Processo não encontrado!")

            self.add_new_move()

            self.add_new_file()
            if self.bot_data.get("ANEXOS", None) is not None:
                self.more_files()

            self.set_file_principal()
            self.sign_files()
            self.finish_move()

            debug = False
            data = [
                {
                    "NUMERO_PROCESSO": self.bot_data.get("NUMERO_PROCESSO"),
                    "tested": "true",
                },
            ]

            if debug is False:
                confirm_protocol = self.confirm_protocol()
                if not confirm_protocol:
                    if self.set_parte() is not True:
                        _raise_execution_error(
                            message="Nao foi possivel confirmar protocolo",
                        )

                    self.finish_move()
                    confirm_protocol = self.confirm_protocol()
                    if not confirm_protocol:
                        _raise_execution_error(
                            message="Nao foi possivel confirmar protocolo",
                        )

                data = self.screenshot_sucesso()
                data.append(confirm_protocol)

            self.append_success(data)

        except Exception as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
            raise ExecutionError(e=e) from e

    def confirm_protocol(self) -> str | None:
        """Empty.

        Returns:
            str | None: The extracted protocol number if available; otherwise, None.

        """
        successMessage = None  # noqa: N806
        with suppress(TimeoutException):
            successMessage = (  # noqa: N806
                self.wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        "#successMessages",
                    )),
                )
                .text.split("Protocolo:")[1]
                .replace(" ", "")
            )

        return successMessage

    def set_parte(self) -> bool:
        """Selecione a parte apropriada conforme especificado nos dados do bot.

        Returns:
            bool: Retorna True se a parte for selecionada com sucesso, caso contrário False.

        """
        self.message = "Selecionando parte"
        self.type_log = "log"
        self.prt()

        table_partes = self.driver.find_element(
            By.CSS_SELECTOR,
            "#juntarDocumentoForm > table:nth-child(28)",
        )
        table_partes = table_partes.find_element(By.TAG_NAME, "tbody").find_elements(
            By.TAG_NAME,
            "tr",
        )

        parte_peticao = self.bot_data.get("PARTE_PETICIONANTE").upper()

        for pos, item in enumerate(table_partes):
            td_partes = table_partes[pos + 1].find_element(By.TAG_NAME, "td")

            if self._advogado_ja_representa(td_partes):
                return True

            if self._seleciona_parte_por_linha(td_partes, parte_peticao, item):
                return True

            if self._seleciona_parte_por_texto(td_partes, parte_peticao, item):
                return True

        return False

    def _advogado_ja_representa(self, td_partes: "WebElement") -> bool:
        """Verifica se o advogado já representa a parte.

        Returns:
            bool: Retorno da verificação

        """
        return "Advogado já representa essa parte" in td_partes.text

    def _seleciona_parte_por_linha(
        self,
        td_partes: "WebElement",
        parte_peticao: str,
        item: "WebElement",
    ) -> bool:
        """Seleciona a parte caso haja múltiplas linhas no texto.

        Returns:
            bool: Retorno da verificação

        Raises:
            ExecutionError: Erro de execução

        """
        if "\n" not in td_partes.text:
            return False
        partes = td_partes.text.split("\n")
        for enum, parte in enumerate(partes):
            if parte.upper() == parte_peticao:
                radio_item = item.find_element(
                    By.CSS_SELECTOR,
                    "input[type='radio']",
                )
                id_radio = radio_item.get_attribute("id")
                self.driver.execute_script(
                    str(el.command_select_parte_protocolo).format(
                        id_radio=id_radio,
                    ),
                )
                radio_item.click()
                set_parte = td_partes.find_elements(By.TAG_NAME, "input")[enum]
                self.id_part = set_parte.get_attribute("id")
                id_part = self.id_part
                return_cmd = self.driver.execute_script(
                    el.command_sel_parte_protocolo2.format(
                        id_part=id_part,
                    ),
                )
                if not self._confirma_selecao_parte(set_parte, id_part, return_cmd):
                    raise ExecutionError(
                        message="Não é possivel selecionar parte",
                    )
                return True
        return False

    def _seleciona_parte_por_texto(
        self,
        td_partes: "WebElement",
        parte_peticao: str,
        item: "WebElement",
    ) -> bool:
        """Seleciona a parte caso o texto corresponda diretamente.

        Returns:
            bool: Retorno da verificação

        Raises:
            ExecutionError: Erro de execução

        """
        chk_info = (td_partes.text.upper() == parte_peticao) or (
            parte_peticao in td_partes.text.upper()
        )
        if not chk_info:
            return False
        radio_item = item.find_element(
            By.CSS_SELECTOR,
            self.elements.input_radio,
        )
        radio_item.click()
        set_parte = td_partes.find_element(By.TAG_NAME, "input")
        self.id_part = set_parte.get_attribute("id")
        cmd2 = f"return document.getElementById('{self.id_part}').checked"
        return_cmd = self.driver.execute_script(cmd2)
        if not self._confirma_selecao_parte(set_parte, self.id_part, return_cmd):
            raise ExecutionError(
                message="Não é possivel selecionar parte",
            )
        return True

    def _confirma_selecao_parte(
        self,
        set_parte: "WebElement",
        id_part: str,
        *,
        return_cmd: bool,
    ) -> bool:
        """Confirma se a parte foi selecionada corretamente.

        Returns:
            bool: Retorno da verificação


        """
        if return_cmd is False:
            set_parte.click()
            cmd2 = f"return document.getElementById('{id_part}').checked"
            return_cmd = self.driver.execute_script(cmd2)
            if return_cmd is False:
                return False
        return True

    def add_new_move(self) -> None:
        """Initiate the addition of a new protocol move with necessary web interactions.

        Raises:
            ExecutionError: If adding the move fails.

        """
        try:
            self.message = "Inicializando peticionamento..."
            self.type_log = "log"
            self.prt()
            button_add_move = self.driver.find_element(By.ID, "peticionarButton")
            button_add_move.click()

            alert = None
            with suppress(TimeoutException):
                alert: type[Alert] = WebDriverWait(self.driver, 5).until(
                    ec.alert_is_present(),
                )

            if alert:
                alert.accept()

            """ Corrigir elements """
            self.message = "Informando tipo de protocolo..."
            self.type_log = "log"
            self.prt()
            input_tipo_move: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'input[name="descricaoTipoDocumento"]',
                )),
            )
            input_tipo_move.click()
            sleep(1)
            input_tipo_move.send_keys(self.bot_data.get("TIPO_PROTOCOLO"))

            sleep(1.5)

            input_move_option: WebElement = self.wait.until(
                ec.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "div#ajaxAuto_descricaoTipoDocumento > ul > li:nth-child(1)",
                    ),
                ),
            )
            input_move_option.click()
            """ Corrigir elements """

        except Exception as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35

            raise ExecutionError(e=e) from e

    def add_new_file(self) -> None:
        """Upload the main petition file and its attachments for a protocol.

        Raises:
            ExecutionError: If file upload encounters an error.

        """
        try:
            file = str(self.bot_data.get("PETICAO_PRINCIPAL"))
            self.message = "Inserindo Petição/Anexos..."
            self.type_log = "log"
            self.prt()
            button_new_file = self.driver.find_element(
                By.CSS_SELECTOR,
                'input#editButton[value="Adicionar"]',
            )
            button_new_file.click()

            sleep(2.5)

            self.driver.switch_to.frame(
                self.driver.find_element(By.CSS_SELECTOR, self.elements.border),
            )
            self.message = f"Enviando arquivo '{file}'"
            self.type_log = "log"
            self.prt()

            file_inpt = Path(self.path_args).parent.resolve()
            css_inptfile = 'input[id="conteudo"]'
            input_file_element: WebElement = WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, css_inptfile)),
            )

            file_to_upload = self.format_string(file)

            path_file = str(file_inpt.joinpath(file_to_upload))

            input_file_element.send_keys(path_file)

            self.wait_progressbar()

            self.message = "Arquivo enviado com sucesso!"
            self.type_log = "log"
            self.prt()

            sleep(1)
            type_file: WebElement = self.wait.until(
                ec.presence_of_element_located((By.ID, "tipo0")),
            )
            type_file.click()
            sleep(0.25)
            type_options = type_file.find_elements(By.TAG_NAME, "option")
            for option in type_options:
                if option.text == self.bot_data.get("TIPO_ARQUIVO"):
                    option.click()
                    break

        except Exception as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35

            raise ExecutionError(e=e) from e

    def set_file_principal(self) -> None:
        """Designate the principal file among the uploaded documents.

        Raises:
            ExecutionError: If the main file is not set correctly.

        """
        try:
            tablefiles: WebElement = self.wait.until(
                ec.presence_of_element_located((By.CLASS_NAME, "resultTable")),
            )
            checkfiles = tablefiles.find_element(By.TAG_NAME, "tbody").find_elements(
                By.TAG_NAME,
                "tr",
            )[0]
            radiobutton = checkfiles.find_elements(By.TAG_NAME, "td")[0].find_element(
                By.CSS_SELECTOR,
                self.elements.input_radio,
            )
            radiobutton.click()

        except Exception as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35

            raise ExecutionError(e=e) from e

    def more_files(self) -> None:
        """Upload additional files as defined in the bot data for protocol documentation.

        Raises:
            ExecutionError: When extra file upload operations fail.

        """
        try:
            sleep(0.5)

            work_dir = Path(self.path_args).parent.resolve()
            anexos_list = [str(self.bot_data.get("ANEXOS"))]
            if "," in self.bot_data.get("ANEXOS"):
                anexos_list = self.bot_data.get("ANEXOS").__str__().split(",")

            for file in anexos_list:
                self.message = f"Enviando arquivo '{file}'"
                file_to_upload = self.format_string(file)
                self.type_log = "log"
                self.prt()
                input_file_element: WebElement = WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((
                        By.XPATH,
                        self.elements.conteudo,
                    )),
                )

                inpt_file = str(work_dir.joinpath(file_to_upload))

                input_file_element.send_keys(inpt_file)
                self.wait_progressbar()
                self.message = f"Arquivo '{file}' enviado com sucesso!"
                self.type_log = "log"
            self.prt()

            sleep(3)
            tablefiles: WebElement = self.wait.until(
                ec.presence_of_element_located((By.CLASS_NAME, "resultTable")),
            )
            checkfiles = tablefiles.find_element(By.TAG_NAME, "tbody").find_elements(
                By.TAG_NAME,
                "tr",
            )

            for pos, _ in enumerate(checkfiles):
                numbertipo = pos + 1
                sleep(0.75)

                with suppress(Exception):
                    type_file = self.driver.find_element(By.ID, f"tipo{numbertipo}")
                    type_file.click()

                sleep(0.25)
                type_options = type_file.find_elements(By.TAG_NAME, "option")
                type_anexos = str(self.bot_data.get("TIPO_ANEXOS")).lower()
                for option in type_options:
                    if str(option.text).lower() == type_anexos:
                        option.click()
                        break

        except Exception as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35

            raise ExecutionError(e=e) from e

    def sign_files(self) -> None:
        """Sign the protocol documents by providing the certificate password and confirming.

        Raises:
            ExecutionError: If the signing process fails.

        """
        try:
            self.message = "Assinando arquivos..."
            self.type_log = "log"
            self.prt()
            password_input = self.driver.find_element(By.ID, "senhaCertificado")
            password_input.click()
            senhatoken = f"{self.token}"
            password_input.send_keys(senhatoken)

            sign_button = self.driver.find_element(
                By.CSS_SELECTOR,
                self.elements.botao_assinar,
            )
            sign_button.click()

            check_p_element = ""
            with suppress(TimeoutException):
                check_p_element: WebElement = WebDriverWait(
                    self.driver,
                    5,
                    0.01,
                ).until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        "#errorMessages > div.box-content",
                    )),
                )

            if check_p_element != "":
                _raise_execution_error(message="Senha Incorreta!")

            confirm_button = self.driver.find_element(
                By.CSS_SELECTOR,
                'input#closeButton[value="Confirmar Inclusão"]',
            )
            confirm_button.click()
            sleep(1)

            self.driver.switch_to.default_content()
            self.message = "Arquivos assinados"
            self.type_log = "log"
            self.prt()

        except Exception as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35

            raise ExecutionError(e=e) from e

    def finish_move(self) -> None:
        """Empty."""
        self.message = f"Concluindo peticionamento do processo {self.bot_data.get('NUMERO_PROCESSO')}"
        self.type_log = "log"
        self.prt()

        finish_button = self.driver.find_element(
            By.CSS_SELECTOR,
            self.elements.botao_concluir,
        )
        finish_button.click()

    def screenshot_sucesso(self) -> list:
        """Capture and merge screenshots after successful protocol processing.

        Returns:
            list: A list containing the process number, success message, and screenshot file path.

        Raises:
            ExecutionError: If an error occurs during the screenshot capture.

        """
        out_dir_path = Path(self.output_dir_path)
        pid = self.pid
        numproc = self.bot_data.get("NUMERO_PROCESSO")

        try:
            table_moves = self.driver.find_element(By.CLASS_NAME, "resultTable")
            table_moves = table_moves.find_elements(
                By.XPATH,
                './/tr[contains(@class, "odd") or contains(@class, "even")][not(@style="display:none;")]',
            )

            table_moves[0].screenshot(out_dir_path.joinpath("tr_0.png"))

            expand = table_moves[0].find_element(
                By.CSS_SELECTOR,
                self.elements.expand_btn_projudi,
            )
            expand.click()

            sleep(1.5)

            table_moves[1].screenshot(out_dir_path.joinpath("tr_1.png"))

            # Abra as imagens
            im_tr1 = Image.open(out_dir_path.joinpath("tr_0.png"))
            im_tr2 = Image.open(out_dir_path.joinpath("tr_1.png"))

            # Obtenha as dimensões das imagens
            width1, height1 = im_tr1.size
            width2, height2 = im_tr2.size

            # Calcule a largura e altura total para combinar as imagens
            total_height = height1 + height2
            total_width = max(width1, width2)

            # Crie uma nova imagem com o tamanho combinado
            combined_image = Image.new("RGB", (total_width, total_height))

            # Cole as duas imagens (uma em cima da outra)
            combined_image.paste(im_tr1, (0, 0))
            combined_image.paste(im_tr2, (0, height1))

            # Salve a imagem combinada

            comprovante1 = f"{pid} - COMPROVANTE 1 - {numproc}.png"
            combined_image.save(
                str(out_dir_path.joinpath(comprovante1)),
            )

            filename = f"Protocolo - {numproc} - PID{pid}.png"
            self.driver.get_screenshot_as_file(
                str(out_dir_path.joinpath(filename)),
            )

            self.message = "Peticionamento concluído com sucesso!"

            self.type_log = "log"
            self.prt()

            return [self.bot_data.get("NUMERO_PROCESSO"), self.message, comprovante1]

        except Exception as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
            raise ExecutionError(e=e) from e

    def remove_files(self) -> None:
        """Delete the uploaded files from the protocol after processing."""
        tablefiles = None
        with suppress(TimeoutException):
            tablefiles: WebElement = WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located((By.CLASS_NAME, "resultTable")),
            )

        if tablefiles:
            sleep(1)
            checkfiles = tablefiles.find_element(By.TAG_NAME, "tbody").find_elements(
                By.TAG_NAME,
                "tr",
            )

            for file in checkfiles:
                with suppress(NoSuchElementException, StaleElementReferenceException):
                    radiobutton = file.find_elements(By.TAG_NAME, "td")[
                        0
                    ].find_element(
                        By.CSS_SELECTOR,
                        self.elements.input_radio,
                    )
                    radiobutton.click()

                    delete_file = self.driver.find_element(
                        By.CSS_SELECTOR,
                        self.elements.botao_deletar,
                    )
                    delete_file.click()

                    alert = None
                    with suppress(TimeoutException):
                        alert: type[Alert] = WebDriverWait(self.driver, 5).until(
                            ec.alert_is_present(),
                        )

                    if alert:
                        alert.accept()

                sleep(2)

    def wait_progressbar(self) -> None:
        """Wait until the progress bar completes the file upload or processing."""
        while True:
            with suppress(Exception):
                divprogressbar: WebElement = self.wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        self.elements.css_containerprogressbar,
                    )),
                )
                divprogressbar = divprogressbar.find_element(
                    By.CSS_SELECTOR,
                    self.elements.css_divprogressbar,
                )
                sleep(1)
                with suppress(Exception):
                    get_style = divprogressbar.get_attribute("style")

                if get_style != "":
                    sleep(1)

                elif get_style == "":
                    break

                continue
            break
