# Plano de acao Codex v5.5

**Data e hora:** 02/08/2026 02:31, `America/Sao_Paulo`
**Repositorio:** `interflownex/All-in-One`
**Branch:** `codex/cloudflare-production-main-20260802`
**Horizonte:** 8 horas, com tolerancia operacional de ate 4 horas

## Objetivo

Preservar Cloudflare Pages produtivo a partir da branch `main`, com dominio
customizado servindo a build All-in-One correta.

## Sequencia priorizada

1. Validar projeto Pages remoto e `production_branch=main`.
2. Publicar build atual com `wrangler pages deploy dist --project-name all-in-one-web --branch main`.
3. Validar `https://brasildesconto.com.br` por HTTP 200, titulo e headers.
4. Rodar testes Cloudflare e validação geral do repositório.
5. Abrir PR, aguardar checks verdes e integrar por Squash and Merge.

## Testes obrigatorios

- `python3 scripts/validate_cloudflare_wsl.py`
- `.venv/bin/python -m pytest --capture=no -q tests/test_cloudflare_wsl_configuration.py tests/test_cloudflare_pages_workflow.py`
- `python3 scripts/validate_repository.py`
- `git diff --check`

## Criterios de aceite

- `wrangler pages deployment list` mostra Production em `main`.
- `brasildesconto.com.br` não serve mais `tmp-valley`.
- `production_branch=main` fica versionado e validado.
- Segredos permanecem fora do Git.
