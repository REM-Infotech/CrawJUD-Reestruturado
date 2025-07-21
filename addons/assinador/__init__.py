# type: ignore  # noqa:  PGH003, D104
"""
Inicializa o módulo de assinatura digital utilizando certificado .p12.

Este módulo fornece a classe SignPy para realizar assinaturas digitais
em arquivos PDF, utilizando certificados digitais no formato PKCS#12 (.p12).

Args:
    Nenhum argumento é necessário para o módulo.

Returns:
    None: Não retorna valor.

Raises:
    Nenhuma exceção específica é levantada pelo módulo.

"""

# type: ignore  # noqa:  PGH003, D104
from os import PathLike
from pathlib import Path
from typing import (
    Union,  # noqa:  I001
)

import jpype.imports  # noqa: F401
from dotenv import dotenv_values

from addons.assinador import load_jvm  # noqa: F401
from addons.assinador.java.io import File, FileInputStream
from addons.assinador.java.lang import Object
from addons.assinador.java.security import KeyStore, Security
from addons.assinador.java.util import ArrayList
from addons.assinador.org.bouncycastle.asn1 import ASN1Primitive
from addons.assinador.org.bouncycastle.asn1.x509 import Certificate
from addons.assinador.org.bouncycastle.cert import X509CertificateHolder
from addons.assinador.org.bouncycastle.cert.jcajce import JcaCertStore
from addons.assinador.org.bouncycastle.cms import (
    CMSProcessableByteArray,
    CMSProcessableFile,
    CMSSignedData,
    CMSSignedDataGenerator,
)
from addons.assinador.org.bouncycastle.cms.jcajce import (
    JcaSignerInfoGeneratorBuilder,
)
from addons.assinador.org.bouncycastle.jce.provider import BouncyCastleProvider
from addons.assinador.org.bouncycastle.operator.jcajce import (
    JcaContentSignerBuilder,
    JcaDigestCalculatorProviderBuilder,
)

# Abrir o arquivo .p12

environ = dotenv_values()
Security.addProvider(BouncyCastleProvider())
StrPath = Union[str, PathLike]
_cms = Union[CMSProcessableByteArray | CMSProcessableFile]
_cont = Union[Path, bytes]


class SignPy:
    """
    Realiza a assinatura digital de um arquivo PDF utilizando certificado digital no formato .p12.

    Args:
        cert_path (str | None): Caminho para o certificado digital (opcional).
        password_cert (str | None): Senha do certificado digital (opcional).

    Returns:
        None: Não retorna valor.

    Raises:
        Exception: Em caso de falha na assinatura ou carregamento do certificado.

    """

    @classmethod
    def assinador(
        cls, cert: str, pw: str, content: _cont, out: StrPath = None
    ) -> bytes:
        """
        Executa o processo de assinatura digital de um conteúdo PDF.

        Args:
            cert (str): Caminho para o certificado digital.
            pw (str): Senha do certificado digital.
            content (Path | bytes): Caminho do arquivo ou conteúdo em bytes.
            out (StrPath): Caminho de saída para o arquivo assinado.

        Returns:
            bytes: Dados assinados no formato CMS.

        Raises:
            TypeError: Caso o tipo de 'content' não seja Path ou bytes.

        """
        self = cls(cert, pw)

        if not any([isinstance(content, Path), isinstance(content, bytes)]):
            raise TypeError("O tipo de 'content' deve ser Path ou bytes.")

        if isinstance(content, Path):
            file = File(str(content))
            cms = CMSProcessableFile(file)

        elif isinstance(content, bytes):
            cms = CMSProcessableByteArray(content)

        gen = self.prepare_signer()
        return self.sign(gen, cms).getEncoded()

    def __init__(self, cert_path: str = None, password_cert: str = None) -> None:
        """
        Inicializa a instância de assinatura com certificado e senha.

        Args:
            cert_path (str | None): Caminho para o certificado digital.
            password_cert (str | None): Senha do certificado digital.

        Returns:
            None: Não retorna valor.

        Raises:
            Exception: Em caso de falha ao carregar o certificado.

        """
        ks = KeyStore.getInstance("PKCS12")
        fis = FileInputStream(cert_path)

        ks.load(fis, list(password_cert))  # senha como lista de chars
        alias = ks.aliases().nextElement()
        self.private_key: Object = ks.getKey(alias, list(password_cert))
        self.certificate: Object = ks.getCertificate(alias)

    def prepare_signer(self) -> CMSSignedDataGenerator:
        """
        Prepara o gerador de assinatura digital com os certificados necessários.

        Args:
            Nenhum argumento.

        Returns:
            CMSSignedDataGenerator: Instância configurada para assinatura.

        Raises:
            Exception: Em caso de falha na preparação do gerador.

        """
        # Prepara a lista de certificados
        cert_list = ArrayList()
        cert_list.add(self.certificate)

        certs = JcaCertStore(cert_list)
        gen = CMSSignedDataGenerator()
        cert = Certificate.getInstance(
            ASN1Primitive.fromByteArray(self.certificate.getEncoded())
        )
        jcsb = JcaContentSignerBuilder("SHA256withRSA")
        sha1_signer: Object = jcsb.build(self.private_key)
        dcp = JcaDigestCalculatorProviderBuilder().build()
        sig = JcaSignerInfoGeneratorBuilder(dcp).build(
            sha1_signer, X509CertificateHolder(cert)
        )
        gen.addSignerInfoGenerator(sig)
        gen.addCertificates(certs)
        return gen

    def sign(self, gen: CMSSignedDataGenerator, cms: _cms) -> CMSSignedData:
        """
        Realiza a assinatura digital do conteúdo informado.

        Args:
            gen (CMSSignedDataGenerator): Gerador de assinatura configurado.
            cms (_cms): Conteúdo a ser assinado (arquivo ou bytes).

        Returns:
            CMSSignedData: Dados assinados no formato CMS.

        Raises:
            Exception: Em caso de falha na assinatura.

        """
        # Gera os dados assinados incluindo o conteúdo (gera o atributo MessageDigest)
        return gen.generate(cms, True)  # <--- alterado para True
