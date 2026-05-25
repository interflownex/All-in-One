# Roadmap

## Entregue: motor de dominio 0.2.0

- Estrutura dos apps e de 25 dominios, incluindo Jobs.
- Runtimes FastAPI com store contratual, autorizacao, transicoes, auditoria e
  outbox.
- PostgreSQL/MongoDB, identidade, RBAC, wallet, escrow, auditoria e eventos.
- Curriculo, busca/publicacao de vagas, importacao PDF da CTPS com procedencia
  exibivel e consulta restrita a empresas Business ativas.
- Docker, Kubernetes inicial, CI/CD e documentacao operacional.

## Proximos incrementos bloqueadores para beta

1. Vincular os adapters produtivos dos endpoints aos schemas PostgreSQL e ao
   barramento RabbitMQ; o store SQLite atual executa o contrato local.
2. Integrar Identity/API Hub com OIDC, MFA, KMS, KYC/KYB e liveness aprovados.
3. Conectar storage privado e verificador autorizado para CTPS Digital, sem
   alterar a classificacao historica dos itens autodeclarados.
4. Integrar payment provider, fiscal brasileiro e conciliacao em sandbox.
5. Implementar jornadas web/mobile dos seis apps e testes E2E.
6. Entregar moderacao OCR/IA, notificacoes e observabilidade.

## Bloqueadores para producao

1. Homologacao regulatoria, LGPD/DPIA, politicas de retencao e consentimento.
2. Pentest, carga, disaster recovery, backup/restore e resposta a incidente.
3. Homologacao de parceiros financeiros, fiscais, transporte e saude.
