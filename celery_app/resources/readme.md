# Resources (Celery App)

Recursos e utilitários de configuração para o Celery. Este módulo reúne arquivos de variáveis de ambiente, utilitários para carregamento de configurações e inicialização do contexto do Celery App.

## Estrutura

- **ENVIRONMENT-VARIABLES.md**: Variáveis de ambiente necessárias para o funcionamento do Celery (ex: credenciais de serviços externos, configurações de e-mail).
- **load_config.py**: Utilitário para carregar configurações do projeto de forma dinâmica.
- **__init__.py**: Inicialização do módulo de recursos.

## Dicas
- Mantenha as variáveis de ambiente seguras e nunca as exponha em repositórios públicos.
- Consulte exemplos de configuração no arquivo ENVIRONMENT-VARIABLES.md.
