from uuid import uuid4

from platform_test_support import fresh_client_for


def actor_headers(
    user_id: str, roles: str = "", scopes: str = "", mfa: bool = False
) -> dict[str, str]:
    headers = {"X-Actor-User-Id": user_id}
    if roles:
        headers["X-Actor-Roles"] = roles
    if scopes:
        headers["X-Actor-Scopes"] = scopes
    if mfa:
        headers["X-MFA-Verified"] = "true"
    return headers


def test_delivery_quote_assignment_completion_journey() -> None:
    delivery = fresh_client_for("delivery")
    customer_id = str(uuid4())
    rider_id = "rider-alpha"
    operator_id = str(uuid4())
    nonce = uuid4().hex

    quote = delivery.post(
        "/pricing/quote",
        headers=actor_headers(customer_id),
        json={
            "distance_km": "7.5",
            "duration_minutes": "22",
            "weight_kg": "3.2",
            "vehicle_type": "motorcycle",
            "insurance": True,
            "declared_value_brl": "250.00",
        },
    )
    assert quote.status_code == 200
    total_brl = quote.json()["total_brl"]

    request = delivery.post(
        "/resources/delivery_requests",
        headers={
            **actor_headers(customer_id),
            "X-Idempotency-Key": f"delivery-{nonce}",
        },
        json={
            "user_id": customer_id,
            "payload": {
                "service_type": "package",
                "origin": {"lat": -23.5505, "lng": -46.6333},
                "destination": {"lat": -23.5617, "lng": -46.6559},
                "quoted_brl": total_brl,
                "declared_value_brl": "250.00",
            },
        },
    )
    assert request.status_code == 201
    request_id = request.json()["id"]
    assert request.json()["status"] == "created"

    assigned = delivery.post(
        f"/resources/delivery_requests/{request_id}/actions/assign",
        headers=actor_headers(operator_id, "owner"),
        json={
            "reason": "rider disponivel",
            "payload": {"assigned_rider_user_id": rider_id},
        },
    )
    assert assigned.status_code == 200
    assert assigned.json()["status"] == "assigned"
    assert assigned.json()["payload"]["assigned_rider_user_id"] == rider_id

    picked_up = delivery.post(
        f"/resources/delivery_requests/{request_id}/actions/pickup",
        headers=actor_headers(operator_id, "owner"),
        json={"reason": "coleta confirmada"},
    )
    assert picked_up.status_code == 200
    assert picked_up.json()["status"] == "picked_up"

    completed = delivery.post(
        f"/resources/delivery_requests/{request_id}/actions/complete",
        headers=actor_headers(operator_id, "owner"),
        json={"reason": "entrega concluida", "payload": {"proof_hash": "pod-ok"}},
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"

    pod = delivery.post(
        "/resources/proofs",
        headers=actor_headers(operator_id, "owner"),
        json={
            "user_id": customer_id,
            "payload": {
                "delivery_request_id": request_id,
                "file_sha256": f"pod-{nonce}",
                "storage_key": f"private/delivery/{request_id}/pod.aesgcm",
                "captured_at": "2026-07-15T07:00:00Z",
                "proof_type": "photo",
                "antifraud_signal": "geo_hash_and_recipient_match",
            },
        },
    )
    assert pod.status_code == 201
    assert pod.json()["status"] == "recorded"
    assert pod.json()["payload"]["storage_key"].endswith("/pod.aesgcm")

    delete_pod = delivery.delete(
        f"/resources/proofs/{pod.json()['id']}",
        headers=actor_headers(operator_id, "owner"),
    )
    assert delete_pod.status_code == 409

    outbox = delivery.get(
        "/events/outbox", headers=actor_headers(operator_id, "auditor")
    )
    assert outbox.status_code == 200
    assert any(event["routing_key"] == "delivery.completed" for event in outbox.json())
    assert any(
        event["routing_key"] == "delivery.proof.recorded" for event in outbox.json()
    )


def test_rider_onboarding_document_vehicle_journey() -> None:
    riders = fresh_client_for("riders")
    rider_id = str(uuid4())
    reviewer_id = str(uuid4())
    nonce = uuid4().hex

    profile = riders.post(
        "/resources/rider_profiles",
        headers=actor_headers(rider_id),
        json={
            "user_id": rider_id,
            "payload": {
                "cnh_number_hash": f"cnh-{nonce}",
                "cnh_category": "AB",
                "wallet_id": str(uuid4()),
            },
        },
    )
    assert profile.status_code == 201
    profile_id = profile.json()["id"]
    assert profile.json()["status"] == "pending_documents"

    submitted = riders.post(
        f"/resources/rider_profiles/{profile_id}/actions/submit",
        headers=actor_headers(rider_id),
        json={"reason": "documentos enviados para analise"},
    )
    assert submitted.status_code == 200
    assert submitted.json()["status"] == "pending_review"

    approved = riders.post(
        f"/resources/rider_profiles/{profile_id}/actions/approve",
        headers=actor_headers(reviewer_id, "compliance_officer", mfa=True),
        json={"reason": "documentos conferidos"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    active = riders.post(
        f"/resources/rider_profiles/{profile_id}/actions/activate",
        headers=actor_headers(reviewer_id, "compliance_officer", mfa=True),
        json={"reason": "rider liberado para operacao"},
    )
    assert active.status_code == 200
    assert active.json()["status"] == "active"

    vehicle = riders.post(
        "/resources/vehicles",
        headers=actor_headers(rider_id),
        json={
            "user_id": rider_id,
            "payload": {
                "rider_profile_id": profile_id,
                "type": "motorcycle",
                "license_plate": f"RID{nonce[:4]}",
            },
        },
    )
    assert vehicle.status_code == 201
    assert vehicle.json()["status"] == "pending_review"

    outbox = riders.get("/events/outbox", headers=actor_headers(reviewer_id, "auditor"))
    assert outbox.status_code == 200
    assert any(event["routing_key"] == "rider.approved" for event in outbox.json())


def test_services_provider_contract_completion_journey() -> None:
    services = fresh_client_for("services")
    provider_id = str(uuid4())
    provider_reference = "provider-alpha"
    customer_id = str(uuid4())
    reviewer_id = str(uuid4())
    nonce = uuid4().hex

    provider = services.post(
        "/resources/providers",
        headers=actor_headers(provider_id),
        json={"user_id": provider_id, "payload": {"category": "maintenance"}},
    )
    assert provider.status_code == 201
    provider_resource_id = provider.json()["id"]

    approved = services.post(
        f"/resources/providers/{provider_resource_id}/actions/approve",
        headers=actor_headers(reviewer_id, "compliance_officer", mfa=True),
        json={"reason": "cadastro tecnico aprovado"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    contract = services.post(
        "/resources/service_contracts",
        headers={**actor_headers(customer_id), "X-Idempotency-Key": f"service-{nonce}"},
        json={
            "user_id": customer_id,
            "payload": {
                "provider_user_id": provider_reference,
                "escrow_id": "escrow-services",
                "visit_price_brl": "79.90",
                "contracted_price_brl": "249.90",
                "scope": "manutencao preventiva residencial",
            },
        },
    )
    assert contract.status_code == 201
    contract_id = contract.json()["id"]
    assert contract.json()["status"] == "draft"

    held = services.post(
        f"/resources/service_contracts/{contract_id}/actions/accept",
        headers=actor_headers(customer_id),
        json={"reason": "orcamento aceito com escrow"},
    )
    assert held.status_code == 200
    assert held.json()["status"] == "held"

    completed = services.post(
        f"/resources/service_contracts/{contract_id}/actions/complete",
        headers=actor_headers(customer_id),
        json={
            "reason": "servico executado",
            "payload": {"evidence_hash": "evidence-ok"},
        },
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"

    outbox = services.get(
        "/events/outbox", headers=actor_headers(reviewer_id, "auditor")
    )
    assert outbox.status_code == 200
    assert any(
        event["routing_key"] == "services.contract.completed" for event in outbox.json()
    )


def test_mobility_fare_ride_and_ticket_journey() -> None:
    mobility = fresh_client_for("mobility")
    passenger_id = str(uuid4())
    driver_id = "driver-alpha"
    operator_id = str(uuid4())
    nonce = uuid4().hex

    fare = mobility.post(
        "/pricing/fare",
        headers=actor_headers(passenger_id),
        json={
            "distance_km": "12.4",
            "duration_minutes": "31",
            "vehicle_type": "comfort",
        },
    )
    assert fare.status_code == 200

    fare_rule = mobility.post(
        "/resources/fare_rules",
        headers=actor_headers(operator_id, "owner"),
        json={
            "user_id": operator_id,
            "payload": {
                "rule_name": f"comfort-{nonce}",
                "base_fare_brl": "8.00",
                "per_km_brl": "2.10",
                "minimum_fare_brl": "12.00",
                "vehicle_type": "comfort",
            },
        },
    )
    assert fare_rule.status_code == 201
    assert fare_rule.json()["status"] == "active"

    route = mobility.post(
        "/resources/routes",
        headers=actor_headers(passenger_id),
        json={
            "user_id": passenger_id,
            "payload": {
                "origin": {"lat": -23.567, "lng": -46.648},
                "destination": {"lat": -23.589, "lng": -46.612},
                "distance_km": "12.4",
                "eta_minutes": 31,
                "route_polyline_hash": f"route-{nonce}",
            },
        },
    )
    assert route.status_code == 201
    assert route.json()["status"] == "quoted"

    ride = mobility.post(
        "/resources/rides",
        headers={**actor_headers(passenger_id), "X-Idempotency-Key": f"ride-{nonce}"},
        json={
            "user_id": passenger_id,
            "payload": {
                "origin": {"lat": -23.567, "lng": -46.648},
                "destination": {"lat": -23.589, "lng": -46.612},
                "vehicle_type": "comfort",
                "fare_brl": fare.json()["fare_brl"],
                "fare_rule_id": fare_rule.json()["id"],
                "route_id": route.json()["id"],
                "eta_minutes": route.json()["payload"]["eta_minutes"],
            },
        },
    )
    assert ride.status_code == 201
    ride_id = ride.json()["id"]
    assert ride.json()["status"] == "requested"

    accepted = mobility.post(
        f"/resources/rides/{ride_id}/actions/accept",
        headers=actor_headers(operator_id, "owner"),
        json={"reason": "motorista aceitou", "payload": {"driver_user_id": driver_id}},
    )
    assert accepted.status_code == 200
    assert accepted.json()["status"] == "accepted"
    assert accepted.json()["payload"]["driver_user_id"] == driver_id

    completed = mobility.post(
        f"/resources/rides/{ride_id}/actions/complete",
        headers=actor_headers(operator_id, "owner"),
        json={"reason": "corrida finalizada"},
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"

    ticket = mobility.post(
        "/resources/tickets",
        headers=actor_headers(passenger_id),
        json={
            "user_id": passenger_id,
            "payload": {
                "route_code": "BUS-875",
                "amount_brl": "6.40",
                "qr_token_hash": "qr-mobility",
                "nfc_token_hash": "nfc-mobility",
            },
        },
    )
    assert ticket.status_code == 201
    assert ticket.json()["status"] == "active"

    used_ticket = mobility.post(
        f"/resources/tickets/{ticket.json()['id']}/actions/use",
        headers=actor_headers(passenger_id),
        json={"reason": "validacao no embarque"},
    )
    assert used_ticket.status_code == 200
    assert used_ticket.json()["status"] == "used"

    outbox = mobility.get(
        "/events/outbox", headers=actor_headers(operator_id, "auditor")
    )
    assert outbox.status_code == 200
    routing_keys = {event["routing_key"] for event in outbox.json()}
    assert {
        "mobility.fare_rule.published",
        "mobility.route.eta_quoted",
        "mobility.ticket.used",
    } <= routing_keys


def test_health_patient_appointment_access_journey() -> None:
    health = fresh_client_for("health")
    patient_id = str(uuid4())
    doctor_id = str(uuid4())
    reviewer_id = str(uuid4())
    nonce = uuid4().hex

    patient = health.post(
        "/resources/patients",
        headers=actor_headers(patient_id),
        json={"user_id": patient_id, "payload": {"health_identifier": f"sus-{nonce}"}},
    )
    assert patient.status_code == 201
    patient_resource_id = patient.json()["id"]

    denied = health.get(
        f"/resources/patients/{patient_resource_id}",
        headers=actor_headers(str(uuid4())),
    )
    assert denied.status_code == 403

    medical_view = health.get(
        f"/resources/patients/{patient_resource_id}",
        headers=actor_headers(doctor_id, "doctor"),
    )
    assert medical_view.status_code == 200
    assert medical_view.json()["id"] == patient_resource_id

    appointment = health.post(
        "/resources/appointments",
        headers=actor_headers(patient_id),
        json={
            "user_id": patient_id,
            "payload": {
                "patient_id": patient_resource_id,
                "professional_user_id": doctor_id,
                "scheduled_at": "2026-06-15T14:00:00Z",
                "care_line": "clinica_geral",
            },
        },
    )
    assert appointment.status_code == 201
    appointment_id = appointment.json()["id"]
    assert appointment.json()["status"] == "draft"

    approved = health.post(
        f"/resources/appointments/{appointment_id}/actions/approve",
        headers=actor_headers(reviewer_id, "compliance_officer", mfa=True),
        json={"reason": "agenda confirmada"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    completed = health.post(
        f"/resources/appointments/{appointment_id}/actions/complete",
        headers=actor_headers(reviewer_id, "compliance_officer"),
        json={"reason": "consulta realizada"},
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"
