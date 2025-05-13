"""Module: protocolo.

Handles protocol-related functionalities in the Projudi system. Extend CrawJUD to manage
protocol operations such as adding moves, uploading files, signing documents, and capturing screenshots.
"""

import os
from contextlib import suppress
from pathlib import Path
from time import sleep
from typing import Self

from PIL import Image
from selenium.common.exceptions import (
    JavascriptException,  # noqa: F401
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.core import CrawJUD
from crawjud.exceptions.bot import CadastroParteError, ExecutionError, PasswordError, ProcNotFoundError, SaveError

# from typing import type


class Protocolo(CrawJUD):
    """Handle protocol operations and execute moves, uploads, signing, and screenshot capture in Projudi.

    This class extends CrawJUD to manage protocols by sequentially processing moves,
    file uploads, digital signing and capturing confirmation screenshots.
    """

    @classmethod
    def initialize(
        cls,
        *args: str | int,
        **kwargs: str | int,
    ) -> Self:
        """Initialize a Protocolo instance with provided arguments.

        Args:
            *args (tuple[str | int]): Variable length positional arguments.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.

        Returns:
            Self: The initialized Protocolo instance.

        """
        return cls(*args, **kwargs)

    def execution(self) -> None:
        """Execute protocol processing over each data frame entry and handle errors.

        Iterates through the data rows and executes protocol operations including moves,
        file uploads, signing and final finalization.
        """
        frame = self.dataFrame()
        self.max_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = value
            if self.is_stoped:
                break

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth_bot()

            try:
                self.queue()

            except Exception as e:
                self.tratamento_erros(exc=e)

        self.finalize_execution()

    def queue(self) -> None:
        """Manage the execution queue for protocol processing.

        Raises:
            ExecutionError: When protocol processing fails.

        """
        try:
            search = self.search_bot()

            if search is not True:
                raise ProcNotFoundError(message="Processo não encontrado!", bot_execution_id=self.pid)

            self.add_new_move()

            # if self.set_parte() is not True:
            #     raise Exception

            self.add_new_file()
            if self.bot_data.get("ANEXOS", None) is not None:
                self.more_files()

            self.set_file_principal()
            self.sign_files()
            self.finish_move()

            debug = False
            data = [{"NUMERO_PROCESSO": self.bot_data.get("NUMERO_PROCESSO"), "tested": "true"}]

            if debug is False:
                confirm_protocol = self.confirm_protocol()
                if not confirm_protocol:
                    if self.set_parte() is not True:
                        raise SaveError(message="Nao foi possivel confirmar protocolo", bot_execution_id=self.pid)

                    self.finish_move()
                    confirm_protocol = self.confirm_protocol()
                    if not confirm_protocol:
                        raise SaveError(message="Nao foi possivel confirmar protocolo", bot_execution_id=self.pid)

                data = self.screenshot_sucesso()
                data.append(confirm_protocol)

            self.append_success(data)

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def confirm_protocol(self) -> str | None:
        """Confirm protocol action and extract the protocol number from the success message.

        Returns:
            str | None: The extracted protocol number if available; otherwise, None.

        """
        successMessage = None  # noqa: N806
        with suppress(TimeoutException):
            successMessage = (  # noqa: N806
                self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "#successMessages")))
                .text.split("Protocolo:")[1]
                .replace(" ", "")
            )

        return successMessage

    def set_parte(self) -> bool:
        """Select the appropriate party as specified in bot data.

        Returns:
            bool: True if the party is successfully selected, otherwise False.

        Raises:
            ExecutionError: If selection of the specified party fails.

        """
        # self.driver.switch_to.frame(self.driver.find_element(By.CSS_SELECTOR, 'iframe[name="userMainFrame"]'))
        message = "Selecionando parte"
        type_log = "log"
        self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)

        table_partes = self.driver.find_element(By.CSS_SELECTOR, "#juntarDocumentoForm > table:nth-child(28)")
        table_partes = table_partes.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")

        selected_parte = False

        for pos, item in enumerate(table_partes):
            td_partes = table_partes[pos + 1].find_element(By.TAG_NAME, "td")

            # if os.getenv("DEBUG", "False").lower() in ("false", "f", "0"):
            if "Advogado já representa essa parte" in td_partes.text:
                return True

            parte_peticao = self.bot_data.get("PARTE_PETICIONANTE").upper()
            chk_info = (td_partes.text.upper() == parte_peticao.upper()) or (
                parte_peticao.upper() in td_partes.text.upper()
            )
            if "\n" in td_partes.text:
                partes = td_partes.text.split("\n")
                for enum, parte in enumerate(partes):
                    if parte.upper() == self.bot_data.get("PARTE_PETICIONANTE").upper():
                        radio_item = item.find_element(By.CSS_SELECTOR, "input[type='radio']")
                        id_radio = radio_item.get_attribute("id")

                        command = f'document.getElementById("{id_radio}").removeAttribute("disabled");'
                        self.driver.execute_script(command)

                        radio_item.click()
                        set_parte = td_partes.find_elements(By.TAG_NAME, "input")[enum]

                        self.id_part = set_parte.get_attribute("id")
                        cmd2 = f"return document.getElementById('{self.id_part}').checked"
                        return_cmd = self.driver.execute_script(cmd2)
                        if return_cmd is False:
                            set_parte.click()
                            cmd2 = f"return document.getElementById('{self.id_part}').checked"
                            return_cmd = self.driver.execute_script(cmd2)
                            if return_cmd is False:
                                raise CadastroParteError(
                                    message="Não é possivel selecionar parte", bot_execution_id=self.pid
                                )

                        selected_parte = True
                        break

            elif chk_info:
                radio_item = item.find_element(By.CSS_SELECTOR, self.elements.input_radio)
                radio_item.click()

                set_parte = td_partes.find_element(By.TAG_NAME, "input")

                self.id_part = set_parte.get_attribute("id")
                cmd2 = f"return document.getElementById('{self.id_part}').checked"
                return_cmd = self.driver.execute_script(cmd2)
                if return_cmd is False:
                    set_parte.click()
                    cmd2 = f"return document.getElementById('{self.id_part}').checked"
                    return_cmd = self.driver.execute_script(cmd2)
                    if return_cmd is False:
                        raise CadastroParteError(message="Não é possível selecionar parte", bot_execution_id=self.pid)

                selected_parte = True
                break

            if selected_parte:
                break

        return selected_parte

    def add_new_move(self) -> None:
        """Initiate the addition of a new protocol move with necessary web interactions.

        Raises:
            ExecutionError: If adding the move fails.

        """
        try:
            message = "Inicializando peticionamento..."
            type_log = "log"
            self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)
            button_add_move = self.driver.find_element(By.ID, "peticionarButton")
            button_add_move.click()

            alert = None
            with suppress(TimeoutException):
                alert: type[Alert] = WebDriverWait(self.driver, 5).until(ec.alert_is_present())

            if alert:
                alert.accept()

            """ Corrigir elements """
            message = "Informando tipo de protocolo..."
            type_log = "log"
            self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)
            input_tipo_move: WebElement = self.wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, 'input[name="descricaoTipoDocumento"]')),
            )
            input_tipo_move.click()
            sleep(1)
            input_tipo_move.send_keys(self.bot_data.get("TIPO_PROTOCOLO"))

            sleep(1.5)

            input_move_option: WebElement = self.wait.until(
                ec.presence_of_element_located(
                    (By.CSS_SELECTOR, "div#ajaxAuto_descricaoTipoDocumento > ul > li:nth-child(1)"),
                ),
            )
            input_move_option.click()
            """ Corrigir elements """

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def add_new_file(self) -> None:
        """Upload the main petition file and its attachments for a protocol.

        Raises:
            ExecutionError: If file upload encounters an error.

        """
        try:
            """PARA CORRIGIR"""
            # file = str(self.bot_data.get("PETICAO_PRINCIPAL"))
            # message = "Inserindo Petição/Anexos..."
            # type_log = "log"
            # self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)
            # button_new_file = self.driver.find_element(
            #     By.CSS_SELECTOR, self.elements.includeContent
            # )
            # button_new_file.click()
            """ PARA CORRIGIR """

            file = str(self.bot_data.get("PETICAO_PRINCIPAL"))
            message = "Inserindo Petição/Anexos..."
            type_log = "log"
            self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)
            button_new_file = self.driver.find_element(By.CSS_SELECTOR, 'input#editButton[value="Adicionar"]')
            button_new_file.click()

            sleep(2.5)

            self.driver.switch_to.frame(self.driver.find_element(By.CSS_SELECTOR, self.elements.border))
            message = f"Enviando arquivo '{file}'"
            type_log = "log"
            self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)

            css_inptfile = 'input[id="conteudo"]'
            input_file_element: WebElement = WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, css_inptfile)),
            )

            file_to_upload = self.format_string(file)

            path_file = os.path.join(Path(self.path_args).parent.resolve(), file_to_upload)

            input_file_element.send_keys(path_file)

            self.wait_progressbar()

            message = "Arquivo enviado com sucesso!"
            type_log = "log"
            self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)

            sleep(1)
            type_file: WebElement = self.wait.until(ec.presence_of_element_located((By.ID, "tipo0")))
            type_file.click()
            sleep(0.25)
            type_options = type_file.find_elements(By.TAG_NAME, "option")
            for option in type_options:
                if option.text == self.bot_data.get("TIPO_ARQUIVO"):
                    option.click()
                    break

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def set_file_principal(self) -> None:
        """Designate the principal file among the uploaded documents.

        Raises:
            ExecutionError: If the main file is not set correctly.

        """
        try:
            tablefiles: WebElement = self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, "resultTable")))
            checkfiles = tablefiles.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")[0]
            radiobutton = checkfiles.find_elements(By.TAG_NAME, "td")[0].find_element(
                By.CSS_SELECTOR,
                self.elements.input_radio,
            )
            radiobutton.click()

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def more_files(self) -> None:
        """Upload additional files as defined in the bot data for protocol documentation.

        Raises:
            ExecutionError: When extra file upload operations fail.

        """
        try:
            sleep(0.5)

            anexos_list = [str(self.bot_data.get("ANEXOS"))]
            if "," in self.bot_data.get("ANEXOS"):
                anexos_list = self.bot_data.get("ANEXOS").__str__().split(",")

            for file in anexos_list:
                message = f"Enviando arquivo '{file}'"
                file_to_upload = self.format_string(file)
                type_log = "log"
                self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)
                input_file_element: WebElement = WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((By.XPATH, self.elements.conteudo)),
                )
                input_file_element.send_keys(
                    f"{os.path.join(Path(self.path_args).parent.resolve())}/{file_to_upload}",
                )
                self.wait_progressbar()
                message = f"Arquivo '{file}' enviado com sucesso!"
                type_log = "log"
            self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)

            sleep(3)
            tablefiles: WebElement = self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, "resultTable")))
            checkfiles = tablefiles.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")

            for pos, _ in enumerate(checkfiles):
                numbertipo = pos + 1
                sleep(0.75)
                try:
                    type_file = self.driver.find_element(By.ID, f"tipo{numbertipo}")
                    type_file.click()
                except Exception:
                    break
                sleep(0.25)
                type_options = type_file.find_elements(By.TAG_NAME, "option")
                type_anexos = str(self.bot_data.get("TIPO_ANEXOS")).lower()
                for option in type_options:
                    if str(option.text).lower() == type_anexos:
                        option.click()
                        break

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def sign_files(self) -> None:
        """Sign the protocol documents by providing the certificate password and confirming.

        Raises:
            ExecutionError: If the signing process fails.

        """
        message = "Assinando arquivos..."
        type_log = "log"
        self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)
        password_input = self.driver.find_element(By.ID, "senhaCertificado")
        password_input.click()
        senhatoken = f"{self.token}"
        password_input.send_keys(senhatoken)

        sign_button = self.driver.find_element(By.CSS_SELECTOR, self.elements.botao_assinar)
        sign_button.click()

        check_p_element = ""
        with suppress(TimeoutException):
            check_p_element: WebElement = WebDriverWait(self.driver, 5, 0.01).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, "#errorMessages > div.box-content")),
            )

        if check_p_element != "":
            raise PasswordError(message="Senha Incorreta!", bot_execution_id=self.pid)

        confirm_button = self.driver.find_element(By.CSS_SELECTOR, 'input#closeButton[value="Confirmar Inclusão"]')
        confirm_button.click()
        sleep(1)

        self.driver.switch_to.default_content()
        message = "Arquivos assinados"
        type_log = "log"
        self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)

    def finish_move(self) -> None:
        """Finalize the protocol move by confirming selections and concluding the operation."""
        message = f"Concluindo peticionamento do processo {self.bot_data.get('NUMERO_PROCESSO')}"
        type_log = "log"
        self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)
        # return_cmd = False

        # id_parte = self.id_part

        # if id_parte:
        #     with suppress(JavascriptException):
        #         cmd2 = f"return document.getElementById('{self.id_part}').checked"
        #         return_cmd = self.driver.execute_script(cmd2)
        #     if return_cmd is False:
        #         self.driver.find_element(By.ID, self.id_part).click()

        finish_button = self.driver.find_element(By.CSS_SELECTOR, self.elements.botao_concluir)
        finish_button.click()

    def screenshot_sucesso(self) -> list:
        """Capture and merge screenshots after successful protocol processing.

        Returns:
            list: A list containing the process number, success message, and screenshot file path.

        Raises:
            ExecutionError: If an error occurs during the screenshot capture.

        """
        try:
            table_moves = self.driver.find_element(By.CLASS_NAME, "resultTable")
            table_moves = table_moves.find_elements(
                By.XPATH,
                './/tr[contains(@class, "odd") or contains(@class, "even")][not(@style="display:none;")]',
            )

            table_moves[0].screenshot(os.path.join(self.output_dir_path, "tr_0.png"))

            expand = table_moves[0].find_element(By.CSS_SELECTOR, self.elements.expand_btn_projudi)
            expand.click()

            sleep(1.5)

            table_moves[1].screenshot(os.path.join(self.output_dir_path, "tr_1.png"))

            # Abra as imagens
            im_tr1 = Image.open(os.path.join(self.output_dir_path, "tr_0.png"))
            im_tr2 = Image.open(os.path.join(self.output_dir_path, "tr_1.png"))

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
            comprovante1 = f"{self.pid} - COMPROVANTE 1 - {self.bot_data.get('NUMERO_PROCESSO')}.png"
            combined_image.save(os.path.join(self.output_dir_path, comprovante1))

            filename = f"Protocolo - {self.bot_data.get('NUMERO_PROCESSO')} - PID{self.pid}.png"
            self.driver.get_screenshot_as_file(os.path.join(self.output_dir_path, filename))

            message = f"Peticionamento do processo Nº{self.bot_data.get('NUMERO_PROCESSO')} concluído com sucesso!"

            type_log = "log"
            self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)

            return [self.bot_data.get("NUMERO_PROCESSO"), message, comprovante1]

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def remove_files(self) -> None:
        """Delete the uploaded files from the protocol after processing.

        Raises:
            ExecutionError: If file removal fails.

        """
        tablefiles = None
        with suppress(TimeoutException):
            tablefiles: WebElement = WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located((By.CLASS_NAME, "resultTable")),
            )

        if tablefiles:
            sleep(1)
            checkfiles = tablefiles.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")

            for file in checkfiles:
                with suppress(NoSuchElementException, StaleElementReferenceException):
                    radiobutton = file.find_elements(By.TAG_NAME, "td")[0].find_element(
                        By.CSS_SELECTOR,
                        self.elements.input_radio,
                    )
                    radiobutton.click()

                    delete_file = self.driver.find_element(By.CSS_SELECTOR, self.elements.botao_deletar)
                    delete_file.click()

                    alert = None
                    with suppress(TimeoutException):
                        alert: type[Alert] = WebDriverWait(self.driver, 5).until(ec.alert_is_present())

                    if alert:
                        alert.accept()

                sleep(2)

    def wait_progressbar(self) -> None:
        """Wait until the progress bar completes the file upload or processing."""
        while True:
            try:
                divprogressbar: WebElement = self.wait.until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.css_containerprogressbar)),
                )
                divprogressbar = divprogressbar.find_element(By.CSS_SELECTOR, self.elements.css_divprogressbar)
                sleep(1)
                try:
                    # adicionar um suppress StaleElementReferenceException
                    get_style = divprogressbar.get_attribute("style")
                except Exception:
                    break

                if get_style != "":
                    sleep(1)

                elif get_style == "":
                    break

            except Exception:
                break
