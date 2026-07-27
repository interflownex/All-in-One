# Tarefas da IA Desenvolvedora

**Versão:** 1.7  
**Data e hora:** 27/07/2026 07:12:49  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `fix/cicd-governanca-v2-8-2026-07-27`  
**Pull Request:** `#50`  
**Issues:** `#49` e `#51`  
**Destino:** Codex e demais IAs desenvolvedoras autorizadas

## 1. Objetivo imediato

Concluir a regressão final do head de limpeza/documentação. A Fase 0 já foi implementada e todos os gates obrigatórios passaram no head funcional `73f04292e44c9ee6a887e76148300bba72734f50`.

Não iniciar Marketplace e não alterar arquivos depois que o head final estiver verde.

## 2. Estado implementado

- artefatos gerados aprovados;
- baseline de 24 módulos preservada;
- suíte unitária completa aprovada;
- checkout raso de Pull Request corrigido;
- contrato Android v2.9 aprovado;
- assinatura e auditoria APK aprovadas;
- `pip-audit`, Bandit, JavaScript e Trivy aprovados;
- Android aprovado em testes, lint e assemble;
- CodeQL aprovado com recompilação limpa;
- SARIF publicado como artefato;
- migrations, triggers e contrato DSN aprovados;
- stores e matriz aprovados;
- Jobs/CTPS aprovado;
- outbox/RabbitMQ aprovado;
- OpenAPI, Compose e DAST aprovados;
- oito workflows temporários/arquivados removidos.

## 3. Primeira ação obrigatória

1. Obter novamente o head do PR `#50`.
2. Consultar somente workflows ligados exatamente a esse head.
3. Confirmar os sete gates obrigatórios.
4. Desconsiderar resultados de commits anteriores como evidência final.
5. Não criar novo commit quando o head final estiver verde.

## 4. Gates obrigatórios

- Continuous Integration;
- Security;
- Database;
- Docker Compose Health Gate;
- OpenAPI;
- Valley DAST;
- Valley Android Security.

## 5. Ações após regressão verde

1. Listar reviews e threads do PR.
2. Responder e resolver somente threads efetivamente atendidas.
3. Revisar o escopo por domínio.
4. Confirmar ausência dos workflows temporários removidos.
5. Confirmar ausência de segredos e do módulo Vision.
6. Atualizar issues `#49` e `#51` por comentário, sem alterar arquivos.
7. Atualizar a descrição do PR por metadados, sem alterar o head.
8. Marcar o PR pronto somente se não houver bloqueio de revisão.
9. Integrar apenas por Squash and Merge, com `expected_head_sha`, quando autorizado.

## 6. Proibições

- push direto na `main`;
- merge com gate vermelho, cancelado, ausente ou em processamento;
- merge sem confirmar o head esperado;
- reativar Vision;
- iniciar Marketplace antes da integração da Fase 0;
- versionar secrets;
- aplicar supressão genérica de scanner;
- recriar workflows temporários sem causa comprovada;
- sobrescrever trabalho paralelo;
- alterar arquivos depois da regressão final verde.

## 7. Fontes de verdade

1. `AGENTS.md`;
2. `docs/governance/MANDATORY_INTEGRATION_POLICY.md`;
3. este `tarefas.md`, versão 1.7;
4. `docs/Pendências Do desenvolvedor.md`, versão 3.0;
5. `docs/relatorios/pendencias/RELATORIO_VARREDURA_STATUS_v3.0_2026-07-27.md`;
6. `docs/relatorios/pendencias/PLANO_ACAO_CODEX_v3.0_2026-07-27.md`;
7. issues `#49` e `#51`;
8. PR `#50`;
9. workflows associados ao head final.

## 8. Próxima fase

Depois da integração segura:

1. Marketplace;
2. Stock;
3. Delivery.

Cada frente deve iniciar com feature flag desligada e possuir contrato, migration reversível, autorização, auditoria, testes, telemetria, alertas e rollback.

## 9. Histórico

| Versão | Data e hora | Alteração |
|---|---|---|
| 1.5 | 27/07/2026 04:29:44 | Plano inicial v2.9. |
| 1.6 | 27/07/2026 05:33:26 | Correções aplicadas e revalidação. |
| 1.7 | 27/07/2026 07:12:49 | Fase 0 implementada, diagnósticos removidos e regressão final preparada. |
