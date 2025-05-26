# CrawJUD-Reestruturado

CrawJUD é uma plataforma de automação para rotinas jurídicas, integrando robôs, APIs, tarefas assíncronas e comunicação em tempo real. O projeto é modularizado para facilitar manutenção, escalabilidade e integração com diferentes sistemas judiciais.

## Estrutura Geral

- **api/**: Backend principal da API, responsável por autenticação, rotas, modelos e integração com banco de dados.
- **celery_app/**: Gerenciador de tarefas assíncronas (Celery), incluindo workers, agendamento e integração com serviços externos.
- **crawjud/**: Núcleo dos robôs de automação, com bots para diferentes sistemas judiciais, utilitários e tratamento de exceções.
- **socketio_server/**: Servidor de comunicação em tempo real via Socket.IO, para logs, notificações e integração com clientes.
- **tests/**: Testes automatizados do projeto.
- **requirements.txt / poetry.lock / pyproject.toml**: Gerenciamento de dependências Python.

## Como executar

1. Instale as dependências:
   ```powershell
   poetry install
   ```
2. Configure as variáveis de ambiente conforme `ENVIRONMENT-VARIABLES.md` nas pastas `crawjud/` e `resources/`.
3. Inicie os serviços conforme a necessidade:
   - API: `python -m api`
   - Celery: `python -m celery_app`
   - Robôs: `python -m crawjud --bot_system <sistema> --bot_name <bot> --path_config <config>`
   - SocketIO: `python -m socketio_server`

Consulte os `readme.md` de cada pasta para detalhes específicos.
