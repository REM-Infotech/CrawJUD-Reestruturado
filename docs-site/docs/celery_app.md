# Celery App

Gerenciador de tarefas assíncronas do projeto, utilizando Celery para execução de jobs, agendamento e integração com serviços externos (ex: envio de e-mails, upload de arquivos, etc).

## Estrutura dos Itens

- **__main__.py**: Ponto de entrada para execução do Celery.
- **main.py**: Inicialização dos workers e beat (agendador).
- **__init__.py**: Configuração principal do Celery e logging.
- **addons/**: Utilitários para Celery (logger, mail, scheduler, storage).
- **exceptions/**: Exceções específicas do contexto Celery.
- **resources/**: Recursos e utilitários de configuração.
- **tasks/**: Tarefas Celery (bot, email, arquivos).
- **types/**: Tipos e contratos utilizados nas tasks.

### Subpastas
- **addons/logger/**: Configuração e handlers de logging para Celery.
- **addons/mail.py**: Utilitário para envio de e-mails.
- **addons/scheduler/**: Agendamento de tarefas.
- **addons/storage/**: Integração com armazenamento externo (ex: Google Cloud).

Consulte os arquivos de cada subpasta para detalhes de implementação.
