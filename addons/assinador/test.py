# noqa: D100
from pathlib import Path  # noqa:  I001

import jpype.imports  # noqa: F401
import load_jvm  # noqa: F401
from dotenv import dotenv_values

from java.io import FileInputStream  # type: ignore  # noqa:  PGH003
from java.security import KeyStore  # type: ignore  # noqa:  PGH003

# Abrir o arquivo .p12

environ = dotenv_values()


class SignPy:  # noqa: D101
    def __init__(  # noqa: D107
        self, cert_path: str | None = None, password_cert: str | None = None
    ) -> None:
        p12_path = str(Path(__file__).cwd().joinpath(environ["PFX_PATH"]))
        p12_password = environ["PASSWORD_PFX"]

        # Carregar o KeyStore do tipo PKCS12
        ks = KeyStore.getInstance("PKCS12")
        fis = FileInputStream(p12_path)
        ks.load(fis, list(p12_password))  # senha como lista de chars

        # Listar os aliases (nomes dos certificados dentro do .p12)
        aliases = ks.aliases()
        while aliases.hasMoreElements():
            alias = aliases.nextElement()
            print("Alias:", alias)

            # Obter a chave privada
            private_key = ks.getKey(alias, list(p12_password))
            print("Private Key:", private_key)

            # Obter o certificado
            cert = ks.getCertificate(alias)
            print("Certificate:", cert)
