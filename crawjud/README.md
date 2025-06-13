# Função principal para inicialização do robô.

```python
def main(bot_name: str, bot_system: str, path_config: Path) -> None:
```

Esta função é responsável por carregar dinamicamente o módulo do robô especificado,
instanciar a classe do robô e executar o método de execução principal.
O nome do robô e do sistema são usados para localizar o módulo correto
dentro da estrutura do projeto. O arquivo de configuração é passado para o
robô durante a inicialização.

## Argumentos:

> Caso esteja chamando a função `main` partir do arquivo `__main__.py`, você deve passar os argumentos:

```python

bot_name (str): Nome do robô a ser inicializado. Deve corresponder ao nome do módulo do robô.
bot_system (str): Nome do sistema ao qual o robô pertence. Deve corresponder ao diretório do sistema.
path_config (Path): Caminho para o arquivo de configuração necessário para inicializar o robô.

```

> Caso esteja executando o robô a partir do terminal, você deve passar os argumentos:

```bash
poetry run python -m crawjud --bot_name "capa" --bot_system "projudi" --path_config "/caminho/para/config.json"
```

## Exemplo:

```python
    main(
        bot_name="capa",  # Nome do robô
        bot_system="projudi",  # Sistema ao qual o robô pertence
        path_config=Path(
            "/caminho/para/config.json",
        ),
    )
```

## Observações:

### _Funcionamento do argumento `path_config`_

O arquivo do Json tem que estar junto com a planilha de execução do robô e o nome da pasta precisa ser o ID da execução do robô.

> Exemplo de estrutura da pasta:

    Q6M2N9 # ID da Execução do Robô
    │ config.json # ou o nome que você escolher `*.json`
    │ planilha.xlsx # ou o nome que você escolher `*.xlsx`

### _Parâmetros do Json_

```json
{
  "pid": "Q6M2N9", # ID Da Execução do Robô
  "schedule": false, # Indica se o robô está sendo executado agendado ou manualmente
  "xlsx": "Provisao_-_02.06.xlsx_CORRETA.xlsx", # Nome do arquivo Excel a ser processado
  "username": "login sistema", # Nome de usuário para autenticação no sistema
  "password": "senha sistema", # Senha para autenticação no sistema
  "login_method": "pw", # Método de login, pode ser "pw" (senha) ou "cert" (certificado)
  "client": "AME - AMAZONAS ENERGIA", # Nome do cliente, usado se o sistema for ELAW
  "total_rows": 44 # Total de linhas a serem processadas no arquivo Excel
}

```

> Caso o sistema não seja o ELAW, mude `client` para `state`

```jsonc
{
  "pid": "Q6M2N9", # ID Da Execução do Robô
  "schedule": false, # Indica se o robô está sendo executado agendado ou manualmente
  "xlsx": "Provisao_-_02.06.xlsx_CORRETA.xlsx", # Nome do arquivo Excel a ser processado
  "username": "login sistema", # Nome de usuário para autenticação no sistema
  "password": "senha sistema", # Senha para autenticação no sistema
  "login_method": "pw", # Método de login, pode ser "pw" (senha) ou "cert" (certificado)
  "state": "AM" # Estado do sistema, usado se o cliente não for ELAW
  "total_rows": 44 # Total de linhas a serem processadas no arquivo Excel
}

```
