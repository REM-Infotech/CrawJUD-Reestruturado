"""Module for managing WebDriver instances and related utilities."""

from __future__ import annotations

import re  # noqa: F401
import traceback  # noqa: F401
from contextlib import suppress
from time import sleep
from typing import TYPE_CHECKING, Self

from selenium.common.exceptions import (  # noqa: F401
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec  # noqa: F401
from selenium.webdriver.support.wait import WebDriverWait  # noqa: F401

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver  # noqa: F401


class WebElementBot(WebElement):  # noqa: D101
    _cuurent_driver: WebDriver = None

    @classmethod
    def set_driver(cls, _driver: WebDriver) -> type[Self]:  # noqa: D102
        cls._cuurent_driver = _driver
        return cls

    def click(self) -> None:
        """Perform a click action on a web element with brief pauses.

        Args:
            element (WebElement): The target web element.

        Implements a click with pre- and post-click delays.

        """
        sleep(0.05)
        super().click()
        sleep(0.05)

    def send_keys(self, word: any) -> None:  # noqa: D102
        send = None
        for key in dir(Keys):
            if getattr(Keys, key) == word:
                send = ""
                self.clr.send_keys(word)
                break

        if send is None:
            self.click()
            for c in str(word):
                sleep(0.001)
                self.clr.send_keys(c)

    def double_click(self) -> None:
        """Double-click on the given webelement."""
        # action = ActionChains(self.driver)
        # action.double_click(element).perform()

    def select_item(self, text: str) -> None:
        """Select an item from a dropdown list based on exact text matching."""
        # element_id = re.search(
        #     r"^[^\[]+\[id=['\"]([^'\"]+)['\"]\]$", elemento
        # ).group()
        # if not element_id:
        #      = self.wait.until(
        #         ec.presence_of_element_located((By.CSS_SELECTOR, elemento))
        #     )
        #     element_id = element.get_attribute("id")

        # element_id = element_id.replace("_panel", "_input").replace(
        #     "_items", "_input"
        # )
        # return self.select2_elaw(
        #     self.driver.find_element(
        #         By.XPATH, f"//select[contains(@id, '{element_id}')]"
        #     ),
        #     text,
        # )

    def clear(self) -> None:  # noqa: D102
        self.click()
        sleep(0.5)
        self.clr.clear()
        sleep(1)

    # def sleep_load(self, *args: str, **kwargs: str) -> None:
    #     """Wait until the loading indicator for a specific element is hidden."""
    #     while True:
    #         sleep(0.5)
    #         load = None
    #         aria_value = None
    #         with suppress(TimeoutException):
    #             load: WebElement = WebDriverWait(self.driver, 5).until(
    #                 ec.presence_of_element_located((By.CSS_SELECTOR, element)),
    #             )

    #         if load:
    #             for attributes in ["aria-live", "aria-hidden", "class"]:
    #                 aria_value = load.get_attribute(attributes)

    #                 if not aria_value:
    #                     continue

    #                 break

    #             if aria_value is None or any(
    #                 value == aria_value
    #                 for value in [
    #                     "off",
    #                     "true",
    #                     "spinner--fullpage spinner--fullpage--show",
    #                 ]
    #             ):
    #                 break

    #         if not load:
    #             break

    def display_none(self) -> None:
        """Wait for an element's display style to change to 'none'.

        Args:
            elemento (WebElement): The element to monitor.

        """
        while True:
            style = self.get_attribute("style")
            if "display: none;" not in style:
                sleep(0.01)
                break

    def wait_caixa(self) -> None:
        """Wait until a modal dialog (caixa) is displayed on the page."""
        while True:
            check_wait = None
            with suppress(NoSuchElementException):
                check_wait = self.clr.find_element(
                    By.CSS_SELECTOR,
                    'div[id="modal:waitContainer"][style="position: absolute; z-index: 100; background-color: inherit; display: none;"]',  # noqa: E501
                )

            if check_wait:
                break

    def wait_fileupload(self) -> None:
        """Wait until the file upload progress completes.

        Checks repeatedly until no progress bar is present.
        """
        while True:
            sleep(0.05)
            div1 = 'div[class="ui-fileupload-files"]'
            div2 = 'div[class="ui-fileupload-row"]'
            div0 = 'div[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_2_1_9_g_1:uploadGedEFile"]'
            progress_bar = None

            div0progress_bar = self.clr.find_element(By.CSS_SELECTOR, div0)
            div1progress_bar = div0progress_bar.find_element(By.CSS_SELECTOR, div1)

            with suppress(NoSuchElementException):
                progress_bar = div1progress_bar.find_element(By.CSS_SELECTOR, div2)

            if progress_bar is None:
                break

    def scroll_to(self) -> None:
        """Scroll the view to the specified web element."""
        action = ActionChains(self.clr)
        action.scroll_to_element(self)
        sleep(0.5)

    def select2_elaw(self, to_search: str) -> None:
        """Select an option from a Select2 dropdown based on a search text.

        Args:
            to_search (str): The option text to search and select.

        """
        # selector: WebElement = self.wait.until(
        #     ec.presence_of_element_located((By.CSS_SELECTOR, element_select))
        # )

        # items = selector.find_elements(By.TAG_NAME, "option")
        # opt_itens: dict[str, str] = {}

        # elementsSelecting = element_select.replace("'", "'")  # noqa: N806
        # if '"' in elementsSelecting:
        #     elementsSelecting = element_select.replace('"', "'")  # noqa: N806

        # for item in items:
        #     value_item = item.get_attribute("value")
        #     cms = f"{elementsSelecting} > option[value='{value_item}']"
        #     text_item = self.driver.execute_script(f'return $("{cms}").text();')

        #     opt_itens.update({text_item.upper(): value_item})

        # value_opt = opt_itens.get(to_search_elaw.upper())

        # if value_opt:
        #     command = f"$('{element_select}').val(['{value_opt}']);"
        #     command2 = f"$('{element_select}').trigger('change');"

        #     if "'" in element_select:
        #         command = f"$(\"{element_select}\").val(['{value_opt}']);"
        #         command2 = f"$(\"{element_select}\").trigger('change');"

        #     self.driver.execute_script(command)
        #     self.driver.execute_script(command2)
