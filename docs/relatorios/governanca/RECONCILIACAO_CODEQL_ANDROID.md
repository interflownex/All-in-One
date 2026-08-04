# Reconciliação do CodeQL para Android

## Decisão

A configuração `java-kotlin: none` introduzida diretamente na `main` em `2dab13399e1fd6a754b73231aac5885b2681d8d9` não é adotada como solução final.

O repositório contém três módulos Android compiláveis em `apps/valley-android`: `app`, `admin` e `universal`. Portanto, o CodeQL Java/Kotlin utiliza `build-mode: manual`, Java 17, Android SDK 36 e Gradle para compilar os três módulos antes da análise.

## Motivo

- `autobuild` falhou porque o projeto Android não está na raiz;
- `none` reduz a fidelidade da análise de linguagem compilada;
- o build manual reutiliza a cadeia já homologada pelos workflows Android;
- falhas de compilação permanecem bloqueantes e visíveis.

## Comando auditável

```bash
cd apps/valley-android
./gradlew :app:assembleDebug :admin:assembleDebug :universal:assembleDebug --no-daemon --stacktrace
```

## Fonte de verdade

A configuração executável está em `.github/workflows/codeql.yml`.
