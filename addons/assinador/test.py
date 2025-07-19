# type: ignore  # noqa:  PGH003, D100
from pathlib import Path  # noqa:  I001

import jpype.imports  # noqa: F401
import load_jvm  # noqa: F401
from dotenv import dotenv_values

from java.io import File, FileInputStream
from java.security import KeyStore
from java.security import Security
from java.util import ArrayList  # noqa: F401
from org.bouncycastle.asn1 import ASN1Primitive
from org.bouncycastle.asn1.x509 import Certificate
from org.bouncycastle.cms import (  # noqa: F401
    CMSSignedDataGenerator,
    CMSProcessableFile,
    CMSProcessableByteArray,
)
from org.bouncycastle.cms.jcajce import JcaSignerInfoGeneratorBuilder  # noqa: F403
from org.bouncycastle.operator.jcajce import (
    JcaDigestCalculatorProviderBuilder,
    JcaContentSignerBuilder,
)  # noqa: F401
from org.bouncycastle.cms import (
    DefaultSignedAttributeTableGenerator,
)  # Adicione este import

from org.bouncycastle.cert import X509CertificateHolder
from org.bouncycastle.cert.jcajce import JcaCertStore  # noqa: F401
from org.bouncycastle.jce.provider import BouncyCastleProvider
from org.bouncycastle.asn1.cms import AttributeTable, Attribute
from org.bouncycastle.asn1 import ASN1ObjectIdentifier, DERUTF8String, DERSet
from org.bouncycastle.tsp import TimeStampTokenGenerator  # noqa: F401

# Abrir o arquivo .p12

environ = dotenv_values()
Security.addProvider(BouncyCastleProvider())


class SignPy:
    """
    Realiza assinatura digital de arquivo, incluindo atributos obrigatórios e recomendados.

    Args:
        cert_path (str | None): Caminho para o certificado digital (.p12).
        password_cert (str | None): Senha do certificado digital.

    Returns:
        CMSProcessableFile: Objeto representando o arquivo processado para assinatura.

    Raises:
        Exception: Em caso de erro na assinatura ou manipulação dos arquivos.

    """

    def __init__(self, cert_path: str = None, password_cert: str = None) -> None:
        """
        Inicializa a classe SignPy carregando o certificado digital e preparando os objetos necessários para assinatura.

        Args:
            cert_path (str | None): Caminho para o certificado digital (.p12).
            password_cert (str | None): Senha do certificado digital.

        Returns:
            None: Este método é um construtor e não retorna valor.

        Raises:
            Exception: Em caso de erro ao carregar o certificado ou inicializar os objetos de assinatura.

        """
        # Carrega variáveis de ambiente e inicializa provider
        p12_path: str = str(Path(__file__).cwd().joinpath(environ["PFX_PATH"]))
        p12_password: str = environ["PASSWORD_PFX"]

        # Carrega o KeyStore do tipo PKCS12
        ks = KeyStore.getInstance("PKCS12")
        fis = FileInputStream(p12_path)
        ks.load(fis, list(p12_password))  # senha como lista de chars
        alias = ks.aliases().nextElement()
        private_key = ks.getKey(alias, list(p12_password))
        certificate = ks.getCertificate(alias)

        # Monta lista de certificados para cadeia de confiança
        cert_list = ArrayList()
        cert_list.add(certificate)

        certs = JcaCertStore(cert_list)
        gen = CMSSignedDataGenerator()
        cert = Certificate.getInstance(
            ASN1Primitive.fromByteArray(certificate.getEncoded())
        )
        sha1_signer = JcaContentSignerBuilder("SHA256withRSA").build(private_key)
        dcp = JcaDigestCalculatorProviderBuilder().build()

        # Atributos obrigatórios e recomendados
        # Identificador da Política de Assinatura (OID fictício de exemplo)
        policy_oid = ASN1ObjectIdentifier("1.2.840.113549.1.9.16.6.1")
        policy_id = Attribute(
            policy_oid, DERSet([DERUTF8String("ID_POLITICA_EXEMPLO_001")])
        )

        # Dados da Assinatura (data/hora)
        from java.util import Date

        assinatura_data = Attribute(
            ASN1ObjectIdentifier("1.2.840.113549.1.9.5"),  # signingTime
            DERSet([DERUTF8String(str(Date()))]),
        )

        # Informações para Arquivamento (exemplo)
        arquivamento_info = Attribute(
            ASN1ObjectIdentifier("1.2.840.113549.1.9.16.2.48"),
            DERSet([DERUTF8String("Arquivo: index.html")]),
        )

        # Informações de Validação (tipo de certificado)
        validacao_info = Attribute(
            ASN1ObjectIdentifier("1.2.840.113549.1.9.16.2.47"),
            DERSet([DERUTF8String("A1")]),
        )

        # Carimbo do Tempo (timestamp fictício)
        carimbo_tempo = Attribute(
            ASN1ObjectIdentifier("1.2.840.113549.1.9.16.2.14"),
            DERSet([DERUTF8String(str(Date()))]),
        )

        for item in [
            assinatura_data,
            arquivamento_info,
            validacao_info,
            carimbo_tempo,
        ]:
            print(item.toString())

        # Monta tabela de atributos assinados usando ASN1EncodableVector
        from org.bouncycastle.asn1 import ASN1EncodableVector  # Import necessário

        atributos_vector = ASN1EncodableVector()
        atributos_vector.add(policy_id)
        atributos_vector.add(assinatura_data)
        atributos_vector.add(arquivamento_info)
        atributos_vector.add(validacao_info)
        atributos_vector.add(carimbo_tempo)

        atributos_assinados = AttributeTable(atributos_vector)

        # Use DefaultSignedAttributeTableGenerator para encapsular o AttributeTable
        signed_attr_generator = DefaultSignedAttributeTableGenerator(
            atributos_assinados
        )

        # Cria o SignerInfoGenerator com atributos
        sig = (
            JcaSignerInfoGeneratorBuilder(dcp)
            .setSignedAttributeGenerator(signed_attr_generator)
            .build(sha1_signer, X509CertificateHolder(cert))
        )

        gen.addSignerInfoGenerator(sig)
        gen.addCertificates(certs)

        # Caminho de certificação já incluso via cert_list
        file = File(str(Path(p12_path).parent.joinpath("index.html")))
        msg = CMSProcessableFile(file)
        # Dados a assinar
        signed_data = gen.generate(msg, False)

        # Escreve arquivo assinado
        with open(str(Path(p12_path).parent.joinpath("index.html.p7s")), "wb") as f:
            f.write(signed_data.getEncoded())


SignPy()
