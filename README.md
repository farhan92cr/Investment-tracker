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




---------------__________________________________________________----------------------------
*********************************************************************************************
((((((((((((((((((((((((((((((((((((((((((((((()))))))))))))))))))))))))))))))))))))))))))))))


# CI/CD SSH Setup — GitHub Actions → Oracle VM

## Step 1 — Create a dedicated GitHub Actions deployment key

The purpose of this key is:

**GitHub Actions → Oracle Cloud VM**

It is NOT the key used for:

**Oracle VM → GitHub**

### On Oracle VM, as `ubuntu`

Create the deployment key:

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy"
```

Save it as:

```text
/home/ubuntu/.ssh/github_actions
```

Leave the passphrase empty.

This creates:

```text
/home/ubuntu/.ssh/github_actions
/home/ubuntu/.ssh/github_actions.pub
```

### Add the public key to authorized_keys

```bash
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
```

Check:

```bash
tail -n 3 ~/.ssh/authorized_keys
```

The new key should end with:

```text
github-actions-deploy
```

### Important

Never share the private key:

```text
/home/ubuntu/.ssh/github_actions
```

The private key is stored only in GitHub Secrets.

---

# Step 2 — GitHub Repository Secrets

In the GitHub repository:

```text
Settings
→ Secrets and variables
→ Actions
→ New repository secret
```

Create these three secrets:

### SSH_PRIVATE_KEY

Value:

```bash
cat /home/ubuntu/.ssh/github_actions
```

Copy the **entire private key**, including:

```text
-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
```

Do NOT share this key publicly.

### SSH_USER

```text
ubuntu
```

### SERVER_HOST

Oracle VM public IP:

```text
130.210.42.159
```

---

# Step 3 — GitHub Actions workflow

Create this file in the local Windows repository:

```text
Investment-tracker\.github\workflows\deploy.yml
```

Initial workflow used:

```yaml
name: Deploy Investment Tracker

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Deploy to Oracle VM
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
          SERVER_HOST: ${{ secrets.SERVER_HOST }}
          SSH_USER: ${{ secrets.SSH_USER }}
        run: |
          mkdir -p ~/.ssh
          printf '%s\n' "$SSH_PRIVATE_KEY" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key

          ssh-keyscan -H "$SERVER_HOST" >> ~/.ssh/known_hosts

          ssh -i ~/.ssh/deploy_key "$SSH_USER@$SERVER_HOST" << 'EOF'
            cd /home/ubuntu/Investment-tracker
            git pull origin main
            docker-compose up -d --build
          EOF
```

### Note

We originally tried:

```yaml
uses: appleboy/ssh-action@v1.2.2
```

then:

```yaml
uses: appleboy/ssh-action@v1.2.0
```

and:

```yaml
uses: appleboy/ssh-action@master
```

GitHub reported:

```text
Unable to resolve action
repository or version not found
```

Therefore, we decided to use the normal SSH client already available on the GitHub Actions Ubuntu runner instead of `appleboy/ssh-action`.

---

# Step 4 — Important discovery: VM → GitHub authentication

The deployment workflow runs:

```bash
git pull origin main
```

as the `ubuntu` user.

Therefore, the `ubuntu` user itself must be able to authenticate to GitHub.

We tested this **inside the Oracle VM**:

```bash
ssh -T git@github.com
```

Result:

```text
git@github.com: Permission denied (publickey).
```

This means:

**`ubuntu` currently does NOT have GitHub SSH authentication configured.**

This must be fixed before the first CI/CD deployment.

---

# Important SSH Key Difference

There are two separate SSH connections:

## A. GitHub Actions → Oracle VM

Uses:

```text
/home/ubuntu/.ssh/github_actions
```

The private key is stored in GitHub:

```text
SSH_PRIVATE_KEY
```

The public key is in:

```text
/home/ubuntu/.ssh/authorized_keys
```

Purpose:

```text
GitHub Actions
      ↓ SSH
Oracle VM
```

---

## B. Oracle VM → GitHub

Needed for:

```bash
git pull origin main
```

The `ubuntu` user currently does not have this configured.

We tested:

```bash
ssh -T git@github.com
```

and received:

```text
Permission denied (publickey)
```

Therefore, we need a separate GitHub authentication key for the `ubuntu` user.

---

# Current Position

We are currently inside the Oracle VM as:

```text
ubuntu
```

at:

```text
/home/ubuntu/Investment-tracker
```

Prompt:

```text
ubuntu@invesment-tracker-vm:~/Investment-tracker$
```

## Next step

Create a GitHub SSH key specifically for the `ubuntu` user:

```bash
ssh-keygen -t ed25519 -C "ubuntu-github"
```

When asked:

```text
Enter file in which to save the key (/home/ubuntu/.ssh/id_ed25519):
```

Press:

```text
Enter
```

When asked for a passphrase, press:

```text
Enter
```

Then press:

```text
Enter
```

again to confirm the empty passphrase.

Expected files:

```text
/home/ubuntu/.ssh/id_ed25519
/home/ubuntu/.ssh/id_ed25519.pub
```

The next task will be to add:

```text
/home/ubuntu/.ssh/id_ed25519.pub
```

to GitHub so that:

```bash
git pull origin main
```

works when executed as `ubuntu`.

---

# Repository Information

GitHub repository:

```text
git@github.com:farhan92cr/Investment-tracker.git
```

Branch:

```text
main
```

Oracle VM project directory:

```text
/home/ubuntu/Investment-tracker
```

Oracle VM user:

```text
ubuntu
```

Oracle VM public IP:

```text
130.210.42.159
```




