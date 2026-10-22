import importlib.util
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


TEST_SECRET = "automated-test-secret-not-for-production"
os.environ["JWT_SECRET_KEY"] = TEST_SECRET

PROJECT_ROOT = Path(__file__).resolve().parent.parent
API_SERVICE_PATH = PROJECT_ROOT / "api-service" / "main.py"

spec = importlib.util.spec_from_file_location(
    "authorization_test_api_service",
    API_SERVICE_PATH,
)
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


@pytest.fixture
def client():
    with TestClient(api.app) as test_client:
        yield test_client


def get_token(client, username, password):
    response = client.post(
        "/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_member_cannot_create_class(client, monkeypatch):
    """Ordinary members must not perform administrator operations."""
    member_token = get_token(client, "alice", "AlicePass123!")

    def unexpected_forward(*args, **kwargs):
        pytest.fail("Unauthorized class creation reached downstream service")

    monkeypatch.setattr(api, "forward_request", unexpected_forward)

    response = client.post(
        "/classes",
        headers={"Authorization": f"Bearer {member_token}"},
        json={
            "name": "Unauthorized Class",
            "instructor": "Test Instructor",
            "capacity": 10,
        },
    )

    assert response.status_code == 403


def test_member_cannot_view_another_users_bookings(client, monkeypatch):
    """Members must only access their own booking information."""
    member_token = get_token(client, "alice", "AlicePass123!")

    def unexpected_forward(*args, **kwargs):
        pytest.fail("Unauthorized booking request reached downstream service")

    monkeypatch.setattr(api, "forward_request", unexpected_forward)

    response = client.get(
        "/bookings/bob",
        headers={"Authorization": f"Bearer {member_token}"},
    )

    assert response.status_code == 403


def test_member_cannot_request_another_users_summary(client, monkeypatch):
    """Members must not request another user's private summary."""
    member_token = get_token(client, "alice", "AlicePass123!")

    def unexpected_forward(*args, **kwargs):
        pytest.fail("Unauthorized summary request reached downstream service")

    monkeypatch.setattr(api, "forward_request", unexpected_forward)

    response = client.get(
        "/summary/bob",
        headers={"Authorization": f"Bearer {member_token}"},
    )

    assert response.status_code == 403


def test_admin_can_request_class_creation(client, monkeypatch):
    """Administrators may request class creation."""
    admin_token = get_token(client, "admin", "AdminPass123!")

    def mock_forward(*args, **kwargs):
        return {"id": 99, "message": "Class created"}

    monkeypatch.setattr(api, "forward_request", mock_forward)

    response = client.post(
        "/classes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Admin Test Class",
            "instructor": "Test Instructor",
            "capacity": 10,
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Class created"