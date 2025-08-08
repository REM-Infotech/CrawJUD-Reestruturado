from __future__ import annotations

import os
import re
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import (
    Any,
    Callable,
    Generator,
    List,
    Literal,
    Mapping,
    Optional,
    ParamSpec,
    Self,
    TypeAlias,
    TypedDict,
    TypeVar,
    Union,
)

import pandas as pd
from clear import clear
from dotenv import load_dotenv
from redis_om import Field, HashModel, JsonModel, NotFoundError
from tqdm import tqdm

description_message = (
    "e.g. '[(C3K7H5, log, 15, 19:37:15)> Salvando arquivos na pasta...]'"
)

T = TypeVar("RedisQuery", bound=Union[JsonModel])
P = ParamSpec("RedisQuerySpecs", bound=Union[JsonModel])
IncEx: TypeAlias = Union[
    set[int],
    set[str],
    Mapping[int, Union["IncEx", bool]],
    Mapping[str, Union["IncEx", bool]],
]

TDict = dict[str, str]


class ItemMessageList(TypedDict):
    """
    TypedDict representing a log message item.

    Attributes:
        id_log (int | None): Unique identifier for the log entry. Example: 1.
        message (str | None): The log message content. Example: "[(C3K7H5, log, 15, 19:37:15)> Salvando arquivos na pasta...]"

    """

    id_log: int  # e.g. 1 (unique identifier for the log entry)
    message: (
        str
        # e.g. "[(C3K7H5, log, 15, 19:37:15)> Salvando arquivos na pasta...]"
    )
    type: str


class BotData(TypedDict):
    """TypedDict for bot data."""

    NUMERO_PROCESSO: str
    GRAU: int | str

    FORO: str  # ESAJ EMISSAO | ELAW CADASTRO
    VALOR_CALCULADO: str  # CAIXA | CALCULADORA TJDFT
    ADVOGADO_INTERNO: str  # ELAW CADASTRO | ELAW COMPLEMENTO
    TIPO_EMPRESA: str  # ELAW CADASTRO | ELAW COMPLEMENTO
    VARA: str  # CAIXIA | ELAW CADASTRO | ELAW COMPLEMENTO
    COMARCA: str  # CAIXIA | ELAW CADASTRO | ELAW COMPLEMENTO

    TIPO_GUIA: str  # ELAW SOLICITACAO DE PAGAMENTO | ESAJ EMISSAO
    VALOR_CAUSA: str  # ELAW CADASTRO | ELAW COMPLEMENTO | ESAJ EMISSAO

    # CAIXA EMISSÃO GUIAS
    TRIBUNAL: str
    AGENCIA: str
    TIPO_ACAO: str
    AUTOR: str
    CPF_CNPJ_AUTOR: str
    REU: str
    CPF_CNPJ_REU: str
    NOME_CUSTOM: str
    TEXTO_DESC: str
    DATA_PGTO: str
    VIA_CONDENACAO: str

    # CALCULADORA TJDFT
    REQUERENTE: str
    REQUERIDO: str
    JUROS_PARTIR: str
    JUROS_PERCENT: str
    DATA_INCIDENCIA: str
    DATA_CALCULO: str
    MULTA_PERCENTUAL: str
    MULTA_DATA: str
    HONORARIO_SUCUMB_PERCENT: str
    HONORARIO_SUCUMB_DATA: str
    HONORARIO_SUCUMB_VALOR: str
    HONORARIO_SUCUMB_PARTIR: str
    PERCENT_MULTA_475J: str
    HONORARIO_CUMPRIMENTO_PERCENT: str
    HONORARIO_CUMPRIMENTO_DATA: str
    HONORARIO_CUMPRIMENTO_VALOR: str
    HONORARIO_CUMPRIMENTO_PARTIR: str
    CUSTAS_DATA: str
    CUSTAS_VALOR: str

    # ELAW ANDAMENTOS
    ANEXOS: list[str]
    DATA: str
    OCORRENCIA: str
    OBSERVACAO: str

    # ELAW CADASTRO
    AREA_DIREITO: str
    SUBAREA_DIREITO: str
    ESTADO: str
    EMPRESA: str
    PARTE_CONTRARIA: str
    ADV_PARTE_CONTRARIA: str
    TIPO_PARTE_CONTRARIA: str
    DOC_PARTE_CONTRARIA: str
    CAPITAL_INTERIOR: str
    ACAO: str
    DATA_DISTRIBUICAO: str
    ESCRITORIO_EXTERNO: str

    # ELAW COMPLEMENTO
    ESFERA: str
    UNIDADE_CONSUMIDORA: str
    LOCALIDADE: str
    BAIRRO: str
    DIVISAO: str
    DATA_CITACAO: str
    FASE: str
    PROVIMENTO: str
    FATO_GERADOR: str
    DESC_OBJETO: str
    OBJETO: str

    # ELAW DOWNLOAD DOCUMENTOS
    TERMOS: str

    # ELAW PROVISIONAMENTO
    PROVISAO: str
    DATA_BASE_CORRECAO: str
    DATA_BASE_JUROS: str
    VALOR_ATUALIZACAO: str
    OBSERVACAO: str

    # ELAW SOLICITACAO DE PAGAMENTO
    TIPO_PAGAMENTO: str
    VALOR_GUIA: str
    DOC_GUIA: str
    DOC_CALCULO: str
    TIPO_CONDENACAO: str
    DESC_PAGAMENTO: str
    DATA_LANCAMENTO: str
    CNPJ_FAVORECIDO: str
    COD_BARRAS: str
    SOLICITANTE: str

    # ESAJ EMISSAO
    CLASSE: str
    NOME_INTERESSADO: str
    CPF_CNPJ: str
    PORTAL: str

    # ESAJ | PROJUDI | PJE CAPA
    TRAZER_COPIA: str

    #  ESAJ | PROJUDI | PJE MOVIMENTACAO
    PALAVRAS_CHAVE: str
    DATA_INICIO: str
    DATA_FIM: str
    INTIMADO: str
    DOC_SEPARADOR: str
    TRAZER_TEOR: str
    USE_GPT: str
    TRAZER_PDF: str

    #  ESAJ | PROJUDI | PJE PROTOCOLO
    ANEXOS: str
    TIPO_PROTOCOLO: str
    TIPO_ARQUIVO: str
    TIPO_ANEXOS: str
    SUBTIPO_PROTOCOLO: str
    PETICAO_PRINCIPAL: str
    PARTE_PETICIONANTE: str


class DictSeparaRegiao(TypedDict):
    """
    Define o dicionário que separa regiões e posições de processos.

    Args:
        regioes (dict[str, list[BotData]]): Dicionário de regiões e bots.
        position_process (dict[str, int]): Posição dos processos por região.

    Returns:
        DictSeparaRegiao: Dicionário com informações de separação de regiões.

    """

    regioes: dict[str, list[BotData]]
    position_process: dict[str, int]


class Resultados(TypedDict):
    """
    Define o retorno do desafio contendo headers, cookies e resultados.

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
    """
    Define o desafio do PJe, contendo a imagem codificada e o token do desafio.

    Args:
        imagem (Base64Str): Imagem do desafio em base64.
        tokenDesafio (str): Token associado ao desafio.

    Returns:
        DictDesafio: Dicionário com informações do desafio.

    """

    imagem: str
    tokenDesafio: str


class DictResults(TypedDict):
    """
    Define os resultados retornados pelo desafio do PJe.

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
    """
    Define o processo judicial e seus principais campos.

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
    poloAtivo: List[Polo]
    poloPassivo: List[Polo]
    assuntos: List[Assunto]
    itensProcesso: List[ItemProcesso]
    expedientes: List[Expediente]
    juizoDigital: bool


class Endereco(TypedDict, total=False):
    """
    Definição do endereço utilizado nos dados do processo judicial.

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
    """
    Define o papel de uma pessoa no processo.

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
    """
    Define o representante de uma parte no processo.

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
    papeis: List[Papel]
    utilizaLoginSenha: bool


class Polo(TypedDict):
    """
    Define uma parte (polo) do processo judicial.

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
    representantes: List[Representante]
    utilizaLoginSenha: bool


class Assunto(TypedDict):
    """
    Define o assunto do processo judicial.

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
    """
    Define um anexo relacionado ao processo.

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
    poloUsuario: Optional[str]
    usuarioJuntada: str
    usuarioCriador: int
    instancia: Optional[str]


class ItemProcesso(TypedDict, total=False):
    """
    Define um item do processo judicial.

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
    anexos: List[Anexo]
    poloUsuario: str


class Expediente(TypedDict, total=False):
    """
    Define um expediente do processo judicial.

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


class ModelRedisHandler(HashModel):
    """
    Defina o modelo ModelRedisHandler para armazenar logs no Redis.

    Args:
        level (str): Nível do log (ex: 'INFO', 'ERROR').
        message (str): Mensagem do log.
        time (str): Data e hora do log.
        module (str): Nome do módulo do sistema.
        module_name (str): Nome específico do módulo.

    Returns:
        ModelRedisHandler: Instância do modelo de log.

    """

    level: str
    message: str
    time: str
    module: str
    module_name: str


class CachedExecutionDict(TypedDict):  # noqa: D101
    processo: str = Field(description="Processo Juridico", primary_key=True)
    pid: str = Field(
        default="desconhecido",
        description="e.g. 'C3K7H5' (identificador do processo)",
    )
    data: dict[str, Any] | list[Any] = Field()


class MessageLogDict(TypedDict):
    """
    Model for message logs.

    Attributes:
        id_log (int): Unique identifier for the log entry (e.g., 1).
        pid (str): Process identifier (e.g., 'C3K7H5').
        message (str): Log message content.
        type (str): Type of log entry (e.g., 'log', 'error', 'success').
        status (str): Status of the process (e.g., 'Em Execução', 'Concluído', 'Erro').
        start_time (str): Timestamp of when the log entry was created (e.g., '01/01/2023 - 19:37:15').
        row (int): Current row number being processed (e.g., 15).
        total (int): Total number of rows to be processed (e.g., 100).
        errors (int): Number of errors encountered (e.g., 2).
        success (int): Number of successful operations (e.g., 98).
        remaining (int): Number of rows remaining to be processed (e.g., 85).

    Methods:
        query_logs(pid: str) -> Self | Type[Self]:
            Retrieves the log entry associated with the given process identifier (pid).

    """

    """Model for message logs."""

    pid: str
    type: str
    messages: list[ItemMessageList]
    status: str
    start_time: str
    row: int
    total: int
    errors: int
    success: int
    remaining: int


class MessageLog(JsonModel):
    """
    Model for message logs.

    Attributes:
        id_log (int): Unique identifier for the log entry (e.g., 1).
        pid (str): Process identifier (e.g., 'C3K7H5').
        message (str): Log message content.
        type (str): Type of log entry (e.g., 'log', 'error', 'success').
        status (str): Status of the process (e.g., 'Em Execução', 'Concluído', 'Erro').
        start_time (str): Timestamp of when the log entry was created (e.g., '01/01/2023 - 19:37:15').
        row (int): Current row number being processed (e.g., 15).
        total (int): Total number of rows to be processed (e.g., 100).
        errors (int): Number of errors encountered (e.g., 2).
        success (int): Number of successful operations (e.g., 98).
        remaining (int): Number of rows remaining to be processed (e.g., 85).

    Methods:
        query_logs(pid: str) -> Self | Type[Self]:
            Retrieves the log entry associated with the given process identifier (pid).

    """

    """Model for message logs."""

    pid: str = Field(
        default="desconhecido",
        description="e.g. 'C3K7H5' (identificador do processo)",
        primary_key=True,
    )

    messages: list[ItemMessageList] = Field(
        default=[
            ItemMessageList(message="Mensagem não informada", id_log=0, type="info")
        ],
        description=description_message,
    )
    status: str = Field(
        default="Desconhecido",
        description="e.g. 'Em Execução', 'Concluído', 'Erro' (status do processo)",
    )
    start_time: str = Field(
        default="00/00/0000 - 00:00:00",
        description="e.g. '01/01/2023 - 19:37:15' (data/hora de início)",
    )
    row: int = Field(description="e.g. 15 (linha atual sendo processada)")
    total: int = Field(description="e.g. 100 (total de linhas a serem processadas)")
    errors: int = Field(description="e.g. 2 (quantidade de erros encontrados)")
    success: int = Field(
        description="e.g. 98 (quantidade de operações bem-sucedidas)"
    )
    remaining: int = Field(description="e.g. 85 (linhas restantes para processar)")

    @classmethod
    def query_logs(cls, pid: str) -> Self:  # noqa: D102
        with suppress(NotFoundError, Exception):
            log_pks = cls.all_pks()

            for pk in log_pks:
                if pk == pid:
                    return cls.get(pk)

    @classmethod
    def all_data(cls) -> list[Self]:  # noqa: D102
        return all_data(cls)

    def model_dump(  # noqa: D102
        self,
        mode: Literal["json", "python"] = "python",
        include: IncEx | None = None,
        exclude: IncEx | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal["none", "warn", "error"] = True,
        fallback: Callable[..., Any] | None = None,
        serialize_as_any: bool = False,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> MessageLogDict:  # noqa: D102
        return MessageLogDict(
            **super().model_dump(
                mode=mode,
                include=include,
                exclude=exclude,
                context=context,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
                round_trip=round_trip,
                warnings=warnings,
                fallback=fallback,
                serialize_as_any=serialize_as_any,
                *args,  # noqa: B026
                **kwargs,
            )
        )


class CachedExecution(JsonModel):  # noqa: D101
    processo: str = Field(description="Processo Juridico", primary_key=True)
    pid: str = Field(
        default="desconhecido",
        description="e.g. 'C3K7H5' (identificador do processo)",
    )
    data: Processo | Any = Field()

    @classmethod
    def all_data(cls) -> list[Self]:  # noqa: D102
        return all_data(cls)

    def model_dump(  # noqa: D102
        self,
        mode: Literal["json", "python"] = "python",
        include: IncEx | None = None,
        exclude: IncEx | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal["none", "warn", "error"] = True,
        fallback: Callable[..., Any] | None = None,
        serialize_as_any: bool = False,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> CachedExecutionDict:  # noqa: D102
        return CachedExecutionDict(
            **super().model_dump(
                mode=mode,
                include=include,
                exclude=exclude,
                context=context,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
                round_trip=round_trip,
                warnings=warnings,
                fallback=fallback,
                serialize_as_any=serialize_as_any,
                *args,  # noqa: B026
                **kwargs,
            )
        )


def all_data(cls: type[T]) -> Generator[T, Any, None]:  # noqa: D102, D103
    pks = list(cls.all_pks())
    cls.total_pks = len(pks)
    for pk in pks:
        yield cls.get(pk)


clear()
load_dotenv()


data_query = CachedExecution.all_data()
path_planilha = Path(__file__).parent.joinpath("Processos.xlsx")

if path_planilha.exists():
    os.remove(path_planilha)

list_dict_representantes: list[dict[str, str]] = []
kw = {
    "path": path_planilha,
    "engine": "openpyxl",
    "mode": "a",
    "if_sheet_exists": "overlay",
}


def formata_assuntos(
    lista: list[dict[str, str]],
) -> Generator[dict[str, datetime | str], Any, None]:
    for item in lista:
        formated_data = {
            f"{k}".upper(): formata_tempo(v)
            for k, v in list(dict(item).items())
            if not isinstance(v, list) or not k.lower() == "id"
        }

        yield formated_data


def formata_endereco(endr_dict: dict[str, str]) -> str:
    return " | ".join([
        f"{endr_k.upper()}: {endr_v.strip()}"
        for endr_k, endr_v in list(endr_dict.items())
    ])


def formata_representantes(
    lista: list[dict[str, str]],
) -> Generator[dict[str, datetime | str], Any, None]:
    for item in lista:
        tipo_parte = item.pop("tipo")
        if item.get("endereco"):
            item.update({"endereco".upper(): formata_endereco(item.get("endereco"))})

        formated_data = {
            f"{k}_{tipo_parte}".upper(): formata_tempo(v)
            for k, v in list(dict(item).items())
            if not isinstance(v, list)
            and not k.lower() == "utilizaLoginSenha".lower()
            and not k.lower() == "situacao".lower()
            and not k.lower() == "login".lower()
            and not k.lower() == "idPessoa".lower()
        }

        yield formated_data


def formata_partes(
    lista: list[dict[str, str]],
) -> Generator[dict[str, datetime | str], Any, None]:
    for item in lista:
        polo_parte = item.pop("polo")
        representantes: list[dict[str, str]] = []

        if item.get("endereco"):
            item.update({"endereco".upper(): formata_endereco(item.get("endereco"))})

        if item.get("representantes"):
            representantes = item.pop("representantes")

        if item.get("papeis"):
            item.pop("papeis")

        formated_data = {
            f"{k}_polo_{polo_parte}".upper(): formata_tempo(v)
            for k, v in list(dict(item).items())
            if not isinstance(v, list)
            and not k.lower() == "utilizaLoginSenha".lower()
            and not k.lower() == "situacao".lower()
            and not k.lower() == "login".lower()
            and not k.lower() == "idPessoa".lower()
        }

        for adv in list(formata_representantes(representantes)):
            _new_data = {"REPRESENTADO": item.get("nome")}
            _new_data.update(adv)
            list_dict_representantes.append(_new_data)

        yield formated_data


def formata_partes_terceiros(
    lista: list[dict[str, str]],
) -> Generator[dict[str, str], Any, None]:
    for item in lista:
        polo_parte = item.pop("polo")
        representantes: list[dict[str, str]] = []

        if item.get("endereco"):
            item.update({"endereco".upper(): formata_endereco(item.get("endereco"))})

        if item.get("representantes"):
            representantes = item.pop("representantes")

        if item.get("papeis"):
            item.pop("papeis")

        formated_data = {
            f"{k}_{polo_parte}".upper(): formata_tempo(v)
            for k, v in list(dict(item).items())
            if not isinstance(v, list)
            and not k.lower() == "utilizaLoginSenha".lower()
            and not k.lower() == "situacao".lower()
            and not k.lower() == "login".lower()
            and not k.lower() == "idPessoa".lower()
        }

        for adv in list(formata_representantes(representantes)):
            _new_data = {"REPRESENTADO": item.get("nome")}
            _new_data.update(adv)
            list_dict_representantes.append(_new_data)

        yield formated_data


def formata_tempo(item: str | bool) -> datetime | float | int | bool | str:
    if isinstance(item, str):
        if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$", item):
            return datetime.strptime(item.split(".")[0], "%Y-%m-%dT%H:%M:%S")

        elif re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}$", item):
            return datetime.strptime(item, "%Y-%m-%dT%H:%M:%S.%f")

    return item


def formata_anexos(
    lista: list[dict[str, str]],
) -> Generator[dict[str, str], Any, None]:
    new_lista: list[dict[str, str]] = []
    for item in lista:
        new_lista.extend(item.pop("anexos"))

    for item in new_lista:
        formated_data = {
            k.upper(): formata_tempo(v)
            for k, v in list(dict(item).items())
            if not isinstance(v, list)
            and (
                k.lower() == "id"
                or k.lower() == "titulo"
                or k.lower() == "idUnicoDocumento".lower()
                or k.lower() == "data"
            )
        }

        yield formated_data


def formata_movimentacao(
    lista: list[dict[str, str]],
) -> Generator[dict[str, str], Any, None]:
    for item in lista:
        if item.get("anexos"):
            item.pop("anexos")

        formated_data = {
            k.upper(): formata_tempo(v)
            for k, v in list(dict(item).items())
            if not isinstance(v, list)
            and (
                k.lower() == "id"
                or k.lower() == "titulo"
                or k.lower() == "idUnicoDocumento".lower()
                or k.lower() == "data"
                or k.lower() == "usuarioCriador".lower()
                or k.lower() == "tipoConteudo".lower()
            )
        }

        yield formated_data


# Salva os dados em lotes para evitar exceder o limite de linhas do Excel
def save_in_batches(
    data: list[dict], sheet_name: str, writer: pd.ExcelWriter, batch_size: int = 5000
) -> None:
    """
    Salva os dados em lotes no arquivo Excel para evitar exceder o limite de linhas.

    Args:
        data (list[dict]): Lista de dicionários com os dados a serem salvos.
        sheet_name (str): Nome da planilha no Excel.
        writer (pd.ExcelWriter): Objeto ExcelWriter para escrita.
        batch_size (int): Tamanho do lote de linhas por escrita.

    Returns:
        None: Não retorna valor.

    """
    df = pd.DataFrame(data)
    try:
        existing_df = pd.read_excel(str(path_planilha), sheet_name=sheet_name)
        df_final = pd.concat([existing_df, df])
        df_final.to_excel(writer, sheet_name=sheet_name, index=False)
    except Exception:
        df.to_excel(writer, sheet_name=sheet_name, index=False)


def formata_geral(
    lista: list[dict[str, str]],
) -> Generator[dict[str, datetime | str], Any, None]:
    for item in lista:
        formated_data = {
            k.upper(): formata_tempo(v)
            for k, v in list(dict(item).items())
            if not isinstance(v, list)
        }

        yield formated_data


def load_data() -> tuple[list, list, list]:
    pbar = tqdm(enumerate(data_query))
    data_save: list[dict[str, str]] = []
    advogados: list[dict[str, str]] = []
    outras_partes_list: list[dict[str, str]] = []
    lista_partes_ativo: list[dict[str, str]] = []
    lista_partes_passivo: list[dict[str, str]] = []
    list_assuntos: list[dict[str, str]] = []  # noqa: N806
    list_anexos: list[dict[str, str]] = []
    list_movimentacoes: list[dict[str, str]] = []
    list_expedientes: list[dict[str, str]] = []
    contagem = 0
    divide_5 = 0
    for _, _item in pbar:
        if not pbar.total:
            pbar.total = int(_item.total_pks) + 1
            pbar.display()
            divide_5 = int(pbar.total / 5)

        _pk = _item.processo
        _data_item = _item.model_dump()["data"]

        if not _data_item.get("numero"):
            print(_data_item)
            continue

        _data_item.pop("numero")

        if _data_item.get("expedientes"):
            list_expedientes.extend([
                {"NUMERO_PROCESSO": _pk, **item}
                for item in list(formata_geral(list(_data_item.pop("expedientes"))))
            ])

        if _data_item.get("itensProcesso"):
            itens_processo: list[dict[str, str]] = _data_item.pop("itensProcesso")
            list_anexos.extend([
                {"NUMERO_PROCESSO": _pk, **item}
                for item in list(
                    formata_anexos(
                        list(filter(lambda x: x.get("anexos"), itens_processo))
                    )
                )
            ])
            list_movimentacoes.extend([
                {"NUMERO_PROCESSO": _pk, **item}
                for item in formata_movimentacao(list(itens_processo))
            ])

        list_assuntos.extend([
            {"NUMERO_PROCESSO": _pk, **item}
            for item in list(formata_assuntos(_data_item.pop("assuntos")))
        ])
        lista_partes_passivo.extend([
            {"NUMERO_PROCESSO": _pk, **item}
            for item in list(formata_partes(_data_item.pop("poloPassivo")))
        ])
        lista_partes_ativo.extend([
            {"NUMERO_PROCESSO": _pk, **item}
            for item in list(formata_partes(_data_item.pop("poloAtivo")))
        ])

        if _data_item.get("poloOutros"):
            outras_partes_list.extend([
                {"NUMERO_PROCESSO": _pk, **item}
                for item in list(
                    formata_partes_terceiros(_data_item.pop("poloOutros"))
                )
            ])

        global list_dict_representantes
        advogados.extend([
            {"NUMERO_PROCESSO": _pk, **item} for item in list_dict_representantes
        ])

        data_save.extend([
            {"NUMERO_PROCESSO": _pk, **item}
            for item in list(formata_geral([_data_item]))
        ])

        if contagem == int(divide_5) or int(pbar.n) + 1 == pbar.total:
            with pd.ExcelWriter(**kw) as writer:
                saves = [
                    (data_save, "Processos", writer),
                    (list_assuntos, "Assuntos", writer),
                    (outras_partes_list, "Outras Partes", writer),
                    (lista_partes_ativo, "Autores", writer),
                    (lista_partes_passivo, "Réus", writer),
                    (advogados, "Advogados", writer),
                    (list_movimentacoes, "Movimentações", writer),
                    (list_anexos, "Anexos Movimentações", writer),
                    (list_expedientes, "Expedientes", writer),
                ]
                for save in saves:
                    save_in_batches(*save)
                    save[0].clear()

                data_save: list[dict[str, str]] = []
                advogados = []
                outras_partes_list = []
                lista_partes_ativo = []
                lista_partes_passivo = []
                list_assuntos: list[dict[str, str]] = []
                list_anexos: list[dict[str, str]] = []
                list_movimentacoes: list[dict[str, str]] = []
                list_expedientes: list[dict[str, str]] = []

            contagem = 0

        contagem += 1
        list_dict_representantes = []


with suppress(Exception):
    if not path_planilha.exists():
        with pd.ExcelWriter(str(path_planilha), "openpyxl", mode="w") as writer:
            pd.DataFrame().to_excel(excel_writer=writer, sheet_name="Processos")


load_data()
