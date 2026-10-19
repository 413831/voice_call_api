"""
Pruebas integrales de la API VoiceCall.

Demuestra la facilidad de testing gracias a:
- Application Factory Pattern: Permite crear clientes de prueba aislados en memoria.
- Arquitectura desacoplada: Validación de respuestas HTTP, códigos de estado y contratos JSON.
"""

import pytest
from flask.testing import FlaskClient
from app import create_app


@pytest.fixture
def client() -> FlaskClient:
    """Fixture que crea una instancia fresca de la app con base de datos en memoria para cada test."""
    app = create_app("sqlite:///:memory:")
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_health_check(client: FlaskClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy", "service": "voice-call-telemetry"}


def test_create_call_success(client: FlaskClient) -> None:
    payload = {
        "phone_number": "+14155552671",
        "duration_seconds": 120,
        "status": "completed",
        "transcript_summary": "User inquired about enterprise pricing and AI voice latency."
    }
    response = client.post("/api/calls", json=payload)
    assert response.status_code == 201

    data = response.get_json()
    assert "id" in data
    assert data["phone_number"] == "+14155552671"
    assert data["duration_seconds"] == 120
    assert data["status"] == "completed"
    assert data["transcript_summary"] == payload["transcript_summary"]
    assert "created_at" in data


def test_create_call_invalid_phone(client: FlaskClient) -> None:
    payload = {
        "phone_number": "invalid-phone",
        "duration_seconds": 60,
    }
    response = client.post("/api/calls", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_create_call_negative_duration(client: FlaskClient) -> None:
    payload = {
        "phone_number": "+14155552671",
        "duration_seconds": -5,
    }
    response = client.post("/api/calls", json=payload)
    assert response.status_code == 400
    assert "duración" in response.get_json()["error"]


def test_create_call_invalid_status(client: FlaskClient) -> None:
    payload = {
        "phone_number": "+14155552671",
        "status": "not-a-valid-status",
    }
    response = client.post("/api/calls", json=payload)
    assert response.status_code == 400
    assert "Estado" in response.get_json()["error"]


def test_get_call_by_id(client: FlaskClient) -> None:
    create_res = client.post("/api/calls", json={"phone_number": "+14155552671"})
    call_id = create_res.get_json()["id"]

    get_res = client.get(f"/api/calls/{call_id}")
    assert get_res.status_code == 200
    assert get_res.get_json()["id"] == call_id


def test_get_call_not_found(client: FlaskClient) -> None:
    response = client.get("/api/calls/non-existent-uuid")
    assert response.status_code == 404
    assert "not found" in response.get_json()["error"]


def test_list_calls_and_pagination(client: FlaskClient) -> None:
    for i in range(3):
        client.post("/api/calls", json={"phone_number": f"+1415555000{i}"})

    response = client.get("/api/calls?limit=2&offset=0")
    assert response.status_code == 200
    items = response.get_json()
    assert len(items) == 2


def test_update_call(client: FlaskClient) -> None:
    create_res = client.post(
        "/api/calls",
        json={"phone_number": "+14155552671", "status": "in-progress"}
    )
    call_id = create_res.get_json()["id"]

    update_payload = {
        "status": "completed",
        "duration_seconds": 185,
        "transcript_summary": "Call wrapped up with confirmation code 9821."
    }
    update_res = client.patch(f"/api/calls/{call_id}", json=update_payload)
    assert update_res.status_code == 200
    updated_data = update_res.get_json()
    assert updated_data["status"] == "completed"
    assert updated_data["duration_seconds"] == 185
    assert updated_data["transcript_summary"] == update_payload["transcript_summary"]


def test_delete_call(client: FlaskClient) -> None:
    create_res = client.post("/api/calls", json={"phone_number": "+14155552671"})
    call_id = create_res.get_json()["id"]

    del_res = client.delete(f"/api/calls/{call_id}")
    assert del_res.status_code == 200

    # Verificar que ya no existe (404)
    get_res = client.get(f"/api/calls/{call_id}")
    assert get_res.status_code == 404
