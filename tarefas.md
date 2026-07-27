# Tarefas da IA Desenvolvedora

**Versão:** 1.6  
**Data e hora:** 27/07/2026 05:33:26  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `fix/cicd-governanca-v2-8-2026-07-27`  
**Pull Request:** `#50`  
**Issue operacional:** `#49`  
**Issue de orquestração:** `#51`  
**Destino:** Codex e demais IAs desenvolvedoras autorizadas

## 1. Objetivo

Concluir a revalidação da Fase 0 no head mais recente do PR `#50`. Não iniciar Marketplace antes de todos os gates obrigatórios estarem verdes.

## 2. Estado confirmado

### Resolvido e implementado

- gate de artefatos gerados liberado;
- dois arquivos `STATUS.md` ausentes criados;
- baseline de 24 módulos preservada;
- adaptador de validação compatível criado sem ocultar erros desconhecidos;
- falso negativo Git do checkout de PR corrigido;
- chamadas externas endurecidas com validação HTTPS e allowlist;
- testes de URL segura criados;
- Bandit reduzido de 9 para 4 achados delimitados;
- exceções B608/B314 restritas por arquivo, regra e validador próprio;
- Android alinhado ao flavor `productionDebug` e ao package ID Firebase legítimo;
- workflows Android alinhados;
- validador PostgreSQL corrigido para não reaplicar DDL de uso único;
- workflow Database atualizado para validar banco já migrado;
- diagnósticos direcionados versionados.

### Em revalidação

1. suíte unitária completa;
2. Security Python e `tests/test_security_gates.py`;
3. testes, lint, assemble e CodeQL Android;
4. contrato, stores e matriz PostgreSQL;
5. regressão de Compose, OpenAPI e DAST.

## 3. Primeira ação obrigatória

1. Obter o head atual da branch e do PR `#50`.
2. Consultar os workflows associados exatamente a esse head.
3. Não usar resultados de commits anteriores.
4. Corrigir somente a primeira falha concreta que permanecer.

## 4. Ordem de retomada

### CI

- confirmar `Check generated artifacts` verde;
- confirmar contrato Android e testes de assinatura verdes;
- capturar primeiro teste unitário falho, caso exista;
- corrigir e adicionar regressão.

### Security

- executar `validate_bandit_scoped_exceptions.py`;
- executar Bandit completo conforme workflow;
- executar `tests/test_security_gates.py`;
- preservar pip-audit, JavaScript e Trivy verdes.

### Android

```bash
cd apps/valley-android
./gradlew testProductionDebugUnitTest lintProductionDebug assembleProductionDebug --no-daemon
```

Confirmar também CodeQL e caminho do APK `app/build/outputs/apk/production/debug/`.

### PostgreSQL

- aplicar migrations em banco limpo;
- validar triggers;
- executar contrato por DSN sem `--repeat-migrations`;
- executar stores prioritários e matriz;
- executar Jobs/CTPS e outbox/RabbitMQ.

### Fechamento

- atualizar issues `#49` e `#51`;
- atualizar PR `#50`;
- atualizar pendências, relatório, plano e este arquivo;
- remover diagnósticos temporários desnecessários;
- manter o PR em rascunho enquanto houver gate vermelho ou em processamento;
- usar Squash and Merge somente após revisão e checks verdes.

## 5. Regras mandatórias

- sem push direto na `main`;
- sem merge com gate vermelho ou em processamento;
- somente Squash and Merge;
- sem segredos;
- Vision excluído;
- sem exclusões em massa;
- sem supressão genérica de scanner;
- sem alegação de conclusão sem evidência;
- preservar trabalho paralelo e buscar o head atual antes de editar;
- Marketplace permanece bloqueado até a conclusão da Fase 0.

## 6. Fontes de verdade

1. `AGENTS.md`;
2. este `tarefas.md`, versão 1.6;
3. `docs/Pendências Do desenvolvedor.md`, versão 2.9;
4. `docs/relatorios/pendencias/RELATORIO_VARREDURA_STATUS_v2.9_2026-07-27.md`;
5. `docs/relatorios/pendencias/PLANO_ACAO_CODEX_v2.9_2026-07-27.md`;
6. issue `#49`;
7. issue `#51`;
8. PR `#50`;
9. workflows associados ao head atual.

## 7. Critérios de aceite

- suíte unitária completa aprovada;
- Bandit e `tests/test_security_gates.py` aprovados;
- Android aprovado em contrato, testes, lint, assemble e CodeQL;
- Database aprovado em migrations, contrato por DSN, stores e matriz;
- Compose, OpenAPI e DAST verdes no mesmo head;
- nenhuma referência operacional ao Vision;
- nenhuma credencial exposta;
- documentação e issues atualizadas;
- PR revisada e integrada por Squash and Merge.

## 8. Histórico

| Versão | Data e hora | Alteração |
|---|---|---|
| 1.0 | 26/07/2026 13:49:32 | Diretriz permanente. |
| 1.1 | 26/07/2026 14:01:53 | Ciclo v2.6. |
| 1.2 | 26/07/2026 23:06:33 | Ciclo v2.7 e Telegram. |
| 1.3 | 27/07/2026 01:55:20 | Início v2.8. |
| 1.4 | 27/07/2026 02:17:29 | Fechamento parcial v2.8. |
| 1.5 | 27/07/2026 04:29:44 | Plano inicial v2.9. |
| 1.6 | 27/07/2026 05:33:26 | Execução dos quatro bloqueadores, correções aplicadas e revalidação em andamento. |
