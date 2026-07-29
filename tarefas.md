# Tarefas da IA Desenvolvedora

**Versão:** 2.7
**Data e hora:** 29/07/2026 05:23
**Fuso horário:** `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`
**Branch:** `codex/flutter-distribuicao-gratuita-2026-07-29`
**Commit-base:** `438d64f46ef341f6a3559dbcb6642cd950ba7291`
**Commit de entrega:** `365be4c`
**Pull request:** será aberto a partir desta branch

## 1. Objetivo

Substituir o canal `google-play-production` por uma distribuição gratuita de
APKs e iniciar a migração do Valley Consumidor para Flutter/Dart, preservando a
interface produzida pelos templates Stitch e os ativos oficiais de marca.

## 2. Contexto

- `google-play-production` era um GitHub Environment, não um pacote Flutter;
- publicar na Google Play pode exigir custos, mas gerar e distribuir APKs por
  GitHub Actions usa o orçamento gratuito disponível da conta;
- downloads locais do SDK Flutter falharam duas vezes por corrupção TLS
  (`curl 56`), tanto no Google Storage quanto no clone GitHub;
- o runner GitHub instala Flutter `3.44.8` e Android sem depender da rede WSL;
- o projeto Stitch autoritativo é `VALLEY APK - Template Completo`, ID
  `2122145924469811680`, com oito grupos de telas;
- a implementação `apps/valley` materializa a interface web/mobile embutida;
- os documentos externos de marca de 29/07/2026 foram consultados, mas seus
  hashes declarados não correspondem aos arquivos de nomes semelhantes na
  pasta Windows; por isso o app usa os binários canônicos já autorizados em
  `config/branding/authorized_assets.json`.

## 3. Escopo

### Incluído

1. app `apps/valley-flutter` em Dart;
2. WebView controlada com bundle local do Valley;
3. cópia exata das logos canônicas All in One e Valley;
4. preparação determinística do bundle Stitch/Vite;
5. geração de APK universal, ARM64, ARMv7 e x86_64;
6. auditoria de conteúdo e assinatura de cada APK;
7. atestação de proveniência e artefato GitHub por 30 dias;
8. remoção do environment e dos contratos `VALLEY_PLAY_*` do release gratuito;
9. testes contratuais para impedir regressão ao canal pago.

### Fora do escopo

- publicar na Google Play;
- remover imediatamente o app Kotlin antes da paridade comprovada;
- modificar artisticamente logomarcas;
- declarar como canônico um arquivo externo cujo hash não foi conciliado;
- migrar neste ciclo cada tela Stitch para widget Flutter nativo.

## 4. Fontes de verdade

1. `AGENTS.md`;
2. `config/stitch/template_project_coordinate.json`;
3. `config/stitch/template_project_state.json`;
4. `config/stitch/screen_manifest.json`;
5. `config/stitch/sync_state.json`;
6. `apps/valley`;
7. `config/branding/authorized_assets.json`;
8. `config/branding/brand_identity.json`;
9. `assets/brand/`;
10. documentação Flutter oficial para `pubspec`, assets, testes e APK;
11. `Arquivo_Mestre_Ativos_Oficiais_All_in_One_Valley_2026-07-29.md`;
12. `Atualizacao_Ativos_Marca_Rodada_002_All_in_One_Valley_2026-07-29.md`.

## 5. Pré-requisitos

- branch de trabalho baseada no Squash and Merge `438d64f`;
- lock multiagente adquirido;
- GitHub Actions habilitado;
- runner Ubuntu com Java 17, Node 22, Flutter 3.44.8 e Android SDK;
- variável opcional `VITE_API_HUB_URL` configurada no repositório;
- nenhum segredo Play necessário para a distribuição gratuita.

## 6. Sequência de execução

1. validar contratos Python, YAML, branding e Stitch;
2. revisar o diff e executar verificação de segredos;
3. criar commit rastreável em português;
4. publicar a branch e abrir PR para `main`;
5. aguardar o workflow `Valley Flutter APK Gratuito`;
6. corrigir qualquer falha de analyze, teste, build ou auditoria;
7. baixar os quatro APKs do run verde;
8. validar hashes, assinatura, conteúdo e identidade do pacote;
9. instalar e abrir o APK ARM64 em dispositivo/emulador Android disponível;
10. conferir carregamento, navegação, login, catálogo e chamadas ao API Hub;
11. integrar somente com todos os gates verdes no mesmo SHA;
12. liberar o lock multiagente.

## 7. Prioridades

1. P0: build e auditoria dos APKs;
2. P0: preservação da marca e do template Stitch;
3. P0: instalação/abertura em Android real;
4. P1: fluxos de autenticação, catálogo e API Hub;
5. P2: migração progressiva de telas WebView para widgets Flutter nativos.

## 8. Testes

```bash
.venv/bin/python -m pytest -q \
  tests/test_valley_flutter_contract.py \
  tests/test_valley_android_workflow_contract.py \
  tests/test_branding_assets.py
python3 scripts/validate_valley_android_release.py
python3 scripts/validate_valley_android_release_v29.py
python3 scripts/check_brand_integrity.py
flutter pub get
dart format --output=none --set-exit-if-changed lib test
flutter analyze
flutter test
flutter build apk --release
flutter build apk --release --split-per-abi
python3 scripts/audit_valley_flutter_apks.py \
  apps/valley-flutter/build/app/outputs/flutter-apk
git diff --check
```

## 9. Critérios de aceite

- nenhuma referência a `google-play-production` ou `VALLEY_PLAY_*` no workflow;
- Flutter 3.44.8 instalado no runner;
- bundle de `apps/valley` copiado para o Flutter após build;
- logos Flutter com SHA-256 idêntico aos ativos canônicos;
- analyze e testes Flutter aprovados;
- quatro APKs maiores que 1 MiB, ZIPs válidos e assinados;
- APKs contêm manifesto, AssetManifest, `index.html` e logo Valley;
- APK ARM64 instala e abre no Android correto;
- fluxos essenciais testados no ambiente funcional;
- PR com gates verdes no mesmo SHA e Squash and Merge.

## 10. Riscos

| Risco | Tratamento |
|---|---|
| TLS WSL corrompe downloads grandes | executar instalação/build no runner GitHub |
| WebView sem API funcional | fornecer `VITE_API_HUB_URL` e testar fronteira real |
| assinatura de desenvolvimento não atualizável | manter como distribuição gratuita; definir keystore estável antes de produção |
| divergência entre documentos e binários externos | bloquear ingestão até conciliar SHA-256 |
| remoção precoce do Kotlin | manter durante migração até paridade validada |
| ação visual sem função | reutilizar implementação funcional `apps/valley` |

## 11. Bloqueios

- build Flutter local bloqueado pela rede TLS do WSL;
- instalação em Android depende de dispositivo ou emulador acessível;
- API Hub funcional depende do valor correto de `VITE_API_HUB_URL`;
- os hashes externos descritos nos documentos de marca não foram localizados nos
  arquivos de nomes semelhantes da pasta Windows.

## 12. Evidências esperadas

- SHA do commit e URL do PR;
- run verde do workflow Flutter;
- logs de analyze, testes, build e auditoria;
- quatro APKs baixados, nomes, tamanhos e SHA-256;
- relatório `apksigner verify`;
- `adb install` e Activity iniciada;
- capturas ou logs dos fluxos essenciais;
- SHA do Squash and Merge.

## 13. Pendências restantes

1. publicar branch e abrir PR;
2. executar o workflow remoto;
3. baixar e validar os APKs;
4. testar em Android;
5. corrigir lacunas encontradas no runtime;
6. decidir keystore gratuita estável para atualizações fora da Play;
7. migrar progressivamente grupos Stitch para widgets Flutter nativos.

## 14. Procedimento de entrega

1. revisar arquivos e segredos;
2. criar commit baseado no diff real;
3. publicar apenas a branch de trabalho;
4. abrir PR para `main`;
5. acompanhar e corrigir gates;
6. baixar os APKs somente de run verde;
7. provar instalação e funcionamento;
8. integrar por Squash and Merge;
9. registrar versão, data/hora, branch, commits, PR e evidências;
10. liberar o lock.

## 15. Histórico

| Versão | Data e hora | Alteração |
|---|---|---|
| 2.6 | 29/07/2026 04:43 | Remediação de marca e scanner integrada pelo PR #80. |
| 2.7 | 29/07/2026 05:23 | Migração Flutter e distribuição gratuita de APKs baseada em Stitch. |
