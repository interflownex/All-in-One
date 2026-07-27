# All-in-One

![All-in-One](assets/brand/all-in-one-logo-official.png)

**Versão documental:** 2.7  
**Atualização:** 26/07/2026 às 23:06:33  
**Fonte operacional:** `docs/Pendências Do desenvolvedor.md`

SuperApp modular com identidade única para consumidores, empresas, riders,
prestadores, mobilidade, Jobs, saúde e operações empresariais. O repositório
implementa microserviços FastAPI, contratos OpenAPI, persistência
PostgreSQL/MongoDB, eventos, controles de segurança, infraestrutura e gates de
CI.

## Estado oficial atual

- 9 superfícies de aplicação catalogadas.
- 24 módulos ativos, com o módulo Vision removido do catálogo operacional.
- `legal`, `property` e `ai_core` sincronizados entre catálogo e Business.
- Auditoria reproduzível em `scripts/audit_confirmation_v7.py`.
- Front-ends, APKs, PDV Desktop e integrações externas em estágios diferentes de
  homologação, descritos no relatório de pendências vigente.
- Nenhuma referência histórica ao Vision deve ser interpretada como módulo ativo.

## Fontes de verdade

1. `AGENTS.md`: regras obrigatórias para agentes.
2. `tarefas.md`: passagem operacional para a próxima IA desenvolvedora.
3. `docs/Pendências Do desenvolvedor.md`: pendências consolidadas.
4. `docs/relatorios/pendencias/`: relatórios e planos versionados.
5. `docs/DOCUMENTATION_INDEX.md`: classificação de toda a documentação.
6. `docs/STATUS_ATUAL.md`: fotografia operacional vigente.
7. `config/module_catalog.json`: catálogo oficial de módulos e aplicações.
8. `config/branding/authorized_assets.json`: ativos de marca autorizados.

## Baseline implementado

- Runtime compartilhado com autorização, workflows, idempotência, auditoria e
  outbox.
- PostgreSQL com migrations, stores tipados, ledger e auditoria append-only.
- MongoDB para memória IA consentida, social e telemetria.
- RabbitMQ com dispatcher transacional e Redis para cache e rate limit.
- Contratos, OpenAPI, Dockerfiles e testes-base dos 24 módulos ativos.
- Jobs com currículo, importação de CTPS em PDF, procedência e armazenamento
  cifrado.
- Orquestração Stitch declarativa e manifestos preservados.
- Aplicações web, Valley Android, APK Admin e PDV Desktop em validação contínua.

## Jobs e CTPS Digital

O usuário pode manter currículo, registrar experiências, buscar vagas e se
candidatar. O módulo Jobs importa PDF da CTPS Digital, preserva hash da
evidência, cifra o arquivo e diferencia conteúdo importado de conteúdo
autodeclarado. A importação não declara verificação oficial externa sem
integração autorizada.

Somente recrutadores vinculados a empresa ativa e com escopo Jobs acessam a base
permitida. Cada consulta individual deve gerar log append-only. Consulte
`docs/JOBS_CTSP_DIGITAL.md`.

## Eventos e Stitch

`workers/outbox_dispatcher` publica eventos de `audit.domain_events` no exchange
RabbitMQ `all-in-one.domain`, confirma a entrega e registra tentativas em
`audit.event_deliveries`.

O planejamento visual usa Google Stitch por projeto isolado. `discover` e `sync`
exigem credencial legítima fornecida fora do Git. Consulte
`docs/STITCH_FRONTEND.md`.

## Execução local

```bash
python -m pip install -r requirements-dev.txt
python scripts/scaffold_modules.py --check
python scripts/audit_confirmation_v7.py
python scripts/validate_repository.py
python -m pytest --import-mode=importlib
docker compose -f infra/docker/docker-compose.yml up --build
```

## Organização

| Caminho | Conteúdo |
|---|---|
| `apps/` | Experiências cliente, empresa, rider e administração |
| `modules/` | 24 módulos ativos e seus testes |
| `contracts/` | Contratos de domínio versionáveis |
| `database/` | Migrations PostgreSQL e validações MongoDB |
| `docs/` | Arquitetura, segurança, operação, roadmap e relatórios |
| `infra/` | Docker, Kubernetes e infraestrutura |
| `workers/` | Dispatchers e consumidores assíncronos |
| `.github/workflows/` | Gates e automações de entrega |

## Governança

- Trabalhar em branch própria.
- Proibir push direto na `main`.
- Executar testes e registrar evidências.
- Integrar por Pull Request e Squash and Merge.
- Manter credenciais fora do Git.
- Não reconstruir ativos oficiais de marca.
- Atualizar `tarefas.md` e os relatórios a cada ciclo relevante.

Integrações reguladas ou externas permanecem bloqueadas para produção até
credenciais legítimas, homologação, DPIA/LGPD e testes E2E documentados.