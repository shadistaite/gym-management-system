import importlib.util
import os
from pathlib import Path

from fastapi.testclient import TestClient

TEST_SECRET = "automated-test-secret-not-for-production"
os.environ["JWT_SECRET_KEY"] = TEST_SECRET

PROJECT_ROOT = Path(__file__).resolve().parent.parent
API_SERVICE_PATH = PROJECT_ROOT / "api-service" / "main.py"

spec = importlib.util.spec_from_file_location(
    "api_validation_main",
    API_SERVICE_PATH,
)
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)

client = TestClient(api.app)


def get_admin_token():
    response = client.post(
        "/login",
        json={
            "username": "admin",
            "password": "AdminPass123!",
        },
    )

    assert response.status_code == 200
    return response.json()["access_token"]


def test_zero_capacity_is_rejected():
    token = get_admin_token()

    response = client.post(
        "/classes",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Invalid Class",
            "instructor": "Sam",
            "capacity": 0,
        },
    )

    assert response.status_code == 422


def test_negative_capacity_is_rejected():
    token = get_admin_token()

    response = client.post(
        "/classes",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Invalid Class",
            "instructor": "Sam",
            "capacity": -5,
        },
    )

    assert response.status_code == 422


def test_excessive_capacity_is_rejected():
    token = get_admin_token()

    response = client.post(
        "/classes",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Invalid Class",
            "instructor": "Sam",
            "capacity": 101,
        },
    )

    assert response.status_code == 422


def test_invalid_booking_id_is_rejected():
    token = get_admin_token()

    response = client.post(
        "/bookings",
        headers={"Authorization": f"Bearer {token}"},
        json={"class_id": -1},
    )

    assert response.status_code == 422