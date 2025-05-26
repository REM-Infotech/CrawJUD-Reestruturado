# Addons (CrawJUD)

Utilitários para os robôs, como autenticação, manipulação de elementos, logs, templates, busca e integração com webdriver. Os addons são essenciais para estender as funcionalidades dos bots e garantir integração com diferentes sistemas e fluxos.

## Estrutura

- **auth/**: Autenticação dos robôs (login, sessão, cookies).
- **elements/**: Manipulação de elementos de interface (seletores, campos, botões).
- **interator/**: Utilitários de iteração e navegação em listas e tabelas.
- **logger/**: Logging dos robôs, integração com sistemas de logs externos.
- **make_templates/**: Geração de templates para automação de documentos.
- **printlogs/**: Envio de logs para o servidor SocketIO.
- **search/**: Utilitários de busca e filtragem de dados.
- **webdriver/**: Integração com drivers de navegador (Selenium, etc).
- **__init__.py**: Inicialização do módulo de addons.

## Dicas
- Consulte a documentação de cada subpasta para exemplos práticos.
- Os addons podem ser reutilizados em diferentes bots para evitar duplicidade de código.
