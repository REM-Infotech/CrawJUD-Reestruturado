# Estrutura do Projeto

## Diretórios Principais

- [`./`](./): Raiz do projeto

  > Arquivos Raiz

  - [`README.md`](./README.md): Informações e instruções do projeto
  - [`LICENSE`](./LICENSE): Licença do projeto
  - `Arquivos de configuração comuns` (ex: [`pyproject.toml`](./pyproject.toml), [`.gitignore`](./.gitignore), etc.)

  > Diretórios

  - [`api/`](./api/__init__.py): Pasta de controle da API
  - [`socketio/`](./socketio/__init__.py): Pasta de controle do Socket.IO server
  - [`celery/`](./crawjud_app/__init__.py): Pasta de controle do gerenciador de tasks

    - [`tasks/`](./crawjud_app/tasks/__init__.py): Pasta de tarefas do Celery App
    - [`exceptions/`](./crawjud_app/exceptions/__init__.py): Tratamento de Erros do Celery App
    - [`resources/`](./crawjud_app/resources/__init__.py): Recursos do Celery App
    - [`addons/`](./crawjud_app/addons/__init__.py): Utilitários do Celery App
    - [`types/`](./crawjud_app/types/__init__.py): Tipos do Celery App

  - `crawjud/`: Pasta de scripts de automação
    - `bots/`: Códigos dos bots
    - `exceptions/`: Tratamento de Erros
    - `addons/`: Utilitários do robô
    - `core/`: Núcleo do robô
