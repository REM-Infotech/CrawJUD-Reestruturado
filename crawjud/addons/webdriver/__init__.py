"""Module for managing WebDriver instances and related utilities."""

from __future__ import annotations

import json
import traceback
from pathlib import Path
from typing import TYPE_CHECKING

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as GeckoOptions
from selenium.webdriver.firefox.service import Service as GeckoService
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager  # noqa: F401
from webdriver_manager.core.file_manager import FileManager  # noqa: F401
from webdriver_manager.core.os_manager import OperationSystemManager  # noqa: F401
from webdriver_manager.firefox import GeckoDriverManager

from crawjud.exceptions import DriverNotCreatedError

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver


class DriverBot:
    """Bot for handling WebDriver operations within CrawJUD framework."""

    preferred_browser: str
    execution_path: str
    list_args: list[str] = [
        "--ignore-ssl-errors=yes",
        "--ignore-certificate-errors",
        "--display=:99",
        "--window-size=1600,900",
        # "--no-sandbox",
        "--kiosk-printing",
        # disable Render and GPU
        # "--disable-gpu",
        # "--disable-dev-shm-usage",
        # "--disable-software-rasterizer",
        # "--disable-renderer-backgrounding",
        # "--disable-backgrounding-occluded-windows",
        "--disable-blink-features=AutomationControlled",
        # "--disable-features=MediaFoundationVideoCapture",
        # disable network prediction
        # "--no-proxy-server",
        # "--disable-software-rasterizer",
        # "--disable-features=VizDisplayCompositor",
    ]
    settings: dict[str, str | list[dict[str, str]] | int] = {
        "recentDestinations": [{"id": "Save as PDF", "origin": "local", "account": ""}],
        "selectedDestinationId": "Save as PDF",
        "version": 2,
    }

    def __init__(self, preferred_browser: str, execution_path: str) -> None:
        """
        Initialize DriverBot with default settings for WebDriver operations in CrawJUD promptly.

        Args:
            preferred_browser (str): The preferred browser for WebDriver operations.
            execution_path (str): The path to the execution directory.

        """
        self.preferred_browser = preferred_browser
        self.execution_path = execution_path

    def __call__(self) -> tuple[WebDriver, WebDriverWait]:
        """Instancia o driver e o wait.

        Returns:
            tuple[WebDriver, WebDriverWait]: Webdriver e WebDriverWait

        Raises:
            DriverNotCreatedError: Erro de criação do WebDriver

        """
        try:
            # system_manager = OperationSystemManager()
            # file_manager = FileManager(os_system_manager=system_manager)
            # cache_manager = DriverCacheManager(file_manager=file_manager)
            if self.preferred_browser == "chrome":
                options = self.configure_chrome()
                # driver_path = ChromeDriverManager(cache_manager=cache_manager).install()
                driver_path = ChromeDriverManager().install()
                service = ChromeService(driver_path)
                driver = webdriver.Chrome(options=options, service=service)
            elif self.preferred_browser == "gecko":
                options = self.configure_gecko()
                driver_path = GeckoDriverManager().install()
                service = GeckoService(driver_path)
                driver = webdriver.Firefox(options=options, service=service)

            wait = WebDriverWait(driver, timeout=10)
            return driver, wait

        except Exception as e:
            exc = "\n".join(traceback.format_exception_only(e))
            raise DriverNotCreatedError(message=exc) from e

    def configure_chrome(self) -> ChromeOptions:
        """Configurações do Options do Chrome.

        Returns:
            ChromeOptions: Instância do Options Chrome

        """
        chrome_options = ChromeOptions()

        list_args = self.list_args
        for argument in list_args:
            chrome_options.add_argument(argument)

        this_path = Path(__file__).parent.resolve().joinpath("extensions")
        for root, _, files in this_path.walk():
            for file_ in files:
                if ".crx" in file_:
                    path_plugin = str(root.joinpath(file_).resolve())
                    chrome_options.add_extension(path_plugin)

        chrome_prefs = {
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_settings.popups": 0,
            "printing.print_preview_sticky_settings.appState": json.dumps(self.settings),
            "download.default_directory": f"{self.execution_path}",
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        }

        chrome_options.add_argument("--incognito")
        chrome_options.add_experimental_option("prefs", chrome_prefs)

        return chrome_options

    def configure_gecko(self) -> GeckoOptions:
        """Configurações do Options do Gecko.

        Returns:
            GeckoOptions: Instância do Options Gecko

        """
        gecko_options = GeckoOptions()
        gecko_options.add_argument("--no-sandbox")
        gecko_options.add_argument("--disable-dev-shm-usage")

        return gecko_options
