# Relatório de Varredura e Status — v3.3

**Data:** 28/07/2026  
**Fuso:** `America/Sao_Paulo`  
**Branch:** `codex/apk-valley-rodada-005-2026-07-28`  
**Commit-base:** `36ca098461d51db4c6165172fbda6244f3d3c194`  
**Issue:** `#63`

| Nome da atividade | Descrição | Passo sendo executado | Dificuldade [1 a 5] | % concluído | Tempo previsto | Etapas [Total] | Concluídas [X] | Pendentes [Y] |
|---|---|---|---:|---:|---|---:|---:|---:|
| Catálogo da Rodada 005 | Registrar 24 ideias e códigos | Implementado | 3 | 100% | concluído | 4 | 4 | 0 |
| Contratos executáveis | Criar regra específica para cada ideia | Implementado em vertical sandbox | 5 | 100% | concluído | 24 | 24 | 0 |
| Feature flags | Bloquear ativação prematura | Implementado, todas desligadas | 4 | 100% | concluído | 4 | 4 | 0 |
| Testes locais | Validar catálogo, regras e regressão | 12 testes aprovados | 4 | 100% | concluído | 12 | 12 | 0 |
| Persistência produtiva | PostgreSQL, migrações e outbox | Não iniciada | 5 | 0% | posterior | 6 | 0 | 6 |
| Integrações externas | PSP, passkeys, transporte e Health | Bloqueada por homologação | 5 | 0% | externo | 8 | 0 | 8 |
| Interfaces móveis | Integrar contratos ao APK | Pendente | 5 | 0% | posterior | 5 | 0 | 5 |
| Gates remotos | Executar no SHA da branch | Aguardando PR | 4 | 20% | após publicação | 5 | 1 | 4 |

## Resultado

A Rodada 005 está implementada como vertical executável e testável. Não está homologada para produção. As feature flags permanecem desligadas e a execução de prova exige sandbox explícito.

## Riscos

- estados ainda são mantidos em memória;
- não há autenticação real no contrato isolado;
- integrações externas não foram simuladas como concluídas;
- regras financeiras, clínicas e jurídicas exigem revisão especializada;
- nenhuma comunicação comercial pode alegar prontidão produtiva.
