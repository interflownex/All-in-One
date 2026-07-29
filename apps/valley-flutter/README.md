# Valley Consumidor em Flutter

Shell Android gratuito do Valley Consumidor. A interface é produzida a partir do projeto Stitch `VALLEY APK - Template Completo` e da implementação web versionada em `apps/valley`.

## Fontes visuais

- `config/stitch/template_project_coordinate.json`;
- `config/stitch/template_project_state.json`;
- `config/stitch/screen_manifest.json`;
- `config/stitch/sync_state.json`;
- `config/branding/authorized_assets.json`;
- `assets/brand/valley-logo-official.png`;
- `assets/brand/all-in-one-logo-official.png`.

Os ativos oficiais são copiados automaticamente durante o build. Não podem ser redesenhados, recoloridos, recortados ou distorcidos.

## Correção funcional

A versão 1.0.1 corrige o empacotamento recursivo do bundle web. Cada APK deve conter o `index.html`, o JavaScript e o CSS referenciados por ele. A auditoria falha quando qualquer recurso estiver ausente.

O release gratuito utiliza modo demonstrativo somente quando o workflow define explicitamente `VITE_VALLEY_ALLOW_DEMO=true`. Nenhuma credencial é incorporada ao APK.

## Desenvolvimento

```bash
flutter pub get
flutter analyze
flutter test
flutter build apk --release
```

O workflow `Valley Flutter APK Gratuito` instala Flutter e Android no runner, recompila `apps/valley`, injeta o bundle em `assets/valley/`, executa os gates e publica o APK universal e as três variantes por arquitetura.
