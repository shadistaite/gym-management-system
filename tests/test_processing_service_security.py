import importlib.util
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_SECRET = "automated-test-secret-not-for-production"
os.environ["JWT_SECRET_KEY"] = TEST_SECRET

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSING_SERVICE_PATH = (
    PROJECT_ROOT / "processing-service" / "main.py"
)

spec = importlib.util.spec_from_file_location(
    "processing_service_main",
    PROCESSING_SERVICE_PATH,
)
processing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(processing)


@pytest.fixture
def client():
    with TestClient(processing.app) as test_client:
        yield test_client


def make_token(username="alice", role="member"):
    import jwt

    return jwt.encode(
        {"sub": username, "role": role},
        TEST_SECRET,
        algorithm="HS256",
    )


def auth_headers(username="alice", role="member"):
    return {
        "Authorization": f"Bearer {make_token(username, role)}"
    }


def test_summary_requires_authentication(client):
    response = client.get("/summary/alice")
    assert response.status_code == 401


def test_invalid_token_is_rejected(client):
    response = client.get(
        "/summary/alice",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


def test_member_cannot_request_another_users_summary(client):
    response = client.get(
        "/summary/bob",
        headers=auth_headers("alice", "member"),
    )
    assert response.status_code == 403


def test_summary_is_generated_from_gym_service(
    client,
    monkeypatch,
):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return [
                {
                    "id": 1,
                    "username": "alice",
                    "class_id": 1,
                    "name": "Yoga",
                    "instructor": "Sarah",
                },
                {
                    "id": 2,
                    "username": "alice",
                    "class_id": 2,
                    "name": "Spin",
                    "instructor": "Mike",
                },
            ]

    def fake_get(url, headers, timeout):
        assert url.endswith("/bookings/alice")
        assert headers["Authorization"].startswith("Bearer ")
        return FakeResponse()

    monkeypatch.setattr(processing.httpx, "get", fake_get)

    response = client.get(
        "/summary/alice",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    summary = response.json()
    assert summary["username"] == "alice"
    assert summary["total_bookings"] == 2
    assert set(summary["classes"]) == {"Yoga", "Spin"}


def test_summary_handles_gym_service_connection_failure(
    client,
    monkeypatch,
):
    import httpx

    def fake_get(url, headers, timeout):
        raise httpx.ConnectError("Test connection failure")

    monkeypatch.setattr(processing.httpx, "get", fake_get)

    response = client.get(
        "/summary/alice",
        headers=auth_headers(),
    )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "Could not retrieve booking data"
    )