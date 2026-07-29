# AIO Admin Android 2.0.0

Aplicativo Android instalável do painel administrativo All in One. O APK usa uma WebView endurecida, restrita à origem configurada, com suporte seguro à janela de autenticação Google e abertura de destinos externos no navegador ou aplicativo correspondente.

## Fonte visual e funcional

- painel publicado: `https://9135635066da434181.v2.appdeploy.ai/`;
- interface-base: `apps/all-in-one-admin`;
- registro do deploy: `apps/all-in-one-admin/appdeploy`;
- manifesto Stitch/Figma: `apps/all-in-one-admin/design/figma-screen-manifest.json`;
- logomarca oficial: `assets/brand/aio-admin-logo-official.png`;
- ícones Android: `src/main/res/mipmap-*/ic_launcher.png`.

A marca foi apenas redimensionada proporcionalmente. Nenhum traço, cor, texto, forma ou composição foi alterado.

## Funções entregues

- autenticação Google com allowlist administrativa;
- visão geral calculada a partir do servidor;
- fila e decisão de aprovações;
- cadastro, edição e exclusão controlada de empresas;
- governança dos 24 módulos ativos, com Vision excluído;
- operações e alertas de segurança;
- relatórios CSV;
- configurações persistentes e notificações;
- auditoria e sincronização WebSocket em tempo real;
- estados de carregamento, vazio, erro, offline e recuperação.

Não existem botões deliberadamente inertes. Toda ação visível navega, consulta, persiste, exporta, autentica, notifica ou apresenta confirmação/erro.

## Compilação

```bash
cd apps/valley-android
./gradlew :admin:testDebugUnitTest :admin:lintDebug :admin:assembleDebug --no-daemon
```

Para apontar o APK a outro ambiente HTTPS homologado:

```bash
A1_ADMIN_URL=https://admin.exemplo.com/ ./gradlew :admin:assembleDebug
```

A URL não pode conter credenciais e permanece protegida pela política de mesma origem.
