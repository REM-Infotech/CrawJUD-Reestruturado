# CrawJUD (Robôs)

Núcleo dos robôs de automação, contendo bots para diferentes sistemas judiciais, utilitários, tratamento de exceções e tipos auxiliares.

## Estrutura dos Itens

- **__main__.py**: Ponto de entrada para execução dos robôs.
- **__init__.py**: Inicialização do módulo.
- **ENVIRONMENT-VARIABLES.md**: Variáveis de ambiente necessárias para execução dos robôs.
- **addons/**: Utilitários para autenticação, manipulação de elementos, logs, templates, busca, webdriver, etc.
- **bots/**: Implementações dos robôs para cada sistema (caixa, calculadoras, elaw, esaj, pje, projudi).
- **core/**: Núcleo de funções e classes base dos robôs.
- **exceptions/**: Exceções específicas dos robôs.
- **types/**: Tipos e contratos utilizados pelos robôs.

### Subpastas
- **addons/auth/**: Autenticação dos robôs.
- **addons/elements/**: Manipulação de elementos de interface.
- **addons/interator/**: Utilitários de iteração.
- **addons/logger/**: Logging dos robôs.
- **addons/printlogs/**: Envio de logs para o servidor SocketIO.
- **addons/search/**: Utilitários de busca.
- **addons/webdriver/**: Integração com drivers de navegador.
- **bots/**: Cada subpasta implementa um robô para um sistema judicial específico.
- **core/data_formatters/**: Funções de formatação de dados.

## Inicializar Robô

```sh
poetry run python -m crawjud --json "path/to/config.json"
```
