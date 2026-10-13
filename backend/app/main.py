from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from prometheus_fastapi_instrumentator import Instrumentator

from sqlalchemy import text
from app.database import Base, engine
from app.routers import auth, stocks, transactions, prices, summary, ai

# MVP-simple table creation. Once the schema stabilizes, swap this for
# Alembic migrations so schema changes are versioned instead of implicit.
with engine.begin() as connection:
    connection.execute(text("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS is_verified BOOLEAN NOT NULL DEFAULT TRUE
    """))
    connection.execute(text("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS verification_token_hash VARCHAR
    """))
    connection.execute(text("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS verification_token_expires_at TIMESTAMP
    """))
    connection.execute(text("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS password_reset_token_hash VARCHAR
    """))
    connection.execute(text("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS password_reset_token_expires_at TIMESTAMP
    """))

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Investment Tracker API")
Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your real frontend URL before going live
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(stocks.router)
app.include_router(transactions.router)
app.include_router(prices.router)
app.include_router(summary.router)
app.include_router(ai.router)


@app.get("/health")
def health():
    return {"status": "ok"}
