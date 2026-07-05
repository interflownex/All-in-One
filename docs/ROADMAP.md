# Roadmap

Plano operacional vivo: consulte `docs/EXECUTION_PLAN.md` para a ordem mandataria de execucao, percentuais por modulo, pendencias e criterios de beta.

## Entregue: motor de dominio 0.2.0

- Estrutura dos apps e de 25 dominios, incluindo Jobs.
- Runtimes FastAPI com store contratual, autorizacao, transicoes, auditoria e
  outbox.
- PostgreSQL/MongoDB, identidade, RBAC, wallet, escrow, auditoria e eventos.
- Curriculo, busca/publicacao de vagas, importacao PDF da CTPS com procedencia
  exibivel e consulta restrita a empresas Business ativas.
- Jobs com adapter PostgreSQL tipado e cofre CTPS AES-256-GCM para execucao
  configurada por DSN/chave secreta.
- Matriz completa de stores PostgreSQL validada em 25 modulos com
  create/get/list/update/soft_delete/idempotency condicional e audit/outbox em
  banco real local.
- Dispatcher RabbitMQ da outbox PostgreSQL com publisher confirms, retry
  auditavel e payload Jobs minimizado.
- Geracao de eventos reais de criacao e transicao do recurso primario
  validada em todos os modulos catalogados com o store compartilhado.
- Ponte do dispatcher verificada em eventos reais do Jobs e na matrix
  PostgreSQL, reforcando o envelope minimo antes da publicacao.
- Harness isolado do dispatcher validado sobre eventos reais do runtime em
  todo o catalogo de modulos, com fake broker para manter o teste
  reproduzivel no ambiente atual.
- Validacao real da outbox e do fluxo Jobs em compose local com PostgreSQL e
  RabbitMQ saudaveis.
- Ligacao entre os metrics Prometheus text do worker da outbox e o dashboard
  Grafana versionado validada em teste automatizado.
- Observabilidade comercial do Marketplace materializada com metricas
  Prometheus text, dashboard Grafana e serie historica de pedidos, suporte,
  reputacao e conversao.
- Orquestracao Google Stitch declarativa com um projeto visual por
  microservico e telas Jobs/Business/User especializadas.
- Docker, Kubernetes inicial, CI/CD e documentacao operacional.
- Jornada comercial Valley com oferta, compra, pagamento sandbox, historico e
  avaliacao pós-conclusao auditavel no Marketplace.
- Suporte/disputa por pedido e resumo comercial para CRM/BI em tempo de demo.

## Proximos incrementos bloqueadores para beta

1. Consolidar o dispatcher real e a observabilidade operacional com eventos de
   todos os dominios.
2. Integrar Identity/API Hub com OIDC, MFA, KMS, KYC/KYB e liveness aprovados.
3. Integrar verificador oficial autorizado para CTPS Digital, sem alterar a
   classificacao historica dos itens autodeclarados; storage privado cifrado
   ja esta implementado.
4. Integrar payment provider, fiscal brasileiro e conciliacao em sandbox.
5. Sincronizar os projetos Stitch com credencial rotacionada, implementar as
   jornadas web/mobile dos seis apps e testes E2E.
6. Expandir a moderacao basica das avaliacoes, suporte/disputa, notificacoes e
   observabilidade comercial.

## Bloqueadores para producao

1. Homologacao regulatoria, LGPD/DPIA, politicas de retencao e consentimento.
2. Pentest, carga, disaster recovery, backup/restore e resposta a incidente.
3. Homologacao de parceiros financeiros, fiscais, transporte e saude.
