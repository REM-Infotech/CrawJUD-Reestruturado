from typing import TypeVar, Generic, Any
import pytest
from crawjud_app.decorators.bot import wrap_init
from crawjud_app.abstract.bot import ClassBot

T = TypeVar("T", bound=ClassBot)

class DummyBot(ClassBot):
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def autenticar(self, *args, **kwargs) -> bool:
        return super().autenticar(*args, **kwargs)# pragma: no cover

    def buscar_processo(self, *args, **kwargs) -> bool:
        return super().buscar_processo(*args, **kwargs)# pragma: no cover

    def execution(self) -> None:
        return super().execution()# pragma: no cover

    def save_success_cache(self, data) -> None:
        return super().save_success_cache(data)# pragma: no cover

    def storage(self) -> Any:
        return super().storage()# pragma: no cover

def test_wrap_init_decorates_init_and_prints_args(monkeypatch) -> None:
    """Teste se wrap_init decora __init__ e exibe argumentos corretamente.

    Args:
        monkeypatch (pytest.MonkeyPatch): Permite interceptar chamadas tqdm.write.

    Returns:
        None: Não retorna valor.

    """
    logs = []

    def fake_write(msg: str) -> None:
        logs.append(msg)

    monkeypatch.setattr("tqdm.tqdm.write", fake_write)

    DecoratedBot = wrap_init(DummyBot)
    bot = DecoratedBot(x=1, y=2)

    assert isinstance(bot, DummyBot)
    assert bot.x == 1
    assert bot.y == 2
    # Verifica se mensagem de instanciamento foi registrada
    assert any("Instanciando DummyBot" in log for log in logs)
