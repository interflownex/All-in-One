# Valley Consumidor em Flutter

Aplicativo Android do Valley Consumidor. A interface é produzida a partir do projeto Stitch `VALLEY APK - Template Completo` e da implementação web versionada em `apps/valley`.

## Fontes visuais

- `config/stitch/template_project_coordinate.json`;
- `config/stitch/template_project_state.json`;
- `config/stitch/screen_manifest.json`;
- `config/stitch/sync_state.json`;
- `config/branding/authorized_assets.json`;
- `assets/brand/valley-logo-official.png`;
- `assets/brand/all-in-one-logo-official.png`.

Os ativos oficiais são copiados automaticamente durante o build. Não podem ser redesenhados, recoloridos, recortados ou distorcidos. A logomarca Valley é usada também como ícone Android sem alteração do arquivo canônico.

## Contrato funcional

A versão 1.1 conecta o WebView ao API Hub por uma ponte nativa HTTPS restrita ao host autorizado. O release não habilita fallback demonstrativo. A interface cobre os oito grupos Stitch do consumidor:

1. onboarding, identidade, perfil e MFA;
2. home, busca, categorias, ofertas, detalhes e favoritos;
3. pedidos, pagamentos de homologação, wallet, escrow, avaliações e disputas;
4. serviços, profissionais, agenda e contratos;
5. delivery, rastreio e suporte;
6. mobilidade, corridas e bilhetes;
7. Jobs, Health e documentos;
8. notificações, privacidade, segurança e configurações.

Cada ação visível deve possuir handler, endpoint, estado de carregamento, sucesso ou erro. O gate `scripts/validate_valley_functional_completeness.py` bloqueia regressões de telas, botões sem ação, servidor ou branding.

## Segurança e conectividade

- API Hub fixado em `https://all-in-one-api-hub.web.app` no release;
- somente HTTPS para chamadas nativas;
- assinatura Ed25519 verificada nas respostas críticas;
- permissões Android de internet e estado de rede materializadas no build;
- backup Android desativado;
- tráfego HTTP em texto claro bloqueado;
- nenhuma credencial incorporada ao APK.

## Desenvolvimento

```bash
npm --prefix apps/valley ci
npm --prefix apps/valley run lint
npm --prefix apps/valley run build
flutter pub get
flutter analyze
flutter test
flutter build apk --release
```

O workflow `Valley Flutter APK Funcional` instala Flutter e Android no runner, recompila `apps/valley`, aplica o ícone oficial, injeta o bundle em `assets/valley/`, executa os gates e publica o APK universal e as três variantes por arquitetura.
