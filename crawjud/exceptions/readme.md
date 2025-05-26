# Exceptions (CrawJUD)

Este módulo centraliza o tratamento de exceções específicas dos robôs CrawJUD. Aqui estão definidas classes de erro para diferentes cenários, facilitando o debug e a manutenção dos bots.

## Estrutura

- **bot.py**: Exceções relacionadas à execução dos bots (ex: falha de login, erro de scraping).
- **elaw.py**: Exceções específicas do sistema Elaw.
- **__init__.py**: Inicialização do módulo de exceções.

## Dicas
- Sempre capture e trate exceções específicas para cada sistema.
- Consulte os exemplos de uso nos próprios arquivos de exceção.
