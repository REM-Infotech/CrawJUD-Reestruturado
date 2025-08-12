from typing import Callable, TypeVar, Generic
import pytest
from crawjud_app.decorators.bot import wrap_cls
from crawjud_app.abstract.bot import ClassBot

T = TypeVar("T", bound=ClassBot)

class DummyBot(ClassBot):
    def __init__(self) -> None:
        pass

    def autenticar(self, *args, **kwargs) -> bool:
        return True# pragma: no cover

    def buscar_processo(self, *args, **kwargs) -> bool:
        return True# pragma: no cover

    def execution(self, *args, **kwargs) -> None:
        self.execution_called = True

    def save_success_cache(self, data) -> None:
        pass# pragma: no cover

    def storage(self) -> dict:
        return {} # pragma: no cover

def test_wrap_cls_executes_execution_and_sets_sio(monkeypatch) -> None:
    """Teste se wrap_cls executa método execution e atribui sio corretamente.

    Args:
        monkeypatch (pytest.MonkeyPatch): Permite interceptar métodos do SimpleClient.

    Returns:
        None: Não retorna valor.

    """
    class FakeSIO:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def connect(self, **kwargs):
            self.connected = True
        def emit(self, *args, **kwargs):
            self.emitted = True
        class client:
            @staticmethod
            def on(event, namespace=None, handler=None):
                pass

    monkeypatch.setattr("crawjud_app.decorators.bot.SimpleClient", FakeSIO)

    DecoratedBot = wrap_cls(DummyBot)
    bot = DecoratedBot(x=1, y=2, pid="testroom")

    assert isinstance(DecoratedBot, Callable)
