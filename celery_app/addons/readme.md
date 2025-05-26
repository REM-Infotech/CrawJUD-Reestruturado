# Addons (Celery App)

Utilitários auxiliares para o Celery, como logging, envio de e-mails, agendamento e integração com armazenamento externo. Os addons facilitam a extensão das funcionalidades do Celery App, promovendo modularidade e reutilização.

## Estrutura

- **logger/**: Configuração e handlers de logging para Celery.
- **mail.py**: Utilitário para envio de e-mails.
- **scheduler/**: Utilitários para agendamento de tarefas periódicas.
- **storage/**: Integração com armazenamento externo (ex: Google Cloud Storage).
- **__init__.py**: Inicialização do módulo de addons.

## Dicas
- Utilize os utilitários de logging para monitorar tarefas em produção.
- O módulo de e-mail pode ser integrado com variáveis de ambiente para maior segurança.
