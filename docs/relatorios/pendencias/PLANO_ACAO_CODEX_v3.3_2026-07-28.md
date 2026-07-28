# Plano de Ação Codex — v3.3

**Atividade:** evolução produtiva da Rodada 005 do APK Valley Consumidor  
**Issue:** `#63`  
**Branch inicial:** `codex/apk-valley-rodada-005-2026-07-28`

## Objetivo

Levar a vertical executável da Rodada 005 à produção por ondas controladas, sem habilitar as 24 ideias simultaneamente.

## Prioridade 0 — segurança e fundação

1. Persistir feature flags e registros em PostgreSQL.
2. Criar migrações, auditoria, idempotência e outbox.
3. Aplicar autenticação, RBAC/ABAC e isolamento por entidade.
4. Integrar telemetria, alertas, rate limit e rollback.
5. Reexecutar CI, Security, Database, OpenAPI e Compose Health.

## Prioridade 1 — pilotos P0

- Identity: homologar passkeys, quórum e antifraude.
- Finance: integrar ledger e PSP sem simular liquidação.
- STOCK: validar catálogo de compatibilidade e revisão humana.
- BPM: garantir exportação, cancelamento e retenção legal.
- Document: implementar sanitização com revisão visual.
- Health: integrar Health Connect/FHIR apenas com consentimento e revisão clínica.
- Legal: revisar finalidades, base legal e experiência sem dark patterns.
- AI Core: persistir memória, expiração e confirmação.

## Prioridade 2 — ideias P1 e P2

Implantar as demais ideias em pilotos regionais ou empresariais separados, sempre com flag própria, contrato, testes, telemetria e rollback.

## Testes obrigatórios

```bash
pytest -q tests/test_valley_consumer_innovation_round_004.py
pytest -q tests/test_valley_consumer_innovation_round_005.py
python3 scripts/validate_repository.py
```

Executar também gates remotos no mesmo SHA da revisão.

## Critérios de aceite

- feature flag persistida e desligada por padrão;
- autenticação e autorização reais;
- migrations reversíveis;
- trilha de auditoria;
- testes unitários, integração e segurança;
- evidência no ambiente correto;
- nenhuma credencial versionada;
- nenhuma alegação de cobertura ou prontidão sem homologação;
- PR revisado e integração exclusivamente por Squash and Merge.

## Bloqueios

PSP, passkeys, operadores de mobilidade, Health Connect/FHIR, aplicativos móveis e revisões especializadas dependem de contratos, credenciais ou profissionais externos.
