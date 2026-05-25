# Status Operacional

## STATUS OPERACIONAL - 2026-05-25 Motor de dominio e Jobs

### Concluido neste ciclo

- Repositorio inicializado a partir do documento mestre All-in-One.
- Catalogo de seis apps e 25 microservicos com contratos e runtimes FastAPI.
- Migracoes PostgreSQL e validadores MongoDB para os dominios centrais.
- Store contratual persistente, transicoes, idempotencia, assinatura de
  gateway produtivo, auditoria e outbox no runtime compartilhado.
- Modulo Jobs com curriculo do usuario final, busca/publicacao de vagas,
  candidatura, importacao CTPS Digital PDF e procedencia exibivel.
- Acesso ao banco de curriculos limitado a empresas Business ativas com
  papel/escopo recrutador e log append-only de visualizacao.
- Infraestrutura e workflows de CI/CD definidos.
- Microservico Jobs incluido no Docker Compose para execucao local.

### Validacoes executadas

- `python scripts/scaffold_modules.py --check`: 462 artefatos sincronizados.
- `python scripts/validate_repository.py`: 25 modulos e 6 apps validados.
- `python scripts/validate_openapi.py`: contratos dos 25 modulos validos.
- `python -m pytest --import-mode=importlib -q`: 104 testes aprovados.
- `pip-audit -r requirements-dev.txt`: nenhuma vulnerabilidade conhecida.
- `bandit -r modules/shared scripts -q`: nenhum achado no codigo produtivo.
- Migracoes PostgreSQL aplicadas em container efemero; quatro triggers
  append-only confirmados, incluindo evidencias e acessos Jobs.
- MongoDB executado em container efemero; quatro colecoes e indices geoespacial/TTL confirmados.
- Checks GitHub do PR: CI, Database, OpenAPI e Security aprovados.

### Pendencias rastreadas

- Integracoes de pagamento/fiscal e validadores KYC/KYB/CTPS oficiais dependem
  de provedores homologados e segredos externos.
- Apps possuem contrato de integracao; interfaces finais entram nas entregas incrementais do roadmap.
- Testes de carga, seguranca dinamica e E2E com provedores serao bloqueadores antes de producao.
- O parser marca importacao documental sem declarar verificacao oficial
  externa enquanto nao existir integrador autorizado.

### Git

- Branch principal: `main`.
- Baseline anterior mesclado: PR `#1` (`67c7ead`).
- Branches `monetization` e `module/*` exigidas foram publicadas no baseline `67c7ead`.
- `main` recebeu em seguida ajustes operacionais de trigger dos workflows para evitar execucoes redundantes ao criar branches.
