"""Module for managing WebDriver instances and related utilities."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, List, ParamSpec, TypeVar, Union

from selenium.webdriver.remote.webdriver import WebDriver  # noqa: F401
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.core.download_manager import WDMDownloadManager
from webdriver_manager.core.driver_cache import DriverCacheManager
from webdriver_manager.core.file_manager import FileManager
from webdriver_manager.core.os_manager import OperationSystemManager

from webdriver._driver import config

if TYPE_CHECKING:
    from selenium.webdriver.common.service import Service

    from webdriver._types import BrowserOptions, ChromeConfig, FirefoxConfig
    from webdriver.config.chrome import ChromeOptions
    from webdriver.config.firefox import FirefoxOptions
    from webdriver.web_element import WebElementBot


work_dir = Path(__file__).cwd()

P = ParamSpec("P")
T = TypeVar("T")


class DriverBot(WebDriver):  # noqa: D101
    def __init__(  # noqa: D107
        self,
        selected_browser: BrowserOptions,
        execution_path: str | Path = None,
        *args: str,
        **kwargs: str,
    ) -> None:
        driver_config = config[selected_browser]

        # Configura o Manager
        self._configure_manager(
            driver_config=driver_config,
            execution_path=execution_path,
        )
        self._configure_service(driver_config=driver_config, **kwargs)
        self._configure_executor(driver_config=driver_config)
        self._configure_options(driver_config=driver_config, **kwargs)

        super().__init__(
            command_executor=self._executor,
            options=self._options,
            web_element_cls=WebElementBot.set_driver(self),
        )

        self._wait = WebDriverWait(self, 5)

    def _configure_manager(
        self,
        driver_config: ChromeConfig | FirefoxConfig,
        execution_path: str | Path = None,
    ) -> str:
        root_dir = (
            Path(execution_path) if execution_path else work_dir.joinpath("temp")
        )
        root_dir.mkdir(exist_ok=True)

        system_manager = OperationSystemManager()
        file_manager = FileManager(os_system_manager=system_manager)
        _manager = driver_config["manager"](
            download_manager=WDMDownloadManager(),
            cache_manager=DriverCacheManager(
                file_manager=file_manager, root_dir=root_dir
            ),
            os_system_manager=system_manager,
        )
        self._manager = _manager
        return _manager

    def _configure_service(
        self,
        driver_config: ChromeConfig | FirefoxConfig,
        **kwargs: Any,
    ) -> None:
        self._service = driver_config["service"](
            executable_path=self._manager.install(),
            port=kwargs.get("PORT", 0),
        )
        self._service.start()

    def _configure_executor(
        self, driver_config: ChromeConfig | FirefoxConfig
    ) -> None:
        driver_config["args_executor"].update({
            "remote_server_addr": self._service.service_url
        })
        self._executor = driver_config["executor"](**driver_config["args_executor"])

    def _configure_options(
        self,
        driver_config: ChromeConfig | FirefoxConfig,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._options = driver_config.get("options")(*args, **kwargs)
        self._options.enable_downloads = True

    @property
    def options(self) -> Union[FirefoxOptions, ChromeOptions]:  # noqa: D102
        return self._options

    @property
    def service(self) -> Service:  # noqa: D102
        return self._service

    @property
    def wait(self) -> WebDriverWait:  # noqa: D102
        return self._wait

    @wait.setter
    def wait(self, new_wait: WebDriverWait) -> None:
        self._wait = new_wait

    def find_element(self, *args: P.args, **kwargs: P.kwargs) -> WebElementBot:  # noqa: D102
        return super().find_element(*args, kwargs)

    def find_elements(self, *args: P.args, **kwargs: P.kwargs) -> List[WebElementBot]:  # noqa: D102
        return super().find_elements(*args, kwargs)
