"""Materializa microservicos e apps declarados em config/module_catalog.json.

Os artefatos gerados formam o baseline operacional. Edite o catalogo ou os
templates deste arquivo e execute novamente para manter os modulos alinhados.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from textwrap import dedent, indent


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "config" / "module_catalog.json"
DB_SCHEMA = {
    "riders": "delivery",
    "permissions": "permissions",
    "ai_core": "ai_core",
    "api_hub": "api_hub",
}
ENDPOINTS = [
    "GET /health",
    "GET /version",
    "GET /status",
    "GET /metrics",
    "GET /catalog",
    "POST /resources/{resource_type}",
    "GET /resources/{resource_type}",
    "GET /resources/{resource_type}/{resource_id}",
    "PATCH /resources/{resource_type}/{resource_id}",
    "DELETE /resources/{resource_type}/{resource_id}",
    "POST /resources/{resource_type}/{resource_id}/actions/{action}",
    "GET /audit/events",
    "GET /events/outbox",
    "POST /create",
    "GET /{id}",
    "PATCH /{id}",
    "DELETE /{id}",
    "GET /list",
    "POST /approve",
    "POST /reject",
    "POST /audit",
]
CUSTOMIZED_ARTIFACTS = {
    # Entrypoints com fluxos reais alem do baseline generico.
    "modules/identity/main.py",
    "modules/finance/main.py",
    "modules/api_hub/main.py",
    "modules/erp/main.py",
    "modules/services/main.py",
    "modules/marketplace/main.py",
    # Dockerfiles copiam o pacote completo do modulo para preservar imports locais.
    "modules/identity/Dockerfile",
    "modules/finance/Dockerfile",
    # Contratos/docs especializados mantidos manualmente apos refinamentos de dominio.
    "modules/finance/CONTRACT.md",
    "modules/finance/DATABASE.md",
    "modules/finance/EVENTS.md",
    "contracts/finance.md",
    "modules/api_hub/OPENAPI.yaml",
    "modules/marketplace/OPENAPI.yaml",
    # Apps com shells vivos possuem estado operacional proprio alem do scaffold.
    "modules/business/tests/test_create_flow.py",
    "modules/permissions/tests/test_create_flow.py",
    "apps/all-in-one-business/README.md",
    "apps/all-in-one-business/STATUS.md",
    "apps/all-in-one-health/README.md",
    "apps/all-in-one-health/STATUS.md",
    "apps/all-in-one-mobility/README.md",
    "apps/all-in-one-mobility/STATUS.md",
    "apps/all-in-one-riders/README.md",
    "apps/all-in-one-riders/STATUS.md",
    "apps/all-in-one-services/README.md",
    "apps/all-in-one-services/STATUS.md",
    "apps/all-in-one-user/STATUS.md",
    "apps/valley/README.md",
    "apps/valley/STATUS.md",
}


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def database_schema(slug: str) -> str:
    return DB_SCHEMA.get(slug, slug)


def render_main(slug: str) -> str:
    return dedent(
        f"""\
        from pathlib import Path
        import sys

        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

        from shared.runtime import create_module_app


        app = create_module_app("{slug}")
        """
    )


def render_readme(module: dict) -> str:
    entities = ", ".join(f"`{entity}`" for entity in module["entities"])
    rendered = dedent(
        f"""\
        # {module["title"]}

        {module["description"]}

        ## Responsabilidade

        Este microservico e isolado por dominio, mas toda criacao mantem `user_id`
        associado ao All-in-One ID. Operacoes mutaveis sao auditadas e exigem o
        cabecalho `X-Actor-User-Id`, salvo o autorregistro inicial em Identity.

        ## Entidades

        {entities}.

        ## Execucao

        ```bash
        pip install -r requirements.txt
        uvicorn main:app --host 0.0.0.0 --port 8000
        ```

        O contrato HTTP esta em `OPENAPI.yaml`; os controles especificos estao
        descritos em `CONTRACT.md` e `SECURITY.md`.
        """
    )
    if module["slug"] == "business":
        special = dedent(
            """\
            `catalog_offers` e o ponto canonico para PF, MEI ou PJ configurar
            produto ou servico que sera normalizado para o Marketplace e exibido
            no Valley quando a publicacao e os filtros publicos estiverem completos.
            """
        )
        rendered = rendered.replace(
            f"{entities}.\n\n## Execucao",
            f"{entities}.\n\n{special}\n## Execucao",
        )
    if module["slug"] == "document":
        special = dedent(
            """\
            `documents` exige `storage_provider`, `storage_bucket`,
            `storage_key`, `file_sha256`, `kms_key_version`, `filename` e
            `content_type`; `versions` registra novas revisoes append-only com
            hash, chave privada e versao KMS.
            """
        )
        rendered = rendered.replace(
            f"{entities}.\n\n## Execucao",
            f"{entities}.\n\n{special}\n## Execucao",
        )
    if module["slug"] == "bpm":
        special = dedent(
            """\
            `sla_policies` define prazos e papel de escalonamento; `tasks`
            registra `due_at`, responsavel, politica de SLA e transicoes
            auditaveis de conclusao/escalonamento.
            """
        )
        rendered = rendered.replace(
            f"{entities}.\n\n## Execucao",
            f"{entities}.\n\n{special}\n## Execucao",
        )
    if module["slug"] == "hr":
        special = dedent(
            """\
            `employees` registra admissao; `payroll_runs` fecha folha com
            aprovacao MFA; `courses` acompanha treinamento obrigatorio ate a
            conclusao auditavel.
            """
        )
        rendered = rendered.replace(
            f"{entities}.\n\n## Execucao",
            f"{entities}.\n\n{special}\n## Execucao",
        )
    if module["slug"] == "vision":
        special = dedent(
            """\
            `streams` guarda somente metadados privados e hash da URL;
            `recordings` preserva hash/storage append-only; `motion_alerts`
            registra deteccoes e incidentes auditaveis.
            """
        )
        rendered = rendered.replace(
            f"{entities}.\n\n## Execucao",
            f"{entities}.\n\n{special}\n## Execucao",
        )
    if module["slug"] == "legal":
        special = dedent(
            """\
            `cases` registra processo com tipo, abertura e risco; `deadlines`
            acompanha prazo processual, alerta com MFA e conclusao auditavel.
            """
        )
        rendered = rendered.replace(
            f"{entities}.\n\n## Execucao",
            f"{entities}.\n\n{special}\n## Execucao",
        )
    return rendered


def render_contract(module: dict) -> str:
    entities = "\n".join(f"- `{item}`" for item in module["entities"])
    events = "\n".join(f"- `{item}`" for item in module["events"])
    routes = "\n".join(f"- `{item}`" for item in ENDPOINTS)
    special = ""
    if module["slug"] == "identity":
        special = "\n- `POST /registrations` cria o All-in-One ID inicial sem ator preexistente e preserva controles de duplicidade.\n"
    if module["slug"] == "jobs":
        special += dedent(
            """

            ## Fluxo Jobs e procedencia

            - `POST /resumes/{resume_id}/imports/ctps-digital` recebe PDF da CTPS Digital, registra hash imutavel e classifica itens extraidos como `validated_by_document_import`.
            - `GET /resumes/{resume_id}/documents/{document_id}/content` descriptografa o PDF somente para o titular autenticado; recrutadores nao recebem o arquivo.
            - Experiencias digitadas em `employment_records` sao sempre `self_declared_unverified`, inclusive trabalho informal e descricoes adicionais.
            - `GET /vacancies` expõe vagas publicadas para candidatos.
            - `GET /recruiting/resumes/{resume_id}` exige empresa ativa no All-in-One Business, papel de recrutador, escopo Jobs e registra cada visualizacao.
            - Candidaturas suportam triagem (`review`), shortlist (`shortlist`) e entrevista agendada (`schedule_interview`) com eventos de outbox para notificacoes operacionais.
            - O importador documental nao equivale a verificacao oficial externa; esse estado permanece exibido em `official_verification_status`.
            - PDFs CTPS ficam cifrados em cofre privado AES-256-GCM; em producao a chave deve vir de vault/KMS.
            - `ALL_IN_ONE_JOBS_POSTGRES_DSN` habilita persistencia tipada em `jobs.*` com auditoria e outbox PostgreSQL.
            """
        )
    if module["slug"] == "business":
        special += dedent(
            """

            ## Publicacao Marketplace e Valley

            - `catalog_offers` exige `offer_type`, `consumer_category`, `company_type`, `company_category`, `business_activity_id`, `source_module` e `source_resource_type`.
            - O Valley so exibe ofertas com `publish_to_valley=true`, publicacao aprovada ou publicada e `visible_to_consumer` ativo.
            - Ofertas locais exigem regiao, coordenadas publicas de base e `service_radius_km`; enderecos sensiveis nunca entram no payload publico.
            - A transicao de publicacao emite `valley.catalog.offer.synced` com allowlist publica.

            ## Convites e memberships

            - `user_company_memberships` exige `company_id` e `role`.
            - A criacao representa convite operacional com status inicial `invited` e emite `business.user.invited`.
            - A acao `activate` exige papel aprovador, MFA e emite `business.role.assigned`.
            - A acao `revoke` exige papel aprovador, MFA e emite `business.user.revoked`.
            """
        )
    if module["slug"] == "delivery":
        special += dedent(
            """

            ## POD e antifraude

            - `proofs` exige `delivery_request_id`, `file_sha256`, `storage_key` e `captured_at`.
            - A criacao de POD registra `delivery.proof.recorded`.
            - POD e append-only/sensivel: nao aceita edicao livre nem exclusao logica pelo runtime generico.
            - Arquivos reais devem ficar em storage privado; o payload versionado guarda apenas hash, chave privada e sinais antifraude minimizados.
            """
        )
    if module["slug"] == "mobility":
        special += dedent(
            """

            ## ETA, NFC e tarifas

            - `routes` exige origem, destino, distancia, ETA e hash de rota para registrar `mobility.route.eta_quoted`.
            - `tickets` exige QR e NFC tokenizados; uso de ticket emite `mobility.ticket.used`.
            - `fare_rules` registra tarifas auditaveis append-only por tipo de veiculo e emite `mobility.fare_rule.published`.
            - ETA dinamico, NFC real e tarifas produtivas dependem de provider homologado; o runtime local guarda somente metadados e hashes operacionais.
            """
        )
    if module["slug"] == "document":
        special += dedent(
            """

            ## Cofre privado e versionamento

            - `documents` exige `storage_provider`, `storage_bucket`, `storage_key`, `file_sha256`, `kms_key_version`, `filename` e `content_type`.
            - `versions` registra revisoes append-only com `document_id`, `version`, `storage_key`, `file_sha256` e `kms_key_version`.
            - `storage_key` e `storage_bucket` devem apontar para cofre privado, sem URL publica.
            - Criacao de documento emite `document.uploaded`; nova versao emite `document.versioned`.
            """
        )
    if module["slug"] == "bpm":
        special += dedent(
            """

            ## Timers, SLA e escalonamento

            - `sla_policies` exige `policy_key`, `response_minutes` e `escalation_role`, com status inicial `active`.
            - `workflow_instances` exige `process_key`, `sla_policy_id` e `started_at`, iniciando em `running` e emitindo `bpm.process.started`.
            - `tasks` exige `workflow_instance_id`, `assignee_user_id`, `due_at` e `sla_policy_id`, iniciando em `open`.
            - A acao `escalate` move tarefas para `escalated`, exige papel aprovador, MFA e emite `bpm.task.escalated`.
            - A acao `complete` move tarefas abertas, em progresso ou escaladas para `completed` e emite `bpm.task.completed`.
            """
        )
    if module["slug"] == "hr":
        special += dedent(
            """

            ## Colaborador, folha e treinamento

            - `employees` exige `company_id`, `employment_type` e `admission_date`.
            - `payroll_runs` exige `company_id`, `period` e `gross_amount_brl`, inicia em `open` e emite `hr.payroll.opened`.
            - A acao `close` fecha folha com papel aprovador, MFA e evento `hr.payroll.closed`.
            - `courses` exige `employee_id`, `course_code`, `title` e `due_at`, inicia em `assigned` e emite `hr.training.assigned`.
            - A acao `complete` conclui treinamento e emite `hr.training.completed`.
            """
        )
    if module["slug"] == "vision":
        special += dedent(
            """

            ## Stream, gravacao e alerta operacional

            - `streams` exige `device_id`, `stream_url_hash`, `protocol` e `started_at`, iniciando em `active` e emitindo `vision.stream.started`.
            - `recordings` exige `stream_id`, `storage_key`, `file_sha256` e `started_at`, e e append-only com evento `vision.recording.stored`.
            - `motion_alerts` exige `device_id`, `stream_id`, `detected_at` e `confidence_score`, iniciando em `detected` e emitindo `vision.motion.detected`.
            - A acao `triage` exige papel aprovador, MFA e cria incidente com `vision.incident.created`.
            - A acao `resolve` exige papel aprovador, MFA e emite `vision.incident.resolved`.
            """
        )
    if module["slug"] == "legal":
        special += dedent(
            """

            ## Caso, prazo e alerta juridico

            - `cases` exige `case_number`, `case_type` e `opened_at`, preserva `risk_brl` como valor monetario auditavel e emite `legal.case.created`.
            - `deadlines` exige `case_id`, `deadline_type` e `due_at`, iniciando em `pending` e emitindo `legal.deadline.created`.
            - A acao `alert` move prazos para `alerted`, exige papel aprovador, MFA e emite `legal.deadline.alerted`.
            - A acao `complete` move prazos pendentes ou alertados para `completed` e emite `legal.deadline.completed`.
            - `hearings` exige `case_id` e `scheduled_at`, iniciando em `scheduled` e emitindo `legal.hearing.scheduled`.
            """
        )
    return dedent(
        f"""\
        # Contrato: {module["title"]}

        ## Descricao

        {module["description"]}

        ## Entidades

        {entities}

        ## APIs

        {routes}
        {special}

        ## Eventos

        {events}

        ## Regras

        - `user_id` e obrigatorio em todo recurso operacional e referencia `identity.users`.
        - Exclusao e logica; registros financeiros, de aprovacao e auditoria nao sao apagados.
        - Aprovacao e rejeicao exigem ator autenticado, justificativa e log imutavel.
        - A empresa ou profissional deve estar aprovado antes de uma operacao publica.

        ## Seguranca e permissoes

        Mutacoes dependem de OAuth2/JWT ou API key no gateway e do escopo do
        modulo. O runtime inicial representa o ator por `X-Actor-User-Id` e
        registra auditoria; o gateway deve validar a credencial antes do repasse.

        ## Monetizacao

        {module["monetization"]}

        ## Integracoes e erros

        Eventos sao entregues pelo barramento RabbitMQ. Respostas esperadas:
        `401` ator ausente, `404` recurso inexistente e `422` regra de validacao
        ou politica anti-burla violada.

        ## Auditoria

        `POST /audit` e todas as mutacoes geram evento destinado a `audit.logs`,
        que e append-only no PostgreSQL.
        """
    )


def render_additional_paths(slug: str) -> str:
    paths = dedent(
        """\
          /catalog:
            get:
              responses:
                '200':
                  description: Contracted domain resources
          /resources/{resource_type}:
            post:
              responses:
                '201':
                  description: Domain resource created
            get:
              responses:
                '200':
                  description: Authorized domain resource collection
          /resources/{resource_type}/{resource_id}:
            get:
              responses:
                '200':
                  description: Authorized domain resource
            patch:
              responses:
                '200':
                  description: Domain resource updated
            delete:
              responses:
                '204':
                  description: Domain resource soft-deleted
          /resources/{resource_type}/{resource_id}/actions/{action}:
            post:
              responses:
                '200':
                  description: Workflow transition recorded
          /audit/events:
            get:
              responses:
                '200':
                  description: Immutable audit evidence
          /events/outbox:
            get:
              responses:
                '200':
                  description: Transactional outbox domain events
        """
    )
    if slug == "identity":
        paths += dedent(
            """\
              /registrations:
                post:
                  security: []
                  responses:
                    '201':
                      description: All-in-One user registration pending validation
            """
        )
    if slug == "jobs":
        paths += dedent(
            """\
              /resumes/{resume_id}/imports/ctps-digital:
                post:
                  requestBody:
                    required: true
                    content:
                      application/pdf:
                        schema:
                          type: string
                          format: binary
                  responses:
                    '201':
                      description: CTPS Digital PDF evidence imported
              /resumes/{resume_id}/complete:
                get:
                  responses:
                    '200':
                      description: Candidate resume grouped by provenance
              /resumes/{resume_id}/documents/{document_id}/content:
                get:
                  responses:
                    '200':
                      description: Candidate-owned encrypted CTPS document content
              /vacancies:
                get:
                  security: []
                  responses:
                    '200':
                      description: Published vacancies
              /recruiting/resumes:
                get:
                  responses:
                    '200':
                      description: Business-authorized candidate search
              /recruiting/resumes/{resume_id}:
                get:
                  responses:
                    '200':
                      description: Audited Business recruiter resume view
            """
        )
    return indent(paths, "  ")


def render_openapi(module: dict) -> str:
    slug = module["slug"]
    title = module["title"].replace('"', "")
    document = dedent(
        f"""\
        openapi: 3.1.0
        info:
          title: All-in-One {title} API
          version: 0.2.0
        servers:
          - url: /api/v1/{slug}
        security:
          - bearerAuth: []
        paths:
          /health:
            get:
              security: []
              responses:
                '200':
                  description: Healthy
          /version:
            get:
              security: []
              responses:
                '200':
                  description: Version information
          /status:
            get:
              responses:
                '200':
                  description: Operational status
          /metrics:
            get:
              responses:
                '200':
                  description: Prometheus metrics
          /create:
            post:
              parameters:
                - $ref: '#/components/parameters/ActorUserId'
              requestBody:
                required: true
                content:
                  application/json:
                    schema:
                      $ref: '#/components/schemas/CreatePayload'
              responses:
                '201':
                  description: Resource created
          /list:
            get:
              responses:
                '200':
                  description: Resource collection
          /{{id}}:
            get:
              parameters:
                - $ref: '#/components/parameters/ResourceId'
              responses:
                '200':
                  description: Resource detail
            patch:
              parameters:
                - $ref: '#/components/parameters/ResourceId'
                - $ref: '#/components/parameters/ActorUserId'
              responses:
                '200':
                  description: Resource updated
            delete:
              parameters:
                - $ref: '#/components/parameters/ResourceId'
                - $ref: '#/components/parameters/ActorUserId'
              responses:
                '204':
                  description: Resource soft-deleted
          /approve:
            post:
              parameters:
                - $ref: '#/components/parameters/ActorUserId'
              requestBody:
                required: true
                content:
                  application/json:
                    schema:
                      $ref: '#/components/schemas/DecisionPayload'
              responses:
                '200':
                  description: Resource approved
          /reject:
            post:
              parameters:
                - $ref: '#/components/parameters/ActorUserId'
              requestBody:
                required: true
                content:
                  application/json:
                    schema:
                      $ref: '#/components/schemas/DecisionPayload'
              responses:
                '200':
                  description: Resource rejected
          /audit:
            post:
              parameters:
                - $ref: '#/components/parameters/ActorUserId'
              requestBody:
                required: true
                content:
                  application/json:
                    schema:
                      $ref: '#/components/schemas/AuditPayload'
              responses:
                '201':
                  description: Audit evidence accepted
        components:
          securitySchemes:
            bearerAuth:
              type: http
              scheme: bearer
              bearerFormat: JWT
          parameters:
            ResourceId:
              name: id
              in: path
              required: true
              schema:
                type: string
                format: uuid
            ActorUserId:
              name: X-Actor-User-Id
              in: header
              required: true
              schema:
                type: string
                format: uuid
          schemas:
            CreatePayload:
              type: object
              required: [user_id]
              properties:
                user_id:
                  type: string
                  format: uuid
                entity_id:
                  type: string
                  format: uuid
                status:
                  type: string
                payload:
                  type: object
                  additionalProperties: true
            DecisionPayload:
              type: object
              required: [id, reason]
              properties:
                id:
                  type: string
                  format: uuid
                reason:
                  type: string
                  minLength: 3
            AuditPayload:
              type: object
              required: [action, resource_type, resource_id]
              properties:
                action:
                  type: string
                resource_type:
                  type: string
                resource_id:
                  type: string
                  format: uuid
                payload:
                  type: object
                  additionalProperties: true
        """
    )
    return document.replace("components:\n", f"{render_additional_paths(slug)}components:\n")


def render_database(module: dict) -> str:
    schema = database_schema(module["slug"])
    entities = "\n".join(f"- `{schema}.{name}`" for name in module["entities"])
    return dedent(
        f"""\
        # Database: {module["title"]}

        Schema relacional principal: `{schema}`.

        ## Entidades planejadas

        {entities}

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
        """
    )


def render_events(module: dict) -> str:
    events = "\n".join(f"- `{item}`" for item in module["events"])
    return dedent(
        f"""\
        # Events: {module["title"]}

        Exchange: `all-in-one.domain`; routing keys:

        {events}

        Eventos carregam `event_id`, `occurred_at`, `actor_user_id`, `user_id`,
        `entity_id`, `correlation_id`, `schema_version` e payload minimizado.
        Consumidores devem ser idempotentes.
        """
    )


def render_security(module: dict) -> str:
    if module["slug"] == "jobs":
        extra = "PDFs CTPS sao cifrados em storage privado; somente o titular recupera o arquivo e cada leitura gera auditoria."
    elif module["slug"] in {"marketplace", "delivery", "services", "mobility"}:
        extra = "Conteudos de texto, links e anexos passam por bloqueio anti-burla e moderacao."
    else:
        extra = "Dados sensiveis devem ser criptografados e expostos somente por escopo autorizado."
    return dedent(
        f"""\
        # Security: {module["title"]}

        - OAuth2/JWT ou API key com escopo de modulo no API Hub.
        - MFA para aprovacoes, pagamentos e leitura de dados sensiveis.
        - RBAC/ABAC, device fingerprint, rate limit e auditoria imutavel.
        - Segredos apenas via vault ou variaveis de ambiente.
        - Retencao, consentimento e anonimizacao em conformidade com LGPD.
        - {extra}
        """
    )


def render_monetization(module: dict) -> str:
    return f"# Monetization: {module['title']}\n\n{module['monetization']}\n\nToda cobranca gera ledger, split e conciliacao auditaveis quando aplicavel.\n"


def render_status(module: dict) -> str:
    return dedent(
        f"""\
        # Status: {module["title"]}

        - Estado: `domain_engine_active`
        - Runtime: FastAPI com persistencia SQLite contratual, autorizacao, auditoria e outbox
        - Contrato: publicado localmente em `OPENAPI.yaml` e `CONTRACT.md`
        - Persistencia: schema e tabelas iniciais cobertos por migracoes
        - Proximo incremento: integracoes externas homologadas e E2E produtivo
        """
    )


def render_tests_md(module: dict) -> str:
    return dedent(
        f"""\
        # Tests: {module["title"]}

        O baseline executa testes de saude, contrato documental, autorizacao de
        mutacoes e fluxo create/read/approve. Integracoes externas, carga e E2E
        completo permanecem gates de evolucao antes da operacao produtiva.
        """
    )


def render_dockerfile() -> str:
    return dedent(
        """\
        FROM python:3.12-slim
        WORKDIR /app
        COPY modules/shared /app/shared
        COPY modules/__MODULE__/requirements.txt /app/requirements.txt
        RUN pip install --no-cache-dir -r requirements.txt
        COPY modules/__MODULE__/main.py /app/main.py
        EXPOSE 8000
        CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
        """
    )


def render_requirements(slug: str) -> str:
    shared = "fastapi==0.136.1\nstarlette==1.3.1\nuvicorn[standard]==0.34.2\npsycopg[binary]==3.3.4\n"
    if slug == "identity":
        return (
            "fastapi==0.136.1\n"
            "starlette==1.3.1\n"
            "uvicorn[standard]==0.34.2\n"
            "PyJWT==2.13.0\n"
            "passlib[argon2]==1.7.4\n"
            "psycopg[binary]==3.3.4\n"
            "motor==3.7.0\n"
            "pymongo==4.11.1\n"
        )
    if slug == "jobs":
        return (
            "cryptography==48.0.1\n"
            "fastapi==0.136.1\n"
            "pypdf==6.13.3\n"
            "psycopg[binary]==3.3.4\n"
            "starlette==1.3.1\n"
            "uvicorn[standard]==0.34.2\n"
        )
    if slug == "api_hub":
        return (
            "fastapi==0.136.1\n"
            "starlette==1.3.1\n"
            "uvicorn[standard]==0.34.2\n"
            "httpx==0.28.1\n"
            "redis==5.2.1\n"
            "PyJWT==2.13.0\n"
            "psycopg[binary]==3.3.4\n"
            "tenacity==9.0.0\n"
        )
    if slug == "finance":
        return "fastapi==0.136.1\npsycopg[binary]==3.3.4\nstarlette==1.3.1\nuvicorn[standard]==0.34.2\n"
    return shared


def render_test_health(slug: str) -> str:
    return dedent(
        f"""\
        from platform_test_support import client_for


        def test_health():
            response = client_for("{slug}").get("/health")
            assert response.status_code == 200
            assert response.json()["module"] == "{slug}"
        """
    )


def render_test_contract(slug: str) -> str:
    return dedent(
        f"""\
        from pathlib import Path


        def test_required_contract_documents_exist():
            module = Path(__file__).parents[1]
            for name in ["CONTRACT.md", "OPENAPI.yaml", "DATABASE.md", "EVENTS.md", "SECURITY.md", "MONETIZATION.md"]:
                assert (module / name).is_file(), f"{{name}} ausente em {slug}"
        """
    )


def render_test_permissions(slug: str) -> str:
    return dedent(
        f"""\
        from uuid import uuid4

        from platform_test_support import client_for


        def test_create_auth_boundary():
            response = client_for("{slug}").post("/create", json={{"user_id": str(uuid4()), "payload": {{}}}})
            assert response.status_code == 401
        """
    )


def render_test_create(slug: str) -> str:
    return dedent(
        f"""\
        from uuid import uuid4

        from platform_test_support import client_for


        def test_create_and_approve_flow():
            client = client_for("{slug}")
            actor = str(uuid4())
            headers = {{"X-Actor-User-Id": actor}}
            created = client.post("/create", headers=headers, json={{"user_id": actor, "payload": {{"source": "test"}}}})
            assert created.status_code == 201
            resource_id = created.json()["id"]
            approved = client.post("/approve", headers=headers, json={{"id": resource_id, "reason": "validated in test"}})
            assert approved.status_code == 200
            assert approved.json()["status"] == "approved"
        """
    )


def render_app_readme(app: dict) -> str:
    return dedent(
        f"""\
        # {app["slug"]}

        {app["scope"]}

        Esta aplicacao consumira o API Hub com o mesmo All-in-One ID. O baseline
        fixa as responsabilidades e contratos; a interface e a jornada visual
        serao implementadas sobre os endpoints versionados dos modulos.
        """
    )


def render_app_status() -> str:
    return "# Status\n\n- Estado: `contract_defined`\n- Dependencia: API Hub e Identity baseline ativos.\n- Pendente: implementacao de interface e testes de jornada.\n"


def expected_files(catalog: dict) -> dict[Path, str]:
    outputs: dict[Path, str] = {}
    for module in catalog["modules"]:
        slug = module["slug"]
        base = ROOT / "modules" / slug
        outputs.update(
            {
                base / "README.md": render_readme(module),
                base / "main.py": render_main(slug),
                base / "requirements.txt": render_requirements(slug),
                base / "CONTRACT.md": render_contract(module),
                base / "STATUS.md": render_status(module),
                base / "OPENAPI.yaml": render_openapi(module),
                base / "DATABASE.md": render_database(module),
                base / "EVENTS.md": render_events(module),
                base / "SECURITY.md": render_security(module),
                base / "MONETIZATION.md": render_monetization(module),
                base / "TESTS.md": render_tests_md(module),
                base / "Dockerfile": render_dockerfile().replace("__MODULE__", slug),
                base / "tests" / "__init__.py": "",
                base / "tests" / "test_health.py": render_test_health(slug),
                base / "tests" / "test_contract.py": render_test_contract(slug),
                base / "tests" / "test_permissions.py": render_test_permissions(slug),
                base / "tests" / "test_create_flow.py": render_test_create(slug),
                ROOT / "contracts" / f"{slug}.md": render_contract(module),
            }
        )
    for app in catalog["apps"]:
        base = ROOT / "apps" / app["slug"]
        outputs[base / "README.md"] = render_app_readme(app)
        outputs[base / "STATUS.md"] = render_app_status()
    for relative_path in CUSTOMIZED_ARTIFACTS:
        outputs.pop(ROOT / relative_path, None)
    return outputs


def customized_artifact_paths() -> list[Path]:
    return sorted(ROOT / relative_path for relative_path in CUSTOMIZED_ARTIFACTS)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Falha se os artefatos estiverem dessincronizados.")
    args = parser.parse_args()
    outputs = expected_files(load_catalog())
    stale: list[str] = []
    missing_customized: list[str] = []
    for path, content in outputs.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(str(path.relative_to(ROOT)))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    if args.check:
        for path in customized_artifact_paths():
            if not path.exists():
                missing_customized.append(str(path.relative_to(ROOT)))
    if stale:
        print("Artefatos dessincronizados:")
        for path in stale:
            print(f"- {path}")
        return 1
    if missing_customized:
        print("Artefatos customizados ausentes:")
        for path in missing_customized:
            print(f"- {path}")
        return 1
    print(f"{len(outputs)} artefatos {'verificados' if args.check else 'gerados'} a partir do catalogo.")
    if args.check:
        print(f"{len(CUSTOMIZED_ARTIFACTS)} artefatos customizados preservados fora do scaffold generico:")
        for path in customized_artifact_paths():
            print(f"- {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
