from __future__ import annotations

from typing import TYPE_CHECKING

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.webdriver.firefox.remote_connection import FirefoxRemoteConnection
from selenium.webdriver.firefox.service import Service as GeckoService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from utils.webdriver.config import configure_chrome, configure_gecko

if TYPE_CHECKING:
    from ._types import OptionsConfig


config: OptionsConfig = {
    "chrome": {
        "service": ChromeService,
        "executor": ChromiumRemoteConnection,
        "options": configure_chrome,
        "manager": ChromeDriverManager,
        "args_executor": {
            "remote_server_addr": "",
            "browser_name": "chrome",
            "vendor_prefix": "goog",
            "keep_alive": True,
            "ignore_proxy": False,
        },
    },
    "firefox": {
        "service": GeckoService,
        "executor": FirefoxRemoteConnection,
        "options": configure_gecko,
        "manager": GeckoDriverManager,
        "args_executor": {
            "remote_server_addr": "",
            "keep_alive": True,
            "ignore_proxy": False,
        },
    },
    "gecko": {
        "service": GeckoService,
        "executor": FirefoxRemoteConnection,
        "options": configure_gecko,
        "manager": GeckoDriverManager,
        "args_executor": {
            "remote_server_addr": "",
            "keep_alive": True,
            "ignore_proxy": False,
        },
    },
}
