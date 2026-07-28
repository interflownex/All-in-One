# Plano de Ação Estruturado para o Codex

**Versão:** 2.9  
**Atualização:** 27/07/2026 05:33:26  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `fix/cicd-governanca-v2-8-2026-07-27`  
**PR:** `#50`  
**Issue operacional:** `#49`  
**Orquestração:** `#51`  
**Ciclo principal:** 8 horas  
**Tolerância:** até 4 horas

## 1. Missão atualizada

Concluir a revalidação das correções aplicadas na Fase 0. O diagnóstico e a implementação já foram executados. A próxima IA deve trabalhar somente sobre falhas comprovadas pelo head mais recente e não iniciar Marketplace enquanto CI, Security, Android e Database não estiverem aprovados.

## 2. Entregas já executadas

- gate de artefatos liberado;
- status operacionais de Valley Business e Valley Rider criados;
- baseline de 24 módulos preservada;
- falso negativo Git de checkout de PR corrigido;
- URLs externas endurecidas e cobertas por testes;
- Bandit reduzido e exceções delimitadas por arquivo e regra;
- Android alinhado ao flavor `productionDebug` e ao cliente Firebase autorizado;
- PostgreSQL corrigido para não reaplicar DDL de uso único;
- diagnósticos direcionados adicionados para CI, Bandit, Android e banco;
- documentação e `tarefas.md` versionados.

## 3. Plano restante de execução

### Bloco 1: resultados da rodada atual

1. Ler os resultados dos workflows no head mais recente.
2. Confirmar, nesta ordem:
   - Continuous Integration;
   - Security Python;
   - Valley Android Security;
   - Database;
   - Compose, OpenAPI e DAST.
3. Não usar resultado de commit anterior como prova.

### Bloco 2: primeira falha real

Quando houver falha:

1. capturar o primeiro teste, arquivo, linha ou comando com erro;
2. reproduzir de forma isolada;
3. corrigir a fonte, não o sintoma;
4. criar ou atualizar teste de regressão;
5. reexecutar somente o gate afetado antes da regressão completa.

### Bloco 3: critérios específicos

#### CI

- `check_generated_artifacts.py` deve permanecer verde;
- contrato Android e testes de assinatura devem permanecer verdes;
- suíte unitária completa deve passar.

#### Security

- validador de exceções delimitadas deve passar;
- Bandit deve passar nos arquivos gerais e revisados;
- `tests/test_security_gates.py` deve passar;
- pip-audit, JavaScript e Trivy devem permanecer verdes.

#### Android

- `testProductionDebugUnitTest`;
- `lintProductionDebug`;
- `assembleProductionDebug`;
- CodeQL;
- APK gerado no caminho de production/debug;
- nenhuma chave debug em release.

#### Database

- migrations e triggers;
- contrato por DSN sem reaplicar DDL;
- stores prioritários;
- matriz de stores;
- Jobs/CTPS;
- outbox/RabbitMQ.

### Bloco 4: fechamento da Fase 0

Somente quando todos os gates obrigatórios estiverem verdes:

1. atualizar issues `#49` e `#51`;
2. atualizar PR `#50` com evidências e head final;
3. atualizar pendências, relatório e `tarefas.md`;
4. remover ou neutralizar workflows temporários de diagnóstico que não devam permanecer;
5. revisar o escopo amplo do PR;
6. marcar o PR como pronto para revisão;
7. integrar exclusivamente por Squash and Merge após revisão.

## 4. Próxima fase funcional

Marketplace somente poderá começar após a Fase 0. A ordem funcional permanece:

1. Marketplace;
2. Stock;
3. Delivery.

Cada frente exige contrato, banco, autorização, auditoria, testes, telemetria e rollback antes de ativação.

## 5. Condições de parada

Parar e registrar bloqueio quando houver:

- gate obrigatório vermelho sem erro reproduzível;
- credencial externa legítima ausente;
- conflito com trabalho paralelo;
- risco de exposição de segredo;
- necessidade de alteração de marca sem ativo oficial;
- ação administrativa reservada ao proprietário do repositório.

## 6. Critérios de saída

- CI completo aprovado;
- Security completo aprovado;
- Android completo aprovado;
- Database completo aprovado;
- Compose, OpenAPI e DAST verdes no mesmo head;
- nenhum segredo exposto;
- Vision ausente do fluxo operacional;
- documentação e issues atualizadas;
- PR revisada e pronta para Squash and Merge, ou bloqueio específico comprovado.
