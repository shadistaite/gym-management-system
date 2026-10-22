import sqlite3
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

DATABASE = "gym.db"


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                instructor TEXT NOT NULL,
                capacity INTEGER NOT NULL CHECK(capacity > 0)
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                class_id INTEGER NOT NULL,
                FOREIGN KEY (class_id) REFERENCES classes(id)
            )
        """)

        count = db.execute(
            "SELECT COUNT(*) FROM classes"
        ).fetchone()[0]

        if count == 0:
            db.executemany(
                """
                INSERT INTO classes (name, instructor, capacity)
                VALUES (?, ?, ?)
                """,
                [
                    ("Yoga", "Sarah", 15),
                    ("Spin", "Mike", 12),
                    ("Strength Training", "Alex", 10),
                ],
            )

    yield


app = FastAPI(title="Gym Service", lifespan=lifespan)


class ClassRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    instructor: str = Field(min_length=1, max_length=100)
    capacity: int = Field(gt=0, le=100)


class BookingRequest(BaseModel):
    class_id: int = Field(gt=0)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/classes")
def list_classes():
    with get_db() as db:
        rows = db.execute(
            """
            SELECT id, name, instructor, capacity
            FROM classes
            ORDER BY id
            """
        ).fetchall()

    return [dict(row) for row in rows]


@app.post("/classes")
def create_class(
    request: ClassRequest,
    x_username: str = Header(),
    x_role: str = Header(),
):
    # Temporary authorization for local development.
    if x_role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    with get_db() as db:
        cursor = db.execute(
            """
            INSERT INTO classes (name, instructor, capacity)
            VALUES (?, ?, ?)
            """,
            (request.name, request.instructor, request.capacity),
        )

    return {
        "id": cursor.lastrowid,
        "message": "Class created",
    }


@app.post("/bookings")
def create_booking(
    request: BookingRequest,
    x_username: str = Header(),
):
    with get_db() as db:
        gym_class = db.execute(
            "SELECT id, capacity FROM classes WHERE id = ?",
            (request.class_id,),
        ).fetchone()

        if gym_class is None:
            raise HTTPException(
                status_code=404,
                detail="Class not found",
            )

        booking_count = db.execute(
            "SELECT COUNT(*) FROM bookings WHERE class_id = ?",
            (request.class_id,),
        ).fetchone()[0]

        if booking_count >= gym_class["capacity"]:
            raise HTTPException(
                status_code=409,
                detail="Class is full",
            )

        existing = db.execute(
            """
            SELECT id FROM bookings
            WHERE username = ? AND class_id = ?
            """,
            (x_username, request.class_id),
        ).fetchone()

        if existing:
            raise HTTPException(
                status_code=409,
                detail="You already booked this class",
            )

        cursor = db.execute(
            """
            INSERT INTO bookings (username, class_id)
            VALUES (?, ?)
            """,
            (x_username, request.class_id),
        )

    return {
        "id": cursor.lastrowid,
        "message": "Booking created",
    }


@app.get("/bookings/{username}")
def list_bookings(
    username: str,
    x_username: str = Header(),
):
    if username != x_username:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    with get_db() as db:
        rows = db.execute(
            """
            SELECT b.id, b.username, c.id AS class_id,
                   c.name, c.instructor
            FROM bookings b
            JOIN classes c ON c.id = b.class_id
            WHERE b.username = ?
            ORDER BY b.id
            """,
            (username,),
        ).fetchall()

    return [dict(row) for row in rows]