# Investment Tracker

A multi-user portfolio tracker: track buys/sells, log prices any time (not just
monthly), and see a live dashboard (sector allocation, invested vs. current
value, per-stock gain/loss, and a growth curve over time).

This is **Phase 1**: a complete app that runs locally with Docker Compose.
No cloud, no CI/CD yet - that's Phase 2 and 3 (see "What's next" below).

## Stack

- **Backend**: Python, FastAPI, SQLAlchemy, JWT auth (`backend/`)
- **Frontend**: React + Vite + recharts (`frontend/`)
- **Database**: Postgres

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose (comes with Docker Desktop)
- That's it - Node/Python don't need to be installed locally, they run inside containers.

## Running it

```bash
cp .env.example .env
# edit .env and set JWT_SECRET to a long random string

docker compose up --build
```

Then open:
- Frontend: http://localhost:5173
- Backend API docs (interactive): http://localhost:8000/docs

Create an account on the signup page, then:
1. **Stock Master** - add each stock you own (ticker, company, sector)
2. **Buy Transactions** - log your buys (SST 15% and levies 6% of brokerage are calculated automatically, same as the original spreadsheet)
3. **Sold Transactions** - log any sales
4. **Prices** - enter a price any time; each entry is timestamped and feeds the dashboard's growth chart
5. **Dashboard** - see it all together

## Project layout

```
investment-tracker/
├── backend/
│   ├── app/
│   │   ├── main.py            FastAPI app, wires everything together
│   │   ├── models.py          Database tables (SQLAlchemy)
│   │   ├── schemas.py         Request/response shapes (Pydantic)
│   │   ├── auth.py            Password hashing + JWT
│   │   ├── calculations.py    All the money-math in one place
│   │   └── routers/           One file per API area (auth, stocks, ...)
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/             One file per screen
│   │   ├── components/        Shared UI (sidebar layout)
│   │   └── lib/                API client + auth context
│   └── Dockerfile
└── docker-compose.yml
```

## Notes on the design

- **Every price entry is kept**, not overwritten - that's what makes "enter a
  price any time, even a few times a day" work, and it's what the growth
  chart is built from.
- **Money math lives in one place** (`backend/app/calculations.py`), so the
  buy/sell/summary endpoints can't drift out of sync with each other.
- **Tables are created automatically on startup** (`Base.metadata.create_all`)
  for now. Once the schema settles down, switch to
  [Alembic](https://alembic.sqlalchemy.org/) migrations so schema changes are
  versioned instead of implicit - a good next exercise.
- **CORS is wide open** (`allow_origins=["*"]`) for local dev - tighten this
  to your real frontend URL before deploying.

## What's next (Phases 2-4)

1. **Ship it** - push this repo to GitHub, provision an Oracle Cloud VM, get
   it live on a real URL with HTTPS.
2. **Automate it** - GitHub Actions so every push builds, tests, and deploys.
   Terraform so the VM/network is defined in code, not clicked together.
3. **Observe it** - Prometheus + Grafana, automated Postgres backups.
4. **Monetize + Phase 2 data** - payments, and (if it's justified by paying
   users) a licensed price-data API to auto-fill end-of-day prices instead of
   manual entry.
