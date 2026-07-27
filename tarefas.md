# Tarefas da IA Desenvolvedora

**Versão:** 1.5  
**Data e hora:** 27/07/2026 04:29:44  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `fix/cicd-governanca-v2-8-2026-07-27`  
**Commit verificado:** `fb49ba0c334054817fbbb129dfbf38f2cf741761`  
**Pull Request:** `#50`  
**Issue operacional:** `#49`  
**Issue de orquestração:** `#51`  
**Destino:** Codex e demais IAs desenvolvedoras autorizadas

## 1. Objetivo

Executar o plano v2.9 e concluir a Fase 0 antes de iniciar Marketplace.

## 2. Estado atual

### Aprovado

- OpenAPI;
- Valley DAST;
- Docker Compose Health Gate;
- auditoria das dependências Python;
- Trivy API Hub, Identity e Jobs;
- auditorias JavaScript;
- contrato Android.

### Bloqueado

1. `Check generated artifacts`;
2. Bandit;
3. Android completo;
4. PostgreSQL por DSN.

## 3. Primeira ação obrigatória

Executar os quatro comandos separadamente:

```bash
python scripts/scaffold_modules.py --check
python scripts/generate_domain_event_fixtures.py --check
python scripts/validate_openapi.py
python scripts/validate_repository.py
```

Corrigir o primeiro que falhar. Não iniciar funcionalidade nova.

## 4. Ordem de retomada

1. liberar artefatos;
2. executar testes unitários;
3. corrigir Bandit;
4. concluir Android;
5. concluir banco;
6. reexecutar todos os gates;
7. atualizar issues, PR e documentação;
8. somente então iniciar Marketplace na issue #51.

## 5. Regras mandatórias

- sem push direto na `main`;
- sem merge com gate vermelho;
- somente Squash and Merge;
- sem segredos;
- Vision excluído;
- sem exclusões em massa;
- sem supressão genérica de scanner;
- sem alegação de conclusão sem evidência;
- PR #50 permanece em rascunho enquanto qualquer gate obrigatório falhar.

## 6. Fontes de verdade

1. `AGENTS.md`;
2. este `tarefas.md`;
3. `docs/Pendências Do desenvolvedor.md`, versão 2.9;
4. `docs/relatorios/pendencias/RELATORIO_VARREDURA_STATUS_v2.9_2026-07-27.md`;
5. `docs/relatorios/pendencias/PLANO_ACAO_CODEX_v2.9_2026-07-27.md`;
6. issue `#49`;
7. issue `#51`;
8. PR `#50`;
9. logs dos workflows do head atual.

## 7. Critérios de aceite

- `check_generated_artifacts.py` aprovado;
- suíte unitária executada e aprovada;
- Bandit e `tests/test_security_gates.py` aprovados;
- Android aprovado em contrato, testes, lint, assemble e CodeQL;
- Database aprovado em migrations, contrato por DSN, stores e matriz;
- Compose, OpenAPI e DAST permanecem verdes;
- nenhuma referência operacional ao Vision;
- nenhuma credencial exposta;
- documentação e issues atualizadas;
- integração por Squash and Merge.

## 8. Histórico

| Versão | Data e hora | Alteração |
|---|---|---|
| 1.0 | 26/07/2026 13:49:32 | Diretriz permanente. |
| 1.1 | 26/07/2026 14:01:53 | Ciclo v2.6. |
| 1.2 | 26/07/2026 23:06:33 | Ciclo v2.7 e Telegram. |
| 1.3 | 27/07/2026 01:55:20 | Início v2.8. |
| 1.4 | 27/07/2026 02:17:29 | Fechamento parcial v2.8. |
| 1.5 | 27/07/2026 04:29:44 | Plano v2.9, quatro bloqueadores atuais e continuidade da Fase 0. |
