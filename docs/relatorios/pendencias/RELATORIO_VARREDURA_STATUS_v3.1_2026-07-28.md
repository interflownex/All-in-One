# Relatório de Varredura e Status

**Versão:** 3.1
**Data e hora:** 28/07/2026 08:39:01
**Fuso:** `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`
**Branch:** `codex/auditoria-valley-rider-2026-07-28`
**Commit-base:** `3834bec6383edd6da08e9fdcf3d74a0de1589df2`
**Issue de orquestração:** `#51`
**Classificação:** `Pendências > Técnico > Equipe técnica`

## Resumo

O Valley Rider integrado pelo PR `#61` preserva os contratos funcionais exigidos, mas a validação local declarada não era reproduzível: `npm run lint` falhava com 8 erros e 1 aviso, e o build falhava depois com incompatibilidade de tipo no SHA-256. As falhas foram corrigidas nesta branch e a cadeia local ficou verde.

| Nome da atividade | Descrição | Passo sendo executado | Dificuldade [1 a 5] | % concluído | Tempo previsto | Etapas [Total] | Concluídas [X] | Pendentes [Y] |
|---|---|---|---:|---:|---|---:|---:|---:|
| Auditoria dos gates locais | Reproduzir lint, build e testes Stitch | concluída | 4 | 100% | 1 h | 4 | 4 | 0 |
| Correção React/TypeScript | Corrigir efeitos, refs, GPS e SHA-256 | concluída | 4 | 100% | 2 h | 6 | 6 | 0 |
| Integridade de marca | Confirmar ativo oficial e ausência de substituto | validação final | 3 | 80% | 30 min | 5 | 4 | 1 |
| QA renderizada | Validar DOM, console, interação e responsividade | bloqueada por `iab` indisponível | 3 | 20% | 1 h | 6 | 1 | 5 |
| Homologação Mapbox | Configurar token público restrito | dependência externa | 4 | 20% | 2 h | 5 | 1 | 4 |
| KYC/OCR e cofre | Homologar provedores e arquivos privados | dependência externa | 5 | 10% | externo | 6 | 1 | 5 |
| Repasse financeiro | Homologar PSP consumidor de `rider_payout` | dependência externa | 5 | 20% | externo | 5 | 1 | 4 |
| Android em campo | Play Integrity, GPS e rede instável | dependência externa | 5 | 10% | 4 h | 6 | 1 | 5 |
| Marca Valley Riders | Ingerir binário oficial aprovado | bloqueada por ativo ausente | 3 | 0% | externo | 3 | 0 | 3 |
| GitHub | Commit, PR, gates e issue | em execução | 3 | 30% | 2 h | 7 | 2 | 5 |

## Evidências locais

- `.venv/bin/pytest -q tests/test_valley_rider_stitch_contract.py`: 5 aprovados;
- `.venv/bin/pytest -q tests/test_valley_rider_stitch_contract.py tests/test_branding_assets.py`: 10 aprovados;
- `npm run lint`: aprovado após correções;
- `npm run build`: aprovado, bundle Vite gerado;
- `npm audit --omit=dev`: 0 vulnerabilidades de produção;
- navegador integrado: bloqueado com `Browser is not available: iab`.

## Riscos e decisão

- as 2 vulnerabilidades altas reportadas por `npm ci` estão em dependências de desenvolvimento e precisam permanecer cobertas pelo gate Security;
- nenhuma homologação externa deve ser declarada pronta sem credencial, contrato e evidência no ambiente correto;
- nenhum binário ou token deve ser adicionado ao Git;
- o PR somente poderá ser integrado por Squash and Merge depois dos gates verdes no mesmo SHA.
