# Valley Consumidor em Flutter

Shell Android gratuita do Valley Consumidor. A interface é produzida a partir
do projeto Stitch `VALLEY APK - Template Completo` e da implementação web
versionada em `apps/valley`.

## Fontes visuais

- `config/stitch/template_project_coordinate.json`;
- `config/stitch/template_project_state.json`;
- `config/stitch/screen_manifest.json`;
- `config/stitch/sync_state.json`;
- `config/branding/authorized_assets.json`;
- `assets/brand/valley-logo-official.png`;
- `assets/brand/all-in-one-logo-official.png`.

Os ativos oficiais são apenas copiados. Não podem ser redesenhados,
recoloridos, recortados ou distorcidos.

## Desenvolvimento

```bash
flutter pub get
flutter analyze
flutter test
flutter build apk --release
```

O workflow `valley-flutter-apk.yml` instala Flutter e Android no runner,
recompila `apps/valley`, injeta o bundle em `assets/valley/`, executa os gates e
publica o APK como artefato gratuito do GitHub Actions.
