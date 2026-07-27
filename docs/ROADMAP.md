# Roadmap do All-in-One + Valley

**Versão:** 1.1  
**Data e hora:** 26/07/2026 às 23:06:33  
**Catálogo oficial:** 24 módulos ativos  
**Issue de orquestração:** `#45`

O plano operacional vigente deve ser lido em conjunto com:

- `docs/Pendências Do desenvolvedor.md`;
- `docs/STATUS_ATUAL.md`;
- `docs/relatorios/pendencias/PLANO_ACAO_CODEX_v2.7_2026-07-26.md`;
- `tarefas.md`.

Documentos extensos anteriores permanecem como histórico técnico. Em caso de
divergência, prevalecem os arquivos listados acima e o catálogo
`config/module_catalog.json`.

## Baseline entregue

- Estrutura de 9 aplicações e 24 módulos ativos.
- Vision removido do catálogo operacional, preservando apenas evidências
  históricas necessárias.
- Runtime FastAPI, contratos, OpenAPI, autorização, auditoria e outbox.
- PostgreSQL, MongoDB, RabbitMQ e Redis em arquitetura versionada.
- Catálogo Business sincronizado com `legal`, `property` e `ai_core`.
- Auditoria de confirmação v7 reproduzível.
- Aplicações web, Valley Android, APK Admin e PDV Desktop em diferentes fases de
  validação.
- Fundação da onda de inovação com feature flags desligadas por padrão.
- Governança de marca para All in One, Valley e Valley Riders.

## Onda atual: estabilização e homologação

### Prioridade crítica

1. Homologar o ambiente público com identidade correta, HTTPS e evidências.
2. Publicar e validar o API Hub, incluindo `/health` e CORS.
3. Reexecutar a auditoria integral das rotas contra o backend público.
4. Proteger assinatura Android e procedimento de recuperação.
5. Homologar Google Sign-In real no APK.

### Prioridade alta

1. Regularizar os PRs `#34`, `#36`, `#37`, `#38` e `#40` contra a `main` atual.
2. Resolver a sobreposição entre `#34` e `#37` antes de qualquer integração.
3. Tornar checks obrigatórios e impedir merges sem evidência.
4. Validar o APK Admin do PR `#36`.
5. Validar o PDV Desktop offline do PR `#38`.
6. Validar a onda de inovação do PR `#40`.
7. Concluir a issue `#24` no projeto Stitch oficial.
8. Incorporar o ativo original aprovado da Valley Riders.
9. Auditar o pacote `.gemini/skills` e seus manifestos.
10. Concluir o executor Telegram e os quatro relatórios diários.

## Implementação iniciada nesta versão

A versão 2.7 inicia a implementação executável do ciclo Telegram por meio de:

- `scripts/telegram_activity_reporter.py`;
- testes unitários sem rede e sem credenciais reais;
- comandos para `activity_started`, `activity_completed` e
  `developer_pending_report`;
- modo `--dry-run` para validação segura;
- retry, timeout e sanitização de mensagens;
- credenciais exclusivamente por variáveis de ambiente.

A agenda automática de quatro relatórios diários continua bloqueada até que o
script passe nos gates e os secrets legítimos estejam configurados.

## Próximos incrementos para beta

1. Consolidar CI, segurança, banco, Docker, OpenAPI e artefatos.
2. Integrar Identity/API Hub com OIDC, MFA, KMS, KYC/KYB e liveness homologados.
3. Integrar PSP, fiscal brasileiro e conciliação em sandbox.
4. Sincronizar Stitch com credencial rotacionada e validar jornadas web/mobile.
5. Validar notificações, dashboards e observabilidade em ambiente vivo.
6. Validar backup, restore e resposta a incidentes.

## Bloqueadores para produção

1. Homologação regulatória, LGPD/DPIA, retenção e consentimento.
2. Pentest, carga, disaster recovery e backup/restore comprovados.
3. Homologação de parceiros financeiros, fiscais, transporte e saúde.
4. Assinaturas e credenciais armazenadas em cofres autorizados.
5. Ambiente público e API Hub com evidências vinculadas ao commit publicado.

## Histórico

| Versão | Data | Alteração principal |
|---|---|---|
| 1.0 | anterior a 26/07/2026 | Roadmap baseado em 25 domínios e bloqueadores iniciais. |
| 1.1 | 26/07/2026 | Consolidação em 24 módulos, prioridades v2.7 e início do executor Telegram. |