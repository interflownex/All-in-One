# Relatório de Varredura e Status

**Versão:** 3.0  
**Data e hora:** 27/07/2026 07:12:49  
**Fuso:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `fix/cicd-governanca-v2-8-2026-07-27`  
**PR central:** `#50`  
**Issues:** `#49` e `#51`  
**Classificação:** `Pendências > Técnico > Equipe técnica`

## 1. Resumo executivo

A Fase 0 foi implementada e comprovada no head funcional `73f04292e44c9ee6a887e76148300bba72734f50`. No mesmo commit, todos os gates obrigatórios passaram:

| Gate | Resultado |
|---|---|
| Continuous Integration | aprovado |
| Security | aprovado |
| Database | aprovado |
| Docker Compose Health Gate | aprovado |
| OpenAPI | aprovado |
| Valley DAST | aprovado |
| Valley Android Security | aprovado |

O PR continua em rascunho e sem merge. Após a prova verde, oito workflows temporários ou arquivados foram removidos individualmente. A última etapa da Fase 0 é repetir os sete gates no head final de limpeza/documentação.

## 2. Problemas corrigidos

### CI

- artefatos e catálogos divergentes;
- contratos Android legados;
- testes de assinatura e auditoria do APK;
- checkout raso de Pull Request;
- merge sintético contado incorretamente como `ahead`;
- contratos duplicados de `pip-audit`;
- teste da coluna reservada `"authorization"`.

### Segurança

- URLs externas sem validação central;
- achados Bandit não classificados;
- exceções B608 e B314 sem verificador próprio;
- tarefas Android ambíguas;
- CodeQL sem código-fonte visível por reaproveitamento de cache Gradle;
- upload SARIF incompatível com a análise local do Pull Request.

### Banco

- reaplicação inválida de migrations de execução única;
- teste Jobs/CTPS bloqueado por host simbólico em coluna `inet`;
- validação de stores interrompida antes do outbox;
- normalização de IPv4/IPv6 ausente na auditoria compartilhada.

## 3. Evidências técnicas

- suíte unitária completa aprovada;
- `pip-audit` aprovado nas dependências declaradas;
- Bandit aprovado com regras restantes ativas;
- auditorias JavaScript aprovadas;
- Trivy aprovado nas três imagens obrigatórias;
- Android aprovado em teste, lint e assemble;
- CodeQL aprovado após `clean`, `--no-build-cache` e `--rerun-tasks`;
- SARIF publicado como artefato;
- migrations, triggers, contrato DSN, 24 stores, matriz, Jobs/CTPS e outbox aprovados;
- OpenAPI, DAST e Compose Health aprovados.

## 4. Limpeza verificada

Foram removidos:

- cinco workflows temporários v2.9;
- três avisos arquivados v2.8.

Dois workflows removidos possuíam permissão de escrita e não devem permanecer após a estabilização. Os workflows permanentes de CI, Security, Database, Compose, OpenAPI, DAST e Android foram preservados.

## 5. Estado da governança

| Item | Estado |
|---|---|
| PR #50 | aberto e em rascunho |
| Merge | não executado |
| Push direto na main | não executado |
| Vision | excluído |
| Secrets | não versionados |
| Squash and Merge | exigido pela política do projeto |
| Exclusividade administrativa do squash | ainda não comprovada |
| Revisão humana/técnica | pendente |

## 6. Riscos remanescentes

1. A regressão do head final ainda precisa concluir.
2. O PR possui escopo amplo e exige revisão por arquivos e domínios.
3. A configuração administrativa pode continuar permitindo outros métodos de merge.
4. Funcionalidades externas dependentes de credenciais permanecem fora da alegação de conclusão.
5. Marketplace não pode começar antes da integração segura da Fase 0.

## 7. Decisão

- manter o PR em rascunho durante a regressão final;
- não criar nova funcionalidade;
- não alterar arquivos depois do head final verde;
- revisar threads e escopo;
- marcar pronto somente após todos os checks verdes;
- integrar exclusivamente por Squash and Merge quando autorizado.
