import os

import jwt
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pwdlib import PasswordHash

app = FastAPI(title="Gym Management API")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY environment variable must be set")

ALGORITHM = "HS256"

password_hash = PasswordHash.recommended()

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
    username: str
    password: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/login")
def login(request: LoginRequest):
    user = users.get(request.username)

    if user is None or not password_hash.verify(
        request.password, user["password_hash"]
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