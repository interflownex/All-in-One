import os
import sys
import uuid
from pathlib import Path
import pytest
from datetime import UTC, datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.shared.identity_postgres_store import IdentityPostgresStore
from modules.shared.finance_postgres_store import FinancePostgresStore
from modules.shared.business_postgres_store import BusinessPostgresStore
from modules.shared.api_hub_postgres_store import ApiHubPostgresStore
from modules.shared.marketplace_postgres_store import MarketplacePostgresStore
from modules.shared.delivery_postgres_store import DeliveryPostgresStore
from modules.shared.services_postgres_store import ServicesPostgresStore
from modules.shared.mobility_postgres_store import MobilityPostgresStore
from modules.shared.jobs_postgres_store import JobsPostgresStore
from modules.shared.outbox_dispatcher import SAFE_PAYLOAD_FIELDS, publication_message

DEFAULT_DSN = os.environ.get(
    "ALL_IN_ONE_POSTGRES_MATRIX_DSN", 
    "postgresql://all_in_one:local-development-only@localhost:5432/all_in_one?connect_timeout=3"
)

# Configuration mapping for each module to its specialized store, primary resource, and required payload
MODULES_CONFIG = {
    "identity": {
        "class": IdentityPostgresStore, 
        "resource": "users",
        "payload": {
            "full_name": "Matrix Tester",
            "cpf_document": f"{uuid.uuid4().hex[:11]}",
            "birth_date": "1990-01-01",
            "email": f"matrix_{uuid.uuid4().hex[:8]}@test.com",
            "phone_e164": "+5511999999999",
            "password_hash": "hash123",
            "face_hash": "face123",
            "liveness_score": "0.99",
            "terms_accepted_at": datetime.now(UTC).isoformat(),
            "lgpd_consent_at": datetime.now(UTC).isoformat()
        }
    },
    "finance": {
        "class": FinancePostgresStore, 
        "resource": "wallets",
        "payload": {
            "wallet_type": "personal",
            "brl_available": 1000,
            "nex_available": 500
        }
    },
    "business": {
        "class": BusinessPostgresStore, 
        "resource": "companies",
        "payload": {
            "name": "Matrix Corp",
            "cnpj": f"{uuid.uuid4().hex[:14]}",
            "business_segment": "technology"
        }
    },
    "api_hub": {
        "class": ApiHubPostgresStore, 
        "resource": "apps",
        "payload": {
            "app_name": "Matrix App",
            "description": "Integration Test App",
            "webhook_url": "https://example.com/webhook"
        }
    },
    "marketplace": {
        "class": MarketplacePostgresStore, 
        "resource": "stores",
        "payload": {
            "name": "Matrix Store",
            "description": "Store for tests",
            "currency": "BRL"
        }
    },
    "delivery": {
        "class": DeliveryPostgresStore, 
        "resource": "shipments",
        "payload": {
            "origin_address": "Rua Teste 1",
            "destination_address": "Rua Teste 2",
            "weight": "1.5"
        }
    },
    "services": {
        "class": ServicesPostgresStore, 
        "resource": "service_orders",
        "payload": {
            "service_type": "maintenance",
            "description": "Matrix test service"
        }
    },
    "mobility": {
        "class": MobilityPostgresStore, 
        "resource": "rides",
        "payload": {
            "pickup_location": "-23.55,-46.63",
            "dropoff_location": "-23.56,-46.64"
        }
    },
    "jobs": {
        "class": JobsPostgresStore, 
        "resource": "candidates",
        "payload": {
            "first_name": "Neo",
            "last_name": "Matrix",
            "skills": ["python", "pytest"]
        }
    },
}

@pytest.mark.parametrize("module_name", list(MODULES_CONFIG.keys()))
def test_postgres_store_matrix_initialization(module_name: str):
    """
    Testa a inicialização e o estado CRUD básico esperado para
    os modulos prioritários definidos no EXECUTION_PLAN.md (Fase 2).
    """
    config = MODULES_CONFIG[module_name]
    store_class = config["class"]
    resource_type = config["resource"]
    payload = config["payload"].copy()
    
    dsn = os.environ.get(f"ALL_IN_ONE_{module_name.upper()}_POSTGRES_DSN") or DEFAULT_DSN
    if "connect_timeout" not in dsn:
        dsn += "&connect_timeout=3" if "?" in dsn else "?connect_timeout=3"
    
    try:
        store = store_class(dsn=dsn)
    except Exception as e:
        pytest.skip(f"Banco de dados nao disponivel para {module_name}: {e}")

    user_id = str(uuid.uuid4())
    actor_id = str(uuid.uuid4())
    entity_id = str(uuid.uuid4())
    idempotency_key = str(uuid.uuid4())
    
    # Adiciona ID ao payload para casos onde ele não gera automaticamente
    payload["id"] = str(uuid.uuid4())

    # 1. CREATE
    created = store.create(
        resource_type=resource_type,
        user_id=user_id,
        entity_id=entity_id,
        status="active",
        payload=payload,
        actor=actor_id,
        unique_fields=(),
        event=f"{module_name}.{resource_type}.created",
        idempotency_key=idempotency_key,
    )
    
    assert created is not None
    assert created["id"] is not None
    assert created["status"] == "active"
    assert created["user_id"] == user_id

    # 2. GET
    fetched = store.get(resource_type=resource_type, resource_id=created["id"])
    assert fetched is not None
    assert fetched["id"] == created["id"]

    # 3. LIST
    listed = store.list(resource_type=resource_type, user_id=user_id)
    assert len(listed) >= 1
    assert any(item["id"] == created["id"] for item in listed)

    # 4. UPDATE (não aplicável a todos os modulos da mesma forma, mas testamos soft_delete se suportado)
    if hasattr(store, "soft_deletable") and resource_type in getattr(store, "soft_deletable", []):
        store.soft_delete(item=fetched, actor=actor_id)
        deleted = store.get(resource_type=resource_type, resource_id=created["id"])
        assert deleted is None  # Deveria estar oculto após soft_delete

@pytest.mark.parametrize("module_name", list(MODULES_CONFIG.keys()))
def test_store_idempotency_behavior(module_name: str):
    config = MODULES_CONFIG[module_name]
    store_class = config["class"]
    resource_type = config["resource"]
    payload = config["payload"].copy()
    
    dsn = os.environ.get(f"ALL_IN_ONE_{module_name.upper()}_POSTGRES_DSN") or DEFAULT_DSN
    if "connect_timeout" not in dsn:
        dsn += "&connect_timeout=3" if "?" in dsn else "?connect_timeout=3"
    
    try:
        store = store_class(dsn=dsn)
    except Exception as e:
        pytest.skip(f"Banco de dados nao disponivel para {module_name}: {e}")

    user_id = str(uuid.uuid4())
    actor_id = str(uuid.uuid4())
    entity_id = str(uuid.uuid4())
    idempotency_key = str(uuid.uuid4())
    
    payload["id"] = str(uuid.uuid4())

    # Primeira chamada
    created_1 = store.create(
        resource_type=resource_type,
        user_id=user_id,
        entity_id=entity_id,
        status="active",
        payload=payload,
        actor=actor_id,
        unique_fields=(),
        event=f"{module_name}.{resource_type}.created",
        idempotency_key=idempotency_key,
    )
    
    # Segunda chamada com a mesma idempotency_key
    created_2 = store.create(
        resource_type=resource_type,
        user_id=user_id,
        entity_id=entity_id,
        status="active",
        payload=payload,
        actor=actor_id,
        unique_fields=(),
        event=f"{module_name}.{resource_type}.created",
        idempotency_key=idempotency_key,
    )
    
    # Devem retornar exatamente o mesmo registro original
    assert created_1["id"] == created_2["id"]

@pytest.mark.parametrize("module_name", list(MODULES_CONFIG.keys()))
def test_audit_outbox_integration(module_name: str):
    config = MODULES_CONFIG[module_name]
    store_class = config["class"]
    resource_type = config["resource"]
    payload = config["payload"].copy()
    
    dsn = os.environ.get(f"ALL_IN_ONE_{module_name.upper()}_POSTGRES_DSN") or DEFAULT_DSN
    if "connect_timeout" not in dsn:
        dsn += "&connect_timeout=3" if "?" in dsn else "?connect_timeout=3"
    
    try:
        store = store_class(dsn=dsn)
    except Exception as e:
        pytest.skip(f"Banco de dados nao disponivel para {module_name}: {e}")

    user_id = str(uuid.uuid4())
    actor_id = str(uuid.uuid4())
    entity_id = str(uuid.uuid4())
    idempotency_key = str(uuid.uuid4())
    
    payload["id"] = str(uuid.uuid4())

    # Executa criação
    created = store.create(
        resource_type=resource_type,
        user_id=user_id,
        entity_id=entity_id,
        status="active",
        payload=payload,
        actor=actor_id,
        unique_fields=(),
        event=f"{module_name}.{resource_type}.created",
        idempotency_key=idempotency_key,
    )

    # Valida Audit Log (se implementado pela subclasse)
    if hasattr(store, "audit_log"):
        logs = store.audit_log()
        assert any(log["resource_id"] == created["id"] for log in logs)
        
    # Valida Outbox Domain Events (se implementado pela subclasse)
    if hasattr(store, "outbox"):
        events = store.outbox()
        # Nota: finance intercepta no outbox via routing_key LIKE payment.%
        assert events
        event = events[0]
        message = publication_message(event)
        expected_payload = {
            key: payload[key]
            for key in SAFE_PAYLOAD_FIELDS.get(event["aggregate_type"], frozenset())
            if key in payload
        }
        assert message["routing_key"] == event["routing_key"]
        assert message["aggregate_type"] == event["aggregate_type"]
        assert message["aggregate_id"] == str(event["aggregate_id"])
        assert message["event_id"] == str(event["id"])
        assert message["correlation_id"] == str(event["correlation_id"])
        assert message["occurred_at"] == event["created_at"].isoformat()
        assert message["payload"] == expected_payload
