"""Module for managing WebDriver instances and related utilities."""

from __future__ import annotations

from contextlib import suppress  # noqa: F401
from pathlib import Path
from time import sleep  # noqa: F401
from typing import TYPE_CHECKING

from selenium import webdriver
from selenium.common.exceptions import (  # noqa: F401
    NoSuchElementException,
)
from selenium.webdriver import Keys  # noqa: F401
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains  # noqa: F401
from selenium.webdriver.common.by import By  # noqa: F401
from selenium.webdriver.firefox.service import Service as GeckoService
from selenium.webdriver.remote.webelement import WebElement  # noqa: F401
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
    from selenium.webdriver.common.options import ArgOptions as Options
    from selenium.webdriver.common.service import Service
from webdriver._presets import (
    BrowserOptions,
)
from webdriver.web_element import WebElementBot

if TYPE_CHECKING:
    from selenium.webdriver.common.options import ArgOptions as Options
    from selenium.webdriver.common.service import Service
    from selenium.webdriver.remote.webdriver import WebDriver  # noqa: F401
    from selenium.webdriver.remote.webelement import WebElement  # noqa: F401


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


class DriverBot(webdriver.Remote):  # noqa: D101
    def __init__(  # noqa: D107
        self,
        selected_browser: BrowserOptions,
        execution_path: str | Path = None,
        *args: str,
        **kwargs: str,
    ) -> None:
        root_dir = Path(execution_path) or Path(__file__).home().joinpath("temp")
        root_dir.mkdir(exist_ok=True)

        system_manager = OperationSystemManager()
        file_manager = FileManager(os_system_manager=system_manager)
        cache_manager = DriverCacheManager(
            file_manager=file_manager, root_dir=root_dir
        )
        download_manager = WDMDownloadManager()
        _manager = dict_driver_manager[selected_browser](
            download_manager=download_manager,
            cache_manager=cache_manager,
            os_system_manager=system_manager,
        ).install()
        self._service = dict_services[selected_browser](
            executable_path=_manager,
            port=kwargs.get("PORT", 0),
        )
        self._service.start()
        self._options = dict_options[selected_browser]()

        super().__init__(
            command_executor=self._service.service_url,
            options=self._options,
            web_element_cls=WebElementBot,
        )

        self._wait = WebDriverWait(self, 5)

    def get_downloadable_files(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003, ANN201, D102
        arg = args
        kwarg = kwargs
        print(arg, kwarg)

    @property
    def options(self) -> Options:  # noqa: D102
        return self._options

    @property
    def service(self) -> Service:  # noqa: D102
        return self._service

    @property
    def wait(self) -> WebDriverWait:  # noqa: D102
        return self._wait
