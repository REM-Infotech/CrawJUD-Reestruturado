# noqa: D100
from pathlib import Path
from typing import Any

from browsermobproxy import Client, Server
from selenium.webdriver.chrome.options import Options

from utils.webdriver._types import (
    ChromePreferences,
)
from utils.webdriver.config.proxy import configure_proxy

work_dir = Path(__file__).cwd()

arguments_list: list[str] = [
    "--ignore-ssl-errors=yes",
    "--ignore-certificate-errors",
    "--display=:0",
    "--window-size=1280,720",
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
    "printing.print_preview_sticky_settings.appState": settings,
    "download.default_directory": "",
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False,
}


class ChromeOptions(Options):  # noqa: D101
    _proxy_client: Client = None

    def __init__(  # noqa: D107
        self,
        extensions_path: Path | str = work_dir,
        preferences: ChromePreferences = chrome_preferences,
        arguments: list[str] = arguments_list,
        with_proxy: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__()

        for argument in arguments:
            self.add_argument(argument)

        for root, _, files in Path(extensions_path).walk():
            for file in list(filter(lambda x: x.endswith(".crx"), files)):
                self.add_extension(str(root.joinpath(file)))

        self.add_experimental_option("prefs", preferences)

        if with_proxy:
            client, server = configure_proxy()
            self._server = server
            self._proxy_client = client
            self.proxy = self._proxy_client.selenium_proxy()
            self.add_argument(f"--proxy-server={self._proxy_client.proxy}")

    @property
    def proxy_client(self) -> Client:  # noqa: D102
        return self._proxy_client

    @proxy_client.setter
    def proxy_client(self, new_proxy: Client) -> None:
        self._proxy_client = new_proxy

    @property
    def proxy_server(self) -> Server:  # noqa: D102
        return self._server


def configure_chrome(
    *args: Any,
    **kwargs: Any,
) -> ChromeOptions:
    """Configurações do Options do Chrome.

    Returns:
        ChromeOptions: Instância do Options Chrome

    """
    return ChromeOptions(*args, **kwargs)
