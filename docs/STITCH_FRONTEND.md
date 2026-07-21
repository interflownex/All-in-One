# Google Stitch Para Front-End

## Estrategia

O planejamento visual e automatizado a partir de `config/module_catalog.json`.
Cada um dos 25 microservicos recebe um projeto isolado no Stitch, com telas
para visao geral, entidades operacionais, auditoria/permissoes e jornadas
especificas quando necessarias. Jobs inclui curriculo com procedencia,
importacao CTPS, busca de vagas e revisao Business auditada.

Além dessa malha técnica por microserviço, a coordenada de produto
`config/stitch/template_project_coordinate.json` exige exatamente três projetos
agregadores, sem fragmentar cada produto: `VALLEY APK - Template Completo`,
`ALL IN ONE - Template Web e Mobile Completo` e
`VALLEY RIDERS APK - Template Completo`. Ela reúne as diretrizes universais,
fontes autoritativas, módulos, superfícies e grupos de telas de cada produto.

`config/stitch/screen_manifest.json` e o contrato compacto e deterministico de
projetos, contagens e telas especializadas; as telas por entidade sao
expandidas pelo orquestrador a partir do catalogo. `config/stitch/sync_state.json`
preserva IDs remotos retornados pelo Stitch para evitar duplicacao.

O branding e mandatorio. `config/branding/brand_identity.json` declara os
ativos oficiais `assets/brand/all-in-one-logo-official.png`,
`assets/brand/all-in-one-logo-light-official.png` e
`assets/brand/valley-logo-official.png`. Todo prompt enviado ao Stitch exige a
marca All-in-One no shell/header global; telas que atendem `valley`,
`valley-business` ou `valley-rider` tambem exigem a logo Valley oficial.

## Seguranca Da Autenticacao

O servidor MCP Stitch e obrigatorio e persistente neste workspace. A entrada
canonica fica em `~/.codex/config.toml`, mantendo o mesmo endpoint da
documentacao oficial do Stitch MCP e substituindo o header literal por
`env_http_headers` para nao persistir segredo em texto:

```toml
[mcp_servers.stitch]
url = 'https://stitch.googleapis.com/mcp'
http_headers = { Accept = 'application/json' }
env_http_headers = { 'X-Goog-Api-Key' = 'STITCH_API_KEY' }
```

Credenciais nunca entram em commits, manifestos ou prompts. Configure
`STITCH_API_KEY` somente via secret local/CI apos rotacao de qualquer chave
exposta em mensagem, log ou captura. A politica versionada fica em
`config/autonomy/stitch_mcp_policy.json`.

## Operacao

```bash
python scripts/stitch_orchestrator.py plan
python scripts/stitch_orchestrator.py status
python scripts/validate_stitch_mcp_config.py
python scripts/stitch_orchestrator.py discover
python scripts/stitch_orchestrator.py sync
python scripts/stitch_orchestrator.py sync --max-operations 5
python scripts/stitch_template_project_sync.py --dry-run
python scripts/stitch_template_project_sync.py --require-remote --max-operations 8
```

`plan` nao acessa a rede e materializa o contrato. `status` compara o manifesto
local com `config/stitch/sync_state.json` e mostra quantos projetos/telas ja tem
ID remoto registrado. `validate_stitch_mcp_config`
confirma a politica versionada e a configuracao persistente sem exigir segredo.
`discover` autentica no MCP e lista as ferramentas anunciadas pelo Stitch.
`sync` cria projetos/telas ausentes e atualiza o estado local sem recriar o que
ja possui identificador. `--max-operations` permite retomar em ciclos menores,
incluindo correcoes de branding em telas antigas marcadas como
`branding_pending`.

O sincronizador dos três projetos grava checkpoint em
`config/stitch/template_project_state.json` depois de cada criação ou edição.
IDs já registrados não são recriados. Mudanças na coordenada alteram seu digest
e obrigam atualização das telas existentes. Quando o MCP retornar erro
reconhecido de quota, rate limit ou esgotamento de recurso, a execução registra
`last_deferred` sem gravar credencial ou mensagem remota e retoma na próxima
execução agendada. Essa continuidade depende de GitHub Actions ativo,
`STITCH_API_KEY` válido e quota disponível; sem esses três requisitos ela não é
tratada como comprovada.

Para uma validacao online manual, exporte `STITCH_API_KEY` no ambiente e rode:

```bash
python scripts/validate_stitch_mcp_config.py --require-secret
python scripts/stitch_orchestrator.py discover
python scripts/stitch_auto_sync.py --require-remote
```

A sincronizacao persistente fica em `.github/workflows/stitch-sync.yml`. Ela roda
em `workflow_dispatch`, nos dias uteis e em pushes que alterem catalogo,
politica, manifesto, branding ou scripts Stitch. O workflow usa somente
`secrets.STITCH_API_KEY`, executa `scripts/stitch_auto_sync.py --require-remote`
e commita `config/stitch/sync_state.json` quando o Stitch retorna IDs remotos.
Sem esse secret, a automacao falha explicitamente em vez de registrar um falso
estado sincronizado.

Os prompts proíbem dados sensiveis, documentos brutos e segredos em mockups.
Antes da implementacao web/mobile, os designs gerados devem ser revisados
contra contratos dos modulos e regras de LGPD.
