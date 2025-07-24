# noqa: D100
import json
from pathlib import Path
from typing import TypedDict

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as GeckoOptions

from webdriver._types import (
    TExtensionsPath,
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


def configure_chrome(
    dir_extensions: TExtensionsPath = None,
    argument: list[str] = arguments_list,
    chrome_prefs: ChromePreferences = chrome_preferences,
) -> ChromeOptions:
    """Configurações do Options do Chrome.

    Returns:
        ChromeOptions: Instância do Options Chrome

    """
    chrome_options = ChromeOptions()
    for argument in arguments_list:
        chrome_options.add_argument(argument)

    if dir_extensions:
        for root, _, files in Path(dir_extensions).walk():
            for file in list(filter(lambda x: x.endswith(".crx"), files)):
                chrome_options.add_extension(str(root.joinpath(file)))

    chrome_options.add_experimental_option("prefs", chrome_prefs)

    return chrome_options


def configure_gecko() -> GeckoOptions:
    """Configurações do Options do Gecko.

    Returns:
        GeckoOptions: Instância do Options Gecko

    """
    gecko_options = GeckoOptions()
    gecko_options.add_argument("--no-sandbox")
    gecko_options.add_argument("--disable-dev-shm-usage")

    return gecko_options
