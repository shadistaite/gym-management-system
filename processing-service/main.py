import os

import httpx
from fastapi import FastAPI, HTTPException, Header
from gym_summary_utils import generate_booking_summary

app = FastAPI(title="Processing Service")

GYM_SERVICE_URL = os.getenv(
    "GYM_SERVICE_URL",
    "http://127.0.0.1:8001",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/summary/{username}")
def generate_summary(
    username: str,
    x_username: str = Header(),
):
    # Users can only request their own summaries.
    if username != x_username:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    try:
        response = httpx.get(
            f"{GYM_SERVICE_URL}/bookings/{username}",
            headers={"X-Username": x_username},
            timeout=5.0,
        )
        response.raise_for_status()
        bookings = response.json()

    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Could not retrieve booking data",
        )

    summary = generate_booking_summary(username, bookings)

    return summary