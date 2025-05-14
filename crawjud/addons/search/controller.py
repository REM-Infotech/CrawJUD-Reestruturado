"""Módulo controller de pesquisa de processos."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.support.wait import WebDriverWait


class SearchController:
    """Controller class for search operations."""

    message: str
    parte_name: str
    typebot: str
    bot_data: str
    type_log: str
    system: str
    driver: WebDriver
    wait: WebDriverWait
    url_segunda_instancia: str
    data_inicio: datetime
    data_fim: datetime
    vara: str
    doc_parte: str
    polo_parte: str

    def __init__(
        self,
        message: str,
        parte_name: str,
        typebot: str,
        bot_data: str,
        type_log: str,
        system: str,
        driver: WebDriver,
        wait: WebDriverWait,
        url_segunda_instancia: str,
        data_inicio: datetime,
        data_fim: datetime,
        vara: str,
        doc_parte: str,
        polo_parte: str,
    ) -> None:
        """Inicializador do SearchController."""
        self.message = message
        self.parte_name = parte_name
        self.typebot = typebot
        self.bot_data = bot_data
        self.type_log = type_log
        self.system = system
        self.driver = driver
        self.wait = wait
        self.url_segunda_instancia = url_segunda_instancia
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.vara = vara
        self.doc_parte = doc_parte
        self.polo_parte = polo_parte
