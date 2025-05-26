# API

Backend principal da aplicação, responsável por expor endpoints RESTful, autenticação, controle de usuários, dashboards e integração com banco de dados.

## Estrutura dos Itens

- **__main__.py**: Ponto de entrada da API (inicializa o servidor).
- **__init__.py**: Inicialização do app Quart, configuração de extensões e banco de dados.
- **quartconf.py**: Configurações da aplicação (variáveis de ambiente, banco, JWT, etc).
- **middleware.py**: Middlewares para tratamento de requisições e respostas.
- **addons/**: Utilitários auxiliares (ex: logger, geração de modelos, cores).
- **models/**: Modelos de dados (ORM) e entidades do sistema.
- **routes/**: Rotas da API, separadas por domínio (auth, dashboard, bot, etc).

### Subpastas
- **addons/logger/**: Configuração e utilitários de logging.
- **addons/make_models/**: Scripts para geração automática de modelos.
- **models/**: Modelos de dados como bots, usuários, agendamentos, etc.
- **routes/bot/**: Rotas relacionadas à execução e controle de bots.
- **routes/config/**: Rotas para configuração do sistema.
- **routes/execution/**: Rotas para execução de tarefas específicas.

Consulte os arquivos de cada subpasta para detalhes de implementação.
