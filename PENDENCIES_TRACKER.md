# Mapa de Pendências - All-in-One

Este arquivo rastreia as pendências identificadas na auditoria de 12 de agosto de 2026.

## P0 - Prioridade Imediata

---

### GOV-01: Separação público/privado
- **id**: GOV-01
- **titulo**: Separação público e privado
- **prioridade**: P0
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: Acesso ao repositório `interflownex/all-in-one-core-private` pendente.
- **dependencias**: []
- **repositorio_destino**: publico
- **evidencia**: a_definir
- **criterio_de_aceite**: Nenhum artefato privado no repositório público; pushes testados por destino.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13

---

### MOB-01: Chave de assinatura Android
- **id**: MOB-01
- **titulo**: Chave de assinatura Android
- **prioridade**: P0
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: Localização exata da keystore e definição de cofre seguro.
- **dependencias**: []
- **repositorio_destino**: nenhum
- **evidencia**: a_definir
- **criterio_de_aceite**: Restauração da chave testada e procedimento documentado.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13

---

### SEC-01: Segredos e acessos
- **id**: SEC-01
- **titulo**: Segredos e acessos
- **prioridade**: P0
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: Acesso a um cofre de segredos (vault).
- **dependencias**: []
- **repositorio_destino**: nenhum
- **evidencia**: a_definir
- **criterio_de_aceite**: Zero segredo no Git e acessos auditáveis.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13

---

### GIT-01: Fila GitHub
- **id**: GIT-01
- **titulo**: Fila GitHub
- **prioridade**: P0
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: Ferramenta para interagir com a API do GitHub para listar e gerenciar issues/PRs.
- **dependencias**: []
- **repositorio_destino**: publico
- **evidencia**: a_definir
- **criterio_de_aceite**: 100% da fila com dono, prioridade e decisão.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13

---

## P1 - Bloqueadores de Homologação

---

### ENV-01: Ambiente de homologação
- **id**: ENV-01
- **titulo**: Ambiente de homologação
- **prioridade**: P1
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: null
- **dependencias**: ["GOV-01", "SEC-01"]
- **repositorio_destino**: privado
- **evidencia**: a_definir
- **criterio_de_aceite**: Deploy verde, URLs estáveis e smoke E2E aprovado.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13

---

### CLD-01: Cloudflare e publicação web
- **id**: CLD-01
- **titulo**: Cloudflare e publicação web
- **prioridade**: P1
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: Token de acesso, Account ID e aceite jurídico do titular da conta Cloudflare.
- **dependencias**: ["SEC-01", "ENV-01"]
- **repositorio_destino**: privado
- **evidencia**: a_definir
- **criterio_de_aceite**: Pages publicado e rotas auditadas contra API real.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13

---

### API-01: API Hub externo
- **id**: API-01
- **titulo**: API Hub externo
- **prioridade**: P1
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: null
- **dependencias**: ["ENV-01"]
- **repositorio_destino**: privado
- **evidencia**: a_definir
- **criterio_de_aceite**: Jornadas externas aprovadas nos 25 microserviços.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13

---

### AUT-01: Firebase/Google OAuth
- **id**: AUT-01
- **titulo**: Firebase/Google OAuth
- **prioridade**: P1
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: Conta de teste controlada.
- **dependencias**: ["ENV-01"]
- **repositorio_destino**: privado
- **evidencia**: a_definir
- **criterio_de_aceite**: Login, renovação, logout e negativa aprovados.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13

---

### GCP-01: GCP/Apigee/IAM/billing
- **id**: GCP-01
- **titulo**: GCP/Apigee/IAM/billing
- **prioridade**: P1
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: Acesso à conta GCP com billing ativo.
- **dependencias**: ["SEC-01"]
- **repositorio_destino**: privado
- **evidencia**: a_definir
- **criterio_de_aceite**: Status remoto verde sem privilégios excessivos.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13

---

### STC-01: Stitch remoto
- **id**: STC-01
- **titulo**: Stitch remoto
- **prioridade**: P1
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: Credencial de acesso ao Stitch.
- **dependencias**: ["SEC-01"]
- **repositorio_destino**: privado
- **evidencia**: a_definir
- **criterio_de_aceite**: Cobertura esperada sem tela remota pendente.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13

---

### DAT-01: PostgreSQL/Mongo/storage reais
- **id**: DAT-01
- **titulo**: PostgreSQL/Mongo/storage reais
- **prioridade**: P1
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: null
- **dependencias**: ["ENV-01"]
- **repositorio_destino**: privado
- **evidencia**: a_definir
- **criterio_de_aceite**: Todos os adapters críticos aprovados em banco vivo.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13

---

### INT-01: Providers regulados
- **id**: INT-01
- **titulo**: Providers regulados
- **prioridade**: P1
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: Contratos e acesso a sandbox de providers.
- **dependencias**: ["ENV-01"]
- **repositorio_destino**: privado
- **evidencia**: a_definir
- **criterio_de_aceite**: Cada provider possui adapter, contrato e fallback seguro.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13

---

### SEC-02: DAST, pentest e permissões
- **id**: SEC-02
- **titulo**: DAST, pentest e permissões
- **prioridade**: P1
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: Ferramentas e autorização para testes de segurança ofensivos.
- **dependencias**: ["ENV-01"]
- **repositorio_destino**: privado
- **evidencia**: a_definir
- **criterio_de_aceite**: Sem achado crítico aberto e relatório de remediação.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13

---

### OPS-02: Backup, restore e DR
- **id**: OPS-02
- **titulo**: Backup, restore e DR
- **prioridade**: P1
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: null
- **dependencias**: ["DAT-01"]
- **repositorio_destino**: privado
- **evidencia**: a_definir
- **criterio_de_aceite**: PostgreSQL, Mongo e storage restaurados dentro da meta.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13

---

## P2 - Produção Confiável e Escalável

---

### OPS-01: Observabilidade e SLOs
- **id**: OPS-01
- **titulo**: Observabilidade e SLOs
- **prioridade**: P2
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: null
- **dependencias**: ["ENV-01"]
- **repositorio_destino**: privado
- **evidencia**: a_definir
- **criterio_de_aceite**: Alertas reais, SLOs medidos e on-call acionável.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13

---

### OPS-03: Incidentes e carga
- **id**: OPS-03
- **titulo**: Incidentes e carga
- **prioridade**: P2
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: null
- **dependencias**: ["ENV-01"]
- **repositorio_destino**: privado
- **evidencia**: a_definir
- **criterio_de_aceite**: Evidências, limites e decisões de capacidade registradas.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13

---

### APP-01: Apps fora da trilha Valley
- **id**: APP-01
- **titulo**: Apps fora da trilha Valley
- **prioridade**: P2
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: null
- **dependencias**: ["API-01"]
- **repositorio_destino**: publico
- **evidencia**: a_definir
- **criterio_de_aceite**: Jornadas prioritárias sem mocks críticos.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13

---

### DOM-01: Logística e operação física
- **id**: DOM-01
- **titulo**: Logística e operação física
- **prioridade**: P2
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: null
- **dependencias**: ["API-01", "INT-01"]
- **repositorio_destino**: privado
- **evidencia**: a_definir
- **criterio_de_aceite**: Jornada física controlada de ponta a ponta.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13

---

### DOM-02: IA, BI e Vision
- **id**: DOM-02
- **titulo**: IA, BI e Vision
- **prioridade**: P2
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: Acesso a providers, datasets e streams reais.
- **dependencias**: ["ENV-01"]
- **repositorio_destino**: privado
- **evidencia**: a_definir
- **criterio_de_aceite**: Qualidade, custo, privacidade e alertas medidos.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13

---

### DOM-03: Fiscal, Health, Legal e Property
- **id**: DOM-03
- **titulo**: Fiscal, Health, Legal e Property
- **prioridade**: P2
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: Homologação regulatória.
- **dependencias**: ["INT-01"]
- **repositorio_destino**: privado
- **evidencia**: a_definir
- **criterio_de_aceite**: Pareceres, consentimentos e integrações aprovados.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13

---

## P3 - Evolução Funcional

---

### COM-01: Go-to-market e custos
- **id**: COM-01
- **titulo**: Go-to-market e custos
- **prioridade**: P3
- **responsavel**: a_definir
- **status**: nao_iniciado
- **bloqueador**: null
- **dependencias**: []
- **repositorio_destino**: nenhum
- **evidencia**: a_definir
- **criterio_de_aceite**: Backlog comercial com margem, custo e dono.
- **prazo**: a_definir
- **ultima_revisao**: 2026-08-13
