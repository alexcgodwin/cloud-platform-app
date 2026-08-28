import os
import time

import psycopg
import redis
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel

app = FastAPI(title="platform-api")

Instrumentator().instrument(app).expose(
    app,
    endpoint="/metrics",
    include_in_schema=False
)

DB = os.getenv(
    "DATABASE_URL",
    "postgresql://platform:platform@localhost:5432/platform"
)

REDIS = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0"
)


class Item(BaseModel):
    name: str


@app.on_event("startup")
def startup():
    for _ in range(30):
        try:
            with psycopg.connect(DB) as c:
                c.execute(
                    "CREATE TABLE IF NOT EXISTS items("
                    "id bigserial primary key,"
                    "name text not null)"
                )
                c.commit()
            return
        except Exception:
            time.sleep(1)


@app.get("/health")
def health():
    return {"status": "ok", "service": "api"}


@app.get("/ready")
def ready():
    with psycopg.connect(DB) as c:
        c.execute("SELECT 1")

    redis.from_url(REDIS).ping()

    return {"status": "ready"}


@app.post("/items")
def create_item(item: Item):
    with psycopg.connect(DB) as c:
        row = c.execute(
            "INSERT INTO items(name) VALUES(%s) RETURNING id,name",
            (item.name,)
        ).fetchone()
        c.commit()

    redis.from_url(REDIS).lpush("jobs", str(row[0]))

    return {
        "id": row[0],
        "name": row[1],
        "queued": True
    }
