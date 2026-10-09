from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, stocks, transactions, prices, summary

# MVP-simple table creation. Once the schema stabilizes, swap this for
# Alembic migrations so schema changes are versioned instead of implicit.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Investment Tracker API")

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


@app.get("/health")
def health():
    return {"status": "ok"}
