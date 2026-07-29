# Tarefas da IA Desenvolvedora

**Versão:** 2.9  
**Data e hora:** 29/07/2026 19:17, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `codex/aio-admin-android-total-2026-07-29`  
**Commit-base:** `188d842c5909dc3e5be5a09574a7809eb761a752`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Público:** Equipe Técnica e gestão administrativa

## 1. Objetivo desta entrega

Entregar o AIO Admin Android 2.0.0 com todas as telas do manifesto administrativo, ações funcionais, backend persistente, autenticação Google, sincronização em tempo real e logomarca oficial no aplicativo e no ícone.

## 2. Fontes de verdade

1. `apps/all-in-one-admin/design/figma-screen-manifest.json`;
2. `apps/all-in-one-admin/design/FIGMA_PROJECT_BRIEF.md`;
3. `apps/all-in-one-admin`;
4. `apps/valley-android/admin/`;
5. `assets/brand/aio-admin-logo-official.png`;
6. AppDeploy `9135635066da434181`;
7. branch e pull request desta atividade.

## 3. Estado implementado

- painel web/backend publicado;
- cinco testes AppDeploy aprovados;
- oito áreas administrativas navegáveis;
- CRUD persistente de empresas, aprovações, operações e segurança;
- 24 módulos ativos no catálogo, Vision excluído;
- métricas calculadas do banco, sem números falsos;
- auditoria e revisão do estado;
- WebSocket para atualização entre sessões;
- CSV, notificações e configurações persistentes;
- WebView Android endurecida com popup OAuth;
- ícones Android gerados somente por redimensionamento proporcional da marca oficial;
- workflow para teste, lint, APK e checksum.

## 4. Testes obrigatórios antes do merge

```bash
cd apps/valley-android
./gradlew :admin:testDebugUnitTest :admin:lintDebug :admin:assembleDebug --no-daemon
```

Também verificar:

- workflow `AIO Admin Android APK` verde no mesmo SHA;
- endpoint público de saúde com `Success`;
- APK abre login Google dentro da janela autorizada;
- todas as oito áreas carregam após login;
- criar e editar uma empresa persiste após reinício;
- decisão de aprovação sincroniza em outra sessão;
- módulo obrigatório não pode ser desabilitado;
- nenhuma tela apresenta botão morto;
- ícone instalado corresponde ao ativo oficial.

## 5. Critérios de aceite

- APK gerado e disponível como artefato GitHub Actions;
- SHA-256 publicado junto ao APK;
- zero erro de compilação, teste ou lint;
- zero segredo versionado;
- nenhuma alteração da arte oficial;
- pull request sem conflito e com diff conhecido;
- integração somente por Squash and Merge com gates verdes.

## 6. Riscos e bloqueios

- a versão atual é um instalador conectado ao servidor AppDeploy; indisponibilidade externa ativa a tela de recuperação;
- distribuição Play Store exige chave de assinatura e conta de publicação, não incluídas no Git;
- permissões administrativas adicionais devem ser incluídas por política versionada, nunca por bypass;
- o slot de imagem web do AppDeploy deve continuar apontando ao ativo oficial, sem substituto desenhado.

## 7. Próxima prioridade do projeto

Após concluir e integrar esta entrega, retornar à issue `#83`, respeitando a ordem Marketplace → Stock → Delivery. A feature flag do checkout permanece desligada até a reserva transacional do Stock ser homologada.

## 8. Histórico

| Versão | Data | Alteração |
|---|---|---|
| 2.8 | 29/07/2026 | Fundação Stock e reservas transacionais. |
| 2.9 | 29/07/2026 | AIO Admin Android 2.0.0, backend AppDeploy, OAuth, ícone oficial e workflow APK. |
