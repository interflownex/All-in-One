# Plano de Ação Estruturado para o Codex

**Versão:** 3.2
**Data e hora:** 28/07/2026 14:51:13
**Repositório:** `interflownex/All-in-One`
**Branch:** `codex/auditoria-valley-rider-2026-07-28`
**Pull Request:** `#62`
**Issue:** `#51`
**Janela:** 8 horas, com tolerância operacional de até 4 horas

## Missão imediata

Publicar a correção determinística dos testes Git, comprovar todos os gates obrigatórios no novo SHA e preparar o PR #62 para revisão sem executar merge automático.

## Sequência

1. validar os testes direcionados do gate Git;
2. executar a suíte equivalente ao CI;
3. atualizar `tarefas.md` e os documentos v3.2;
4. revisar diff e segredos;
5. commitar e publicar a branch;
6. aguardar CI, Compose Health e Security;
7. atualizar PR e issue com o SHA e evidências;
8. marcar o PR pronto somente se todos os gates estiverem verdes.

## Critérios de aceite

- testes Git independentes de refs ambientais;
- `907 passed` ou resultado superior na suíte do CI;
- lint/build e testes do Rider verdes;
- QA desktop/mobile comprovada;
- ausência de segredos e diff limpo;
- todos os gates obrigatórios verdes no mesmo SHA;
- branch sem divergência de `main`;
- integração exclusivamente por Squash and Merge.

## Tolerância de até 4 horas

- corrigir somente a primeira falha reproduzível do novo SHA;
- reexecutar jobs com falha transitória depois de confirmar a causa;
- não criar novo commit enquanto o commit atual estiver em validação;
- após 12 horas, atualizar causas, bloqueios, evidências e próximos passos nestes documentos.
