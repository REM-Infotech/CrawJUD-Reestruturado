import time
import traceback
from contextlib import suppress

from selenium.webdriver.common.by import By

from crawjud_app.bots.elaw.cadastro.cadastro import PreCadastro
from crawjud_app.bots.elaw.cadastro.complement import CadastroComplementar
from crawjud_app.common.exceptions.bot import ExecutionError


class ElawCadadastro(CadastroComplementar, PreCadastro):
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

            except Exception as e:
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

        except Exception as e:
            self.logger.exception("".join(traceback.format_exception(exc=e)))
            raise ExecutionError(e=e) from e
