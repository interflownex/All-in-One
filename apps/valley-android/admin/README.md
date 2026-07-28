# All in One Admin para Android

Aplicativo Android instalável que abre o Painel Web Admin publicado em:

`https://9135635066da434181.v2.appdeploy.ai/`

## Escopo

- catálogo oficial com 24 módulos;
- módulo Vision removido;
- cadastro empresarial;
- ativação, ocultação e desativação de módulos;
- operação, relatórios, exportação CSV e auditoria;
- WebView restrita a HTTPS, sem acesso a arquivos locais e sem conteúdo misto;
- links externos são encaminhados ao navegador do dispositivo.

## Build local

```bash
cd apps/valley-android
./gradlew :admin:testDebugUnitTest :admin:assembleDebug --no-daemon
```

APK gerado em:

`apps/valley-android/admin/build/outputs/apk/debug/admin-debug.apk`

## Publicação

O APK debug é assinado automaticamente pelo Android SDK e serve para instalação e homologação interna. Uma versão destinada à Google Play exige chave de upload e Play App Signing próprios do aplicativo Admin.

## Revalidação de integração

Branch submetida em 28/07/2026 a novo ciclo completo contra a `main`
estabilizada, preservando os gates Android, CodeQL, segurança e empacotamento.
