from typing import TypeVar, Generic
import os
import pytest
from utils.types import StrPath, TReturnMessageMail, TReturnMessageExecutBot, TReturnMessageUploadFile

def test_strpath_accepts_str_and_pathlike() -> None:
    """Verifique se StrPath aceita str e PathLike.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    """
    caminho_str: StrPath = "caminho/arquivo.txt"
    caminho_pathlike: StrPath = os.path.join("caminho", "arquivo.txt")
    assert isinstance(caminho_str, str)
    assert isinstance(caminho_pathlike, str)

def test_return_message_mail_literal() -> None:
    """Verifique se TReturnMessageMail aceita apenas valor específico.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    """
    mensagem: TReturnMessageMail = "E-mail enviado com sucesso!"
    assert mensagem == "E-mail enviado com sucesso!"

def test_return_message_execut_bot_literal() -> None:
    """Verifique se TReturnMessageExecutBot aceita apenas valor específico.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    """
    mensagem: TReturnMessageExecutBot = "Execução encerrada com sucesso!"
    assert mensagem == "Execução encerrada com sucesso!"

def test_return_message_upload_file_literal() -> None:
    """Verifique se TReturnMessageUploadFile aceita apenas valor específico.

    Args:
        Nenhum.

    Returns:
        None: Não retorna valor.

    """
    mensagem: TReturnMessageUploadFile = "Arquivo enviado com sucesso!"
    assert mensagem == "Arquivo enviado com sucesso!"
