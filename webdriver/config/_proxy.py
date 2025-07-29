from browsermobproxy import Client as ProxyClient
from browsermobproxy import Server
from dotenv import dotenv_values

environ = dotenv_values()


def configure_proxy() -> ProxyClient:
    server = Server(environ["BROWSERMOB_PATH"])
    server.start()
    return server.create_proxy()
