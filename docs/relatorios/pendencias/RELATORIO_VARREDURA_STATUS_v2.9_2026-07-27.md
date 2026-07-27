# Relatório de Varredura e Status

**Versão:** 2.9  
**Data e hora:** 27/07/2026 04:29:44  
**Última execução registrada:** 27/07/2026 04:49:00  
**Fuso:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `fix/cicd-governanca-v2-8-2026-07-27`  
**PR central:** `#50`  
**Issues:** `#49` e `#51`

## Resumo executivo

O ciclo v2.8 reduziu os bloqueadores de cinco frentes amplas para quatro gates específicos. OpenAPI, Valley DAST, Docker Compose, auditoria de dependências, Trivy e auditorias JavaScript passaram. O PR #50 continua em rascunho porque CI, Bandit, Android completo e PostgreSQL por DSN ainda falham.

O diagnóstico isolado v2.9 foi executado e transformou a falha genérica do CI em causas objetivas. Os dois arquivos `STATUS.md` ausentes nos aplicativos operacionais foram criados. A correção do validador foi preparada para alinhar a baseline de 24 módulos, o comando atual do `pip-audit` e a separação entre Valley e Valley Riders.

## Estado dos workflows no head verificado

| Workflow | Estado |
|---|---|
| Continuous Integration | Falha em `Check generated artifacts` |
| Security | Falha em Bandit e Android |
| Database | Falha em `Validate PostgreSQL real contract by DSN` |
| Docker Compose Health Gate | Aprovado |
| OpenAPI | Aprovado |
| Valley DAST | Aprovado |

## Resultado do diagnóstico isolado

| Comando | Código inicial | Achado |
|---|---:|---|
| `scaffold_modules.py --check` | 1 | ausentes `apps/valley_business/STATUS.md` e `apps/valley_rider/STATUS.md` |
| `generate_domain_event_fixtures.py --check` | 0 | aprovado |
| `validate_openapi.py` | 0 | aprovado |
| `validate_repository.py` | 1 | quatro regras desatualizadas ou incompletas |

### Regras identificadas no validador

1. ainda exigia 25 módulos, mas o catálogo oficial possui 24;
2. ainda exigia a string `pip-audit --local`, embora o workflow audite `requirements-dev.txt`;
3. tratava `light_logo_asset` como obrigatório mesmo quando o campo não existe;
4. misturava `valley-rider` na lista de aplicativos Valley, embora o manifesto o classifique em `riders_apps`.

## Correções executadas

- criado `apps/valley_business/STATUS.md`;
- criado `apps/valley_rider/STATUS.md`;
- preparada correção exata e idempotente de `scripts/validate_repository.py`;
- diagnóstico configurado para repetir os quatro comandos após a remediação;
- evidência publicada como artefato do workflow v2.9.

## Principais achados gerais

1. A suíte principal não chega aos testes unitários porque o gate composto de artefatos falha.
2. `pip-audit` e Trivy já passaram; a falha Python de segurança restante é Bandit.
3. O contrato Android passou, mas a etapa completa de testes, lint, build e análise falha.
4. Migrations e triggers passaram; a falha de banco está no validador de contrato real por DSN.
5. O repositório ainda permite três métodos de merge.
6. A issue #51 mantém Marketplace → Stock → Delivery bloqueados até a estabilização.

## Tabela de acompanhamento

| Nome da atividade | Descrição | Passo sendo executado | Dificuldade [1 a 5] | % concluído | Tempo previsto | Etapas [Total] | Concluídas [X] | Pendentes [Y] |
|---|---|---|---:|---:|---|---:|---:|---:|
| CI principal | Liberar suíte unitária | Aplicar correções do validador | 5 | 82% | 45min | 6 | 5 | 1 |
| Scaffold | Sincronizar artefatos customizados | Status operacionais criados | 4 | 100% | concluído | 4 | 4 | 0 |
| Bandit | Corrigir código inseguro real | Classificar achados médios/altos | 5 | 35% | 2h | 6 | 2 | 4 |
| Android | Validar pipeline completo | Isolar subetapa | 5 | 70% | 1h30 | 6 | 4 | 2 |
| Banco | Validar contrato real e stores | Capturar erro por DSN | 5 | 75% | 1h30 | 8 | 6 | 2 |
| Compose | Health dos serviços | Aprovado | 4 | 100% | concluído | 5 | 5 | 0 |
| OpenAPI | Contratos HTTP | Aprovado | 3 | 100% | concluído | 4 | 4 | 0 |
| DAST | Segurança dinâmica web | Aprovado | 4 | 100% | concluído | 4 | 4 | 0 |

## Decisão

- manter PR #50 em rascunho;
- concluir a remediação do validador e repetir o gate;
- não iniciar Marketplace ainda;
- não mesclar enquanto houver gate obrigatório vermelho.
