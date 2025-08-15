"""Empty."""

import time
import traceback
from contextlib import suppress
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from crawjud.bots.elaw.cadastro.cadastro import PreCadastro
from crawjud.bots.elaw.cadastro.complement import CadastroComplementar
from crawjud.common.exceptions.bot import ExecutionError
from crawjud.common.exceptions.raises import raise_execution_error

campos_validar: list[str] = [
    "estado",
    "comarca",
    "foro",
    "vara",
    "divisao",
    "fase",
    "provimento",
    "fato_gerador",
    "objeto",
    "tipo_empresa",
    "tipo_entrada",
    "acao",
    "escritorio_externo",
    "classificacao",
    "toi_criado",
    "nota_tecnica",
    "liminar",
]


class ElawCadadastro(CadastroComplementar, PreCadastro):
    """Empty."""

    def __init__(
        self,
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Initialize the Cadastro instance.

        This method initializes the cadastro class by calling the base class's
        __init__ method, setting up the bot, performing authentication, and initializing
        the start time.

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
        """Execute the main processing loop for registrations.

        Iterates over each entry in the data frame and processes it.
        Handles authentication and error logger.

        """
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
                windows = self.driver.window_handles

                if len(windows) == 0:
                    with suppress(Exception):
                        self.driver_launch(
                            message="Webdriver encerrado inesperadamente, reinicializando...",
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
        try:
            self.bot_data = self.elaw_formats(self.bot_data)
            pid = self.pid
            prt = self.prt
            driver = self.driver
            elements = self.elements
            bot_data = self.bot_data
            search = self.search_bot()

            if search is True:
                self.append_success([
                    bot_data.get("NUMERO_PROCESSO"),
                    "Processo já cadastrado!",
                    pid,
                ])

            elif search is not True:
                self.message = "Processo não encontrado, inicializando cadastro..."
                self.type_log = "log"
                prt()

                btn_newproc = driver.find_element(
                    By.CSS_SELECTOR,
                    elements.botao_novo,
                )
                btn_newproc.click()

                start_time = time.perf_counter()

                self.area_direito()
                self.subarea_direito()
                self.next_page()
                self.info_localizacao()
                self.informa_estado()
                self.informa_comarca()
                self.informa_foro()
                self.informa_vara()
                self.informa_proceso()
                self.informa_empresa()
                self.set_classe_empresa()
                self.parte_contraria()
                self.uf_proc()
                self.acao_proc()
                self.advogado_interno()
                self.adv_parte_contraria()
                self.data_distribuicao()
                self.info_valor_causa()
                self.escritorio_externo()
                self.tipo_contingencia()

                end_time = time.perf_counter()
                execution_time = end_time - start_time
                calc = execution_time / 60
                splitcalc = str(calc).split(".")
                minutes = int(splitcalc[0])
                seconds = int(float(f"0.{splitcalc[1]}") * 60)

                self.message = (
                    f"Formulário preenchido em {minutes} minutos e {seconds} segundos"
                )
                self.type_log = "log"
                prt()

                self.salvar_tudo()

                if self.confirm_save() is True:
                    self.print_comprovante()

        except ExecutionError as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
            self.logger.exception("".join(traceback.format_exception(exc=e)))
            raise ExecutionError(e=e) from e

    def validar_campos(self) -> None:
        """Validate the required fields.

        This method checks each required field in the process to ensure
        they are properly filled. It logs the validation steps and raises
        an error if any required field is missing.
        """
        self.message = "Validando campos"
        self.type_log = "log"
        self.prt()

        validar: dict[str, str] = {
            "NUMERO_PROCESSO": self.bot_data.get("NUMERO_PROCESSO"),
        }
        message_campo: list[str] = []

        for campo in campos_validar:
            campo_validar: str = self.elements.dict_campos_validar.get(campo)
            command = f"return $('{campo_validar}').text()"
            element = self.driver.execute_script(command)

            if not element or element.lower() == "selecione":
                message = f'Campo "{campo}" não preenchido'
                raise_execution_error(message)

            message_campo.append(
                f'<p class="fw-bold">Campo "{campo}" Validado | Texto: {element}</p>',
            )
            validar.update({campo.upper(): element})

        self.append_validarcampos([validar])
        message_campo.append('<p class="fw-bold">Campos validados!</p>')
        self.message = "".join(message_campo)
        self.type_log = "info"
        self.prt()

    def validar_advogado(self) -> str:
        """Validate the responsible lawyer.

        This method ensures that the responsible lawyer field is filled and
        properly selected. It logs the validation steps and raises an error
        if the field is not properly filled.

        Returns:
        str
            The name of the responsible lawyer.


        Raises:
            ExecutionError: If the responsible lawyer field is not filled.

        """
        self.message = "Validando advogado responsável"
        self.type_log = "log"
        self.prt()

        campo_validar = self.elements.dict_campos_validar.get("advogado_interno")
        command = f"return $('{campo_validar}').text()"
        element = self.driver.execute_script(command)

        if not element or element.lower() == "selecione":
            raise ExecutionError(
                message='Campo "Advogado Responsável" não preenchido',
            )

        self.message = f'Campo "Advogado Responsável" | Texto: {element}'
        self.type_log = "info"
        self.prt()

        sleep(0.5)

        return element

    def validar_advs_participantes(self) -> None:
        """Validate participating lawyers.

        This method ensures that the responsible lawyer is present in the
        list of participating lawyers. It logs the validation steps and
        raises an error if the responsible lawyer is not found.

        Raises:
            ExecutionError: If the responsible lawyer
                is not found in the list of participating lawyers.

        """
        data_bot = self.bot_data
        adv_name = data_bot.get("ADVOGADO_INTERNO", self.validar_advogado())

        if not adv_name.strip():
            raise ExecutionError(
                message="Necessário advogado interno para validação!",
            )

        self.message = "Validando advogados participantes"
        self.type_log = "log"
        self.prt()

        tabela_advogados = self.driver.find_element(
            By.CSS_SELECTOR,
            self.elements.tabela_advogados_resp,
        )

        not_adv = None
        with suppress(NoSuchElementException):
            tr_not_adv = self.elements.tr_not_adv
            not_adv = tabela_advogados.find_element(By.CSS_SELECTOR, tr_not_adv)

        if not_adv is not None:
            raise ExecutionError(message="Sem advogados participantes!")

        advs = tabela_advogados.find_elements(By.TAG_NAME, "tr")

        for adv in advs:
            advogado = adv.find_element(By.TAG_NAME, "td").text
            if advogado.lower() == adv_name.lower():
                break

        else:
            raise ExecutionError(
                message=(
                    "Advogado responsável não encontrado",
                    " na lista de advogados participantes!",
                ),
            )

        self.message = "Advogados participantes validados"
        self.type_log = "info"
        self.prt()
