from uuid import uuid4

from fastapi.testclient import TestClient

from modules.dynamic_forms.main import app, get_store


class FakeStore:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple, dict]] = []

    def _call(self, operation: str, *args, **kwargs):
        self.calls.append((operation, args, kwargs))
        return {
            "operation": operation,
            "tenant_id": kwargs.get("tenant_id") or (args[0] if args else None),
        }

    def list_catalog(self, domain=None):
        self.calls.append(("list_catalog", (domain,), {}))
        return [{"id": "catalog-1", "domain": domain or "business"}]

    def list_definitions(self, tenant_id, status=None):
        self.calls.append(("list_definitions", (tenant_id,), {"status": status}))
        return [{"id": "definition-1", "tenant_id": tenant_id}]

    def list_bindings(self, catalog_ids):
        self.calls.append(("list_bindings", (catalog_ids,), {}))
        return [{"id": "binding-1", "field_catalog_id": catalog_ids[0]}]

    def get_blueprint(self, tenant_id, version_id):
        return self._call("get_blueprint", tenant_id, version_id)

    def create_definition(self, **kwargs):
        return self._call("create_definition", **kwargs)

    def replace_blueprint(self, *args):
        return self._call("replace_blueprint", *args)

    def request_homologation(self, *args):
        return self._call("request_homologation", *args)

    def review_homologation(self, *args):
        return self._call("review_homologation", *args)

    def publish_version(self, *args):
        return self._call("publish_version", *args)

    def submit_form(self, *args):
        return self._call("submit_form", *args)


fake_store = FakeStore()
app.dependency_overrides[get_store] = lambda: fake_store
client = TestClient(app)


ACTOR_ID = str(uuid4())
TENANT_ID = str(uuid4())


def headers(
    *, roles: str, scopes: str, mfa: bool = False, tenant_id: str = TENANT_ID
) -> dict[str, str]:
    return {
        "X-Actor-User-Id": ACTOR_ID,
        "X-Actor-Roles": roles,
        "X-Actor-Scopes": scopes,
        "X-MFA-Verified": str(mfa).lower(),
        "X-Business-Id": TENANT_ID,
        "X-Business-Status": "active",
        "X-Tenant-Id": tenant_id,
    }


def test_api_exige_ator_e_tenant() -> None:
    assert client.get("/catalog").status_code == 401
    response = client.get("/catalog", headers={"X-Tenant-Id": TENANT_ID})
    assert response.status_code == 401


def test_api_rejeita_tenant_divergente_do_contexto_empresarial() -> None:
    response = client.get(
        "/catalog",
        headers=headers(
            roles="form_designer", scopes="forms:read", tenant_id=str(uuid4())
        ),
    )
    assert response.status_code == 403
    assert "Tenant" in response.json()["detail"]


def test_catalogo_exige_role_e_escopo() -> None:
    denied_role = client.get(
        "/catalog", headers=headers(roles="viewer", scopes="forms:read")
    )
    assert denied_role.status_code == 403
    denied_scope = client.get(
        "/catalog", headers=headers(roles="form_designer", scopes="")
    )
    assert denied_scope.status_code == 403
    allowed = client.get(
        "/catalog?domain=business",
        headers=headers(roles="form_designer", scopes="forms:read"),
    )
    assert allowed.status_code == 200
    assert allowed.json()[0]["domain"] == "business"


def test_bindings_sao_consultados_apenas_por_ids_de_catalogo() -> None:
    catalog_id = uuid4()
    response = client.get(
        f"/catalog/bindings?catalog_ids={catalog_id}",
        headers=headers(roles="form_designer", scopes="forms:read"),
    )
    assert response.status_code == 200
    assert response.json()[0]["field_catalog_id"] == str(catalog_id)


def test_criacao_exige_idempotencia_e_encaminha_tenant_autoritativo() -> None:
    body = {
        "module_id": "business",
        "business_context": "company.onboarding",
        "name": "Cadastro empresarial",
        "change_summary": "Versao inicial",
    }
    missing = client.post(
        "/definitions",
        json=body,
        headers=headers(roles="form_designer", scopes="forms:write"),
    )
    assert missing.status_code == 422
    allowed_headers = headers(roles="form_designer", scopes="forms:write") | {
        "X-Idempotency-Key": "definition-request-1"
    }
    response = client.post("/definitions", json=body, headers=allowed_headers)
    assert response.status_code == 201
    assert response.json()["tenant_id"] == TENANT_ID
    assert fake_store.calls[-1][2]["actor_user_id"] == ACTOR_ID


def test_blueprint_tem_limites_pydantic_antes_do_store() -> None:
    response = client.put(
        f"/versions/{uuid4()}/blueprint",
        json={"blocks": [], "fields": []},
        headers=headers(roles="form_designer", scopes="forms:write"),
    )
    assert response.status_code == 422


def test_homologacao_exige_mfa() -> None:
    request_headers = headers(roles="form_reviewer", scopes="forms:review") | {
        "X-Idempotency-Key": "review-request-1"
    }
    response = client.post(
        f"/homologations/{uuid4()}/review",
        json={"result": "approved", "evidence": {"testes": "aprovados"}},
        headers=request_headers,
    )
    assert response.status_code == 403
    assert "MFA" in response.json()["detail"]


def test_publicacao_exige_role_escopo_mfa_e_idempotencia() -> None:
    version_id = uuid4()
    body = {
        "environment": "production",
        "tenant_scope": {"tenant_id": TENANT_ID},
        "channels": ["web", "mobile"],
    }
    publish_headers = headers(
        roles="form_publisher", scopes="forms:publish", mfa=True
    ) | {"X-Idempotency-Key": "publish-request-1"}
    response = client.post(
        f"/versions/{version_id}/publish", json=body, headers=publish_headers
    )
    assert response.status_code == 201
    assert response.json()["operation"] == "publish_version"
    assert fake_store.calls[-1][1][0] == TENANT_ID


def test_usuario_pode_submeter_somente_com_escopo_e_idempotencia() -> None:
    definition_id = uuid4()
    submit_headers = headers(roles="form_user", scopes="forms:submit") | {
        "X-Idempotency-Key": "submission-request-1"
    }
    response = client.post(
        f"/forms/{definition_id}/submissions",
        json={"values": {str(uuid4()): "valor"}, "source": "mobile"},
        headers=submit_headers,
    )
    assert response.status_code == 201
    assert response.json()["operation"] == "submit_form"
    assert fake_store.calls[-1][1][0] == TENANT_ID
