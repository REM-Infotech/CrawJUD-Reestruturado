"""Define TypedDicts para formulários jurídicos utilizados na interface FormBot.

Inclui estruturas para autenticação, upload de arquivos, pautas, partes de processo e PJE.
"""

from datetime import datetime
from typing import TypedDict

from werkzeug.datastructures import FileMultiDict


class JuridicoFormFileAuth(TypedDict):
    """Representa formulário com arquivo principal e autenticação.

    Args:
        xlsx (FileMultiDict): Arquivo Excel enviado.
        creds (str): Credenciais do usuário.
        state (str): Estado do formulário.
        confirm_fields (bool): Indica se os campos foram confirmados.
        periodic_task (bool): Indica se é tarefa periódica.
        task_name (str | None): Nome da tarefa agendada.
        task_hour_minute (str | None): Horário agendado no formato "HH:MM".
        email_notify (str | None): E-mail para notificação.
        days_task (list | None): Dias para execução da tarefa periódica.

    Returns:
        TypedDict: Estrutura de dados do formulário.

    """

    xlsx: FileMultiDict
    creds: str
    state: str
    confirm_fields: bool
    periodic_task: bool
    task_name: str | None
    task_hour_minute: str | None
    email_notify: str | None
    days_task: list | None


class JuridicoFormMultipleFiles(TypedDict):
    """Representa formulário com múltiplos arquivos e autenticação.

    Args:
        xlsx (FileMultiDict): Arquivo Excel principal.
        otherfiles (list[FileMultiDict]): Lista de outros arquivos enviados.
        creds (str): Credenciais do usuário.
        state (str): Estado do formulário.
        confirm_fields (bool): Indica se os campos foram confirmados.
        periodic_task (bool): Indica se é tarefa periódica.
        task_name (str | None): Nome da tarefa agendada.
        task_hour_minute (str | None): Horário agendado no formato "HH:MM".
        email_notify (str | None): E-mail para notificação.
        days_task (list | None): Dias para execução da tarefa periódica.

    Returns:
        TypedDict: Estrutura de dados do formulário.

    """

    xlsx: FileMultiDict
    otherfiles: list[FileMultiDict]
    creds: str
    state: str
    confirm_fields: bool
    periodic_task: bool
    task_name: str | None
    task_hour_minute: str | None
    email_notify: str | None
    days_task: list | None


class JuridicoFormOnlyAuth(TypedDict):
    """Representa formulário contendo apenas autenticação e opções de agendamento.

    Args:
        creds (str): Credenciais do usuário.
        state (str): Estado do formulário.
        confirm_fields (bool): Indica se os campos foram confirmados.
        periodic_task (bool): Indica se é tarefa periódica.
        task_name (str | None): Nome da tarefa agendada.
        task_hour_minute (str | None): Horário agendado no formato "HH:MM".
        email_notify (str | None): E-mail para notificação.
        days_task (list | None): Dias para execução da tarefa periódica.

    Returns:
        TypedDict: Estrutura de dados do formulário.

    """

    creds: str
    state: str
    confirm_fields: bool
    periodic_task: bool
    task_name: str | None
    task_hour_minute: str | None
    email_notify: str | None
    days_task: list | None


class JuridicoFormOnlyFile(TypedDict):
    """Representa formulário contendo apenas arquivo principal e opções de agendamento.

    Args:
        xlsx (FileMultiDict): Arquivo Excel enviado.
        state (str): Estado do formulário.
        confirm_fields (bool): Indica se os campos foram confirmados.
        periodic_task (bool): Indica se é tarefa periódica.
        task_name (str | None): Nome da tarefa agendada.
        task_hour_minute (str | None): Horário agendado no formato "HH:MM".
        email_notify (str | None): E-mail para notificação.
        days_task (list | None): Dias para execução da tarefa periódica.

    Returns:
        TypedDict: Estrutura de dados do formulário.

    """

    xlsx: FileMultiDict
    state: str
    confirm_fields: bool
    periodic_task: bool
    task_name: str | None
    task_hour_minute: str | None
    email_notify: str | None
    days_task: list | None


class JuridicoFormPautas(TypedDict):
    """Representa formulário para consulta de pautas em varas jurídicas.

    Args:
        varas (list[str]): Lista de varas jurídicas.
        data_inicio (str | datetime): Data inicial da consulta.
        data_fim (str | datetime): Data final da consulta.
        creds (str): Credenciais do usuário.
        state (str): Estado do formulário.
        confirm_fields (bool): Indica se os campos foram confirmados.
        periodic_task (bool): Indica se é tarefa periódica.
        task_name (str | None): Nome da tarefa agendada.
        task_hour_minute (str | None): Horário agendado no formato "HH:MM".
        email_notify (str | None): E-mail para notificação.
        days_task (list | None): Dias para execução da tarefa periódica.

    Returns:
        TypedDict: Estrutura de dados do formulário.

    """

    varas: list[str]
    data_inicio: str | datetime
    data_fim: str | datetime
    creds: str
    state: str
    confirm_fields: bool
    periodic_task: bool
    task_name: str | None
    task_hour_minute: str | None
    email_notify: str | None
    days_task: list | None


class JuridicoFormProcParte(TypedDict):
    """Representa formulário para consulta de processos por parte.

    Args:
        parte_name (str): Nome da parte.
        doc_parte (str): Documento da parte.
        polo_parte (str): Polo da parte no processo.
        varas (list[str]): Lista de varas jurídicas.
        data_inicio (str | datetime): Data inicial da consulta.
        data_fim (str | datetime): Data final da consulta.
        creds (str): Credenciais do usuário.
        state (str): Estado do formulário.
        confirm_fields (bool): Indica se os campos foram confirmados.
        periodic_task (bool): Indica se é tarefa periódica.
        task_name (str | None): Nome da tarefa agendada.
        task_hour_minute (str | None): Horário agendado no formato "HH:MM".
        email_notify (str | None): E-mail para notificação.
        days_task (list | None): Dias para execução da tarefa periódica.

    Returns:
        TypedDict: Estrutura de dados do formulário.

    """

    parte_name: str
    doc_parte: str
    polo_parte: str
    varas: list[str]
    data_inicio: str | datetime
    data_fim: str | datetime
    varas: list[str]
    creds: str
    state: str
    confirm_fields: bool
    periodic_task: bool
    task_name: str | None
    task_hour_minute: str | None
    email_notify: str | None
    days_task: list | None


class JuridicoFormPJE(TypedDict):
    """Representa formulário para consulta de processos no PJE.

    Args:
        varas (list[str]): Lista de varas jurídicas.
        data_inicio (str | datetime): Data inicial da consulta.
        data_fim (str | datetime): Data final da consulta.
        creds (str): Credenciais do usuário.
        state (str): Estado do formulário.
        confirm_fields (bool): Indica se os campos foram confirmados.
        periodic_task (bool): Indica se é tarefa periódica.
        task_name (str | None): Nome da tarefa agendada.
        task_hour_minute (str | None): Horário agendado no formato "HH:MM".
        email_notify (str | None): E-mail para notificação.
        days_task (list | None): Dias para execução da tarefa periódica.

    Returns:
        TypedDict: Estrutura de dados do formulário.

    """

    xlsx: str
    confirm_fields: bool
    confirm_fields: bool
    periodic_task: bool
    task_name: str | None
    task_hour_minute: str | None
    email_notify: str | None
    days_task: list | None
