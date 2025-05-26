# Tasks (Celery App)

Tarefas assíncronas gerenciadas pelo Celery. Este módulo reúne tasks para execução de bots, envio de e-mails, manipulação de arquivos e outras rotinas automatizadas.

## Estrutura

- **bot.py**: Tarefas relacionadas à execução de bots de automação.
- **email.py**: Tarefas de envio de e-mails assíncronos.
- **files.py**: Tarefas de manipulação de arquivos (upload, download, processamento).
- **__init__.py**: Inicialização do módulo de tarefas.

## Dicas
- Utilize tasks para desacoplar processos demorados da API principal.
- Consulte exemplos de uso nos próprios arquivos de tasks.
