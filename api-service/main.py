import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from pwdlib import PasswordHash

app = FastAPI(title="Gym Management API")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY environment variable must be set")

ALGORITHM = "HS256"

GYM_SERVICE_URL = os.getenv(
    "GYM_SERVICE_URL",
    "http://127.0.0.1:8001",
)

PROCESSING_SERVICE_URL = os.getenv(
    "PROCESSING_SERVICE_URL",
    "http://127.0.0.1:8002",
)

password_hash = PasswordHash.recommended()
bearer_scheme = HTTPBearer()

# Demo users for the local assignment.
# Passwords are hashed instead of stored as plain text.
users = {
    "alice": {
        "password_hash": password_hash.hash("AlicePass123!"),
        "role": "member",
    },
    "bob": {
        "password_hash": password_hash.hash("BobPass123!"),
        "role": "member",
    },
    "admin": {
        "password_hash": password_hash.hash("AdminPass123!"),
        "role": "admin",
    },
}


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)


class ClassRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    instructor: str = Field(min_length=1, max_length=100)
    capacity: int = Field(gt=0, le=100)


class BookingRequest(BaseModel):
    class_id: int = Field(gt=0)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        username = payload.get("sub")
        role = payload.get("role")

        # Only accept known users with their assigned roles.
        user = users.get(username) if username else None

        if user is None or role != user["role"]:
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


def forward_request(
    method: str,
    url: str,
    token: str,
    json_body: Optional[dict] = None,
):
    try:
        response = httpx.request(
            method,
            url,
            headers={"Authorization": f"Bearer {token}"},
            json=json_body,
            timeout=5.0,
        )
        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as exc:
        if exc.response.status_code in (401, 403, 404, 409, 422):
            raise HTTPException(
                status_code=exc.response.status_code,
                detail="The requested operation was rejected by the service",
            )

        raise HTTPException(
            status_code=502,
            detail="A downstream service returned an error",
        )

    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Could not communicate with a downstream service",
        )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/login")
def login(request: LoginRequest):
    user = users.get(request.username)

    if user is None or not password_hash.verify(
        request.password,
        user["password_hash"],
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)

    token = jwt.encode(
        {
            "sub": request.username,
            "role": user["role"],
            "exp": expires_at,
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@app.get("/classes")
def list_classes(
    current_user: dict = Depends(get_current_user),
):
    return forward_request(
        "GET",
        f"{GYM_SERVICE_URL}/classes",
        current_user["token"],
    )


@app.post("/classes")
def create_class(
    request: ClassRequest,
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    return forward_request(
        "POST",
        f"{GYM_SERVICE_URL}/classes",
        current_user["token"],
        json_body=request.dict(),
    )


@app.post("/bookings")
def create_booking(
    request: BookingRequest,
    current_user: dict = Depends(get_current_user),
):
    return forward_request(
        "POST",
        f"{GYM_SERVICE_URL}/bookings",
        current_user["token"],
        json_body=request.dict(),
    )


@app.get("/bookings/{username}")
def list_bookings(
    username: str,
    current_user: dict = Depends(get_current_user),
):
    if username != current_user["username"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    return forward_request(
        "GET",
        f"{GYM_SERVICE_URL}/bookings/{username}",
        current_user["token"],
    )


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

    return forward_request(
        "GET",
        f"{PROCESSING_SERVICE_URL}/summary/{username}",
        current_user["token"],
    )