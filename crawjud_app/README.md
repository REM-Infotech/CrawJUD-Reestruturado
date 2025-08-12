# Documentação da Pasta crawjud_app

## Sumário

- [Introdução](#introdução)
- [Estrutura de Diretórios](#estrutura-de-diretórios)
- [Descrição dos Componentes](#descrição-dos-componentes)
- [Exemplo de Uso](#exemplo-de-uso)

## Introdução

Esta pasta contém os módulos e recursos relacionados à configuração e execução do Celery no projeto. O Celery é utilizado para gerenciamento de tarefas assíncronas e processamento em background.

## Estrutura de Diretórios

- `addons/`: Funcionalidades adicionais para o Celery.
- `custom/`: Customizações específicas para o projeto.
- `exceptions/`: Definição de exceções customizadas.
- `resources/`: Recursos auxiliares, como variáveis de ambiente.
- `tasks/`: Definição das tarefas Celery.
- `types/`: Tipos e estruturas de dados utilizadas.
- `__init__.py`, `__main__.py`, `main.py`: Arquivos principais de inicialização e execução do Celery.

## Descrição dos Componentes

- **`main.py`**: Responsável pela configuração e inicialização da aplicação Celery.
- **`resources/ENVIRONMENT-VARIABLES.md`**: Documentação das variáveis de ambiente necessárias para integração com serviços externos.
- **`tasks/`**: Contém as definições das tarefas que serão executadas de forma assíncrona.

## Exemplo de Uso

Para executar o worker do Celery:

```bash
celery -A crawjud_app.main worker --loglevel=info
```

Consulte a documentação de cada subpasta para detalhes específicos.
