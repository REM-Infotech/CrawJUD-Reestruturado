# noqa: D100

from pathlib import Path
from typing import Any

from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options

from webdriver._types import FirefoxPreferences
from webdriver.config._proxy import configure_proxy

work_dir = Path(__file__).cwd()


firefox_preferences = {
    "browser.download.folderList": 2,
    "browser.download.manager.showWhenStarting": False,
    "pdfjs.disabled": True,
    "browser.helperApps.neverAsk.saveToDisk": "application/x-gzip",
    "browser.download.dir": str(work_dir.joinpath("temp", "downloads")),
}


class FirefoxOptions(Options):  # noqa: D101
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
            self._proxy_client = configure_proxy()
            self.proxy = self._proxy_client.selenium_proxy()


def configure_gecko(
    *args: Any,
    **kwargs: Any,
) -> FirefoxOptions:
    """Configurações do Options do Chrome.

    Returns:
        ChromeOptions: Instância do Options Chrome

    """
    return FirefoxOptions(*args, **kwargs)
