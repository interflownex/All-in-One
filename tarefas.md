# Tarefas da IA Desenvolvedora

**Versão:** 2.1  
**Data e hora:** 28/07/2026  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `codex/apk-valley-rodada-005-2026-07-28`  
**Commit-base:** `36ca098461d51db4c6165172fbda6244f3d3c194`  
**Issue de orquestração:** `#63`  
**Classificação:** `Pendências > Técnico > Equipe técnica`  
**Aplicação:** `modules/valley_consumer`

## 1. Objetivo

Evoluir a Rodada 005 do APK Valley Consumidor, atualmente implementada como vertical executável em sandbox, até pilotos e produção homologada por ondas controladas.

## 2. Estado atual

- os códigos `VLY-20260728-01` a `VLY-20260728-24` estão registrados;
- as 24 ideias possuem regras específicas e endpoint executável;
- as 24 feature flags começam desligadas;
- escritas de teste exigem `X-Innovation-Sandbox: true` enquanto a flag estiver desligada;
- a rota de contrato não permite habilitar produção diretamente;
- a Rodada 004 permanece registrada e não foi substituída;
- o teste local específico aprovou `12 passed`;
- a issue `#63` centraliza a orquestração;
- Vision permanece excluído.

## 3. Escopo implementado

1. catálogo e prioridades da Rodada 005;
2. contratos de API para as 24 ideias;
3. validações específicas de segurança e negócio;
4. registros lógicos em memória para prova de contrato;
5. feature flags e bloqueio de produção;
6. testes unitários e de regressão da presença da Rodada 004;
7. documentação de implementação;
8. relatório de status e plano de ação v3.3.

## 4. Fontes de verdade

1. `AGENTS.md`;
2. este `tarefas.md`;
3. `config/module_catalog.json`;
4. `modules/valley_consumer/innovation_round_004.py`;
5. `modules/valley_consumer/innovation_round_005.py`;
6. `docs/inovacao/APK_Valley_Consumidor_Rodada_005_Implementacao_2026-07-28.md`;
7. `docs/relatorios/pendencias/RELATORIO_VARREDURA_STATUS_v3.3_2026-07-28.md`;
8. `docs/relatorios/pendencias/PLANO_ACAO_CODEX_v3.3_2026-07-28.md`;
9. issue `#63`;
10. pull request da branch desta atividade.

## 5. Pré-requisitos

- atualizar a branch com `main` sem descartar trabalho alheio;
- adquirir lock multiagente antes de editar;
- não versionar credenciais;
- manter todas as flags desligadas até homologação;
- usar PostgreSQL, migrações e outbox antes de piloto real;
- executar revisão jurídica, financeira, clínica e de proteção de dados conforme o módulo.

## 6. Próxima sequência

### P0 — regressão da entrega

1. executar testes das Rodadas 004 e 005;
2. executar `python3 scripts/validate_repository.py`;
3. validar OpenAPI e segurança;
4. revisar o diff e procurar segredos;
5. aguardar gates remotos no mesmo SHA;
6. atualizar a issue `#63` com resultados.

### P0 — fundação produtiva

1. criar tabelas e migrações para flags, registros e estados;
2. aplicar autenticação, RBAC/ABAC e isolamento por entidade;
3. incluir idempotência, auditoria e outbox;
4. adicionar rate limit, telemetria, alertas e rollback;
5. impedir execução sandbox em ambiente produtivo.

### P1 — pilotos prioritários

- Identity: passkeys, quórum e antifraude;
- Finance: ledger e PSP homologado;
- STOCK: catálogo técnico e revisão humana;
- BPM: saída, exportação e retenção;
- Document: sanitização visualmente revisada;
- Health: Health Connect/FHIR e consentimento temporário;
- Legal: finalidades e bases legais revisadas;
- AI Core: persistência e expiração de memória.

### P2 — demais módulos

Implantar cada ideia em piloto separado, sempre com flag, autorização, testes, telemetria e rollback. Não ativar as 24 ideias simultaneamente.

## 7. Testes

```bash
pytest -q tests/test_valley_consumer_innovation_round_004.py
pytest -q tests/test_valley_consumer_innovation_round_005.py
python3 scripts/validate_repository.py
```

Gates remotos esperados:

- Continuous Integration;
- Security;
- Database;
- Docker Compose Health Gate;
- OpenAPI;
- gates Valley aplicáveis.

## 8. Critérios de aceite

- testes reproduzíveis aprovados no SHA final;
- persistência e migrações reversíveis;
- autorização e auditoria reais;
- dependências externas homologadas;
- flags desligadas por padrão;
- nenhuma credencial no Git;
- Vision ausente;
- documentação atualizada;
- PR revisado;
- integração somente por Squash and Merge, sem auto-merge.

## 9. Riscos e bloqueios

- contratos atuais usam memória e não são persistência produtiva;
- passkeys, PSP, transporte, Health Connect e FHIR dependem de provedores;
- regras financeiras, jurídicas e clínicas exigem especialistas;
- interfaces Android/iOS ainda precisam consumir os contratos;
- cobertura nacional não pode ser declarada sem evidência;
- feature flags não devem ser ativadas antes de gates e homologação.

## 10. Evidências esperadas

- saída dos testes;
- SHA do head da branch;
- número e URL do PR;
- status dos gates no mesmo SHA;
- OpenAPI da Rodada 005;
- evidências de banco, autenticação e integrações reais nas etapas futuras;
- atualização da issue `#63`.

## 11. Procedimento de entrega

1. confirmar diff e ausência de segredos;
2. executar testes locais;
3. publicar somente a branch de trabalho;
4. abrir PR em rascunho;
5. registrar testes, limites e bloqueios;
6. aguardar gates;
7. não habilitar auto-merge;
8. integrar somente após autorização, revisão e Squash and Merge.

## 12. Histórico

| Versão | Data | Alteração |
|---|---|---|
| 1.8 | 28/07/2026 | Rodada 004 do APK Valley registrada. |
| 1.9 | 28/07/2026 | Auditoria do Valley Rider e plano de homologação. |
| 2.0 | 28/07/2026 | PR #62, QA Rider e testes Git determinísticos. |
| 2.1 | 28/07/2026 | Rodada 005 implementada como vertical executável com 24 contratos e feature flags. |
