from __future__ import annotations

from pathlib import Path
from typing import (
    Callable,
    Literal,
    ParamSpec,
    Type,
    TypedDict,
    TypeVar,
    Union,
)

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.remote_connection import ChromeRemoteConnection
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as GeckoOptions
from selenium.webdriver.firefox.remote_connection import FirefoxRemoteConnection
from selenium.webdriver.firefox.service import Service as GeckoService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

P = ParamSpec("optionsConstructor", bound=Union[str, Path])
BrowserOptions = Literal["chrome", "gecko", "firefox"]
TExtensionsPath = TypeVar("ExtensionsPath", bound=Union[str, Path])

driver_options = TypeVar(
    "DriverOptions",
    bound=Union[Callable[..., GeckoOptions] | Callable[..., ChromeOptions]],
)

ChromePreferences = TypedDict(
    "ChromePreferences",
    {
        "download.prompt_for_download": bool,
        "plugins.always_open_pdf_externally": bool,
        "profile.default_content_settings.popups": int,
        "printing.print_preview_sticky_settings.appState": str,
        "download.default_directory": str,
        "credentials_enable_service": bool,
        "profile.password_manager_enabled": bool,
    },
)

FirefoxPreferences = TypedDict(
    "FirefoxPreferences",
    {
        "browser.download.folderList": int,
        "browser.download.manager.showWhenStarting": bool,
        "browser.download.dir": str,
        "browser.helperApps.neverAsk.saveToDisk": str,
        "pdfjs.disabled": bool,
    },
)


ChromeConfig = TypedDict(
    "ChromeConfig",
    {
        "name": str,
        "service": Type[ChromeService],
        "executor": Type[ChromeRemoteConnection],
        "options": driver_options,
        "manager": Type[ChromeDriverManager],
    },
)

FirefoxConfig = TypedDict(
    "FirefoxConfig",
    {
        "name": str,
        "service": Type[GeckoService],
        "executor": Type[FirefoxRemoteConnection],
        "options": driver_options,
        "manager": Type[GeckoDriverManager],
        "args_executor": dict[str, str],
    },
)

OptionsConfig = TypedDict(
    "OptionsConfig",
    {"chrome": ChromeConfig, "firefox": FirefoxConfig, "gecko": FirefoxConfig},
)
