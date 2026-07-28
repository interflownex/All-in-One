# Pendências do Desenvolvedor

**Versão:** 3.2
**Data e hora da atualização:** 28/07/2026 14:51:13
**Fuso horário:** `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`
**Branch de execução:** `codex/auditoria-valley-rider-2026-07-28`
**Pull Request central desta atividade:** `#62`
**Issue operacional:** `#49`
**Issue de orquestração funcional:** `#51`
**Versão anterior consolidada:** 3.1
**Classificação:** `Pendências > Técnico > Equipe técnica`
**Públicos impactados:** Pessoa Física, Pessoa Jurídica, equipe técnica, gestão e investidores

## 1. Situação executiva

A Fase 0 de estabilização foi implementada. No head funcional `73f04292e44c9ee6a887e76148300bba72734f50`, todos os gates obrigatórios ficaram verdes no mesmo commit:

- Continuous Integration;
- Security;
- Database;
- Docker Compose Health Gate;
- OpenAPI;
- Valley DAST;
- Valley Android Security.

Os workflows temporários de diagnóstico e remediação foram removidos após a comprovação. O Pull Request `#50` permanece em rascunho e sem merge. O head de limpeza e documentação deverá repetir todos os gates obrigatórios antes de ser marcado como pronto para revisão.

## 2. Regras permanentes

1. Nenhuma alteração direta na `main`.
2. Nenhum merge com gate obrigatório vermelho, cancelado, ausente ou em processamento.
3. Integração somente por **Squash and Merge**.
4. Nenhuma credencial, token, senha, chave ou certificado no Git.
5. O módulo Vision permanece excluído.
6. Nenhuma exclusão em massa sem inventário, SHA e justificativa.
7. Nenhuma tarefa é concluída apenas pela existência de código ou documento.
8. São obrigatórios teste reproduzível, evidência do ambiente correto, commit e Pull Request.
9. O arquivo `tarefas.md` deve ser atualizado em toda entrega técnica.
10. Marketplace somente começa depois da integração segura da Fase 0.

## 3. Entregas técnicas concluídas

### 3.1 CI e artefatos

- gate de artefatos gerados aprovado;
- baseline oficial preservada em 24 módulos ativos;
- arquivos de status de Valley Business e Valley Rider adicionados;
- contratos Android alinhados a `productionDebug`;
- auditoria e assinatura do APK aprovadas;
- suíte unitária completa aprovada;
- checkout raso de Pull Request tratado sem contar o merge sintético como divergência;
- testes de regressão adicionados para o contrato Android e sincronização Git.

### 3.2 Segurança

- `pip-audit -r requirements-dev.txt` aprovado;
- comando legado `pip-audit --local` removido dos contratos executáveis;
- Bandit aprovado com exceções delimitadas por arquivo e regra;
- auditorias JavaScript aprovadas;
- Trivy aprovado nas imagens API Hub, Identity e Jobs;
- chamadas externas endurecidas com HTTPS, porta padrão e allowlist;
- CodeQL Android aprovado após recompilação limpa e rastreada;
- SARIF gerado e publicado como evidência do Pull Request;
- nenhuma supressão genérica adicionada.

### 3.3 Android

- cliente Firebase alinhado ao package ID `com.example.valley`;
- testes `productionDebug` aprovados;
- lint `productionDebug` aprovado;
- montagem do APK `productionDebug` aprovada;
- chave de depuração bloqueada em release;
- manifesto seguro confirmado;
- CodeQL Java/Kotlin aprovado;
- produção release continua condicionada a secrets legítimos.

### 3.4 PostgreSQL e auditoria

- migrations aplicadas em banco limpo;
- triggers imutáveis confirmados;
- contrato por DSN aprovado sem reaplicar DDL de execução única;
- todos os stores prioritários aprovados;
- matriz de stores aprovada;
- Jobs e cofre CTPS aprovados;
- outbox PostgreSQL e RabbitMQ aprovados;
- IP de auditoria normalizado para o tipo PostgreSQL `inet`;
- hosts simbólicos são gravados como `NULL`, sem contaminar a trilha de auditoria.

### 3.5 Limpeza concluída

Foram removidos individualmente, após inspeção:

- `v29-targeted-diagnostics.yml`;
- `v29-database-diagnostic.yml`;
- `v29-isolate-generated-gate.yml`;
- `v29-apply-validator-fix.yml`;
- `v29-codeql-android-diagnostic.yml`;
- três workflows arquivados do ciclo v2.8.

Os gates permanentes foram preservados.

## 4. Pendência crítica restante

### Valley Rider — gates locais corrigidos

A auditoria do commit integrado `3834bec6383edd6da08e9fdcf3d74a0de1589df2` confirmou os cinco testes do contrato Stitch, mas reproduziu 8 erros e 1 aviso no lint e, após o lint, um erro TypeScript no build. A branch v3.1 corrige:

- efeitos React que atualizavam estado sincronicamente;
- leitura de `gpsWatch.current` durante renderização;
- ausência de estado renderizável explícito para o GPS;
- expressões sem efeito e bloco `catch` vazio;
- tipagem SHA-256 incompatível com `Uint8Array`;
- dependência do efeito de sincronização automática de rota.

Após a correção, lint, build, testes Stitch e testes de marca passaram. O navegador integrado `iab` não estava disponível, mas a prova visual foi posteriormente concluída pelo fallback Playwright descrito abaixo.

### Valley Rider — QA e CI do PR #62

A prova renderizada foi concluída por Playwright com o Chromium já disponível no ambiente:

- HTTP 200 e título `Valley Rider`;
- logomarca canônica `/assets/brand/valley-logo-official.png`;
- ausência de overlay de framework;
- interação `Criar conta` para `Novo cadastro`;
- seis campos obrigatórios renderizados;
- capturas desktop 1440 × 1000 e mobile 390 × 844 sem corte ou sobreposição.

O evento `pull_request` aprovou CI, Compose Health e Security no commit `5cf3a1a`. O evento `push` encontrou dois testes do gate Git dependentes das referências ambientais do checkout. A correção substitui essas execuções ambientais por testes unitários determinísticos das funções `comparison` e `current_branch`. A suíte local equivalente ao CI aprovou `907 passed, 79 skipped`.

### Regressão final do head limpo

O último head funcional comprovado foi `73f04292e44c9ee6a887e76148300bba72734f50`. Como a limpeza e esta documentação criam novo commit, é obrigatório confirmar novamente, no head final:

- CI;
- Security;
- Database;
- Compose Health;
- OpenAPI;
- Valley DAST;
- Valley Android Security.

Nenhum arquivo deverá ser alterado depois dessa regressão antes da decisão de revisão.

## 5. Pendências altas posteriores à Fase 0

1. Desabilitar administrativamente `merge commit` e `rebase merge`, mantendo somente squash.
2. Revisar o escopo amplo do PR `#50` e seus 261 arquivos alterados antes da integração.
3. Verificar e resolver threads de revisão pendentes.
4. Regularizar PRs antigos ainda abertos ou substituídos.
5. Homologar APK Admin com instalação, hash e smoke test.
6. Homologar PDV Desktop com instalador, hashes e operação offline.
7. Rebasear o executor Telegram sobre a base integrada.
8. Homologar domínio público, Identity, API Hub e `/health`.
9. Sincronizar Stitch com credencial legítima.
10. Incorporar o PNG original autorizado da Valley Riders.

## 6. Próxima sequência funcional

Após a integração segura da Fase 0:

1. Marketplace;
2. Stock;
3. Delivery.

Cada frente deverá começar com feature flag desligada e incluir contrato, banco, autorização, auditoria, testes, telemetria, alertas e rollback.

## 7. Quadro de acompanhamento

| Atividade | Estado | Dificuldade | Conclusão | Evidência restante |
|---|---|---:|---:|---|
| CI e artefatos | Implementado | 5 | 100% | repetir no head final |
| Segurança Python/JS/containers | Implementado | 5 | 100% | repetir no head final |
| Android e CodeQL | Implementado | 5 | 100% | repetir no head final |
| PostgreSQL, Jobs/CTPS e outbox | Implementado | 5 | 100% | repetir no head final |
| Limpeza de workflows temporários | Concluída | 3 | 100% | confirmar ausência no diff final |
| Governança exclusiva por squash | Bloqueio administrativo | 4 | 60% | configuração do repositório |
| Revisão do PR #50 | Pendente | 5 | 20% | threads e aprovação |
| Marketplace | Bloqueado | 5 | 0% | merge seguro da Fase 0 |

## 8. Critérios para marcar o PR como pronto

- todos os sete gates obrigatórios verdes no head final;
- nenhum workflow temporário remanescente;
- nenhuma thread de revisão pendente sem resposta;
- escopo do PR revisado;
- ausência de segredos;
- Vision ausente;
- documentos v3.0 e `tarefas.md` v1.7 presentes;
- método de integração definido como squash.

## 9. Histórico

| Versão | Data e hora | Alteração principal |
|---|---|---|
| 2.8 | 27/07/2026 02:17:29 | Estabilização parcial e evidências iniciais. |
| 2.9 | 27/07/2026 05:33:26 | Correções dos quatro bloqueadores e revalidação. |
| 3.0 | 27/07/2026 07:12:49 | Fase 0 implementada, gates verdes no head funcional, diagnósticos removidos e regressão final exigida. |
| 3.1 | 28/07/2026 08:39:01 | Auditoria do Valley Rider, correção de lint/build e registro do bloqueio da prova renderizada. |
| 3.2 | 28/07/2026 14:51:13 | PR #62 aberto, QA renderizada concluída e regressão do checkout raso corrigida. |
