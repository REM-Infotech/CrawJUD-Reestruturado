import time
from pathlib import Path

from browsermobproxy import Server
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager as FirefoxDriverManager

work_dir = Path(__file__).cwd()


def inicializar_selenium_com_browsermob(
    headless: bool = True,
) -> tuple[webdriver.Chrome, Server, dict]:
    """
    Inicializa o Selenium WebDriver com Chrome, utilizando webdriver_manager e BrowserMob Proxy.

    Args:
        caminho_browsermob (str): Caminho para o executável do BrowserMob Proxy.
        headless (bool): Define se o navegador será executado em modo headless.

    Returns:
        tuple[webdriver.Chrome, Server, dict]: Retorna uma tupla contendo o driver
        do Selenium, a instância do servidor BrowserMob Proxy e o proxy criado.

    Raises:
        FileNotFoundError: Caso o caminho do BrowserMob Proxy seja inválido.
        Exception: Para outros erros de inicialização.

    """
    # Inicia o servidor do BrowserMob Proxy
    server = Server("/opt/browsermob-proxy/bin/browsermob-proxy")
    server.start()
    proxy = server.create_proxy()

    # Configura as opções do Chrome
    firefox_options = FirefoxOptions()
    firefox_profile = firefox_options.profile or webdriver.FirefoxProfile(
        str(work_dir.joinpath("temp"))
    )

    firefox_profile.set_preference("browser.download.folderList", 2)
    firefox_profile.set_preference("browser.download.manager.showWhenStarting", False)
    firefox_profile.set_preference(
        "browser.download.dir", str(work_dir.joinpath("downloads"))
    )
    firefox_profile.set_preference(
        "browser.helperApps.neverAsk.saveToDisk", "application/x-gzip"
    )

    firefox_options.set_preference("pdfjs.disabled", True)
    firefox_options.proxy = proxy.selenium_proxy()

    firefox_options.profile = firefox_profile
    # Instala e inicializa o ChromeDriver usando webdriver_manager
    driver = webdriver.Firefox(
        service=FirefoxService(FirefoxDriverManager().install()),
        options=firefox_options,
    )
    return driver, server, proxy
    # Retorna o driver, o servidor e o proxy para uso externo


# Exemplo de uso:
driver, server, proxy = inicializar_selenium_com_browsermob()
proxy.new_har("exemplo", options={"captureHeaders": True, "captureContent": True})
driver.get("https://pje.trt11.jus.br/primeirograu/login.seam")

# Loop para monitorar e imprimir o HAR a cada nova requisição
ultimo_tamanho = 0

main_window = driver.current_window_handle

try:
    while True:
        # Obtém o HAR atual
        har_atual = proxy.har
        entradas = har_atual.get("log", {}).get("entries", [])
        # Percorre as novas requisições
        for entrada in entradas[ultimo_tamanho:]:
            url = entrada.get("request", {}).get("url", "")

            response = entrada.get("response")
            content = response.get("content")
            # Verifica se a URL corresponde ao padrão desejado
            if "/pje-consulta-api/api/processos/" in url and "/documentos/" in url:
                print(f"Interceptada URL de interesse: {url}")

                driver.switch_to.new_window("tab")

                driver.get(url)

                time.sleep(5)

                driver.switch_to.window(main_window)

        # Atualiza o tamanho para não processar as mesmas entradas novamente
        ultimo_tamanho = len(entradas)
        time.sleep(1)  # Aguarda 1 segundo antes de checar novamente
except KeyboardInterrupt:
    # Permite sair do loop com Ctrl+C
    print("Monitoramento interrompido pelo usuário.")

driver.quit()
server.stop()
