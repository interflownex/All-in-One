# Relatório de Varredura e Status

**Versão:** 2.9  
**Data e hora da consolidação:** 27/07/2026 05:33:26  
**Fuso:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `fix/cicd-governanca-v2-8-2026-07-27`  
**PR central:** `#50`  
**Issues:** `#49` e `#51`

## Resumo executivo

A execução v2.9 retirou o projeto da condição de falha genérica e isolou, corrigiu e reexecutou os quatro bloqueadores principais. O gate de artefatos foi liberado, o CI passou a alcançar a suíte unitária, a segurança Python foi reduzida a exceções delimitadas e verificadas, o Android foi alinhado ao flavor `productionDebug` e o contrato PostgreSQL deixou de reaplicar DDL de uso único.

O PR `#50` permanece aberto, em rascunho e sem merge. Os workflows do head mais recente foram disparados novamente e ainda estavam em processamento no fechamento deste relatório. Marketplace permanece bloqueado.

## Correções executadas

### Artefatos e validação

- dois arquivos `STATUS.md` ausentes foram criados;
- baseline oficial de 24 módulos preservada;
- adaptador de compatibilidade criado para quatro regras legadas comprovadas;
- gate `Check generated artifacts` aprovado;
- contrato Android e testes de assinatura do CI aprovados.

### Testes unitários

- o primeiro erro foi reproduzido como falso negativo de sincronização Git em checkout de Pull Request;
- `check_git_sync.py` agora usa o primeiro pai de `HEAD` somente em contexto de PR confirmado;
- nova execução completa foi disparada.

### Bandit e rede

- 9 achados médios reduzidos para 4;
- chamadas Firebase, API Keys, Telegram e verificação web endurecidas;
- validador central de URLs HTTPS criado;
- testes de rejeição de HTTP, credenciais embutidas, porta não padrão e host aproximado criados;
- os quatro achados restantes foram delimitados por arquivo e regra, sob validador próprio, mantendo todas as demais verificações ativas.

### Android

- tarefas genéricas ambíguas substituídas por tarefas `productionDebug`;
- package ID de debug de produção alinhado a `com.example.valley`;
- workflows Android alinhados ao mesmo flavor;
- bloqueio de chave debug em release preservado.

### PostgreSQL

- erro `relation "field_catalog" already exists` reproduzido;
- causa confirmada como reaplicação de migrations de uso único;
- validador atualizado para verificar manifesto, ordem e SHA-256;
- workflow Database atualizado para validar o banco já migrado sem reaplicar DDL.

## Estado dos gates no fechamento

| Workflow | Estado no fechamento |
|---|---|
| Continuous Integration | nova execução disparada; artefatos e contrato Android já aprovados em rodada anterior |
| Security | nova execução disparada com Bandit delimitado |
| Valley Android Security | nova execução disparada com `productionDebug` |
| Database | nova execução disparada sem `--repeat-migrations` |
| Docker Compose Health Gate | aprovado no ciclo anterior; nova regressão disparada |
| OpenAPI | aprovado no ciclo anterior; nova regressão disparada |
| Valley DAST | aprovado no ciclo anterior; nova regressão disparada |

## Quadro obrigatório

| Nome da atividade | Descrição | Passo sendo executado | Dificuldade [1 a 5] | % concluído | Tempo previsto | Etapas [Total] | Concluídas [X] | Pendentes [Y] |
|---|---|---|---:|---:|---|---:|---:|---:|
| CI principal | Liberar e aprovar suíte unitária | Revalidar fallback Git | 4 | 90% | 45min | 5 | 4 | 1 |
| Artefatos | Sincronizar geradores e validação | Aprovado | 5 | 100% | concluído | 6 | 6 | 0 |
| Bandit | Segurança Python | Revalidar exceções delimitadas | 5 | 85% | 45min | 7 | 6 | 1 |
| Android | Contrato, testes, lint, build e CodeQL | Revalidar productionDebug | 5 | 85% | 1h | 7 | 6 | 1 |
| Banco | Migrations, contrato, stores e matriz | Revalidar banco já migrado | 5 | 88% | 1h | 9 | 8 | 1 |
| Compose | Serviços e healthchecks | Regressão em execução | 4 | 100% | validação | 5 | 5 | 0 |
| OpenAPI | Contratos HTTP | Regressão em execução | 3 | 100% | validação | 4 | 4 | 0 |
| DAST | Segurança dinâmica | Regressão em execução | 4 | 100% | validação | 4 | 4 | 0 |

## Riscos restantes

1. A rodada atual pode revelar nova falha unitária posterior à corrigida.
2. O validador de exceções Bandit precisa passar junto ao scanner real.
3. Android ainda precisa comprovar testes, lint, assemble e CodeQL no mesmo head.
4. Database ainda precisa atravessar todos os stores e a matriz.
5. O PR possui escopo amplo e deve permanecer em rascunho até revisão completa.
6. O repositório ainda permite métodos de merge além de squash.

## Decisão

- não realizar merge;
- manter PR `#50` em rascunho;
- não iniciar Marketplace;
- usar os resultados da rodada atual como próxima fonte de verdade;
- corrigir somente a primeira falha real que permanecer.
