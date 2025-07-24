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
from selenium.webdriver.common.action_chains import ActionChains  # noqa: F401
from selenium.webdriver.common.by import By  # noqa: F401
from selenium.webdriver.remote.webelement import WebElement  # noqa: F401
from selenium.webdriver.support.wait import WebDriverWait  # noqa: F401
from webdriver_manager.core.download_manager import WDMDownloadManager
from webdriver_manager.core.driver_cache import DriverCacheManager  # noqa: F401
from webdriver_manager.core.file_manager import FileManager  # noqa: F401
from webdriver_manager.core.os_manager import OperationSystemManager  # noqa: F401

from webdriver._driver import config
from webdriver._types import BrowserOptions
from webdriver.web_element import WebElementBot

if TYPE_CHECKING:
    from selenium.webdriver.common.options import ArgOptions as Options
    from selenium.webdriver.common.service import Service
    from selenium.webdriver.remote.webdriver import WebDriver  # noqa: F401
    from selenium.webdriver.remote.webelement import WebElement  # noqa: F401


class DriverBot(webdriver.Remote):  # noqa: D101
    def __init__(  # noqa: D107
        self,
        selected_browser: BrowserOptions,
        execution_path: str | Path = None,
        *args: str,
        **kwargs: str,
    ) -> None:
        root_dir = (
            Path(execution_path)
            if execution_path
            else Path(__file__).home().joinpath("temp")
        )
        root_dir.mkdir(exist_ok=True)
        driver_config = config[selected_browser]

        # Configura o Manager
        system_manager = OperationSystemManager()
        file_manager = FileManager(os_system_manager=system_manager)
        _manager = driver_config["manager"](
            download_manager=WDMDownloadManager(),
            cache_manager=DriverCacheManager(
                file_manager=file_manager, root_dir=root_dir
            ),
            os_system_manager=system_manager,
        ).install()

        # Configura o service
        self._service = driver_config["service"](
            executable_path=_manager,
            port=kwargs.get("PORT", 0),
        )
        self._service.start()

        # Configura o executor
        driver_config["args_executor"].update({
            "remote_server_addr": self.service.service_url
        })
        _executor = driver_config["executor"](**driver_config["args_executor"])

        self._options = driver_config.get("options")()

        super().__init__(
            command_executor=_executor,
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
