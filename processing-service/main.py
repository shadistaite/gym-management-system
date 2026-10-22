import os

import httpx
import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from gym_summary_utils import generate_booking_summary

app = FastAPI(title="Processing Service")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"

if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY environment variable must be set"
    )

GYM_SERVICE_URL = os.getenv(
    "GYM_SERVICE_URL",
    "http://127.0.0.1:8001",
)

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )

        username = payload.get("sub")
        role = payload.get("role")

        # Only accept known users with their assigned roles.
        trusted_users = {
            "alice": "member",
            "bob": "member",
            "admin": "admin",
        }

        if not username or trusted_users.get(username) != role:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )

        return {
            "username": username,
            "role": role,
            "token": credentials.credentials,
        }

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/summary/{username}")
def generate_summary(
    username: str,
    current_user: dict = Depends(get_current_user),
):
    if username != current_user["username"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    try:
        response = httpx.get(
            f"{GYM_SERVICE_URL}/bookings/{username}",
            headers={
                "Authorization": f"Bearer {current_user['token']}"
            },
            timeout=5.0,
        )
        response.raise_for_status()
        bookings = response.json()

    except httpx.HTTPStatusError as exc:
        if exc.response.status_code in (401, 403):
            raise HTTPException(
                status_code=exc.response.status_code,
                detail="Gym Service rejected the request",
            )

        raise HTTPException(
            status_code=502,
            detail="Could not retrieve booking data",
        )

    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Could not retrieve booking data",
        )

    return generate_booking_summary(username, bookings)