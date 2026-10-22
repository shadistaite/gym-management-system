import importlib.util
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_SECRET = "automated-test-secret-not-for-production"
os.environ["JWT_SECRET_KEY"] = TEST_SECRET

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GYM_SERVICE_PATH = PROJECT_ROOT / "gym-service" / "main.py"

spec = importlib.util.spec_from_file_location(
    "gym_service_main",
    GYM_SERVICE_PATH,
)
gym = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gym)


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(gym, "DATABASE", str(tmp_path / "test_gym.db"))

    with TestClient(gym.app) as test_client:
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


def test_classes_require_authentication(client):
    response = client.get("/classes")
    assert response.status_code == 401


def test_member_can_view_classes(client):
    response = client.get("/classes", headers=auth_headers())
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_member_cannot_create_class(client):
    response = client.post(
        "/classes",
        headers=auth_headers(),
        json={
            "name": "Restricted Class",
            "instructor": "Sam",
            "capacity": 10,
        },
    )
    assert response.status_code == 403


def test_admin_can_create_class(client):
    response = client.post(
        "/classes",
        headers=auth_headers("admin", "admin"),
        json={
            "name": "Evening Pilates",
            "instructor": "Sam",
            "capacity": 10,
        },
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Class created"


def test_booking_requires_valid_class_id(client):
    response = client.post(
        "/bookings",
        headers=auth_headers(),
        json={"class_id": 0},
    )
    assert response.status_code == 422


def test_member_cannot_view_another_users_bookings(client):
    response = client.get(
        "/bookings/bob",
        headers=auth_headers("alice", "member"),
    )
    assert response.status_code == 403


def test_invalid_token_is_rejected(client):
    response = client.get(
        "/classes",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401