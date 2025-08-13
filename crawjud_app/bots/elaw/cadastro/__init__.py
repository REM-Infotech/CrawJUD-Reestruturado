import time

from crawjud_app.bots.elaw.cadastro.cadastro import PreCadastro
from crawjud_app.bots.elaw.cadastro.complement import CadastroComplementar


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
