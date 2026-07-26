# Plano de Ação Estruturado para o Codex

**Versão:** 2.6  
**Data:** 26/07/2026  
**Repositório:** `interflownex/All-in-One`  
**Issue de orquestração:** `#28` (legada) / `#TBD` (primícias v2.6)  
**Ciclo principal:** 8 horas  
**Tolerância operacional:** até 4 horas adicionais  
**Limite para nova atualização:** 12 horas

## 1. Missão

Implantar de forma incremental, auditável, reversível e protegida por feature flags as primícias autorizadas (1,2,3,4,5 e 7–24), preservando integralmente o módulo STOCK e mantendo o recurso 6 fora de escopo.

## 2. Fundação transversal obrigatória (ordem fixa)

1. **Feature flags**: registrar as 23 flags `primicia.*` com padrão desligado em produção e ativação por ambiente/empresa/usuário.
2. **Entitlements e cobrança**: centralizar direitos por usuário/empresa/módulo/recurso/plano/validade/limite/consumo.
3. **Auditoria + eventos**: exigir ator, entidade, ação, estado anterior/posterior, correlação e resultado.
4. **Outbox transacional**: publicação idempotente com retry e DLQ.
5. **Segurança/privacidade**: menor privilégio, segregação por tenant, consentimento granular, retenção configurável e logs sem dado sensível.

## 3. Ondas de implantação (fatiamento pequeno e reversível)

### Onda A — Primícias 1 a 5 (núcleo de identidade, governança e dinheiro)

- Recurso 1 (Identity)
- Recurso 2 (Business)
- Recurso 3 (Permissions)
- Recurso 4 (Finance)
- Recurso 5 (Marketplace)

**Entrega mínima por recurso:** domínio, migration, repositório/serviço, endpoint + OpenAPI, evento, permissão tenant-aware, auditoria, testes e rollback.

### Onda B — Primícias 7 a 12 (operação logística e fechamento)

- Recurso 7 (Delivery)
- Recurso 8 (Riders)
- Recurso 9 (Services)
- Recurso 10 (Mobility Premium)
- Recurso 11 (Jobs)
- Recurso 12 (ERP)

**Regra crítica adicional:** Recurso 10 exige entitlement `primicia.mobility.intention_route_premium`, cotação com validade e cobrança única pós-confirmação.

### Onda C — Primícias 13 a 17 (inteligência operacional por exceção)

- Recurso 13 (WMS)
- Recurso 14 (TMS)
- Recurso 15 (CRM)
- Recurso 16 (BPM)
- Recurso 17 (Document)

**Regra crítica adicional:** nenhuma decisão automatizada sem trilha de revisão humana quando houver impacto jurídico, financeiro ou de segurança.

### Onda D — Primícias 18 a 24 (pendente de especificação completa)

- Recursos 18, 19, 20, 21, 22, 23 e 24

**Status:** bloqueado por dependência externa enquanto o enunciado oficial permanecer truncado.

## 4. Critérios de aceite executáveis por recurso

Cada recurso só pode ser marcado como concluído quando houver:

1. regra de negócio implementada;
2. persistência e migration aplicável;
3. endpoint funcional e contrato OpenAPI atualizado;
4. evento versionado em outbox;
5. autorização e isolamento por empresa;
6. trilha de auditoria completa;
7. interface web/móvel conectada ao backend real;
8. testes com feature flag **ON** e **OFF**;
9. métrica operacional mínima;
10. procedimento de rollback validado;
11. evidência rastreável (arquivo/commit/teste/log).

## 5. Plano de execução de 8 horas

### Bloco 1 (0h–1h30): Fundação transversal
- catálogo de feature flags `primicia.*`;
- baseline de entitlement;
- check de auditoria/event envelope;
- smoke test de desligamento imediato das flags.

### Bloco 2 (1h30–3h30): Onda A
- começar por recursos 1 e 3 (controle de identidade e autorização);
- em seguida recurso 4 (financeiro), recurso 2 (consórcio) e recurso 5 (coalizão).

### Bloco 3 (3h30–5h30): Onda B
- priorizar recurso 10 (Premium) para travar regra comercial e cobrança única;
- concluir recursos 7, 8, 9, 11 e 12 com testes de integração.

### Bloco 4 (5h30–7h): Onda C
- implementar recursos 13, 14 e 15;
- fechar recursos 16 e 17 com rollback por flag.

### Bloco 5 (7h–8h): Governança e evidências
- executar testes relevantes;
- consolidar relatórios e evidências;
- atualizar pendências + issue de orquestração.

## 6. Tolerância operacional de 4 horas

Usar a tolerância para:

1. corrigir regressões causadas pelas ondas A/B/C;
2. estabilizar métricas e contrato de eventos;
3. completar evidências faltantes para aceite.

## 7. Atualização obrigatória após 12 horas

Atualizar os documentos com:

- tarefas concluídas;
- falhas e causas;
- bloqueios ativos;
- evidências de teste;
- próximos passos priorizados.

## 8. Condições de parada

Parar e registrar bloqueio quando houver:

- ausência de requisito funcional oficial (caso atual dos recursos 18–24);
- dependência jurídica/comercial sem autorização;
- credencial legítima ausente;
- risco de sobrescrever trabalho de outro agente.
