# Plano de Ação Codex v5.3

**Data e hora:** 02/08/2026 01:46, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `codex/desativar-gke-local-first-20260802`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Público-alvo:** Equipe Técnica

## Janela planejada

Plano dimensionado para até 8 horas, com tolerância operacional de até 4 horas
para validações remotas e CI.

## Sequência de execução

1. Validar que `main` não tem workflow pago automático no modo local-first.
2. Manter o workflow GKE apenas manual, com confirmação explícita de billing.
3. Executar testes e `scripts/validate_repository.py`.
4. Abrir PR para `main`, aguardar gates verdes e integrar por Squash and Merge.
5. Atualizar a issue de orquestração #51 com o status v5.3.
6. Manter #107 aberto até billing/IAM/APIs serem resolvidos externamente.

## Prioridades

1. Não contornar billing, IAM ou enforcement do Google Cloud.
2. Não simular sucesso de deploy GKE.
3. Não usar `continue-on-error` para esconder falhas reais.
4. Não executar Google Cloud pago automaticamente enquanto o modo local-first
   estiver ativo.
5. Preservar Cloudflare, Docker, Antigravity, Tailscale e Stitch já validados.

## Testes

- `.venv/bin/python -m pytest --capture=no -q tests/test_gke_workflow_local_first.py`;
- `python3 scripts/validate_repository.py`;
- `gh pr checks <PR> --watch --interval 10`.

## Critérios de aceite

- `.github/workflows/deploy.yml` não contém `push` automático para `main`;
- o deploy GKE real só roda com `confirm_gcp_billing_enabled=true`;
- a política local-first mantém `GOOGLE_CLOUD_ENABLED=false` por padrão;
- CI obrigatório fica verde no mesmo SHA;
- #107 permanece registrada como bloqueio externo, não como concluída.

## Riscos e bloqueios

- Billing GCP continua dependente de ação administrativa externa e pode gerar
  custo.
- Se o deploy GKE for necessário futuramente, a execução deve ser manual,
  autenticada e validada no mesmo SHA.

## Procedimento de entrega

Commitar em branch de trabalho, abrir PR para `main`, aguardar checks verdes,
integrar por Squash and Merge, sincronizar `main` local e comentar o status na
issue #51.
