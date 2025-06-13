## Função principal para inicialização do robô.

```python
def main(bot_name: str, bot_system: str, path_config: Path) -> None:
```

Esta função é responsável por carregar dinamicamente o módulo do robô especificado,
instanciar a classe do robô e executar o método de execução principal.
O nome do robô e do sistema são usados para localizar o módulo correto
dentro da estrutura do projeto. O arquivo de configuração é passado para o
robô durante a inicialização.

### Argumentos:

```python

bot_name (str): Nome do robô a ser inicializado. Deve corresponder ao nome do módulo do robô.
bot_system (str): Nome do sistema ao qual o robô pertence. Deve corresponder ao diretório do sistema.
path_config (Path): Caminho para o arquivo de configuração necessário para inicializar o robô.

```

### Exemplo:

```python
    main(
        bot_name="capa",  # Nome do robô
        bot_system="projudi",  # Sistema ao qual o robô pertence
        path_config=Path(
            "/caminho/para/config.json",
        ),
    )
```

## Disclaimer:

> Funcionamento do`path_config`

O arquivo do Json tem que estar junto com a planilha de execução do robô.
Os parâmetros do Json devem ser:

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
