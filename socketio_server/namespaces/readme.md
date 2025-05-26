# Namespaces (SocketIO Server)

Namespaces do SocketIO para diferentes canais de comunicação. Cada namespace representa um canal lógico para manipulação de arquivos, logs, notificações e outros eventos em tempo real.

## Estrutura

- **files.py**: Namespace para manipulação de arquivos (upload, download, notificações).
- **logs.py**: Namespace para logs em tempo real.
- **notifications.py**: Namespace para notificações de eventos.
- **__init__.py**: Inicialização do módulo de namespaces.

## Dicas
- Utilize namespaces para segmentar eventos e garantir escalabilidade do servidor.
- Consulte exemplos de uso nos próprios arquivos de namespaces.
