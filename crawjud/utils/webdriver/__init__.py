"""Module for managing WebDriver instances and related utilities."""

from __future__ import annotations

from contextlib import suppress
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    AnyStr,
    ClassVar,
    ParamSpec,
)

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm
from webdriver_manager.core.download_manager import WDMDownloadManager
from webdriver_manager.core.driver_cache import DriverCacheManager
from webdriver_manager.core.file_manager import FileManager
from webdriver_manager.core.os_manager import OperationSystemManager

from crawjud.utils.webdriver._driver import config
from crawjud.utils.webdriver.config.proxy import (
    ContentData,
    Cookie,
    DictHARProxy,
    EntryRequest,
    HARProxy,
    Header,
    Page,
    RequestData,
    ResponseData,
)
from crawjud.utils.webdriver.config.proxy import (
    CreatorInfo as CreatorInfo,
)
from crawjud.utils.webdriver.web_element import WebElementBot

if TYPE_CHECKING:
    from collections.abc import Generator

    from browsermobproxy import Client
    from selenium.webdriver.common.service import Service

    from crawjud.utils.webdriver._types import (
        BrowserOptions,
        ChromeConfig,
        FirefoxConfig,
    )
    from crawjud.utils.webdriver.config.chrome import ChromeOptions
    from crawjud.utils.webdriver.config.firefox import FirefoxOptions

work_dir = Path(__file__).cwd()

P = ParamSpec("P")


class DriverBot[T](WebDriver):  # noqa: D101
    _har: DictHARProxy = None
    _log: ClassVar[dict[str, DictHARProxy]] = {}
    _count: int = 0

    def __init__(  # noqa: D107
        self,
        selected_browser: BrowserOptions,
        execution_path: str | Path | None = None,
        *,
        with_proxy: bool = False,
        **kwargs: T,
    ) -> None:
        driver_config = config[selected_browser]
        tqdm.write(with_proxy)
        kwargs.update({"with_proxy": with_proxy})
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
        self.new_har()

    def _configure_manager(
        self,
        driver_config: ChromeConfig | FirefoxConfig,
        execution_path: str | Path = __file__,
    ) -> str:
        root_dir = work_dir.joinpath("temp")
        if execution_path and execution_path != __file__:
            root_dir = Path(execution_path)

        root_dir.mkdir(exist_ok=True, parents=True)

        system_manager = OperationSystemManager()
        file_manager = FileManager(os_system_manager=system_manager)
        manager_ = driver_config["manager"](
            download_manager=WDMDownloadManager(),
            cache_manager=DriverCacheManager(
                file_manager=file_manager,
                root_dir=root_dir,
            ),
            os_system_manager=system_manager,
        )
        self._manager = manager_
        return manager_

    def _configure_service(
        self,
        driver_config: ChromeConfig | FirefoxConfig,
        **kwargs: T,
    ) -> None:
        self._service = driver_config["service"](
            executable_path=self._manager.install(),
            port=kwargs.get("PORT", 0),
        )
        self._service.start()

    def _configure_executor(
        self,
        driver_config: ChromeConfig | FirefoxConfig,
    ) -> None:
        driver_config["args_executor"].update({
            "remote_server_addr": self._service.service_url,
        })
        self._executor = driver_config["executor"](**driver_config["args_executor"])

    def _configure_options(
        self,
        driver_config: ChromeConfig | FirefoxConfig,
        *args: T,
        **kwargs: T,
    ) -> None:
        self._options = driver_config.get("options")(*args, **kwargs)
        self._options.enable_downloads = True

    @property
    def options(self) -> FirefoxOptions | ChromeOptions:
        return self._options

    @property
    def service(self) -> Service:
        return self._service

    @property
    def wait(self) -> WebDriverWait:
        return self._wait

    def quit(self) -> None:
        with suppress(Exception):
            self.options.proxy_client.close()
            self.options.proxy_server.stop()

        return super().quit()

    @wait.setter
    def wait(self, new_wait: WebDriverWait) -> None:
        self._wait = new_wait

    def find_element(self, *args: P.args, **kwargs: P.kwargs) -> WebElementBot:
        return super().find_element(*args, **kwargs)

    def find_elements(self, *args: P.args, **kwargs: P.kwargs) -> list[WebElementBot]:
        return super().find_elements(*args, **kwargs)

    @property
    def current_HAR(self) -> HARProxy:  # noqa: N802
        if not self._har:
            self._log = self.client.har
            self._har = self._log.get("log")

        self._har.update({
            "entries": self._entry_generator(),
            "pages": self._pages_generator(),
        })

        return HARProxy(**self._har)

    def new_har(
        self,
        ref: AnyStr = "default",
        options: T = None,
        title: T = None,
    ) -> None:
        if options is None:
            options = {"captureHeaders": True, "captureContent": True}
        self.client.new_har(ref, options, title)

    @property
    def client(self) -> Client:
        return self.options.proxy_client

    def _entry_generator(
        self,
    ) -> Generator[EntryRequest, Any, None]:
        slice_ = self._count
        list_entries: list = self.client.har.get("log").get("entries")
        self._count = len(self.client.har.get("log").get("entries"))
        if slice_ > 0:
            list_entries: list = list_entries[slice_:]

        for entry in list_entries:
            yield EntryRequest(
                pageref=entry.get("pageref"),
                startedDateTime=entry.get("startedDateTime"),
                request=self._request(entry.get("request")),
                response=self._response(entry.get("response")),
                cache=entry.get("cache", {}),
                timings=entry.get("timings", {}),
                serverIPAddress=entry.get("serverIPAddress", "127.0.0.1"),
                time=entry.get("time", 0),
            )

    def _pages_generator(self) -> Generator[Page, Any, None]:
        for page in self.client.har.get("log").get("pages"):
            yield Page(**page)

    def _request(self, request: dict) -> RequestData:
        return RequestData(
            method=request.get("method"),
            httpVersion=request.get("httpVersion"),
            url=request.get("url"),
            cookies=[Cookie(**cookie) for cookie in request.get("cookies")],
            headers=[Header(**header) for header in request.get("headers")],
            queryString=[""],
            headersSize=request.get("headersSize"),
            bodySize=request.get("bodySize"),
            comment=request.get("comment"),
        )

    def _response(self, response: dict) -> ResponseData:
        return ResponseData(
            status=response.get("status", 200),
            statusText=response.get("statusText", ""),
            httpVersion=response.get("httpVersion", ""),
            cookies=[Cookie(**cookie) for cookie in response.get("cookies")],
            headers=[Header(**header) for header in response.get("headers")],
            content=ContentData(
                size=response.get("content", {}).get("size", 0),
                mimeType=response.get("content", {}).get("mimeType", ""),
                comment=response.get("content", {}).get("comment", ""),
                text=response.get("content", {}).get("text", ""),
            ),
            redirectURL=response.get("redirectURL"),
            headersSize=response.get("headersSize", 0),
            bodySize=response.get("bodySize", 0),
            comment=response.get("comment", ""),
        )
