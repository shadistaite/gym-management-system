import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Configure a test-only secret before importing the API.
os.environ["JWT_SECRET_KEY"] = "automated-test-secret-not-for-production"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
API_SERVICE_PATH = PROJECT_ROOT / "api-service"

sys.path.insert(0, str(API_SERVICE_PATH))

import main as api


@pytest.fixture
def client():
    with TestClient(api.app) as test_client:
        yield test_client


@pytest.fixture
def alice_token(client):
    response = client.post(
        "/login",
        json={
            "username": "alice",
            "password": "AlicePass123!",
        },
    )

    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def bob_token(client):
    response = client.post(
        "/login",
        json={
            "username": "bob",
            "password": "BobPass123!",
        },
    )

    assert response.status_code == 200
    return response.json()["access_token"]


def test_valid_login_succeeds(client):
    response = client.post(
        "/login",
        json={
            "username": "alice",
            "password": "AlicePass123!",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_invalid_password_is_rejected(client):
    response = client.post(
        "/login",
        json={
            "username": "alice",
            "password": "WrongPassword!",
        },
    )

    assert response.status_code == 401


def test_unknown_user_is_rejected(client):
    response = client.post(
        "/login",
        json={
            "username": "unknown-user",
            "password": "SomePassword123!",
        },
    )

    assert response.status_code == 401


def test_classes_require_authentication(client):
    response = client.get("/classes")

    assert response.status_code == 401


def test_invalid_token_is_rejected(client):
    response = client.get(
        "/classes",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_member_cannot_create_class(client, alice_token):
    response = client.post(
        "/classes",
        headers={"Authorization": f"Bearer {alice_token}"},
        json={
            "name": "Restricted Class",
            "instructor": "Sam",
            "capacity": 10,
        },
    )

    assert response.status_code == 403


def test_member_cannot_view_another_users_bookings(
    client,
    alice_token,
):
    response = client.get(
        "/bookings/bob",
        headers={"Authorization": f"Bearer {alice_token}"},
    )

    assert response.status_code == 403


def test_member_cannot_request_another_users_summary(
    client,
    alice_token,
):
    response = client.get(
        "/summary/bob",
        headers={"Authorization": f"Bearer {alice_token}"},
    )

    assert response.status_code == 403


def test_authenticated_class_listing_forwards_request(
    client,
    alice_token,
    monkeypatch,
):
    def fake_forward_request(method, url, token, json_body=None):
        assert method == "GET"
        assert url.endswith("/classes")
        assert token == alice_token

        return [
            {
                "id": 1,
                "name": "Yoga",
                "instructor": "Sarah",
                "capacity": 15,
            }
        ]

    monkeypatch.setattr(api, "forward_request", fake_forward_request)

    response = client.get(
        "/classes",
        headers={"Authorization": f"Bearer {alice_token}"},
    )

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Yoga"


def test_admin_can_request_class_creation(
    client,
    monkeypatch,
):
    login_response = client.post(
        "/login",
        json={
            "username": "admin",
            "password": "AdminPass123!",
        },
    )

    assert login_response.status_code == 200
    admin_token = login_response.json()["access_token"]

    def fake_forward_request(method, url, token, json_body=None):
        assert method == "POST"
        assert url.endswith("/classes")
        assert token == admin_token
        assert json_body["name"] == "Evening Pilates"

        return {
            "id": 4,
            "message": "Class created",
        }

    monkeypatch.setattr(api, "forward_request", fake_forward_request)

    response = client.post(
        "/classes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Evening Pilates",
            "instructor": "Sam",
            "capacity": 10,
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Class created"


def test_invalid_class_capacity_is_rejected(client, alice_token):
    response = client.post(
        "/classes",
        headers={"Authorization": f"Bearer {alice_token}"},
        json={
            "name": "Invalid Class",
            "instructor": "Sam",
            "capacity": 0,
        },
    )

    assert response.status_code == 422