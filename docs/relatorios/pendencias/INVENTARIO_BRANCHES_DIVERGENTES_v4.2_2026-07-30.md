# Inventário de Branches Divergentes v4.2

**Data:** 30/07/2026 18:54:50, `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`
**Branch:** `codex/corrigir-pendencias-relacionais-v42-20260730`
**Commit-base:** `52b4a18c9b9a45c1a985ce22d974f9f8487dadc4`

Foram comparadas as 29 heads de trabalho então existentes com `main`, histórico
de PRs e commits. A única ref com zero commit exclusivo,
`backup/migracao-privada-antes-2026-07-25`, foi arquivada na tag anotada
`archive/backup-migracao-privada-2026-07-25` (objeto preservado
`bdbe40467004ace774c2a6545077072a441be247`) e removida como branch.

As 28 refs abaixo possuem commits únicos e permanecem preservadas. A presença
neste inventário não autoriza integração direta.

| Branch | SHA preservado | Classe |
|---|---|---|
| `audit/confirmacao-v7-governanca-2026-07-23` | `089a483a170b0d410d57ba3c018d3378415410b4` | auditoria sem PR |
| `backup/admin-web-apk-before-rebuild-2026-07-28` | `0c9de2967e273f0a547087964ebc8f30f845db16` | backup |
| `backup/apk-valley-rodada-004-legacy-2026-07-28` | `64b2a40b09dff16869cd2414e45c285a4ac28b36` | backup |
| `backup/health-watch-safezone-before-rebuild-2026-07-28` | `cbcfd7f461800939f093214fc56532dd10eda7eb` | backup |
| `backup/innovation-wave-001-before-rebuild-2026-07-28` | `34da05fd7dc1a8fd66f094d7db41526031315f38` | backup |
| `backup/pdv-desktop-before-rebuild-2026-07-28` | `432c5ce8be8a0c7f7d71a25f6042c24443745268` | backup |
| `backup/pr34-workflow-concorrente-2026-07-26` | `0076ac1c83cc745c8023b8b514d3c3f9df0d5b86` | backup |
| `codex/auditoria-valley-rider-2026-07-28` | `8f1d6366c268ba657a035c6e8e2c0001da43a002` | tip posterior à PR associada |
| `codex/corrigir-dependabot-2026-07-29` | `bd8561adfcb0ddbe4a345d98b6050565a4ca62d0` | segurança antiga |
| `codex/corrigir-gate-android-2026-07-29` | `c69eb72a4bd6d626c6921e3db5217dd853bbf4ae` | CI antiga |
| `codex/flutter-distribuicao-gratuita-2026-07-29` | `5b992cb192356b1d1a1ababec91cfcc3db265b6f` | distribuição a revisar |
| `codex/remover-vision-atualizar-stock-2026-07-25` | `9e76a6dc61f20cb6c29aae289471ce074eef6140` | implementação antiga |
| `codex/rodada-002-decisoes-funcional-2026-07-28` | `aed7fbe35880cd22ee4d715d753feadb3a89cc00` | somente decisões/documentos; não desbloqueia #69 |
| `copilot/commit` | `f2ab1ed1ddf5e662939d842cd23b3770cb787824` | commits sem PR |
| `copilot/diretrizes-implantacao-primicias-selecionadas` | `57b5ee45926dd9d85c0bdba5e2db8e67df79f138` | diretriz sem PR |
| `deploy/render-blueprint` | `3192ae492f65f99ba9d8f6c3be0f75a9153dccae` | deploy alternativo |
| `docs/marketplace-fase-1-baseline-2026-07-28` | `309ef819cf80232902378c2102d43b789364d99f` | documentação antiga |
| `docs/pendencias-documentacao-v2-7-telegram-2026-07-26` | `2485d4e320b0ee7c4aeb6b52a9c814e50037ef02` | documentação antiga |
| `feat/brand-integrity-data-ui` | `2e3bba709a3576bbebc694a94a8b4a4b92887916` | tip posterior à PR associada |
| `feat/marketplace-checkout-idempotent-issue-78` | `1eb361ae7a72eba3c94949afe146335453f4443d` | provável duplicata da PR #94 |
| `feat/marketplace-checkout-idempotente-2026-07-29` | `e99b4d93754a3be44a0e3946f6cac952ad3edba9` | provável duplicata da PR #94 |
| `feat/stock-cj-aliexpress-integration-admin-2026-07-26` | `47b7a87fb9fa790d739b8a46147b312ca4508a46` | integração não homologada |
| `feature/primicias-selecionadas-v1` | `550a75a760afa9e0f9a6ca0dca2ad331e78cf6cf` | implementação agregadora |
| `fix/all-in-one-final-stabilization-2026-07-26` | `5cdc87e0215ecdd4346be4c3b4648a036320456a` | baseline antiga |
| `fix/generated-artifacts-gate` | `9f502f2622bd03097bfb965169c190fc67fe73cf` | gate antigo |
| `fix/vscode-local-artifact-exclusions-2026-07-29` | `8c95eab3b483306b7f2912866f179dc447cde811` | correção substituída |
| `security/pre-migration-hardening-2026-07-25` | `416c85782535326e8656e5541aff081a2e5bdc10` | hardening antigo |
| `security/pre-migration-hardening-refresh-2026-07-25` | `d2415a0395e292da4feb4f7bec8fb9d3fbb1403b` | hardening antigo |

## Critério de resolução

Comparar cada diff com `main`, mapear substituição por issue/PR, testar o escopo
e então reaplicar seletivamente, arquivar por tag ou manter bloqueada. Nunca
integrar um tip divergente sem gates verdes no mesmo SHA.
