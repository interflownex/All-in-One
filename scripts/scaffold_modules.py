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
    return dedent(
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


def render_contract(module: dict) -> str:
    entities = "\n".join(f"- `{item}`" for item in module["entities"])
    events = "\n".join(f"- `{item}`" for item in module["events"])
    routes = "\n".join(f"- `{item}`" for item in ENDPOINTS)
    special = ""
    if module["slug"] == "identity":
        special = "\n- `POST /registrations` cria o All-in-One ID inicial sem ator preexistente e preserva controles de duplicidade.\n"
    if module["slug"] == "jobs":
        special = dedent(
            """

            ## Fluxo Jobs e procedencia

            - `POST /resumes/{resume_id}/imports/ctps-digital` recebe PDF da CTPS Digital, registra hash imutavel e classifica itens extraidos como `validated_by_document_import`.
            - `GET /resumes/{resume_id}/documents/{document_id}/content` descriptografa o PDF somente para o titular autenticado; recrutadores nao recebem o arquivo.
            - Experiencias digitadas em `employment_records` sao sempre `self_declared_unverified`, inclusive trabalho informal e descricoes adicionais.
            - `GET /vacancies` expõe vagas publicadas para candidatos.
            - `GET /recruiting/resumes/{resume_id}` exige empresa ativa no All-in-One Business, papel de recrutador, escopo Jobs e registra cada visualizacao.
            - O importador documental nao equivale a verificacao oficial externa; esse estado permanece exibido em `official_verification_status`.
            - PDFs CTPS ficam cifrados em cofre privado AES-256-GCM; em producao a chave deve vir de vault/KMS.
            - `ALL_IN_ONE_JOBS_POSTGRES_DSN` habilita persistencia tipada em `jobs.*` com auditoria e outbox PostgreSQL.
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
                base / "requirements.txt": (
                    "cryptography==48.0.0\nfastapi==0.136.1\npypdf==6.12.1\npsycopg[binary]==3.3.4\nstarlette==1.0.1\nuvicorn[standard]==0.34.2\n"
                    if slug == "jobs"
                    else "fastapi==0.136.1\nstarlette==1.0.1\nuvicorn[standard]==0.34.2\n"
                ),
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
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Falha se os artefatos estiverem dessincronizados.")
    args = parser.parse_args()
    outputs = expected_files(load_catalog())
    stale: list[str] = []
    for path, content in outputs.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(str(path.relative_to(ROOT)))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    if stale:
        print("Artefatos dessincronizados:")
        for path in stale:
            print(f"- {path}")
        return 1
    print(f"{len(outputs)} artefatos {'verificados' if args.check else 'gerados'} a partir do catalogo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
