# Coordenada Mestre dos Templates Stitch

## Resultado obrigatório

O Stitch deve manter exatamente três projetos agregadores de produto:

1. `VALLEY APK - Template Completo` — Android e web mobile incorporada;
2. `ALL IN ONE - Template Web e Mobile Completo` — web responsiva, mobile web e aplicativo mobile;
3. `VALLEY RIDERS APK - Template Completo` — Android e web mobile incorporada.

Cada projeto deve reunir todas as ferramentas, recursos, telas e jornadas do
respectivo produto. A divisão técnica anterior por microserviço permanece como
fonte de referência e não autoriza fragmentar esses três templates de produto.

## Contrato executável

A fonte de verdade é
`config/stitch/template_project_coordinate.json`. Ela define para cada projeto:

- objetivo, marcas, superfícies e módulos;
- grupos de telas que devem ser gerados dentro do mesmo projeto;
- português do Brasil e identidade oficial obrigatórios;
- CRUDs, dashboards, relatórios, filtros, importações e exportações aplicáveis;
- ações funcionais, estados completos, acessibilidade e responsividade;
- bindings, permissões, auditoria, segurança e proibição de inventar contratos;
- herança das diretrizes existentes e das alterações versionadas posteriores.

EVIDÊNCIAS: `config/stitch/template_project_coordinate.json`,
`config/branding/brand_identity.json`, `config/module_catalog.json`,
`docs/data-audit/artifacts/coordenadas_stitch.json`.

## Continuidade automática e limites reais

`scripts/stitch_template_project_sync.py` cria ou atualiza os três projetos e
grava checkpoint após cada operação remota em
`config/stitch/template_project_state.json`. Uma rodada limitada por
`--max-operations` retoma do primeiro grupo pendente. Uma alteração na
coordenada muda seu digest e coloca as telas anteriores na fila de atualização.

Erros reconhecidos de quota, rate limit, tokens ou recurso esgotado registram
uma retomada pendente sem persistir conteúdo sensível do erro. O workflow
`.github/workflows/stitch-sync.yml` tenta novamente nos dias úteis e também
quando arquivos Stitch são enviados à `main`.

A retomada no dia seguinte somente ocorre de fato quando GitHub Actions está
ativo, o secret `STITCH_API_KEY` é válido e o provedor disponibiliza quota.
Essas dependências não podem ser substituídas por uma declaração de autonomia.

## Aceite

- exatamente três IDs remotos de projeto registrados;
- todos os 24 grupos de tela possuem ID remoto e digest atual;
- nenhuma credencial aparece em Git, prompts ou logs;
- a marca oficial é aplicada proporcionalmente;
- alterações de coordenada são reaplicadas às telas afetadas;
- ausência de quota gera checkpoint e não duplicação;
- validação humana final confirma bindings, acessibilidade, LGPD e ausência de botões mortos.

EVIDÊNCIAS: `config/stitch/template_project_state.json`,
`scripts/stitch_template_project_sync.py`, `.github/workflows/stitch-sync.yml`.
