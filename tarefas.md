# Tarefas da IA Desenvolvedora

**Versão:** 2.5
**Data e hora:** 29/07/2026 04:40:39
**Fuso horário:** `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`
**Branch:** `codex/branding-scanner-issue-79`
**Commit-base:** `6f76c6359eca268aaafc301a51c0f754be8998c8`
**Issue:** `#79`
**Referência de governança v2.9:** `21a6ba6b0fbeb4afeaa336b7b0bbec6c51a0a9ff`
**PRs preservados:** `#75` e `#77`, fechados sem merge

## 1. Objetivo

Reaplicar sobre a `main` atual as remediações de marca, scanner e lint
preservadas na issue #79, sem repetir a correção Android já integrada pelo PR
#76 e sem incorporar os 304 arquivos acumulados no PR #75.

## 2. Contexto

- o PR #76 integrou em `6f76c63` o adaptador Android v2.9 e tornou redundante a
  parcela Android do PR #77;
- o PR #77 ficou totalmente verde, mas foi fechado sem merge após a `main`
  avançar e tornar seu escopo misto;
- a issue #79 preserva os arquivos de branding, scanner e lint para reaplicação
  controlada;
- o scanner da `main` confundia crases Markdown, bundles gerados e regras CSS
  vizinhas com violações de marca;
- após eliminar falsos positivos, foram confirmados dois símbolos substitutos
  (`A1` e `AIO`) e um favicon Valley não autorizado;
- os ativos canônicos existem e a política permite sua restauração sem alterar
  a arte;
- o lint Valley reprovava um parâmetro morto no callback `PepitaWidget`.

## 3. Escopo

### Incluído

1. corrigir o parsing do scanner e adicionar três testes de regressão;
2. substituir símbolos alternativos pelo PNG oficial All in One;
3. copiar o PNG canônico no preparo do pacote PDV Windows;
4. apontar o favicon Valley para o SVG autorizado;
5. remover o parâmetro morto do callback Valley sem mudar comportamento;
6. manter o marcador legado do validador coerente com `ProductionDebug`;
7. validar, publicar e integrar por Squash and Merge.

### Fora do escopo

- redesenhar, recolorir, recortar ou modificar ativos oficiais;
- reabrir ou mesclar os PRs #75 e #77;
- repetir o adaptador Android já integrado no PR #76;
- corrigir catálogo geral, Dependabot ou novas evoluções Marketplace;
- encerrar diagnósticos visuais do VS Code sem sessão GitHub autenticada.

## 4. Fontes de verdade

1. `AGENTS.md`;
2. issue #79;
3. `config/branding/authorized_assets.json`;
4. `config/branding/brand_identity.json`;
5. `scripts/check_brand_integrity.py`;
6. `.github/workflows/security.yml`;
7. `scripts/validate_valley_android_release.py`;
8. `scripts/validate_valley_android_release_v29.py`;
9. commit `6f76c6359eca268aaafc301a51c0f754be8998c8`;
10. commit `21a6ba6b0fbeb4afeaa336b7b0bbec6c51a0a9ff`;
11. este `tarefas.md`.

## 5. Pré-requisitos

- branch criada diretamente de `origin/main`;
- lock multiagente do escopo `workspace`;
- ausência de merge/rebase conflitante;
- `.venv`, Node e dependências locais disponíveis;
- head do PR inalterado entre validação e merge;
- nenhuma credencial ou segredo no diff.

## 6. Sequência de execução

1. concluir o cherry-pick técnico e resolver somente `tarefas.md`;
2. executar integridade de marca e testes do scanner;
3. executar validadores e testes Valley;
4. executar lint/build User e Valley;
5. executar testes PDV e remover artefatos transitórios gerados localmente;
6. revisar diff, segredos, conflitos e arquivos sensíveis;
7. publicar a branch e abrir PR vinculado à issue #79;
8. aguardar todos os checks no mesmo SHA;
9. revisar head, mergeabilidade e comentários;
10. integrar exclusivamente por Squash and Merge;
11. atualizar `origin/main`, registrar evidências e liberar o lock.

## 7. Testes

```bash
python3 scripts/check_brand_integrity.py --fix
python3 scripts/check_brand_integrity.py
.venv/bin/python -m pytest -q \
  tests/test_brand_integrity_scanner.py \
  tests/test_security_workflow_contract.py \
  tests/test_valley_android_workflow_contract.py \
  tests/test_valley_android_signing.py
python3 scripts/validate_valley_android_release.py
python3 scripts/validate_valley_android_release_v29.py
npm --prefix apps/all-in-one-user run lint
npm --prefix apps/all-in-one-user run build
npm --prefix apps/all-in-one-pdv-desktop test
npm --prefix apps/valley run lint
npm --prefix apps/valley run build
git diff --check
git fsck --connectivity-only --no-dangling
```

## 8. Critérios de aceite

- integridade de marca aprovada após nova varredura;
- três testes do scanner e oito testes contratuais aprovados;
- símbolos substitutos removidos e ativos canônicos usados proporcionalmente;
- favicon Valley aponta para `favicon-valley.svg`;
- lint/build User e Valley aprovados;
- quatro testes PDV aprovados;
- validadores Valley v1 e v2.9 aprovados;
- diff sem segredos, conflitos ou artefatos gerados;
- PR contém somente os 11 arquivos autorizados;
- gates verdes no mesmo SHA;
- integração por Squash and Merge.

## 9. Riscos

| Risco | Tratamento |
|---|---|
| falso positivo do scanner | testes por fragmento sintático e Markdown |
| pacote PDV sem logo | copiar o ativo canônico no script de preparo |
| artefato gerado no Git | remover cópia local e alteração transitória do store |
| nova mudança da `main` | integrar antes do commit e revalidar |
| duplicar PR #76 | reaplicar apenas o residual da issue #79 |

## 10. Bloqueios

- os cinco diagnósticos `extHost2` dependem de autenticação e reload do VS Code;
- os 83 alertas Dependabot da `main` pertencem a frente separada;
- nenhum bloqueio permite enfraquecer gate ou fabricar ativo.

## 11. Evidências esperadas

- SHA do commit e PR da issue #79;
- lista dos 11 arquivos;
- saídas dos testes, builds e validadores;
- integridade de marca aprovada;
- checks remotos verdes no mesmo head;
- SHA do Squash and Merge;
- lock multiagente liberado.

## 12. Pendências restantes

1. concluir o cherry-pick;
2. revalidar no novo baseline;
3. publicar a branch e abrir PR;
4. acompanhar gates;
5. integrar com Squash and Merge;
6. autenticar/recarregar o VS Code para confirmar os diagnósticos visuais.

## 13. Procedimento de entrega

1. revisar o diff final e resultados;
2. criar commit rastreável em português;
3. publicar somente a branch de trabalho;
4. vincular o PR à issue #79;
5. mesclar apenas com gates verdes e head validado;
6. atualizar a `main` local e confirmar o merge;
7. liberar o lock;
8. informar versão, data/hora, repositório, branch, commits, issue e PR.

## 14. Histórico

| Versão | Data e hora | Alteração |
|---|---|---|
| 2.0 | 28/07/2026 | PR #62, QA Rider e testes Git determinísticos. |
| 2.1 | 28/07/2026 | Rodada 005 com contratos e feature flags. |
| 2.2 | 28/07/2026 | Marketplace Fase 1 e governança de pendências. |
| 2.3 | 28/07/2026 | A1 Admin Web/Mobile, Android seguro e pacote Figma. |
| 2.4 | 29/07/2026 | PRs #74/#76 integrados; #75 rejeitado por escopo. |
| 2.5 | 29/07/2026 04:40:39 | Issue #79 reaplicada sobre a `main` após fechamento seguro do PR #77. |
