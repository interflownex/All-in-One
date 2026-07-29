# A1 Admin Android

Aplicativo Android instalável do painel administrativo All in One. O módulo mantém uma WebView restrita à origem configurada e abre destinos externos no navegador ou aplicativo correspondente.

## Fonte visual

O shell responsivo oficial fica em:

`apps/all-in-one-admin`

Ele fornece a versão web e a versão mobile usadas como referência pelo novo projeto Figma.

## URL do painel

O valor padrão continua apontando para o painel homologado atual. Para compilar contra uma nova publicação do shell, use uma das opções:

```bash
A1_ADMIN_URL=https://admin.exemplo.com/ ./gradlew :admin:assembleDebug
```

ou:

```bash
./gradlew :admin:assembleDebug -PA1_ADMIN_URL=https://admin.exemplo.com/
```

A URL precisa usar HTTPS, ter host válido, não conter credenciais e permanece protegida por política de mesma origem.

## Validação

```bash
./gradlew :admin:testDebugUnitTest :admin:lintDebug :admin:assembleDebug
```

O workflow `.github/workflows/admin-android-apk.yml` continua responsável pelo APK manual, enquanto o gate do template valida o shell web e os testes da política de URL.
