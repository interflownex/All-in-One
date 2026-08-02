# Plano de acao Codex v5.4

**Data e hora:** 02/08/2026 02:09, `America/Sao_Paulo`
**Repositorio:** `interflownex/All-in-One`
**Branch:** `codex/cloudflare-completo-coerente-20260802`
**Horizonte:** 8 horas, com tolerancia operacional de ate 4 horas

## Objetivo

Manter Cloudflare completo e coerente no workspace WSL local-first, com Pages,
Tunnel e MCPs validados, CI sem falhas falsas e segredos fora do Git.

## Sequencia priorizada

1. Confirmar `wrangler`, `cloudflared`, Cloudflare Pages e Tunnel pelo validador
   `scripts/validate_cloudflare_wsl.py`.
2. Confirmar variaveis nao sensiveis no GitHub Variables.
3. Confirmar `CLOUDFLARE_ACCOUNT_ID` no GitHub Secrets.
4. Manter `CLOUDFLARE_API_TOKEN` apenas como segredo externo persistente; se
   ausente, nao tentar publicar por CI.
5. Validar build web local e workflow de Pages.
6. Abrir PR, aguardar gates verdes e integrar por Squash and Merge.
7. Comentar a issue `#51` com PR, SHA, testes e bloqueio externo remanescente.

## Testes obrigatorios

- `python3 scripts/configure_cloudflare_wsl.py --apply`
- `python3 scripts/validate_cloudflare_wsl.py`
- `cd apps/all-in-one && npm ci && npm run build`
- `.venv/bin/python -m pytest --capture=no -q tests/test_cloudflare_pages_workflow.py tests/test_cloudflare_wsl_configuration.py tests/test_gke_workflow_local_first.py`
- `python3 scripts/validate_repository.py`
- `git diff --check`

## Criterios de aceite

- Workflow Cloudflare Pages usa `wrangler` `4.118.0`.
- Workflow nao falha em `push` quando o token persistente de Cloudflare nao foi
  configurado.
- Deploy automatico segue bloqueado ate `CLOUDFLARE_API_TOKEN` existir em
  GitHub Secrets.
- Cloudflare Tunnel nao publica SSH nem bancos.
- Chaves SSH, PDF sensivel e tokens permanecem fora do Git.

## Pendencias restantes

- Criar ou fornecer `CLOUDFLARE_API_TOKEN` persistente e escopado para Pages.
- Configurar `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` caso a notificacao
  automatica de deploy web seja desejada.
