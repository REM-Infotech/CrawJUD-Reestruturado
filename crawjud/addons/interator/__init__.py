"""Interaction module: Interact with web elements using Selenium; perform clicks and keys actions promptly.

This module provides the Interact class containing helper functions for interacting with
web elements, including clicking, sending keys, and waiting for visual changes.
"""

from __future__ import annotations

from contextlib import suppress
from time import sleep
from typing import TYPE_CHECKING

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.exceptions.bot import NotFoundError

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement


class Interact:
    """Provide helper methods to interact with web elements via Selenium WebDriver.

    Each method ensures actions are performed with appropriate delays and error handling.
    """

    driver: WebDriver
    wait: WebDriverWait
    pid: str

    def __init__(self, driver: WebDriver, wait: WebDriverWait, pid: str) -> None:
        """Initialize Interact instance.

        Set up required attributes for element interactions.
        """
        self.driver = driver
        self.wait = wait
        self.pid = pid

    def send_key(self, element: WebElement, word: any) -> None:
        """Send keys to a web element character by character if needed.

        Args:
            element (WebElement): The target web element.
            word (any): The text or key code to send.

        Sends the whole key if it matches a Selenium key.

        """
        send = None
        for key in dir(Keys):
            if getattr(Keys, key) == word:
                send = ""
                element.send_keys(word)
                break

        if send is None:
            element.click()
            sleep(0.05)
            for c in str(word):
                sleep(0.001)
                element.send_keys(c)

    def click(self, element: WebElement) -> None:
        """Perform a click action on a web element with brief pauses.

        Args:
            element (WebElement): The target web element.

        Implements a click with pre- and post-click delays.

        """
        sleep(0.05)
        element.click()
        sleep(0.05)

    def double_click(self, element: WebElement) -> None:
        """Double-click on the given web element.

        Args:
            element (WebElement): The element to double-click.

        Uses ActionChains to perform the double click.

        """
        action = ActionChains(self.driver)
        action.double_click(element).perform()

    def select_item(self, elemento: str, text: str) -> bool:
        """Select an item from a dropdown list based on exact text matching.

        Args:
            elemento (str): CSS selector for the dropdown.
            text (str): The exact text of the item to select.

        Returns:
            bool: True if the selection is successful; otherwise, raises NotFoundError.

        """
        itens: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, elemento))
        )

        self.display_none(itens)
        sleep(0.5)

        if not text.isupper():
            itens = list(
                filter(
                    lambda item: not item.text.isupper(),
                    itens.find_element(By.CSS_SELECTOR, "ul").find_elements(
                        By.TAG_NAME, "li"
                    ),
                ),
            )

        elif text.isupper():
            itens = itens.find_element(By.TAG_NAME, "ul").find_elements(
                By.TAG_NAME, "li"
            )

        item = next(filter(lambda item: text == item.text, itens), None)

        if not item:
            raise NotFoundError(
                message=f'Item "{text}" não encontrado!', bot_execution_id=self.pid
            )

        action = ActionChains(self.driver)
        action.double_click(item).perform()

        return True

    def clear(self, element: WebElement) -> None:
        """Clear the text content of the specified web element.

        Args:
            element (WebElement): The element to clear.

        """
        element.click()
        sleep(0.5)
        element.clear()
        sleep(1)

    def sleep_load(self, element: str = 'div[id="j_id_3x"]') -> None:
        """Wait until the loading indicator for a specific element is hidden.

        Args:
            element (str, optional): A CSS selector for the loading element. Defaults to 'div[id="j_id_3x"]'.

        """
        while True:
            sleep(0.5)
            load = None
            aria_value = None
            with suppress(TimeoutException):
                load: WebElement = WebDriverWait(self.driver, 5).until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, element)),
                )

            if load:
                for attributes in ["aria-live", "aria-hidden", "class"]:
                    aria_value = load.get_attribute(attributes)

                    if not aria_value:
                        continue

                    break

                if aria_value is None or any(
                    value == aria_value
                    for value in [
                        "off",
                        "true",
                        "spinner--fullpage spinner--fullpage--show",
                    ]
                ):
                    break

            if not load:
                break

    def display_none(self, elemento: WebElement) -> None:
        """Wait for an element's display style to change to 'none'.

        Args:
            elemento (WebElement): The element to monitor.

        """
        while True:
            style = elemento.get_attribute("style")

            if "display: none;" not in style:
                sleep(0.01)
                break

    def wait_caixa(self) -> None:
        """Wait until a modal dialog (caixa) is displayed on the page."""
        while True:
            check_wait = None
            with suppress(NoSuchElementException):
                check_wait = self.driver.find_element(
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

            div0progress_bar = self.driver.find_element(By.CSS_SELECTOR, div0)
            div1progress_bar = div0progress_bar.find_element(By.CSS_SELECTOR, div1)

            with suppress(NoSuchElementException):
                progress_bar = div1progress_bar.find_element(By.CSS_SELECTOR, div2)

            if progress_bar is None:
                break

    def scroll_to(self, element: WebElement) -> None:
        """Scroll the view to the specified web element.

        Args:
            element (WebElement): The element to scroll into view.

        """
        action = ActionChains(self.driver)
        action.scroll_to_element(element)
        sleep(0.5)

    def select2_elaw(self, element_select: str, to_search_elaw: str) -> None:
        """Select an option from a Select2 dropdown based on a search text.

        Args:
            element_select (str): CSS selector for the Select2 element.
            to_search_elaw (str): The option text to search and select.

        """
        selector: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, element_select))
        )

        items = selector.find_elements(By.TAG_NAME, "option")
        opt_itens: dict[str, str] = {}

        elementsSelecting = element_select.replace("'", "'")  # noqa: N806
        if '"' in elementsSelecting:
            elementsSelecting = element_select.replace('"', "'")  # noqa: N806

        for item in items:
            value_item = item.get_attribute("value")
            cms = f"{elementsSelecting} > option[value='{value_item}']"
            text_item = self.driver.execute_script(f'return $("{cms}").text();')

            opt_itens.update({text_item.upper(): value_item})

        value_opt = opt_itens.get(to_search_elaw.upper())

        if value_opt:
            command = f"$('{element_select}').val(['{value_opt}']);"
            command2 = f"$('{element_select}').trigger('change');"

            if "'" in element_select:
                command = f"$(\"{element_select}\").val(['{value_opt}']);"
                command2 = f"$(\"{element_select}\").trigger('change');"

            self.driver.execute_script(command)
            self.driver.execute_script(command2)
