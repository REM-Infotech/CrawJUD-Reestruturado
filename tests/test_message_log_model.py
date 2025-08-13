import pytest
from unittest.mock import patch
from utils.models.logs import MessageLog, ItemMessageList

# language: python



def test_messagelog_default_values() -> None:
    """Verifica se a instância de MessageLog utiliza valores padrão corretamente.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    Raises:
        AssertionError: Se algum valor padrão estiver incorreto.

    """
    log = MessageLog(row=0, total=0, errors=0, success=0, remaining=0)
    assert log.pid == "desconhecido"
    assert log.status == "Desconhecido"
    assert log.start_time == "00/00/0000 - 00:00:00"
    assert isinstance(log.messages, list)
    assert log.messages[0]["message"] == "Mensagem não informada"
    assert log.row == 0
    assert log.total == 0
    assert log.errors == 0
    assert log.success == 0
    assert log.remaining == 0

def test_messagelog_custom_values() -> None:
    """Testa a criação de MessageLog com valores customizados.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    Raises:
        AssertionError: Se os valores customizados não forem atribuídos corretamente.

    """
    messages = [
        ItemMessageList(message="Teste", id_log=1, type="info"),
        ItemMessageList(message="Erro", id_log=2, type="error"),
    ]
    log = MessageLog(
        pid="PROC123",
        messages=messages,
        status="Concluído",
        start_time="01/01/2024 - 10:00:00",
        row=10,
        total=100,
        errors=1,
        success=99,
        remaining=0,
    )
    assert log.pid == "PROC123"
    assert log.status == "Concluído"
    assert log.start_time == "01/01/2024 - 10:00:00"
    assert log.messages == messages
    assert log.row == 10
    assert log.total == 100
    assert log.errors == 1
    assert log.success == 99
    assert log.remaining == 0

def test_messagelog_model_dump() -> None:
    """Testa se o método model_dump retorna um dicionário correto.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    Raises:
        AssertionError: Se o dicionário retornado não corresponder aos dados do modelo.

    """
    messages = [ItemMessageList(message="Log", id_log=1, type="log")]
    log = MessageLog(
        pid="PID1",
        messages=messages,
        status="Em Execução",
        start_time="02/02/2024 - 12:00:00",
        row=5,
        total=50,
        errors=0,
        success=5,
        remaining=45,
    )
    dump = log.model_dump()
    assert isinstance(dump, dict)
    assert dump["pid"] == "PID1"
    assert dump["messages"] == messages
    assert dump["status"] == "Em Execução"
    assert dump["start_time"] == "02/02/2024 - 12:00:00"
    assert dump["row"] == 5
    assert dump["total"] == 50
    assert dump["errors"] == 0
    assert dump["success"] == 5
    assert dump["remaining"] == 45

def test_messagelog_query_logs_found() -> None:
    """Testa o método query_logs quando o log existe.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    Raises:
        AssertionError: Se o log não for encontrado corretamente.

    """
    # Mocka all_pks e get para simular registro existente
    with patch.object(MessageLog, "all_pks", return_value=["PID2"]), \
         patch.object(MessageLog, "get", return_value=MessageLog(
            pid="PID2", messages=[], status="OK", start_time="01/01/2024", row=1, total=1, errors=0, success=1, remaining=0)):
        log = MessageLog.query_logs("PID2")
        assert log is not None
        assert log.pid == "PID2"

def test_messagelog_query_logs_not_found() -> None:
    """Testa o método query_logs quando o log não existe.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    Raises:
        AssertionError: Se o método não retornar None para log inexistente.

    """
    with patch.object(MessageLog, "all_pks", return_value=["PID3"]), \
         patch.object(MessageLog, "get", return_value=None):
        log = MessageLog.query_logs("PIDX")
        assert log is None

def test_messagelog_all_data() -> None:
    """Testa o método all_data para retornar todos os logs.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    Raises:
        AssertionError: Se a lista retornada não contiver todos os logs simulados.

    """
    logs = [
        MessageLog(pid="P1", messages=[], status="OK", start_time="01", row=1, total=1, errors=0, success=1, remaining=0),
        MessageLog(pid="P2", messages=[], status="OK", start_time="02", row=2, total=2, errors=0, success=2, remaining=0),
    ]
    # Mocka all_data para retornar logs simulados
    with patch("utils.models.logs.all_data", return_value=logs):
        result = MessageLog.all_data()
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].pid == "P1"
        assert result[1].pid == "P2"
