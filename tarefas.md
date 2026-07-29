# Tarefas da IA Desenvolvedora

**Versão:** 2.7
**Data e hora:** 29/07/2026 04:30:18
**Fuso horário:** `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`
**Branch:** `codex/corrigir-gate-android-2026-07-29`
**Commit-base:** `f1681dd2cbff145a661254cb1ce49f059121d7f2`
**Referência de governança v2.9:** `21a6ba6b0fbeb4afeaa336b7b0bbec6c51a0a9ff`
**Pull request anterior bloqueado por escopo:** `#75` — fechado sem merge
**Pull request da correção isolada:** `#77`

## 1. Objetivo

Alinhar o validador legado do release Valley Android ao contrato v2.9 já
implementado no workflow de segurança, mantendo os gates de produção e isolando
a correção das 304 alterações não relacionadas acumuladas no PR anterior.

## 2. Contexto

- `origin/main` já usa as tarefas explícitas `testProductionDebugUnitTest`,
  `lintProductionDebug` e `assembleProductionDebug`;
- `scripts/validate_valley_android_release.py` ainda exigia as tarefas genéricas
  antigas e reprovava o workflow correto;
- as tags `actions/checkout@v6`, `actions/setup-python@v6` e
  `actions/setup-node@v6` existem nos repositórios oficiais;
- `google-play-production` é um environment válido e obrigatório no contrato de
  release;
- os cinco diagnósticos do `extHost2` dependem da resolução autenticada e do
  cache da extensão GitHub Actions no VS Code;
- o PR #75 ficou verde, mas foi bloqueado para merge porque continha 304
  arquivos, 32.228 exclusões e oito commits fora do escopo declarado;
- o commit `21a6ba6` instituiu a governança v2.9 e é ancestral da `main` atual.
- a branch limpa integrou por fast-forward o PR #74 no commit `f1681dd` sem
  sobreposição com os arquivos desta correção.

## 3. Escopo

### Incluído

1. alterar somente o marcador obsoleto do validador Valley;
2. atualizar este documento com instruções autossuficientes;
3. executar validadores, testes contratuais, integridade de marca e verificações
   Git;
4. publicar uma branch limpa e abrir um pull request novo para `main`;
5. fechar o PR #75 sem mesclá-lo, registrando o motivo.
6. restaurar usos objetivos da marca canônica encontrados pelo gate obrigatório,
   sem alterar a arte oficial.
7. remover o parâmetro morto do callback `PepitaWidget` que bloqueava o lint do
   Valley, sem mudar o comportamento.

### Fora do escopo

- alterar as versões válidas das GitHub Actions;
- remover ou renomear o environment protegido;
- integrar as remoções de skills acumuladas na branch anterior;
- corrigir pendências gerais de catálogo ou Dependabot;
- declarar os diagnósticos visuais encerrados sem recarregar o VS Code
  autenticado.

## 4. Fontes de verdade

1. `AGENTS.md`;
2. `config/autonomy/pending_work_priority_policy.json`;
3. `config/autonomy/multi_agent_sync_policy.json`;
4. `.github/workflows/security.yml`;
5. `.github/workflows/valley-android-release.yml`;
6. `scripts/validate_valley_android_release.py`;
7. `scripts/validate_valley_android_release_v29.py`;
8. commit `21a6ba6b0fbeb4afeaa336b7b0bbec6c51a0a9ff`;
9. documentação e tags oficiais das GitHub Actions;
10. este `tarefas.md`.
11. `config/branding/authorized_assets.json`;
12. `config/branding/brand_identity.json`.

## 5. Pré-requisitos

- worktree limpo e sem merge/rebase ativo;
- branch criada diretamente de `origin/main`;
- lock multiagente do escopo `workspace`;
- credencial Git disponível fora do repositório;
- ambiente virtual `.venv` funcional;
- nenhuma mudança de head após a validação final.

## 6. Sequência de execução e prioridades

### P0 — correção e entrega

1. confirmar que o diff contém apenas o validador, scanner/teste de marca,
   restaurações canônicas e `tarefas.md`;
2. executar os testes e validadores listados abaixo;
3. executar busca por segredos e revisar arquivos sensíveis;
4. criar commit rastreável em português;
5. publicar a branch sem force-push;
6. abrir novo PR para `main`;
7. fechar o PR #75 sem merge e explicar o bloqueio de escopo;
8. aguardar gates verdes no mesmo SHA;
9. revisar mergeabilidade, revisões e mudança de head;
10. integrar exclusivamente por Squash and Merge;
11. atualizar referências locais e liberar o lock.

### P1 — diagnóstico do editor

1. autenticar o GitHub no VS Code;
2. executar `Developer: Reload Window`;
3. confirmar que a coleção `extHost2` foi recalculada;
4. somente então encerrar os cinco diagnósticos visuais.

## 7. Testes

```bash
python3 scripts/validate_valley_android_release.py
python3 scripts/validate_valley_android_release_v29.py
.venv/bin/python -m pytest -q \
  tests/test_security_workflow_contract.py \
  tests/test_valley_android_workflow_contract.py \
  tests/test_valley_android_signing.py
python3 scripts/check_brand_integrity.py
.venv/bin/python -m pytest -q tests/test_brand_integrity_scanner.py
git diff --check
git fsck --connectivity-only --no-dangling
cd apps/all-in-one-user && npm run lint && npm run build
cd ../all-in-one-pdv-desktop && npm test
cd ../valley && npm run lint && npm run build
```

Verificação das tags oficiais:

```bash
git ls-remote --exit-code https://github.com/actions/checkout.git refs/tags/v6
git ls-remote --exit-code https://github.com/actions/setup-python.git refs/tags/v6
git ls-remote --exit-code https://github.com/actions/setup-node.git refs/tags/v6
```

## 8. Critérios de aceite

- ambos os validadores Valley aprovados;
- oito testes contratuais aprovados;
- integridade de marca aprovada;
- diff sem whitespace inválido ou marcadores de conflito;
- branch baseada diretamente na `main` atual;
- PR novo contém somente os arquivos declarados;
- nenhum segredo ou ativo oficial alterado;
- símbolos substitutos `A1` e `AIO` removidos em favor do PNG canônico;
- favicon Valley aponta para o SVG autorizado;
- head validado permanece inalterado;
- checks obrigatórios verdes;
- merge executado por Squash and Merge;
- PR #75 encerrado sem integrar o diff acumulado.

## 9. Riscos

| Risco | Tratamento |
|---|---|
| merge acidental de 304 arquivos | usar branch nova baseada em `origin/main` |
| regressão para tarefas Android genéricas | teste e validador v2.9 bloqueiam |
| falso positivo do editor | validar tags oficiais e exigir recarga autenticada |
| mudança do head após aprovação | invalidar a autorização técnica e testar novamente |
| segredo no diff | busca direcionada e revisão de arquivos sensíveis |

## 10. Bloqueios

- a confirmação visual dos diagnósticos depende da sessão GitHub no VS Code;
- alertas Dependabot da branch padrão pertencem a uma frente separada;
- nenhuma pendência externa autoriza enfraquecer gates ou remover o environment.

## 11. Evidências esperadas

- SHA da branch limpa e do commit final;
- saída dos dois validadores e oito testes;
- saída da integridade de marca e verificações Git;
- lista exata de arquivos do novo PR;
- URL do novo PR e estado dos checks;
- comentário de encerramento do PR #75;
- SHA do Squash and Merge, quando autorizado pelos gates.

## 12. Pendências restantes

1. validar e versionar a correção;
2. publicar a branch limpa;
3. abrir e acompanhar o novo PR;
4. encerrar o PR #75 sem merge;
5. executar Squash and Merge somente após gates verdes;
6. autenticar e recarregar o VS Code para confirmar a limpeza visual.

## 13. Procedimento de entrega

1. revisar o diff e os resultados reproduzíveis;
2. registrar commit e publicar somente a branch de trabalho;
3. incluir testes, riscos e bloqueios no novo PR;
4. verificar checks e revisões no SHA final;
5. integrar por Squash and Merge;
6. buscar `origin/main` e confirmar o commit integrado;
7. liberar o lock multiagente;
8. informar versão, data/hora, repositório, branch, commits e PR.

## 14. Histórico resumido

| Versão | Data e hora | Alteração |
|---|---|---|
| 2.0 | 28/07/2026 | PR #62, QA Rider e testes Git determinísticos. |
| 2.1 | 28/07/2026 | Rodada 005 com contratos e feature flags. |
| 2.2 | 28/07/2026 | Marketplace Fase 1 e governança de pendências. |
| 2.3 | 28/07/2026 | A1 Admin Web/Mobile, Android seguro e pacote Figma. |
| 2.4 | 29/07/2026 04:16:09 | Correção CI isolada da branch acumulada e referência v2.9 registrada. |
| 2.5 | 29/07/2026 04:18:52 | Scanner corrigido e violações objetivas de marca restauradas com ativos canônicos. |
| 2.6 | 29/07/2026 04:27:17 | Gate de lint Valley corrigido sem alterar o comportamento do widget. |
| 2.7 | 29/07/2026 04:30:18 | PR #77 aberto e PR #75 encerrado sem merge após auditoria de escopo. |
