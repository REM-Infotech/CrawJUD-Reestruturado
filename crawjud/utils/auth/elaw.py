"""Módulo de controle de autenticação Elaw."""

from time import sleep
from typing import TYPE_CHECKING

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from crawjud.interfaces.controllers.bots.systems.elaw import ElawBot

if TYPE_CHECKING:
    from selenium.webdriver.remote.webelement import WebElement


class ElawAuth(ElawBot):
    """Classe de autenticação Elaw."""

    def auth(self) -> bool:
        self.driver.get("https://amazonas.elaw.com.br/login")

        # wait until page load
        username: WebElement = self.wait.until(
            ec.presence_of_element_located((By.ID, "username")),
        )
        username.send_keys(self.username)

        password: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "#password")),
        )
        password.send_keys(self.password)

        entrar: WebElement = self.wait.until(
            ec.presence_of_element_located((By.ID, "j_id_a_1_5_f")),
        )
        entrar.click()

        sleep(7)

        url = self.driver.current_url

        return url != "https://amazonas.elaw.com.br/login"
