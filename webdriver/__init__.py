"""Module for managing WebDriver instances and related utilities."""

from __future__ import annotations

import traceback  # noqa: F401
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.options import ArgOptions as Options
from selenium.webdriver.common.service import Service
from selenium.webdriver.firefox.service import Service as GeckoService
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait  # noqa: F401
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.download_manager import WDMDownloadManager
from webdriver_manager.core.driver_cache import DriverCacheManager  # noqa: F401
from webdriver_manager.core.file_manager import FileManager  # noqa: F401
from webdriver_manager.core.manager import DriverManager
from webdriver_manager.core.os_manager import OperationSystemManager  # noqa: F401
from webdriver_manager.firefox import GeckoDriverManager

from webdriver.configure import configure_chrome, configure_gecko

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver  # noqa: F401

BrowserOptions = Literal["chrome", "gecko", "firefox"]


class WebElementBot(WebElement): ...  # noqa: D101


class DriverBot(webdriver.Remote):  # noqa: D101
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
        super().__init__(
            _service.service_url, options=_options, web_element_cls=WebElementBot
        )

    def get_downloadable_files(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003, ANN201, D102
        arg = args
        kwarg = kwargs
        print(arg, kwarg)
