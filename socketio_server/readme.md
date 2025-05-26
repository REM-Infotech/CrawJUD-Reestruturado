# SocketIO Server

Servidor de comunicação em tempo real baseado em Socket.IO, responsável por transmitir logs, notificações e eventos entre os robôs, API e clientes.

## Estrutura dos Itens

- **__main__.py**: Ponto de entrada do servidor SocketIO.
- **__init__.py**: Inicialização do app Quart e configuração do SocketIO.
- **middleware.py**: Middlewares para tratamento de requisições.
- **addons/**: Utilitários auxiliares (ex: logger).
- **constructor/**: Classes auxiliares para manipulação de arquivos e sessões.
- **domains/**: Serviços de domínio (ex: manipulação de arquivos, sessões).
- **namespaces/**: Namespaces do SocketIO (ex: bots, logs).
- **types/**: Tipos e contratos utilizados pelo servidor.

### Subpastas
- **addons/logger/**: Configuração e utilitários de logging para o servidor SocketIO.
- **constructor/file.py**: Manipulação de arquivos recebidos via SocketIO.
- **domains/file_service.py**: Serviço para manipulação de arquivos e sessões de usuário.
- **namespaces/**: Namespaces para diferentes canais de comunicação.

Consulte os arquivos de cada subpasta para detalhes de implementação.
