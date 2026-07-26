# Mapeamento Tecnico - 24 Ideias Aprovadas

Versao: 1.0
Data: 2026-07-26
Hora: 14:32:04
Fuso: America/Sao_Paulo
Repositorio: interflownex/All-in-One
Branch: feature/primicias-selecionadas-v1
Commit de referencia: 77fa6fab5f1c881ba6289dc288dc64e20421614a

## Objetivo

Mapear os alvos tecnicos minimos por ideia para iniciar implementacao rastreavel sem perda de escopo.

## Fonte de verdade usada

- config/module_catalog.json
- contracts/\*.md
- modules/<modulo>/main.py
- database/postgres/migrations/
- tests/

## Tabela de mapeamento por ideia

| Codigo          | Modulo primario | Integracoes-chave                                | Arquivos-alvo minimos                                        | Testes minimos                       | Nivel   |
| --------------- | --------------- | ------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------ | ------- |
| VLY-20260726-01 | jobs            | identity, document, business, permissions        | modules/jobs/main.py, contracts/jobs.md                      | tests de emissor e compartilhamento  | alta    |
| VLY-20260726-02 | identity        | permissions, finance, api_hub, ai_core           | modules/identity/main.py, modules/api_hub/main.py            | testes de risco e step-up auth       | critica |
| VLY-20260726-03 | business        | identity, marketplace, crm, legal, bi            | modules/business/main.py, contracts/business.md              | testes de selo explicavel            | alta    |
| VLY-20260726-04 | api_hub         | identity, permissions, finance, health, document | modules/api_hub/main.py, contracts/api_hub.md                | testes de consentimento e revogacao  | alta    |
| VLY-20260726-05 | permissions     | todos os modulos                                 | modules/permissions/main.py, modules/shared/feature_flags.py | testes de expirar e finalidade       | critica |
| VLY-20260726-06 | marketplace     | stock, finance, delivery, business, permissions  | modules/marketplace/main.py, contracts/marketplace.md        | testes de carrinho cooperativo       | alta    |
| VLY-20260726-07 | finance         | ai_core, document, business, api_hub             | modules/finance/main.py, contracts/finance.md                | testes de recorrencia e limites      | critica |
| VLY-20260726-08 | stock           | marketplace, ai_core, delivery, document         | modules/stock/main.py, contracts/stock.md                    | testes de compatibilidade            | alta    |
| VLY-20260726-09 | ai_core         | todos os modulos                                 | modules/ai_core/main.py, contracts/ai_core.md                | testes local-vs-cloud fallback       | alta    |
| VLY-20260726-10 | bi              | marketplace, delivery, services, mobility, stock | modules/bi/main.py, contracts/bi.md                          | testes de agregacao anonima          | media   |
| VLY-20260726-11 | delivery        | riders, tms, wms, marketplace, finance           | modules/delivery/main.py, contracts/delivery.md              | testes de janela viva e QR           | alta    |
| VLY-20260726-12 | services        | ai_core, marketplace, document, finance          | modules/services/main.py, contracts/services.md              | testes de escopo comparavel          | alta    |
| VLY-20260726-13 | riders          | delivery, identity, permissions, crm             | modules/riders/main.py, contracts/riders.md                  | testes de acessibilidade de entrega  | media   |
| VLY-20260726-14 | mobility        | ai_core, bi, health, services                    | modules/mobility/main.py, contracts/mobility.md              | testes de preferencia de rota        | media   |
| VLY-20260726-15 | tms             | delivery, wms, marketplace, bi                   | modules/tms/main.py, contracts/tms.md                        | testes de opcao logistica            | media   |
| VLY-20260726-16 | wms             | stock, marketplace, identity, business           | modules/wms/main.py, contracts/wms.md                        | testes de retirada sem fila          | alta    |
| VLY-20260726-17 | crm             | document, permissions, ai_core, business         | modules/crm/main.py, contracts/crm.md                        | testes de portabilidade de historico | alta    |
| VLY-20260726-18 | erp             | marketplace, services, delivery, finance, bpm    | modules/erp/main.py, contracts/erp.md                        | testes de evento de vida             | media   |
| VLY-20260726-19 | bpm             | modulos por jornada                              | modules/bpm/main.py, contracts/bpm.md                        | testes de processo com autorizacao   | alta    |
| VLY-20260726-20 | document        | marketplace, legal, finance, permissions         | modules/document/main.py, contracts/document.md              | testes de validade e alertas         | alta    |
| VLY-20260726-21 | health          | identity, permissions, document, health_connect  | modules/health/main.py, contracts/health.md                  | testes de cartao offline controlado  | alta    |
| VLY-20260726-22 | hr              | jobs, finance, business, marketplace             | modules/hr/main.py, contracts/hr.md                          | testes de beneficios portateis       | media   |
| VLY-20260726-23 | legal           | document, ai_core, bpm, permissions              | modules/legal/main.py, contracts/legal.md                    | testes de contrato em camadas        | alta    |
| VLY-20260726-24 | property        | mobility, bi, services, finance, document        | modules/property/main.py, contracts/property.md              | testes de radar de vida              | media   |

## Flags recomendadas

- feature.primicia.identity_escudo_antigolpe
- feature.primicia.permissions_prazo_finalidade
- feature.primicia.finance_piloto_contas
- feature.primicia.ai_core_helena_no_aparelho
- feature.primicia.marketplace_carrinho_cooperativo
- feature.primicia.delivery_janela_viva

## Riscos transversais

1. Consentimento e retencao de dados em desacordo com finalidade.
2. Regressao de autenticacao e autorizacao entre modulos.
3. Acoplamento alto em API Hub sem versionamento de contrato.
4. Falta de cobertura de testes de expiracao temporal.

## Criterio de pronto para cada ideia

- Flag criada e documentada.
- Endpoints e contratos atualizados.
- Migration versionada quando houver mudanca de dados.
- Testes de modulo passando.
- Evidencia funcional registrada no relatorio da onda.

## Historico

- v1.0 (2026-07-26 14:32:04 -03): mapeamento inicial dos alvos tecnicos para as 24 ideias aprovadas.
