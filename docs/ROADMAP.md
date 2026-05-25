# Roadmap

## Entregue: motor de dominio 0.2.0

- Estrutura dos apps e de 25 dominios, incluindo Jobs.
- Runtimes FastAPI com store contratual, autorizacao, transicoes, auditoria e
  outbox.
- PostgreSQL/MongoDB, identidade, RBAC, wallet, escrow, auditoria e eventos.
- Curriculo, busca/publicacao de vagas, importacao PDF da CTPS com procedencia
  exibivel e consulta restrita a empresas Business ativas.
- Jobs com adapter PostgreSQL tipado e cofre CTPS AES-256-GCM para execucao
  configurada por DSN/chave secreta.
- Dispatcher RabbitMQ da outbox PostgreSQL com publisher confirms, retry
  auditavel e payload Jobs minimizado.
- Orquestracao Google Stitch declarativa com um projeto visual por
  microservico e telas Jobs/Business/User especializadas.
- Docker, Kubernetes inicial, CI/CD e documentacao operacional.

## Proximos incrementos bloqueadores para beta

1. Expandir o adapter PostgreSQL ja implementado para Jobs aos demais dominios;
   a publicacao da outbox no RabbitMQ ja esta implementada.
2. Integrar Identity/API Hub com OIDC, MFA, KMS, KYC/KYB e liveness aprovados.
3. Integrar verificador oficial autorizado para CTPS Digital, sem alterar a
   classificacao historica dos itens autodeclarados; storage privado cifrado
   ja esta implementado.
4. Integrar payment provider, fiscal brasileiro e conciliacao em sandbox.
5. Sincronizar os projetos Stitch com credencial rotacionada, implementar as
   jornadas web/mobile dos seis apps e testes E2E.
6. Entregar moderacao OCR/IA, notificacoes e observabilidade.

## Bloqueadores para producao

1. Homologacao regulatoria, LGPD/DPIA, politicas de retencao e consentimento.
2. Pentest, carga, disaster recovery, backup/restore e resposta a incidente.
3. Homologacao de parceiros financeiros, fiscais, transporte e saude.
