# noqa: D100

from pathlib import Path
from typing import Any

from browsermobproxy import Client, Server
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options

from crawjud.utils.webdriver._types import FirefoxPreferences
from crawjud.utils.webdriver.config.proxy import configure_proxy

work_dir = Path(__file__).cwd()


firefox_preferences = {
    "browser.download.folderList": 2,
    "browser.download.manager.showWhenStarting": False,
    "pdfjs.disabled": True,
    "browser.helperApps.neverAsk.saveToDisk": "application/x-gzip",
    "browser.download.dir": str(work_dir.joinpath("temp", "downloads")),
}


class FirefoxOptions(Options):  # noqa: D101
    _proxy_client: Client = None

    def __init__(  # noqa: D107
        self,
        extensions_path: Path | str = work_dir,
        preferences: FirefoxPreferences = firefox_preferences,
        with_proxy: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__()

        self.profile = FirefoxProfile()

        for k, v in list(firefox_preferences.items()):
            self.profile.set_preference(k, v)

        if with_proxy:
            client, server = configure_proxy()
            self._proxy_client = client
            self._server = server
            self.proxy = self._proxy_client.selenium_proxy()

    @property
    def proxy_client(self) -> Client:
        return self._proxy_client

    @proxy_client.setter
    def proxy_client(self, new_proxy: Client) -> None:
        self._proxy_client = new_proxy

    @property
    def proxy_server(self) -> Server:
        return self._server


def configure_gecko(
    *args: Any,
    **kwargs: Any,
) -> FirefoxOptions:
    """Configurações do Options do Chrome.

    Returns:
        ChromeOptions: Instância do Options Chrome

    """
    return FirefoxOptions(*args, **kwargs)
