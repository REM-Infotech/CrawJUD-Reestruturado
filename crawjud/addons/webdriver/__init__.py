"""Module for managing WebDriver instances and related utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as GeckoService
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager
from webdriver_manager.core.file_manager import FileManager
from webdriver_manager.core.os_manager import OperationSystemManager
from webdriver_manager.firefox import GeckoDriverManager

from crawjud.exceptions import DriverNotCreatedError

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver


class DriverBot:
    """Bot for handling WebDriver operations within CrawJUD framework."""

    preferred_browser: str

    def __init__(self, preferred_browser: str) -> None:
        """
        Initialize DriverBot with default settings for WebDriver operations in CrawJUD promptly.

        Args:
            None.

        """
        self.preferred_browser = preferred_browser

    def __call__(self) -> tuple[WebDriver, WebDriverWait]:
        driver = None
        if self.preferred_browser == "chrome":
            cache_manager = DriverCacheManager(file_manager=FileManager(os_system_manager=OperationSystemManager()))
            service = ChromeService(ChromeDriverManager(cache_manager=cache_manager).install())
            driver = webdriver.Chrome(options=self.configure_chrome(), service=service)
        elif self.preferred_browser == "gecko":
            options = self.configure_gecko()
            service = GeckoService(GeckoDriverManager().install())
            driver = webdriver.Firefox(options=options, service=service)

        if not driver:
            raise DriverNotCreatedError

        wait = WebDriverWait(driver, timeout=10)
        return driver, wait

    def configure_chrome():
        pass

    def configure_gecko():
        pass
