import json
from pathlib import Path
from typing import TypedDict, TypeVar, Union

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
    # disable Render and GPU
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--disable-software-rasterizer",
    "--disable-renderer-backgrounding",
    "--disable-backgrounding-occluded-windows",
    "--disable-blink-features=AutomationControlled",
    # "--disable-features=MediaFoundationVideoCapture",
    # disable network prediction
    # "--no-proxy-server",
    # "--disable-software-rasterizer",
    # "--disable-features=VizDisplayCompositor",
]

TExtensionsPath = TypeVar("ExtensionsPath", bound=Union[str, Path])

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
