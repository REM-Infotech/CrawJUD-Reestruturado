"""Module for managing WebDriver instances and related utilities."""

from __future__ import annotations

import json
from contextlib import suppress  # noqa: F401
from pathlib import Path
from time import sleep  # noqa: F401
from typing import TYPE_CHECKING

from browsermobproxy import Client as ProxyClient
from browsermobproxy import Server
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

BROWSERMOB_PATH = "/opt/browsermob-proxy/bin/browsermob-proxy/bin"


class DriverBot(webdriver.Remote):  # noqa: D101
    _proxy: ProxyClient = None

    @property
    def proxy(self) -> ProxyClient:  # noqa: D102
        return self._proxy

    @proxy.setter
    def proxy(self, new_value: ProxyClient) -> None:
        self._proxy = new_value

    def __init__(  # noqa: D107
        self,
        selected_browser: BrowserOptions,
        execution_path: str | Path = None,
        dir_extensions: str | Path = None,
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
        server = Server(BROWSERMOB_PATH)
        server.start()
        proxy = server.create_proxy()
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

        self._options = driver_config.get("options")(
            proxy=proxy,
            dir_extensions=dir_extensions,
            chrome_prefs={
                "download.prompt_for_download": False,
                "plugins.always_open_pdf_externally": True,
                "profile.default_content_settings.popups": 0,
                "printing.print_preview_sticky_settings.appState": json.dumps({
                    "recentDestinations": [
                        {"id": "Save as PDF", "origin": "local", "account": ""}
                    ],
                    "selectedDestinationId": "Save as PDF",
                    "version": 2,
                }),
                "download.default_directory": str(execution_path),
                "credentials_enable_service": True,
                "profile.password_manager_enabled": True,
            },
        )
        self.proxy = proxy
        self._options.enable_downloads = True
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
