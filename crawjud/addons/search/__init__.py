"""Módulo de pesquisa CrawJUD."""

from contextlib import suppress
from datetime import datetime
from time import sleep

import pytz
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.exceptions import ExecutionError as ExecutionError

search_systems = {
    "elaw": ElawSearch,
    "esaj": EsajSearch,
    "projudi": ProjudiSearch,
}

search_types = Unior[type[ElawSearch], Type[EsajSearch], Type[ProjudiSearch]]
