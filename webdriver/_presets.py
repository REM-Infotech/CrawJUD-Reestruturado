from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Literal, TypedDict, TypeVar, Union

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as GeckoService
from selenium.webdriver.remote.webelement import WebElement  # noqa: F401
from selenium.webdriver.support.wait import WebDriverWait  # noqa: F401
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.manager import DriverManager
from webdriver_manager.firefox import GeckoDriverManager

from webdriver.configure import configure_chrome, configure_gecko

if TYPE_CHECKING:
    from selenium.webdriver.common.options import ArgOptions as Options
    from selenium.webdriver.common.service import Service


BrowserOptions = Literal["chrome", "gecko", "firefox"]
TExtensionsPath = TypeVar("ExtensionsPath", bound=Union[str, Path])

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


arguments_list: list[str] = [
    "--ignore-ssl-errors=yes",
    "--ignore-certificate-errors",
    "--display=:0",
    "--window-size=1600,900",
    "--no-sandbox",
    "--kiosk-printing",
    "--incognito",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--disable-software-rasterizer",
    "--disable-renderer-backgrounding",
    "--disable-backgrounding-occluded-windows",
    "--disable-blink-features=AutomationControlled",
    "--disable-features=MediaFoundationVideoCapture",
    "--no-proxy-server",
    "--disable-software-rasterizer",
    "--disable-features=VizDisplayCompositor",
]


settings: dict[str, str | list[dict[str, str]] | int] = {
    "recentDestinations": [{"id": "Save as PDF", "origin": "local", "account": ""}],
    "selectedDestinationId": "Save as PDF",
    "version": 2,
}

chrome_preferences: ChromePreferences = {
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True,
    "profile.default_content_settings.popups": 0,
    "printing.print_preview_sticky_settings.appState": json.dumps(settings),
    "download.default_directory": "",
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False,
}
