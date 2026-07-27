# Plano de Ação Estruturado para o Codex

**Versão:** 2.9  
**Data e hora:** 27/07/2026 04:29:44  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `fix/cicd-governanca-v2-8-2026-07-27`  
**PR:** `#50`  
**Issue operacional:** `#49`  
**Orquestração:** `#51`  
**Ciclo principal:** 8 horas  
**Tolerância:** até 4 horas

## Missão

Concluir a Fase 0 de estabilização, transformando os quatro bloqueadores restantes em correções verificadas. Não iniciar Marketplace enquanto a PR #50 não tiver uma linha de integração confiável.

## Bloco 1: 0h a 1h30 — artefatos gerados

1. Executar separadamente:
   - `scaffold_modules.py --check`;
   - `generate_domain_event_fixtures.py --check`;
   - `validate_openapi.py`;
   - `validate_repository.py`.
2. Registrar código de saída e diff de cada comando.
3. Corrigir a fonte do primeiro desvio.
4. Repetir `check_generated_artifacts.py`.
5. Liberar a suíte unitária.

## Bloco 2: 1h30 a 3h30 — Bandit

1. Ler `bandit-summary.md`.
2. Separar achados por arquivo e severidade.
3. Corrigir primeiro:
   - URL sem allowlist de esquema;
   - XML inseguro;
   - SQL dinâmico não parametrizado.
4. Usar `# nosec` apenas com justificativa específica e teste.
5. Executar Bandit e `tests/test_security_gates.py`.

## Bloco 3: 3h30 a 5h — Android

1. Executar contrato Android.
2. Garantir `gradlew` executável.
3. Executar testes unitários.
4. Executar lint.
5. Gerar APK debug.
6. Executar CodeQL.
7. Registrar a primeira subetapa falha e corrigir.

## Bloco 4: 5h a 6h30 — PostgreSQL

1. Aplicar migrations.
2. Executar `validate_postgres_real_dsn.py`.
3. Registrar tabela, coluna, índice ou trigger divergente.
4. Corrigir o primeiro contrato.
5. Executar stores e matriz.

## Bloco 5: 6h30 a 7h30 — regressão completa

Reexecutar CI, Security, Database, Compose, OpenAPI e DAST.

## Bloco 6: 7h30 a 8h — fechamento

- atualizar issues #49 e #51;
- atualizar PR #50;
- atualizar pendências, relatório e tarefas;
- manter rascunho se houver gate vermelho;
- preparar Squash and Merge somente com critérios atendidos.

## Tolerância de até 4 horas

Usar somente para concluir correções já iniciadas. Não abrir nova frente funcional.

## Critérios de saída

- quatro bloqueadores resolvidos;
- testes unitários executados;
- todos os gates obrigatórios verdes;
- nenhuma credencial exposta;
- Vision ausente do fluxo operacional;
- documentação atualizada;
- PR pronta para revisão ou bloqueio específico comprovado.
