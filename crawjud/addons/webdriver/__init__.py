"""Module for managing WebDriver instances and related utilities."""

from __future__ import annotations

import json
import platform
import shutil
import traceback
import zipfile
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from os import getcwd, path
from pathlib import Path

import requests
from selenium.webdriver.remote.webdriver import WebDriver

from crawjud.bot.core import (
    BarColumn,
    Chrome,
    DownloadColumn,
    Group,
    Live,
    Options,
    Panel,
    Progress,
    Service,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
    WebDriverWait,
)
from crawjud.bot.core import (
    CrawJUD as CrawJUD,
)

if __name__ == "__main__":
    from getchrome_version import another_chrome_ver, chrome_ver
else:
    from crawjud.bot.Utils.Driver.getchrome_version import another_chrome_ver, chrome_ver  # noqa: F401


class DriverBot:
    """Bot for handling WebDriver operations within CrawJUD framework."""

    def __init__(self) -> None:
        """
        Initialize DriverBot with default settings for WebDriver operations in CrawJUD promptly.

        Args:
            None.

        """

    list_args_ = [
        "--ignore-ssl-errors=yes",
        "--ignore-certificate-errors",
        "--display=:99",
        "--window-size=1600,900",
        # "--no-sandbox",
        "--kiosk-printing",
        # disable Render and GPU
        # "--disable-gpu",
        # "--disable-dev-shm-usage",
        # "--disable-software-rasterizer",
        # "--disable-renderer-backgrounding",
        # "--disable-backgrounding-occluded-windows",
        "--disable-blink-features=AutomationControlled",
        # "--disable-features=MediaFoundationVideoCapture",
        # disable network prediction
        # "--no-proxy-server",
        # "--disable-software-rasterizer",
        # "--disable-features=VizDisplayCompositor",
    ]

    @property
    def list_args(self) -> list[str]:
        """Get the list of arguments for WebDriver."""
        return self.list_args_

    @list_args.setter
    def list_args(self, new_args: list[str]) -> None:
        """Set a new list of arguments for WebDriver.

        Args:
            new_args (list[str]): The new arguments to set.

        """
        self.list_args_ = new_args

    def create_path_accepted(self) -> None:
        """Create the path for the WebDriver instance."""
        if platform.system() == "Windows" and self.login_method == "cert":
            state = str(self.state)
            self.path_accepted = Path(
                path.join(Path(getcwd()).resolve(), "Browser", state, self.username, "chrome"),
            )
            path_exist = self.path_accepted.exists()
            if path_exist:
                for root, _, __ in self.path_accepted.walk():
                    try:
                        shutil.copytree(root, self.chr_dir)
                    except Exception:
                        err = traceback.format_exc()
                        self.logger.exception(err)

            elif not path_exist:
                self.path_accepted.mkdir(parents=True, exist_ok=True)

    def add_options(self, chrome_options: Options) -> None:
        """Add options to the Chrome WebDriver instance."""
        self.chr_dir = Path(self.pid_path).joinpath("chrome").resolve()
        chrome_options.add_argument(f"user-data-dir={str(self.chr_dir)}")

        list_args = self.list_args
        for argument in list_args:
            chrome_options.add_argument(argument)

        this_path = Path(__file__).parent.resolve().joinpath("extensions")
        for root, _, files in this_path.walk():
            for file_ in files:
                if ".crx" in file_:
                    path_plugin = str(root.joinpath(file_).resolve())
                    chrome_options.add_extension(path_plugin)

        chrome_prefs = {
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_settings.popups": 0,
            "printing.print_preview_sticky_settings.appState": json.dumps(self.settings),
            "download.default_directory": f"{self.pid_path}",
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        }

        if self.system == "projudi":
            chrome_options.add_argument("--incognito")
        chrome_options.add_experimental_option("prefs", chrome_prefs)

    def driver_launch(self, message: str = "Inicializando WebDriver") -> tuple[WebDriver, WebDriverWait]:
        """
        Launch WebDriver with options and extensions, then return driver and wait to run well.

        Args:
            message (str, optional): Initialization message.

        Returns:
            tuple[WebDriver, WebDriverWait]: The launched driver and its wait instance.

        Raises:
            Exception: Propagates any exception raised during driver launch.

        """
        try:
            self.pid_path = self.output_dir_path.resolve()

            self.message = message
            self.type_log = "log"
            self.prt()

            chrome_options = Options()

            # chrome_options.binary_location = str(Path(getcwd()).joinpath("chrome-win64", "chrome.exe"))

            self.create_path_accepted()
            self.add_options(chrome_options)

            getdriver = SetupDriver(destination=self.pid_path)
            path_chrome = None
            if message != "Inicializando WebDriver":
                version = getdriver.code_ver
                chrome_name = f"chromedriver{version}"
                if platform.system() == "Windows":
                    chrome_name += ".exe"

                existspath_ = self.pid_path.joinpath(chrome_name)
                path_chrome = existspath_ if existspath_.exists() else None

            if path_chrome is None:
                path_chrome = self.pid_path.joinpath(getdriver()).resolve()

            serve = Service(path_chrome)
            driver = Chrome(service=serve, options=chrome_options)

            wait = WebDriverWait(driver, 20, 0.01)
            driver.delete_all_cookies()

            self.message = "WebDriver inicializado"
            self.type_log = "log"
            self.prt()

            return (driver, wait)

        except Exception as e:
            raise e


class SetupDriver:
    """Utility to download and configure the appropriate WebDriver binary."""

    another_ver = False
    current_version = ""
    try:
        current_version = chrome_ver()
        chrome_v = ".".join(current_version.split(".")[:-1])

    except Exception:
        another_ver = True
        chrome_v = another_chrome_ver()

    # another_ver = True
    # chrome_v = another_chrome_ver()
    # _url_driver: str = None

    @property
    def url_driver(self) -> str:
        """Retrieve the URL for downloading the WebDriver.

        Returns:
            str: The URL for downloading the WebDriver.

        """
        return SetupDriver._url_driver

    @url_driver.setter
    def url_driver(self, url: str) -> None:
        """Set the URL for downloading the WebDriver.

        Args:
            url (str): The URL for downloading the WebDriver.

        """
        SetupDriver._url_driver = url

    @property
    def code_ver(self) -> str:
        """Retrieve the major version of the installed Chrome browser.

        Returns:
            str: The major version of the installed Chrome browser.

        """
        return SetupDriver.chrome_v

    @code_ver.setter
    def code_ver(self, version: str) -> None:
        """Set the major version of the installed Chrome browser.

        Args:
            version (str): The major version of the installed Chrome browser.

        """
        SetupDriver.chrome_v = version

    progress = Progress(
        TimeElapsedColumn(),
        TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
    )

    current_app_progress = Progress(TimeElapsedColumn(), TextColumn("{task.description}"))

    grp = Group(current_app_progress, progress)
    painel = Panel(grp)

    progress_group = Group(painel)

    def __init__(self, destination: Path = None, **kwargs: dict[str, any]) -> None:
        """
        Initialize SetupDriver to download and configure the appropriate WebDriver binary aptly.

        Args:
            destination (Path, optional): Destination directory for WebDriver.
            **kwargs: Additional configuration parameters.

        """
        if destination is None:
            destination = Path(__file__).parent.resolve().joinpath("webdriver")
            destination.mkdir(exist_ok=True, parents=True)

        self.url_driver = self.get_url()
        new_stem = f"chromedriver{self.code_ver}.zip"
        root_dir = Path(__file__).parent.cwd()
        without_stem = root_dir.joinpath("crawjud", "bot", "webdriver", "chromedriver")
        self.file_path = without_stem.with_stem(new_stem).resolve()

        if platform.system() == "Linux":
            self.file_path = self.file_path.with_suffix("")
            self.fileN = self.file_path.name

        elif platform.system() == "Windows":
            self.file_path = self.file_path.with_suffix(".exe")
            self.fileN = self.file_path.name

        for key, value in list(kwargs.items()):
            setattr(self, key, value)

        self.destination = destination

    def __call__(self) -> str:
        """
        Execute driver setup process, download and extract WebDriver, then copy to destination.

        Args:
            None.

        Returns:
            str: Name of the downloaded WebDriver file.

        """
        with Live(self.progress_group):
            with ThreadPoolExecutor() as pool:
                self.configure_bar(pool)

        shutil.copy(self.file_path, self.destination)
        return self.destination.name

    def configure_bar(self, pool: ThreadPoolExecutor) -> None:
        """
        Configure download progress bar for obtaining the WebDriver with ThreadPoolExecutor.

        Args:
            pool (ThreadPoolExecutor): Executor for handling parallel downloads.

        """
        self.current_task_id = self.current_app_progress.add_task("[bold blue] Baixando Chromedriver")
        task_id = self.progress.add_task("download", filename=self.fileN.upper(), start=False)

        self.destination = self.destination.joinpath(self.fileN).resolve()
        root_path = Path(self.file_path).parent.resolve()
        if not self.file_path.exists():
            if not root_path.exists():
                root_path.mkdir(exist_ok=True, parents=True)

            pool.submit(self.copy_url, task_id, self.file_path)

        elif root_path.exists():
            if self.file_path.exists():
                self.current_app_progress.update(
                    self.current_task_id,
                    description="[bold green] Carregado webdriver salvo em cache!",
                )
                shutil.copy(self.file_path, self.destination)

    def get_url(self) -> str:
        """
        Construct download URL for WebDriver based on Chrome version and system architecture.

        Args:
            None.

        Returns:
            str: Constructed URL for downloading WebDriver.

        """
        # Verifica no endpoint qual a versão disponivel do WebDriver
        if self.another_ver is True:
            l_old_v = self.code_ver.split(".")
            l_old_v.pop(-1)

            self.code_ver = ".".join(l_old_v)

        url_chromegit = f"https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_{self.code_ver}"
        results = requests.get(url_chromegit, timeout=60)
        self.code_ver = results.text

        system = platform.system().replace("dows", "").lower()
        arch = platform.architecture()
        if type(arch) is tuple:
            arch = arch[0].replace("bit", "")

        os_sys = f"{system}{arch}"
        # Baixa o WebDriver conforme disponivel no repositório
        url_driver = "storage.googleapis.com/chrome-for-testing-public/"

        set_url = [self.code_ver, os_sys, os_sys]
        for pos, item in enumerate(set_url):
            if pos == len(set_url) - 1:
                url_driver += f"chromedriver-{item}.zip"
                continue

            url_driver += f"{item}/"

        return url_driver

    def copy_url(self, task_id: TaskID, path: Path) -> None:
        """
        Download, extract, and move WebDriver from URL zip file to specified path ready now.

        Args:
            task_id (TaskID): ID for progress tracking.
            url (str): URL to download from.
            path (Path): File path to save and extract WebDriver.

        """
        zip_name = path.with_name(f"{path.name}.zip")
        response = requests.get(f"https://{self.url_driver}", stream=True, timeout=60)
        # input("teste")
        # This will break if the response doesn't contain content length
        self.progress.update(task_id, total=int(response.headers["Content-length"]))

        with zip_name.open("wb") as dest_file:
            self.progress.start_task(task_id)
            for data in iter(partial(response.raw.read, 32768), b""):
                dest_file.write(data)
                self.progress.update(task_id, advance=len(data))

        # input(str("member"))
        # Extract the zip file

        with zipfile.ZipFile(zip_name, "r") as zip_ref:
            # Extract each file directly into the subfolder
            for member in zip_ref.namelist():
                # input(str(member))
                self.progress.print(member)
                self.progress.update(task_id)

                not_chrome1 = member.split("/")[-1].lower() == "chromedriver.exe"
                not_chrome2 = member.split("/")[-1].lower() == "chromedriver"

                if not_chrome1 or not_chrome2:
                    # Get the original file name without any directory structure
                    dir_name = path.name
                    extracted_path = Path(zip_ref.extract(member, dir_name))
                    base_name = extracted_path.name
                    # If the extracted path has directories, move the file directly into the subfolder
                    chk = base_name and extracted_path.is_dir()
                    if chk:
                        continue

                    shutil.move(extracted_path, path)

        zip_name.unlink()
        self.current_app_progress.update(self.current_task_id, description="[bold green] ChromeDriver Baixado!")
