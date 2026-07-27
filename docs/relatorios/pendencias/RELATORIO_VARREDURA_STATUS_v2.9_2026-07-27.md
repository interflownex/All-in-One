# Relatório de Varredura e Status

**Versão:** 2.9  
**Data e hora:** 27/07/2026 04:29:44  
**Fuso:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `fix/cicd-governanca-v2-8-2026-07-27`  
**Commit verificado:** `fb49ba0c334054817fbbb129dfbf38f2cf741761`  
**PR central:** `#50`  
**Issues:** `#49` e `#51`

## Resumo executivo

O ciclo v2.8 reduziu os bloqueadores de cinco frentes amplas para quatro gates específicos. OpenAPI, Valley DAST, Docker Compose, auditoria de dependências, Trivy e auditorias JavaScript passaram. O PR #50 continua em rascunho porque CI, Bandit, Android completo e PostgreSQL por DSN ainda falham.

## Estado dos workflows no head verificado

| Workflow | Estado |
|---|---|
| Continuous Integration | Falha em `Check generated artifacts` |
| Security | Falha em Bandit e Android |
| Database | Falha em `Validate PostgreSQL real contract by DSN` |
| Docker Compose Health Gate | Aprovado |
| OpenAPI | Aprovado |
| Valley DAST | Aprovado |

## Principais achados

1. A suíte principal não chega aos testes unitários porque o gate composto de artefatos falha.
2. `pip-audit` e Trivy já passaram; a falha Python de segurança restante é Bandit.
3. O contrato Android passou, mas a etapa completa de testes, lint, build e análise falha.
4. Migrations e triggers passaram; a falha de banco está no validador de contrato real por DSN.
5. O repositório ainda permite três métodos de merge.
6. A issue #51 mantém Marketplace → Stock → Delivery bloqueados até a estabilização.

## Tabela de acompanhamento

| Nome da atividade | Descrição | Passo sendo executado | Dificuldade [1 a 5] | % concluído | Tempo previsto | Etapas [Total] | Concluídas [X] | Pendentes [Y] |
|---|---|---|---:|---:|---|---:|---:|---:|
| CI principal | Liberar suíte unitária | Isolar comando falho | 5 | 70% | 1h | 6 | 4 | 2 |
| Bandit | Corrigir código inseguro real | Classificar achados médios/altos | 5 | 35% | 2h | 6 | 2 | 4 |
| Android | Validar pipeline completo | Isolar subetapa | 5 | 70% | 1h30 | 6 | 4 | 2 |
| Banco | Validar contrato real e stores | Capturar erro por DSN | 5 | 75% | 1h30 | 8 | 6 | 2 |
| Compose | Health dos serviços | Aprovado | 4 | 100% | concluído | 5 | 5 | 0 |
| OpenAPI | Contratos HTTP | Aprovado | 3 | 100% | concluído | 4 | 4 | 0 |
| DAST | Segurança dinâmica web | Aprovado | 4 | 100% | concluído | 4 | 4 | 0 |

## Decisão

- manter PR #50 em rascunho;
- executar diagnóstico isolado na própria branch;
- não iniciar Marketplace ainda;
- não mesclar enquanto os quatro bloqueadores persistirem.
