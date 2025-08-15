"""Agrupamento de Literais."""

from typing import Literal

type MessageNadaEncontrado = Literal["Nenhum processo encontrado"]
type MessageTimeoutAutenticacao = Literal[
    "Tempo de espera excedido para validação de sessão"
]

type AppName = Literal["Quart", "Worker"]
type TypeLog = Literal["log", "success", "warning", "info", "error"]
type StatusType = Literal["Inicializando", "Em Execução", "Finalizado", "Falha"]
type TReturnMessageMail = Literal["E-mail enviado com sucesso!"]
type TReturnMessageExecutBot = Literal["Execução encerrada com sucesso!"]
type TReturnMessageUploadFile = Literal["Arquivo enviado com sucesso!"]
