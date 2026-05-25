# Google Stitch Para Front-End

## Estrategia

O planejamento visual e automatizado a partir de `config/module_catalog.json`.
Cada um dos 25 microservicos recebe um projeto isolado no Stitch, com telas
para visao geral, entidades operacionais, auditoria/permissoes e jornadas
especificas quando necessarias. Jobs inclui curriculo com procedencia,
importacao CTPS, busca de vagas e revisao Business auditada.

`config/stitch/screen_manifest.json` e o contrato compacto e deterministico de
projetos, contagens e telas especializadas; as telas por entidade sao
expandidas pelo orquestrador a partir do catalogo. `config/stitch/sync_state.json`
preserva IDs remotos retornados pelo Stitch para evitar duplicacao.

## Seguranca Da Autenticacao

O servidor MCP e `https://stitch.googleapis.com/mcp`. Credenciais nunca entram
em commits, manifestos ou prompts. Configure `STITCH_API_KEY` ou
`STITCH_ACCESS_TOKEN` somente via secret local/CI apos rotacao de qualquer
chave exposta em mensagem, log ou captura.

## Operacao

```bash
python scripts/stitch_orchestrator.py plan
python scripts/stitch_orchestrator.py discover
python scripts/stitch_orchestrator.py sync
```

`plan` nao acessa a rede e materializa o contrato. `discover` autentica no MCP
e lista as ferramentas anunciadas pelo Stitch. `sync` cria projetos/telas
ausentes e atualiza o estado local sem recriar o que ja possui identificador.

Os prompts proíbem dados sensiveis, documentos brutos e segredos em mockups.
Antes da implementacao web/mobile, os designs gerados devem ser revisados
contra contratos dos modulos e regras de LGPD.
