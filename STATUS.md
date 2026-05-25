# Status Operacional

## STATUS OPERACIONAL - 2026-05-25 Jobs, Outbox RabbitMQ E Stitch

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
- PDFs da CTPS armazenados em cofre privado AES-256-GCM; somente o titular
  recupera o documento e toda leitura e auditada.
- Adapter Jobs PostgreSQL tipado ativavel por DSN, usando tabelas `jobs.*`,
  auditoria central e outbox; SQLite permanece apenas como contrato local.
- Infraestrutura e workflows de CI/CD definidos.
- Microservico Jobs incluido no Docker Compose para execucao local.
- Dispatcher transacional publica `audit.domain_events` em RabbitMQ com
  confirmacao, retry auditavel e entrega append-only.
- Payload RabbitMQ do fluxo Jobs e minimizado, sem PDF CTPS, storage key ou
  texto livre do curriculo.
- Orquestrador Stitch gera e sincroniza um projeto por microservico, cobrindo
  telas especificas de Jobs para candidato e recrutador Business.

### Validacoes executadas

- `python scripts/scaffold_modules.py --check`: 462 artefatos sincronizados.
- `python scripts/validate_repository.py`: 25 modulos e 6 apps validados.
- `python scripts/validate_openapi.py`: contratos dos 25 modulos validos.
- `python -m pytest --import-mode=importlib -q`: 111 testes aprovados e tres
  testes de infraestrutura separados por configuracao.
- `ALL_IN_ONE_JOBS_POSTGRES_TEST_DSN=... python -m pytest --import-mode=importlib -q tests/test_jobs_postgres_integration.py`:
  um teste de integracao aprovado em PostgreSQL 16 efemero.
- `pip-audit -r requirements-dev.txt`: nenhuma vulnerabilidade conhecida.
- `bandit -r modules/shared scripts workers -q`: nenhum achado no codigo produtivo.
- Sete migracoes PostgreSQL aplicadas em container efemero; quatro triggers
  append-only confirmados, incluindo evidencias e acessos Jobs.
- MongoDB executado em container efemero; quatro colecoes e indices geoespacial/TTL confirmados.
- Checks GitHub do PR anterior `#4`: CI, Database, OpenAPI e Security aprovados.

### Validacoes Do Incremento Em Andamento

- O workflow Database passa a validar entrega real PostgreSQL para RabbitMQ e
  registro append-only de confirmacao/retry.
- A tentativa local desta prova foi impedida pelo Docker Desktop, que nao
  iniciou novos containers; o gate GitHub Linux e obrigatorio neste incremento.
- O manifesto Stitch local valida 25 projetos isolados e telas obrigatorias
  para Jobs; a criacao remota requer credencial rotacionada por secret.

### Pendencias rastreadas

- Integracoes de pagamento/fiscal e validadores KYC/KYB/CTPS oficiais dependem
  de provedores homologados e segredos externos.
- Apps possuem contrato de integracao; interfaces finais entram nas entregas incrementais do roadmap.
- Testes de carga, seguranca dinamica e E2E com provedores serao bloqueadores antes de producao.
- O parser marca importacao documental sem declarar verificacao oficial
  externa enquanto nao existir integrador autorizado.
- Qualquer chave Stitch exposta fora de secret deve ser revogada antes da
  sincronizacao remota; nenhuma chave e persistida neste repositorio.

### Git

- Branch principal: `main`.
- Motor de dominio/Jobs mesclado no PR `#3` (`7edc49f`) e cofre CTPS com
  adapter PostgreSQL mesclado no PR `#4` (`6bdb01f`).
- Branches `monetization` e `module/*` exigidas foram publicadas no baseline `67c7ead`.
- `main` recebeu em seguida ajustes operacionais de trigger dos workflows para evitar execucoes redundantes ao criar branches.
