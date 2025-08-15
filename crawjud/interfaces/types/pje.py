"""Modulo de tipos utilizados para representar estrutura de dados do PJe.

Inclui definições de TypedDict para endereços, papéis, representantes, polos,
assuntos, anexos, itens de processo, expedientes e processos, facilitando a
tipagem e documentação dos dados manipulados pelos bots.

"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

TDict = dict[str, str]

if TYPE_CHECKING:
    from crawjud.interfaces.dict.bot import BotData


class DictSeparaRegiao(TypedDict):
    """Define o dicionário que separa regiões e posições de processos.

    Args:
        regioes (dict[str, list[BotData]]): Dicionário de regiões e bots.
        position_process (dict[str, int]): Posição dos processos por região.

    """

    regioes: dict[str, list[BotData]]
    position_process: dict[str, int]


class Resultados(TypedDict):
    """Define o retorno do desafio contendo headers, cookies e resultados.

    Args:
        headers (TDict): Cabeçalhos da requisição.
        cookies (TDict): Cookies da requisição.
        results (DictResults): Resultados do desafio.

    Returns:
        Resultados: Dicionário com informações do retorno do desafio.

    """

    headers: TDict
    cookies: TDict
    results: DictResults


class DictDesafio(TypedDict):
    """Define o desafio do PJe, contendo a imagem codificada e o token do desafio.

    Args:
        imagem (Base64Str): Imagem do desafio em base64.
        tokenDesafio (str): Token associado ao desafio.

    Returns:
        DictDesafio: Dicionário com informações do desafio.

    """

    imagem: str
    tokenDesafio: str


class DictResults(TypedDict):
    """Define os resultados retornados pelo desafio do PJe.

    Args:
        id_processo (str): Identificador do processo.
        captchatoken (str): Token do captcha.
        text (str): Texto de resposta.
        data_request (Processo): Dados do processo retornados.

    Returns:
        DictResults: Dicionário com informações dos resultados do desafio.

    """

    id_processo: str
    captchatoken: str
    text: str
    data_request: Processo


class Processo(TypedDict):
    """Define o processo judicial e seus principais campos.

    Args:
        id (int): Identificador do processo.
        numero (str): Número do processo.
        classe (str): Classe do processo.
        orgaoJulgador (str): Órgão julgador.
        segredoJustica (bool): Indica segredo de justiça.
        justicaGratuita (bool): Indica justiça gratuita.
        distribuidoEm (str): Data de distribuição.
        autuadoEm (str): Data de autuação.
        valorDaCausa (float): Valor da causa.
        poloAtivo (List[Polo]): Lista de polos ativos.
        poloPassivo (List[Polo]): Lista de polos passivos.
        assuntos (List[Assunto]): Lista de assuntos.
        itensProcesso (List[ItemProcesso]): Lista de itens do processo.
        expedientes (List[Expediente]): Lista de expedientes.
        juizoDigital (bool): Indica se é juízo digital.

    Returns:
        Processo: Dicionário com informações do processo.

    """

    id: int
    numero: str
    classe: str
    orgaoJulgador: str
    segredoJustica: bool
    justicaGratuita: bool
    distribuidoEm: str
    autuadoEm: str
    valorDaCausa: float
    poloAtivo: list[Polo]
    poloPassivo: list[Polo]
    assuntos: list[Assunto]
    itensProcesso: list[ItemProcesso]
    expedientes: list[Expediente]
    juizoDigital: bool


class Endereco(TypedDict, total=False):
    """Definição do endereço utilizado nos dados do processo judicial.

    Args:
        logradouro (str): Nome da rua ou avenida.
        numero (str): Número do endereço.
        complemento (str): Complemento do endereço.
        bairro (str): Bairro do endereço.
        municipio (str): Município do endereço.
        estado (str): Estado do endereço.
        cep (str): Código postal.

    Returns:
        Endereco: Dicionário com informações do endereço.


    """

    logradouro: str
    numero: str
    complemento: str
    bairro: str
    municipio: str
    estado: str
    cep: str


class Papel(TypedDict):
    """Define o papel de uma pessoa no processo.

    Args:
        id (int): Identificador do papel.
        nome (str): Nome do papel.
        identificador (str): Código identificador do papel.

    Returns:
        Papel: Dicionário com informações do papel.

    """

    id: int
    nome: str
    identificador: str


class Representante(TypedDict):
    """Define o representante de uma parte no processo.

    Args:
        id (int): Identificador do representante.
        idPessoa (int): Identificador da pessoa.
        nome (str): Nome do representante.
        login (str): Login do representante.
        tipo (str): Tipo de representante.
        documento (str): Documento do representante.
        tipoDocumento (str): Tipo do documento.
        endereco (Endereco): Endereço do representante.
        polo (str): Polo do representante.
        situacao (str): Situação do representante.
        papeis (List[Papel]): Lista de papéis do representante.
        utilizaLoginSenha (bool): Indica se utiliza login e senha.

    Returns:
        Representante: Dicionário com informações do representante.

    """

    id: int
    idPessoa: int
    nome: str
    login: str
    tipo: str
    documento: str
    tipoDocumento: str
    endereco: Endereco
    polo: str
    situacao: str
    papeis: list[Papel]
    utilizaLoginSenha: bool


class Polo(TypedDict):
    """Define uma parte (polo) do processo judicial.

    Args:
        id (int): Identificador do polo.
        idPessoa (int): Identificador da pessoa.
        nome (str): Nome do polo.
        login (str): Login do polo.
        tipo (str): Tipo do polo.
        documento (str): Documento do polo.
        tipoDocumento (str): Tipo do documento.
        endereco (Endereco): Endereço do polo.
        polo (str): Polo (ativo/passivo).
        situacao (str): Situação do polo.
        representantes (List[Representante]): Lista de representantes.
        utilizaLoginSenha (bool): Indica se utiliza login e senha.

    Returns:
        Polo: Dicionário com informações do polo.

    """

    id: int
    idPessoa: int
    nome: str
    login: str
    tipo: str
    documento: str
    tipoDocumento: str
    endereco: Endereco
    polo: str
    situacao: str
    representantes: list[Representante]
    utilizaLoginSenha: bool


class Assunto(TypedDict):
    """Define o assunto do processo judicial.

    Args:
        id (int): Identificador do assunto.
        codigo (str): Código do assunto.
        descricao (str): Descrição do assunto.
        principal (bool): Indica se é o assunto principal.

    Returns:
        Assunto: Dicionário com informações do assunto.

    """

    id: int
    codigo: str
    descricao: str
    principal: bool


class Anexo(TypedDict):
    """Define um anexo relacionado ao processo.

    Args:
        id (int): Identificador do anexo.
        idUnicoDocumento (str): ID único do documento.
        titulo (str): Título do anexo.
        tipo (str): Tipo do anexo.
        tipoConteudo (str): Tipo do conteúdo.
        data (str): Data do anexo.
        ativo (bool): Indica se está ativo.
        documentoSigiloso (bool): Indica se é sigiloso.
        usuarioPerito (bool): Indica se é usuário perito.
        documento (bool): Indica se é documento.
        publico (bool): Indica se é público.
        poloUsuario (Optional[str]): Polo do usuário.
        usuarioJuntada (str): Usuário que juntou o anexo.
        usuarioCriador (int): Usuário criador do anexo.
        instancia (Optional[str]): Instância do anexo.

    Returns:
        Anexo: Dicionário com informações do anexo.

    """

    id: int
    idUnicoDocumento: str
    titulo: str
    tipo: str
    tipoConteudo: str
    data: str
    ativo: bool
    documentoSigiloso: bool
    usuarioPerito: bool
    documento: bool
    publico: bool
    poloUsuario: str | None
    usuarioJuntada: str
    usuarioCriador: int
    instancia: str | None


class ItemProcesso(TypedDict, total=False):
    """Define um item do processo judicial.

    Args:
        id (int): Identificador do item.
        idUnicoDocumento (str): ID único do documento.
        titulo (str): Título do item.
        tipo (str): Tipo do item.
        tipoConteudo (str): Tipo do conteúdo.
        data (str): Data do item.
        ativo (bool): Indica se está ativo.
        documentoSigiloso (bool): Indica se é sigiloso.
        usuarioPerito (bool): Indica se é usuário perito.
        documento (bool): Indica se é documento.
        publico (bool): Indica se é público.
        mostrarHeaderData (bool): Indica se mostra header de data.
        usuarioJuntada (str): Usuário que juntou o item.
        usuarioCriador (int): Usuário criador do item.
        instancia (str): Instância do item.
        anexos (List[Anexo]): Lista de anexos.
        poloUsuario (str): Polo do usuário.

    Returns:
        ItemProcesso: Dicionário com informações do item do processo.

    """

    id: int
    idUnicoDocumento: str
    titulo: str
    tipo: str
    tipoConteudo: str
    data: str
    ativo: bool
    documentoSigiloso: bool
    usuarioPerito: bool
    documento: bool
    publico: bool
    mostrarHeaderData: bool
    usuarioJuntada: str
    usuarioCriador: int
    instancia: str
    anexos: list[Anexo]
    poloUsuario: str


class Expediente(TypedDict, total=False):
    """Define um expediente do processo judicial.

    Args:
        destinatario (str): Destinatário do expediente.
        tipo (str): Tipo do expediente.
        meio (str): Meio de envio.
        dataCriacao (str): Data de criação.
        dataCiencia (str): Data de ciência.
        fechado (bool): Indica se está fechado.

    Returns:
        Expediente: Dicionário com informações do expediente.

    """

    destinatario: str
    tipo: str
    meio: str
    dataCriacao: str
    dataCiencia: str
    fechado: bool
