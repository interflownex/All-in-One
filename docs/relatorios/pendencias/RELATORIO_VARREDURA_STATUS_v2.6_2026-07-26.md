# Relatório de Varredura e Status

**Versão:** 2.6  
**Data:** 26/07/2026  
**Repositório:** `interflownex/All-in-One`  
**Branch verificada:** `copilot/diretrizes-implantacao-primicias-selecionadas`  
**Commit de referência:** `8af9b72f7fceb6f149198501f964af1e553ea4e9`  
**Issue de orquestração:** `#28` (legada) / `#TBD` (primícias v2.6)

## 1. Auditoria executada

Comandos executados:

- `git status --short --branch`
- `git remote -v`
- `git log --oneline --decorate -20`
- `git diff --stat`
- `git diff --name-status`

Resumo objetivo:

- branch ativa fora da `main` e com upstream configurado;
- sem diff local no início da varredura;
- repositório com base funcional (módulos, migrations, outbox e auditoria), porém sem artefatos explícitos das primícias selecionadas;
- recurso 6 permanece **excluído por diretriz executiva** e STOCK preservado.

## 2. Matriz de estado real por recurso

| Nº | Módulo | Recurso | Estado | Parte existente | Lacunas | Dependências | Risco |
|---:|---|---|---|---|---|---|---|
| 1 | Identity | Cofre de Provas Mínimas | estrutura-base existente | módulo identity + consentimentos | entidades/APIs/eventos de prova mínima ausentes | identity, permissions, document, outbox | alto |
| 2 | Business | Consórcio Relâmpago Empresarial | estrutura-base existente | empresas/memberships/aprovação | consórcio temporário, split e encerramento auditável ausentes | business, legal, finance, bpm | alto |
| 3 | Permissions | Procuração Operacional Expirável | estrutura-base existente | RBAC/ABAC/lógicas de autorização | delegação com janela, valor, local, finalidade e revogação dedicada ausente | permissions, finance, audit | alto |
| 4 | Finance | Dinheiro com Destino | estrutura-base existente | ledger/split/escrow/faturamento | alocação por finalidade com simulação e reversão compensatória ausente | finance, erp, audit/outbox | alto |
| 5 | Marketplace | Compra em Coalizão Local | estrutura-base existente | catálogo, pedidos, disputas | coalizão, thresholds, bids e pedido coletivo ausentes | marketplace, finance, delivery | alto |
| 6 | STOCK | Demanda Antes da Vitrine | bloqueado por dependência externa | STOCK ativo no catálogo e em operação | implementação proibida | governança de escopo | baixo |
| 7 | Delivery | Entrega de Trajeto Aproveitado | estrutura-base existente | delivery/riders operacionais | capacidade ociosa por trajeto + matching seguro ausentes | delivery, riders, identity | alto |
| 8 | Riders | Passaporte de Evidências Operacionais | estrutura-base existente | módulo riders ativo | credenciais de evidência, disputa e revogação ausentes | riders, identity, legal | alto |
| 9 | Services | Contrato por Resultado Componível | estrutura-base existente | serviços e contratos base | milestones com aceite/disputa e pagamento por marco ausentes | services, finance, legal | alto |
| 10 | Mobility | Rota de Intenções Premium | estrutura-base existente | mobility com rota base | cotação/otimização/confirmação/faturamento premium + entitlement ausentes | mobility, billing, finance, api_hub | crítico |
| 11 | Jobs | Janela de Trabalho Reversa | estrutura-base existente | jobs/recrutamento já ativos | disponibilidade reversa com privacidade e anti-discriminação ausente | jobs, identity, permissions | alto |
| 12 | ERP | Fechamento Contínuo por Exceção | estrutura-base existente | ERP + billing base | score de completude, exceções e snapshot auditável ausentes | erp, finance, approvals | alto |
| 13 | WMS | Mapa de Certeza do Estoque | estrutura-base existente | WMS e inventário base | score de confiança e contagem dirigida ausentes | wms, stock, erp | alto |
| 14 | TMS | Bolsa Cega de Capacidade Logística | estrutura-base existente | TMS e fluxos logísticos base | anonimização/mutual accept/disclosure progressivo ausentes | tms, legal, permissions | alto |
| 15 | CRM | Livro de Promessas ao Cliente | estrutura-base existente | CRM operacional | promessas, owner, prazo, confirmação cliente e quebra rastreável ausentes | crm, ai_core, audit | alto |
| 16 | BPM | Laboratório de Processo Enxuto | estrutura-base existente | BPM e workflow base | simulação isolada reproduzível com ativação por flag ausente | bpm, feature flags, metrics | alto |
| 17 | Document | Documento Vivo de Obrigações | estrutura-base existente | gestão documental e versão base | âncora de cláusula em obrigação rastreável ausente | document, legal, notifications | alto |
| 18 | HR | Escala de Afinidade Justa | bloqueado por dependência externa | módulo hr ativo | requisito detalhado truncado no enunciado | hr, legal, compliance | médio |
| 19 | Health | Cápsula de Continuidade | bloqueado por dependência externa | módulo health ativo | requisito detalhado truncado no enunciado | health, legal, document | médio |
| 20 | Legal | Radar de Impacto | bloqueado por dependência externa | módulo legal ativo | requisito detalhado truncado no enunciado | legal, bpm, audit | médio |
| 21 | Property | Capacidade Compartilhada | bloqueado por dependência externa | módulo property ativo | requisito detalhado truncado no enunciado | property, tms, legal | médio |
| 22 | BI | Perguntas Não Feitas | bloqueado por dependência externa | módulo bi ativo | requisito detalhado truncado no enunciado | bi, ai_core, pipelines | médio |
| 23 | AI Core | Recibo de Memória | bloqueado por dependência externa | módulo ai_core ativo | requisito detalhado truncado no enunciado | ai_core, consent, audit | médio |
| 24 | API Hub | Contrato Adaptativo | bloqueado por dependência externa | api_hub e openapi base | requisito detalhado truncado no enunciado | api_hub, security, versioning | médio |

## 3. Quadro de execução (obrigatório)

| Nome da atividade | Descricao | Passo sendo executado | Dificuldade [1 a 5] | % concluido | Tempo previsto | Etapas [Total] | Concluidas [X] | Pendentes [Y] |
|---|---|---|---:|---:|---|---:|---:|---:|
| Fundação transversal | Feature flags, entitlement, auditoria/eventos, segurança | Planejamento técnico consolidado com matriz publicada | 5 | 40% | 8h | 10 | 4 | 6 |
| Primícias 1–5 | Identity, Business, Permissions, Finance, Marketplace | Decomposição em backlog implementável e reversível | 5 | 20% | 8h | 15 | 3 | 12 |
| Primícias 7–17 | Delivery até Document | Decomposição por módulo e contratos de API/evento | 5 | 15% | 8h | 22 | 3 | 19 |
| Primícias 18–24 | HR até API Hub | Bloqueado por truncamento do enunciado | 4 | 0% | 8h | 14 | 0 | 14 |
| Governança de escopo | Exclusão do recurso 6 e preservação do STOCK | Validado e registrado nos artefatos v2.6 | 3 | 100% | 30min | 3 | 3 | 0 |

## 4. Bloqueios objetivos

1. Enunciado truncado a partir do recurso 18, impedindo especificação funcional final dos recursos 18–24.
2. `preflight --integrate` do guardião multiagente falhou por falta de remoto acessível no momento da execução.

## 5. Próximo passo obrigatório

Prosseguir com implantação incremental pelos recursos 1–17 (fundação transversal primeiro) e só abrir implementação dos recursos 18–24 após receber o complemento oficial do enunciado.
