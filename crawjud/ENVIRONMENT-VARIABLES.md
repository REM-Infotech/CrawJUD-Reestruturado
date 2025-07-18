# Variáveis de Ambiente do Projeto CrawJUD

Este documento apresenta todas as variáveis de ambiente utilizadas no projeto, suas descrições e exemplos de uso. Configure estas variáveis no arquivo `.env` na raiz do projeto.

## Sumário

- [Configurações Flask](#configuracoes-flask)
- [Configurações Flask-Mail](#configuracoes-flask-mail)
- [Banco de Dados (SQLAlchemy)](#banco-de-dados-sqlalchemy)
- [Configurações Celery](#configuracoes-celery)
- [Configurações Redis](#configuracoes-redis)
- [Configurações MinIO](#configuracoes-minio)
- [Configurações SocketIO](#configuracoes-socketio)
- [Configurações CrawJUD](#configuracoes-crawjud)
- [Configurações Google Cloud](#configuracoes-google-cloud)

---

## Configurações Flask

```bash
WITH_REDIS="true"                # Habilita integração com Redis
APP_SECRET="11111"               # Chave secreta da aplicação
JWT_APP_SECRET="22222"           # Chave secreta para JWT
# DEBUG, TESTING, TEMPLATES_AUTO_RELOAD podem ser configurados conforme necessidade
```

## Configurações Flask-Mail

```bash
MAIL_SERVER="localhost"          # Servidor SMTP
MAIL_PORT="587"                  # Porta do servidor SMTP
MAIL_USE_TLS="false"             # Utiliza TLS
MAIL_USE_SSL="false"             # Utiliza SSL
MAIL_USERNAME=""                 # Usuário do e-mail
MAIL_PASSWORD=""                 # Senha do e-mail
MAIL_DEFAULT_SENDER="teste@teste.com" # E-mail remetente padrão
```

## Banco de Dados (SQLAlchemy)

```bash
SQLALCHEMY_DATABASE_URI="sqlite:///local.db" # URI do banco de dados SQLite
JAVA_HOME="C:\Oracle_JDK-21"                # Caminho para o Java (se necessário)
```

## Configurações Celery

```bash
BROKER_URL="redis://localhost:6379/0"       # URL do broker Celery (Redis)
RESULT_BACKEND="db+sqlite:///results.db"    # Backend de resultados Celery
TASK_IGNORE_RESULT=True                      # Ignora resultados das tasks
BROKER_CONNECTION_RETRY_ON_STARTUP=True      # Tenta reconectar broker ao iniciar
TIMEZONE="America\Manaus"                   # Fuso horário padrão
TASK_CREATE_MISSING_QUEUES=True              # Cria filas ausentes automaticamente
REDIS_OM_URL="redis://localhost:6379/0"     # URL Redis OM
```

## Configurações Redis

```bash
REDIS_HOST="localhost"                      # Host do Redis
REDIS_PORT=6379                              # Porta do Redis
REDIS_DB=0                                   # Banco do Redis
REDIS_PASSWORD=""                           # Senha do Redis
REDIS_URI="redis://localhost:6379"           # URI completa do Redis
```

## Configurações MinIO

```bash
MINIO_URL_SERVER="seu_minio:9000"           # URL do servidor MinIO
MINIO_ACCESS_KEY="sua_access_key"           # Access key MinIO
MINIO_SECRET_KEY="sua_secret_key"           # Secret key MinIO
MINIO_BUCKET_NAME="outputexec-bots"         # Nome do bucket MinIO
```

## Configurações SocketIO

```bash
SOCKETIO_SERVER_URL="http://localhost:5000" # URL do servidor SocketIO
SOCKETIO_SERVER_NAMESPACE="/logsbot"        # Namespace do servidor SocketIO
```

## Configurações CrawJUD

```bash
ROOT_USERNAME="seu_usuario_root"            # Usuário root
ROOT_PASSWORD="sua_senha_root"              # Senha root
ROOT_EMAIL="seu_email@dominio.com"          # E-mail root
ROOT_CLIENT="Nome do Cliente"               # Nome do cliente root
ROOT_CPF_CNPJ_CLIENT="00000000000000"       # CPF/CNPJ do cliente root
```

## Configurações Google Cloud

```bash
GCS_BUCKET_NAME="seu_bucket_gcs"            # Nome do bucket GCS
GCS_PROJECT_ID="seu_projeto_gcp"            # ID do projeto GCP
GCS_CREDENTIALS='...'                        # Credenciais do serviço (JSON)
```

> **Observação:**
>
> - Variáveis booleanas devem ser informadas como "true" ou "false" (string).
> - Para variáveis sensíveis (senhas, chaves), mantenha o arquivo `.env` seguro e fora de versionamento público.

---

### Exemplo de `.env` mínimo

```bash
APP_SECRET="sua_chave_secreta"
SQLALCHEMY_DATABASE_URI="sqlite:///local.db"
MINIO_URL_SERVER="seu_minio:9000"
MINIO_ACCESS_KEY="sua_access_key"
MINIO_SECRET_KEY="sua_secret_key"
SOCKETIO_SERVER_URL="http://localhost:5000"
```
