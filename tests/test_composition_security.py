import importlib.util
import os
from pathlib import Path

import jwt
from fastapi.testclient import TestClient


def load_gym_service():
    os.environ["JWT_SECRET_KEY"] = "composition-test-secret-key-32-bytes-min"

    module_path = (
        Path(__file__).resolve().parents[1]
        / "gym-service"
        / "main.py"
    )

    spec = importlib.util.spec_from_file_location(
        "composition_gym_service",
        module_path,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def test_gym_service_rejects_admin_token_for_unknown_user(
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)
    gym = load_gym_service()

    token = jwt.encode(
        {
            "sub": "unknown-user",
            "role": "admin",
        },
        "composition-test-secret-key-32-bytes-min",
        algorithm="HS256",
    )

    with TestClient(gym.app) as client:
        response = client.post(
            "/classes",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Test Class",
                "instructor": "Test Instructor",
                "capacity": 10,
            },
        )

    # This assertion should fail before the fix because the
    # Gym Service currently accepts the forged administrator claim.
    assert response.status_code == 401