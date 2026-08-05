# Padrão visual e de entrega obrigatório para aplicativos mobile

Esta regra complementa o `AGENTS.md` raiz e vale para todos os projetos atuais ou futuros sob `mobile/`.

Fontes de verdade obrigatórias:

- `config/ui/global_visual_delivery_policy.json`
- `docs/design/PADRAO_GLOBAL_ENTREGA_VISUAL_REUTILIZAVEL.md`
- `config/branding/authorized_assets.json`
- `config/branding/brand_identity.json`

Nenhum projeto pode desativar localmente essa política. Antes de concluir alterações visuais, executar:

```bash
python3 scripts/validate_global_visual_delivery.py
python3 -m pytest tests/test_global_visual_delivery_policy.py -q
```

Falhas bloqueiam conclusão e merge.
