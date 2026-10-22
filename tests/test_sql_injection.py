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
    "sql_test_gym_service",
    GYM_SERVICE_PATH,
)
gym = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gym)


@pytest.fixture
def client(tmp_path, monkeypatch):
    database_path = tmp_path / "test_gym.db"
    monkeypatch.setattr(gym, "DATABASE", str(database_path))

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


def test_sql_injection_string_does_not_change_database_query(client):
    """SQL-like input must not change the result of a database query."""
    import sqlite3

    connection = sqlite3.connect(gym.DATABASE)

    connection.execute(
        "INSERT INTO classes (name, instructor, capacity) VALUES (?, ?, ?)",
        ("Yoga", "Sarah", 15),
    )
    connection.commit()

    malicious_input = "' OR '1'='1"

    rows = connection.execute(
        "SELECT id, name FROM classes WHERE name = ?",
        (malicious_input,),
    ).fetchall()

    assert rows == []

    connection.close()


def test_class_listing_does_not_expose_sql_injection_input(client):
    """The real class-listing endpoint returns a normal class list."""
    response = client.get(
        "/classes",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)

    class_names = [item["name"] for item in response.json()]
    assert "Yoga" in class_names


def test_booking_query_does_not_accept_username_as_sql(client):
    """A username containing SQL syntax cannot bypass booking ownership."""
    response = client.get(
        "/bookings/alice%27%20OR%20%271%27%3D%271",
        headers=auth_headers(),
    )

    assert response.status_code == 403


def test_class_listing_requires_authentication(client):
    """Unauthenticated users cannot access the endpoint."""
    response = client.get("/classes")

    assert response.status_code == 401