# type: ignore  # noqa: PGH003
"""
Assina arquivos utilizando certificados ICP-Brasil, incluindo atributos obrigatórios.

Este módulo realiza a assinatura digital de arquivos conforme as exigências da ICP-Brasil,
inserindo atributos obrigatórios como OID de política, data/hora e identificadores específicos.

Args:
    Nenhum argumento de linha de comando.

Returns:
    None: O arquivo assinado é salvo no mesmo diretório do certificado.

Raises:
    KeyError: Caso variáveis de ambiente não estejam definidas.
    Exception: Para erros gerais de assinatura.

"""

from pathlib import Path  # noqa:  I001

import jpype.imports  # noqa: F401
import load_jvm  # noqa: F401
from dotenv import dotenv_values

from java.io import File, FileInputStream
from java.security import KeyStore
from java.security import Security
from java.util import ArrayList, Date, Hashtable  # noqa: F401
from org.bouncycastle.asn1 import ASN1ObjectIdentifier, ASN1Primitive
from org.bouncycastle.asn1.cms import Attribute, AttributeTable
from org.bouncycastle.asn1.x509 import Certificate
from org.bouncycastle.cms import (  # noqa: F401
    CMSSignedDataGenerator,
    CMSProcessableFile,
    DefaultSignedAttributeTableGenerator,
)
from org.bouncycastle.cms.jcajce import JcaSignerInfoGeneratorBuilder  # noqa: F403
from org.bouncycastle.operator.jcajce import (
    JcaDigestCalculatorProviderBuilder,
    JcaContentSignerBuilder,
)  # noqa: F401

from org.bouncycastle.cert import X509CertificateHolder
from org.bouncycastle.cert.jcajce import JcaCertStore  # noqa: F401
from org.bouncycastle.jce.provider import BouncyCastleProvider

# Carrega variáveis de ambiente
environ = dotenv_values()
Security.addProvider(BouncyCastleProvider())


class SignPy:
    """
    Realiza assinatura digital CMS com atributos obrigatórios da ICP-Brasil.

    Args:
        cert_path (str | None): Caminho para o certificado PFX/P12.
        password_cert (str | None): Senha do certificado.

    Returns:
        None: Salva o arquivo assinado no disco.

    Raises:
        KeyError: Se variáveis de ambiente não forem encontradas.
        Exception: Para falhas na assinatura.

    """

    def __init__(  # noqa: D107
        self,
        cert_path: str | None = None,
        password_cert: str | None = None,
    ) -> None:
        # Determina o caminho do certificado e senha
        p12_path: str = str(Path(__file__).cwd().joinpath(environ["PFX_PATH"]))
        p12_password: str = environ["PASSWORD_PFX"]

        # Carrega o KeyStore PKCS12
        ks = KeyStore.getInstance("PKCS12")
        fis = FileInputStream(p12_path)
        ks.load(fis, list(p12_password))  # senha como lista de chars
        alias = ks.aliases().nextElement()
        private_key = ks.getKey(alias, list(p12_password))
        certificate = ks.getCertificate(alias)

        # Prepara lista de certificados
        cert_list = ArrayList()
        cert_list.add(certificate)
        certs = JcaCertStore(cert_list)

        # Instancia gerador de assinatura
        gen = CMSSignedDataGenerator()
        cert = Certificate.getInstance(
            ASN1Primitive.fromByteArray(certificate.getEncoded())
        )
        sha1_signer = JcaContentSignerBuilder("SHA256withRSA").build(private_key)
        dcp = JcaDigestCalculatorProviderBuilder().build()

        # Monta atributos obrigatórios ICP-Brasil
        # OID de política de assinatura (exemplo: 2.16.76.1.7.1.1.2.2.1)
        policy_oid = ASN1ObjectIdentifier("2.16.76.1.7.1.1.2.2.1")
        # OID para data/hora da assinatura (1.2.840.113549.1.9.5)
        signing_time_oid = ASN1ObjectIdentifier("1.2.840.113549.1.9.5")
        # OID ICP-Brasil obrigatório (exemplo: 2.16.76.1.3.1)
        icpbr_attr_oid = ASN1ObjectIdentifier("2.16.76.1.3.1")

        # Cria tabela de atributos assinados
        signed_attrs = Hashtable()
        # Adiciona política de assinatura
        signed_attrs.put(policy_oid, Attribute(policy_oid, [policy_oid]))
        # Adiciona data/hora da assinatura
        signed_attrs.put(signing_time_oid, Attribute(signing_time_oid, [Date()]))
        # Adiciona OID ICP-Brasil obrigatório para certificado A1 (2.16.76.1.3.1)
        # O valor deve ser o CPF do titular codificado conforme a especificação da ICP-Brasil
        signed_attrs.put(
            icpbr_attr_oid,
            Attribute(
                icpbr_attr_oid, [ASN1ObjectIdentifier("1234567890")]
            ),  # Substitua pelo valor ASN.1 correto do CPF
        )

        # Gera tabela de atributos assinados
        attr_table = AttributeTable(signed_attrs)
        attr_gen = DefaultSignedAttributeTableGenerator(attr_table)

        # Monta o SignerInfo com atributos obrigatórios
        sig = (
            JcaSignerInfoGeneratorBuilder(dcp)
            .setSignedAttributeGenerator(attr_gen)
            .build(sha1_signer, X509CertificateHolder(cert))
        )

        gen.addSignerInfoGenerator(sig)
        gen.addCertificates(certs)

        # Prepara arquivo a ser assinado
        file = File(str(Path(p12_path).parent.joinpath("index.html")))
        msg = CMSProcessableFile(file)

        # Gera assinatura CMS
        signed_data = gen.generate(msg, False)

        # Salva assinatura no disco
        with open(str(Path(p12_path).parent.joinpath("index.html.p7s")), "wb") as f:
            f.write(signed_data.getEncoded())

        # Mensagem de sucesso
        print("Assinatura gerada em 'index.html.p7s'")


SignPy()
