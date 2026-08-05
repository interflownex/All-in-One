# Padrão visual e de entrega obrigatório para frontends

Esta regra complementa o `AGENTS.md` raiz e vale para todos os projetos sob `frontend/`.

## Fontes de verdade

- `config/ui/global_visual_delivery_policy.json`
- `docs/design/PADRAO_GLOBAL_ENTREGA_VISUAL_REUTILIZAVEL.md`
- `config/branding/authorized_assets.json`
- `config/branding/brand_identity.json`

## Regras mandatórias

- Nenhum aplicativo pode desativar localmente a política visual global.
- Usar exclusivamente os ativos oficiais de marca previstos nos manifestos.
- Preservar logomarcas sem redesenho, recoloração, recorte, distorção ou substituição.
- Aplicar os tokens tipográficos mínimos definidos na política global.
- Botões equivalentes devem usar a mesma fonte e o mesmo tamanho.
- Botões de intenção devem seguir o padrão plastificado/acrílico translúcido, alto relevo, sombra visível e texto em baixo relevo, sem imagens ou ícones salvo autorização funcional expressa.
- Entregas visuais devem conter tela pronta, PNGs reutilizáveis independentes, Markdown e `MANIFESTO_SHA256.json`.
- Recortes da tela pronta não contam como ativos reutilizáveis.
- Telas aprovadas só podem ser alteradas mediante autorização expressa do proprietário.

## Validação obrigatória

Antes de concluir qualquer alteração visual ou de front-end, executar:

```bash
python3 scripts/validate_global_visual_delivery.py
python3 -m pytest tests/test_global_visual_delivery_policy.py -q
```

Falha nesses comandos bloqueia a conclusão e o merge.
