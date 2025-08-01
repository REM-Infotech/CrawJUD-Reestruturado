"""
Define a estrutura de dados para logs de mensagens do sistema.

Contém o tipo MessageLog, utilizado para padronizar as informações de logs
gerados durante a execução dos processos.

"""

from typing import TypedDict


class MessageLog(TypedDict):
    """
    Representa a estrutura de um registro de log de mensagem.

    Args:
        id_log (int): Identificador único do registro de log.
        message (str): Mensagem detalhada do log.
        type (str): Tipo do log (ex: "log", "error", "success").
        pid (str): Identificador do processo relacionado ao log.
        status (str): Status atual do processo (ex: "Em Execução", "Concluído", "Erro").
        start_time (str): Data e hora de início do processo.
        row (int): Número da linha atual processada.
        total (int): Total de linhas processadas.
        errors (int): Quantidade de erros encontrados.
        success (int): Quantidade de operações bem-sucedidas.
        remaining (int): Quantidade de linhas restantes para processamento.

    Returns:
        TypedDict: Estrutura contendo os campos padronizados para logs de mensagens.

    """

    message: (
        str
        | None  # e.g. "[(C3K7H5, log, 15, 19:37:15)> Salvando arquivos na pasta...]"
    )
    type: str | None  # e.g. "log", "error", "success"
    pid: str | None  # e.g. "C3K7H5"
    status: str  # e.g. "Em Execução", "Concluído", "Erro"
    start_time: str  # e.g. "01/01/2023 - 19:37:15"

    # counts
    row: int | None  # e.g. 15 (current row number)
    total: int | None  # e.g. 100 (total rows processed)
    errors: int | None  # e.g. 2 (number of errors encountered)
    success: int | None  # e.g. 98 (number of successful operations)
    remaining: int | None  # e.g. 85 (rows remaining to be processed)
