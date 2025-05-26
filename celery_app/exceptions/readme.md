# Exceptions (Celery App)

Este módulo centraliza o tratamento de exceções específicas para o contexto do Celery, como erros de envio de e-mail, falhas em tarefas assíncronas e problemas de integração com serviços externos.

## Estrutura

- **mail.py**: Exceções relacionadas ao envio de e-mails (ex: falha de autenticação, erro de conexão).
- **__init__.py**: Inicialização do módulo de exceções.

## Dicas
- Sempre trate exceções específicas para facilitar o debug e a manutenção das tasks.
- Consulte exemplos de uso nos próprios arquivos de exceção.
