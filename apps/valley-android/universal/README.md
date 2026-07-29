# Valley Universal Android 1.0.0

Aplicativo Android instalável do Valley Universal. O módulo abre a aplicação web publicada em um contêiner endurecido, mantendo a mesma experiência responsiva disponível no navegador e na PWA.

## Aplicação publicada

- AppDeploy ID: `84e9680fcfa2a84551`;
- URL: `https://84e9680fcfa2a84551.v2.appdeploy.ai/`;
- frontend: React/Vite responsivo;
- backend: autenticação, perfis, contextos, solicitações e aprovações;
- contextos: Pessoal, Rider, Business, One Service e PDV;
- ambiente administrativo: separado e protegido por allowlist.

## Segurança Android

- somente URL-base HTTPS;
- bloqueio de credenciais na URL configurada;
- navegação interna limitada à mesma origem;
- destinos externos abertos fora da WebView principal;
- acesso a arquivos e conteúdo local desabilitado;
- conteúdo misto HTTP/HTTPS bloqueado;
- Safe Browsing habilitado quando suportado;
- depuração WebView somente no build debug;
- login Google aberto em janela WebView separada;
- cookies de terceiros aceitos somente na janela de autenticação;
- nenhuma interface JavaScript nativa exposta.

## Marca

O ícone é copiado durante o build diretamente de:

`assets/brand/valley-logo-official.png`

A imagem oficial não é redesenhada nem alterada. O processo apenas a disponibiliza como recurso Android.

## Compilação

```bash
cd apps/valley-android
./gradlew :universal:testDebugUnitTest :universal:lintDebug :universal:assembleDebug --no-daemon
```

Para apontar o APK a outro ambiente homologado:

```bash
VALLEY_UNIVERSAL_URL=https://valley.exemplo.com/ \
  ./gradlew :universal:assembleDebug --no-daemon
```

A URL alternativa precisa usar HTTPS, possuir host válido e não conter credenciais.

## Distribuição

O workflow `.github/workflows/valley-universal-android-apk.yml` gera:

- `Valley-Universal-1.0.0-debug.apk`;
- `Valley-Universal-1.0.0-debug.apk.sha256`.

Os APKs especializados existentes permanecem independentes. Este módulo representa a vertente universal.
