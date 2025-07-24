# noqa: D100
from pathlib import Path

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as GeckoOptions

from crawjud.addons.webdriver._presets import (
    ChromePreferences,
    TExtensionsPath,
    arguments_list,
    chrome_preferences,
)


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


def configure_gecko() -> GeckoOptions:
    """Configurações do Options do Gecko.

    Returns:
        GeckoOptions: Instância do Options Gecko

    """
    gecko_options = GeckoOptions()
    gecko_options.add_argument("--no-sandbox")
    gecko_options.add_argument("--disable-dev-shm-usage")

    return gecko_options
