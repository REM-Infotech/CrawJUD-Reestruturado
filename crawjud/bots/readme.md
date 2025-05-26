# Bots (CrawJUD)

Este módulo contém as implementações dos robôs de automação para diferentes sistemas judiciais. Cada subpasta representa um sistema distinto, com código especializado para interagir com portais, baixar documentos, processar movimentações e extrair informações relevantes.

## Estrutura

- **caixa/**: Robôs para o sistema Caixa Econômica Federal.
- **calculadoras/**: Robôs para sistemas de cálculo judicial.
- **elaw/**: Robôs para o sistema Elaw.
- **esaj/**: Robôs para o sistema ESAJ (Tribunais de Justiça).
- **pje/**: Robôs para o sistema PJe (Processo Judicial Eletrônico).
- **projudi/**: Robôs para o sistema Projudi.

## Exemplo de Execução

```sh
poetry run python -m crawjud --bot_system esaj --bot_name <nome_bot> --path_config <config.json>
```

## Observações
- Consulte a documentação de cada subpasta para detalhes de configuração e exemplos de uso.
- Os robôs podem ser integrados com o SocketIO Server para logs em tempo real.
