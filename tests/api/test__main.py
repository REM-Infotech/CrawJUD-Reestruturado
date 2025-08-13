import pytest
import logging
from unittest.mock import AsyncMock, patch, MagicMock

import api._main as main_module

@pytest.mark.asyncio
async def test_main_app_runs_with_default_env(monkeypatch):
    """
    Testa se a função main_app executa corretamente com variáveis de ambiente padrão.

    Args:
        monkeypatch (pytest.MonkeyPatch): Permite modificar variáveis de ambiente.

    Returns:
        None: Não retorna valor.

    """
    # Mock funções e objetos dependentes
    mock_app = MagicMock()
    monkeypatch.setenv("API_HOST", "127.0.0.1")
    monkeypatch.setenv("API_PORT", "5000")

    with patch.object(main_module, "create_app", new=AsyncMock(return_value=mock_app)), \
         patch.object(main_module.io, "init_app", new=AsyncMock()), \
         patch.object(main_module, "register_namespaces", new=AsyncMock()), \
         patch.object(main_module.io, "run", new=AsyncMock()) as mock_run, \
         patch.object(main_module, "dict_config", return_value=({}, None)), \
         patch.object(main_module.Path, "cwd", return_value=main_module.Path(".")):
        await main_module.main_app()
        mock_run.assert_awaited_once()
        args, kwargs = mock_run.call_args
        assert kwargs["host"] == "127.0.0.1"
        assert kwargs["port"] == 5000
        assert kwargs["ssl_keyfile"] is None
        assert kwargs["ssl_certfile"] is None

@pytest.mark.asyncio
async def test_main_app_keyboard_interrupt(monkeypatch):
    """
    Testa se main_app ignora KeyboardInterrupt sem lançar exceção.

    Args:
        monkeypatch (pytest.MonkeyPatch): Permite modificar variáveis de ambiente.

    Returns:
        None: Não retorna valor.

    """
    async def raise_keyboard_interrupt(*args, **kwargs):
        raise KeyboardInterrupt

    with patch.object(main_module, "create_app", new=raise_keyboard_interrupt):
        # Não deve levantar exceção
        await main_module.main_app()
