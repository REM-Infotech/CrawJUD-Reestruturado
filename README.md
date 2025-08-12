# CrawJUD

[![Quality Gate Status](https://sonar.robotz.dev/api/project_badges/measure?project=REM-Infotech_CrawJUD-Reestruturado_9dae535d-6359-43cc-bdea-9d270cb528ce&metric=alert_status&token=sqb_f805bd2b1e570f147292c4dd8b69fed196d068af)](https://sonar.robotz.dev/dashboard?id=REM-Infotech_CrawJUD-Reestruturado_9dae535d-6359-43cc-bdea-9d270cb528ce)

CrawJUD é uma plataforma modular para automação de rotinas jurídicas, integrando robôs, APIs, tarefas assíncronas e comunicação em tempo real. O projeto prioriza escalabilidade, manutenção e integração com sistemas judiciais diversos.

## Principais Módulos

- **api/**: Backend principal (autenticação, rotas REST, dashboards, banco de dados)
- **crawjud_app/**: Gerenciador de tarefas assíncronas (jobs, agendamento, integrações externas)
- **crawjud/**: Núcleo dos robôs de automação (bots, utilitários, exceções)
- **socketio_server/**: Comunicação em tempo real via Socket.IO (logs, notificações)
- **tests/**: Testes automatizados

## Execução Rápida

1. Instale as dependências:
   ```powershell
   poetry install
   ```
2. Configure as variáveis de ambiente conforme os arquivos `ENVIRONMENT-VARIABLES.md` em `crawjud/` e `crawjud_app/resources/`.
3. Inicie os serviços desejados:
   - API: `python -m api`
   - Celery: `python -m crawjud_app`
   - Robôs: `python -m crawjud --bot_system <sistema> --bot_name <bot> --path_config <config>`
   - SocketIO: `python -m socketio_server`

Consulte os READMEs de cada módulo para instruções detalhadas.

## Exemplos de Uso

- **Executar robô:**

  1. Configure o arquivo JSON do robô (ver instruções em `crawjud/README.md`).
  2. Execute o comando do módulo `crawjud` com os parâmetros necessários.
  3. Acompanhe logs em tempo real pelo SocketIO Server.

- **Tarefa assíncrona (e-mail, upload):**
  1. Dispare a tarefa via API ou Celery App.
  2. O Celery processa a fila e executa a ação.

## Documentação e Suporte

- [Estrutura detalhada do projeto](PROJECT-STRUCTURE.md)
- [Variáveis de ambiente](crawjud/ENVIRONMENT-VARIABLES.md)
- Documentação específica em cada subpasta

## Contribuição

Contribuições são bem-vindas! Siga o padrão de documentação e consulte as instruções de cada módulo.
