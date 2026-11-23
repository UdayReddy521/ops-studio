"""Staging example for testing the lead follow-up flow over HTTP."""
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from fastapi import FastAPI, HTTPException
from pydantic import AwareDatetime, BaseModel, Field


class Enquiry(BaseModel):
    id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,64}$")
    owner: str = Field(min_length=1, max_length=120)
    due_at: AwareDatetime


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")


def create_app(
    database: str | Path = "reports/lead-followup.sqlite3",
    *,
    clock: Callable[[], datetime] | None = None,
) -> FastAPI:
    database = Path(database)
    database.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(database)) as db, db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS enquiries (
                id TEXT PRIMARY KEY,
                owner TEXT NOT NULL,
                due_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS reminders (
                enquiry_id TEXT PRIMARY KEY,
                owner TEXT NOT NULL,
                delivered_at TEXT NOT NULL
            );
        """)

    app = FastAPI(title="Ops Studio Lead Follow-up")

    @app.post("/enquiries", status_code=201)
    def register(enquiry: Enquiry):
        due_at = utc_text(enquiry.due_at)
        with closing(sqlite3.connect(database)) as db, db:
            try:
                db.execute("INSERT INTO enquiries VALUES (?, ?, ?)",
                           (enquiry.id, enquiry.owner, due_at))
            except sqlite3.IntegrityError as exc:
                raise HTTPException(409, "Enquiry ID already exists") from exc
        return {"id": enquiry.id, "owner": enquiry.owner, "due_at": due_at}

    @app.get("/enquiries/{enquiry_id}")
    def get_enquiry(enquiry_id: str):
        with closing(sqlite3.connect(database)) as db:
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM enquiries WHERE id = ?", (enquiry_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "Enquiry not found")
        return dict(row)

    @app.post("/reminders/run")
    def deliver_due_reminders():
        now = utc_text(datetime.now(timezone.utc) if clock is None else clock())
        with closing(sqlite3.connect(database)) as db, db:
            result = db.execute("""
                INSERT INTO reminders (enquiry_id, owner, delivered_at)
                SELECT id, owner, ? FROM enquiries WHERE due_at <= ?
                ON CONFLICT(enquiry_id) DO NOTHING
            """, (now, now))
            delivered = result.rowcount
        return {"delivered_to_test_inbox": delivered}

    @app.get("/reminders")
    def test_inbox():
        with closing(sqlite3.connect(database)) as db:
            db.row_factory = sqlite3.Row
            return [dict(row) for row in db.execute(
                "SELECT * FROM reminders ORDER BY delivered_at, enquiry_id"
            )]

    return app
