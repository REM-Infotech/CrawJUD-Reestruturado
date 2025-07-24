"""Module for managing WebDriver instances and related utilities."""

from __future__ import annotations

import traceback
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.options import ArgOptions as Options
from selenium.webdriver.common.service import Service
from selenium.webdriver.firefox.service import Service as GeckoService
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.download_manager import WDMDownloadManager
from webdriver_manager.core.driver_cache import DriverCacheManager  # noqa: F401
from webdriver_manager.core.file_manager import FileManager  # noqa: F401
from webdriver_manager.core.manager import DriverManager
from webdriver_manager.core.os_manager import OperationSystemManager  # noqa: F401
from webdriver_manager.firefox import GeckoDriverManager

from crawjud.addons.webdriver.configure import configure_chrome, configure_gecko
from crawjud.exceptions import DriverNotCreatedError

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver

BrowserOptions = Literal["chrome", "gecko", "firefox"]


class BotDriver(webdriver.Remote):  # noqa: D101
    dict_services: dict[str, type[Service]] = {
        "chrome": ChromeService,
        "firefox": GeckoService,
        "gecko": GeckoService,
    }

    dict_options: dict[str, type[Options]] = {
        "chrome": configure_chrome,
        "firefox": configure_gecko,
        "gecko": configure_gecko,
    }

    dict_driver_manager: dict[str, type[DriverManager]] = {
        "chrome": ChromeDriverManager,
        "firefox": GeckoDriverManager,
        "gecko": GeckoDriverManager,
    }

    def __init__(self, selected_browser: BrowserOptions) -> None:  # noqa: D107
        root_dir = Path(__file__).cwd().joinpath("temp")
        root_dir.mkdir(exist_ok=True)

        system_manager = OperationSystemManager()
        file_manager = FileManager(os_system_manager=system_manager)
        cache_manager = DriverCacheManager(
            file_manager=file_manager, root_dir=root_dir
        )
        download_manager = WDMDownloadManager()
        _manager = self.dict_driver_manager[selected_browser](
            download_manager=download_manager,
            cache_manager=cache_manager,
            os_system_manager=system_manager,
        )

        _options = self.dict_options[selected_browser]()
        _service = self.dict_services[selected_browser](_manager)

        super().__init__(_service.service_url, options=_options)

    def get_downloadable_files(self, *args, **kwargs):  # noqa: ANN002, ANN003, ANN201, D102
        arg = args
        kwarg = kwargs
        print(arg, kwarg)


class ChromeDriver(webdriver.Chrome):  # noqa: D101
    def get_downloadable_files(self, *args, **kwargs):  # noqa: ANN002, ANN003, ANN201, D102
        arg = args
        kwarg = kwargs
        print(arg, kwarg)


class GeckoDriver(webdriver.Firefox):  # noqa: D101
    def get_downloadable_files(self, *args, **kwargs):  # noqa: ANN002, ANN003, ANN201, D102
        arg = args
        kwarg = kwargs

        print(arg, kwarg)


class DriverBot:
    """Bot for handling WebDriver operations within CrawJUD framework."""

    preferred_browser: str
    execution_path: str
    list_args: list[str] = [
        "--ignore-ssl-errors=yes",
        "--ignore-certificate-errors",
        "--display=:0",
        "--window-size=1600,900",
        "--no-sandbox",
        "--kiosk-printing",
        # disable Render and GPU
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-software-rasterizer",
        "--disable-renderer-backgrounding",
        "--disable-backgrounding-occluded-windows",
        "--disable-blink-features=AutomationControlled",
        # "--disable-features=MediaFoundationVideoCapture",
        # disable network prediction
        # "--no-proxy-server",
        # "--disable-software-rasterizer",
        # "--disable-features=VizDisplayCompositor",
    ]
    settings: dict[str, str | list[dict[str, str]] | int] = {
        "recentDestinations": [
            {"id": "Save as PDF", "origin": "local", "account": ""}
        ],
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
            root_dir = Path(__file__).cwd().joinpath("temp")

            root_dir.mkdir(exist_ok=True)

            system_manager = OperationSystemManager()
            file_manager = FileManager(os_system_manager=system_manager)
            cache_manager = DriverCacheManager(
                file_manager=file_manager, root_dir=root_dir
            )
            driver = None
            download_manager = WDMDownloadManager()
            if self.preferred_browser == "chrome":
                options = self.configure_chrome()
                # driver_path = ChromeDriverManager(cache_manager=cache_manager).install()
                driver_path = ChromeDriverManager().install()
                service = ChromeService(driver_path)
                driver = ChromeDriver(options=options, service=service)

            elif self.preferred_browser == "gecko":
                options = self.configure_gecko()
                driver_path = GeckoDriverManager(
                    download_manager=download_manager,
                    cache_manager=cache_manager,
                    os_system_manager=system_manager,
                ).install()
                service = GeckoService(driver_path)
                driver = GeckoDriver(options=options, service=service)
            wait = WebDriverWait(driver, timeout=10)
            return driver, wait

        except Exception as e:
            exc = "\n".join(traceback.format_exception_only(e))
            raise DriverNotCreatedError(message=exc) from e
