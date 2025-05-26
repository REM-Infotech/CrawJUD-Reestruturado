# CrawJUD-Reestruturado

CrawJUD é uma plataforma de automação para rotinas jurídicas, integrando robôs, APIs, tarefas assíncronas e comunicação em tempo real. O projeto é modularizado para facilitar manutenção, escalabilidade e integração com diferentes sistemas judiciais.

## Visão Geral

O projeto é composto por múltiplos módulos independentes, que se comunicam entre si para automatizar fluxos jurídicos:

- **API**: Backend principal, responsável por autenticação, rotas RESTful, dashboards e integração com banco de dados.
- **Celery App**: Gerenciador de tarefas assíncronas, utilizado para execução de jobs, agendamento e integração com serviços externos (e-mail, upload, etc).
- **CrawJUD**: Núcleo dos robôs de automação, com bots para diferentes sistemas judiciais, utilitários e tratamento de exceções.
- **SocketIO Server**: Servidor de comunicação em tempo real via Socket.IO, para logs, notificações e integração com clientes.
- **Tests**: Testes automatizados do projeto.

## Estrutura Geral

- **api/**: Backend principal da API, responsável por autenticação, rotas, modelos e integração com banco de dados.
- **celery_app/**: Gerenciador de tarefas assíncronas (Celery), incluindo workers, agendamento e integração com serviços externos.
- **crawjud/**: Núcleo dos robôs de automação, com bots para diferentes sistemas judiciais, utilitários e tratamento de exceções.
- **socketio_server/**: Servidor de comunicação em tempo real via Socket.IO, para logs, notificações e integração com clientes.
- **tests/**: Testes automatizados do projeto.
- **requirements.txt / poetry.lock / pyproject.toml**: Gerenciamento de dependências Python.

## Guia Rápido de Execução

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

## Exemplos de Fluxo de Trabalho

- **Execução de um robô**:
  1. Configure o arquivo de configuração do robô.
  2. Execute o comando do módulo `crawjud` com os parâmetros desejados.
  3. Acompanhe logs e notificações em tempo real pelo SocketIO Server.

- **Envio de e-mail assíncrono**:
  1. Dispare uma tarefa via API ou diretamente pelo Celery App.
  2. O Celery processa a fila e utiliza os utilitários de e-mail.

## Documentação

- [Estrutura detalhada do projeto](PROJECT-STRUCTURE.md)
- [Variáveis de ambiente](crawjud/ENVIRONMENT-VARIABLES.md)
- [Documentação de cada módulo nas subpastas]

## Contribuindo

Contribuições são bem-vindas! Siga as instruções de cada módulo e mantenha o padrão de documentação para facilitar a manutenção e o uso do mkdocs.
