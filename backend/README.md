# LedgerMind AI — Backend

FastAPI backend for LedgerMind AI, with authenticated business workspaces, template-driven records, reports and deterministic intelligence checks. Supported business types are **Restaurant** and **Supermarket**.

## Requirements

- Python 3.12 or newer
- PostgreSQL
- PowerShell on Windows (commands below use PowerShell syntax)

## Setup

From the `backend` directory:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Edit `.env` and replace `CHANGE_ME` in `DATABASE_URL` with your local PostgreSQL
password. Create a PostgreSQL database named `ledgermind_ai` before using the
database readiness endpoint. Do not commit `.env` or put real credentials in source files.

## Run the API

```powershell
alembic upgrade head
uvicorn app.main:app --reload
```

Useful endpoints:

- `http://127.0.0.1:8000/` — service identification
- `http://127.0.0.1:8000/api/v1/health/live` — process liveness
- `http://127.0.0.1:8000/api/v1/health/ready` — database readiness
- `http://127.0.0.1:8000/docs` — interactive API documentation

## Authentication endpoints

- `POST /api/v1/auth/register` — create an account and session
- `POST /api/v1/auth/login` — authenticate and issue a session
- `POST /api/v1/auth/logout` — revoke the current bearer session
- `GET /api/v1/auth/me` — read the current profile
- `PATCH /api/v1/auth/me` — update the profile name
- `POST /api/v1/auth/change-password` — change password and revoke active sessions
- `GET /api/v1/businesses` — list only businesses the current user is authorized to access

Protected endpoints require `Authorization: Bearer <access_token>`. A business UUID is not an authorization credential. Requests for businesses without a membership return `404` to avoid disclosing whether another user's business exists.

## Migrations

Alembic migrations `0001_business_onboarding` and `0002_daily_records` remain unchanged. `0003_authentication` adds users, revocable sessions and business memberships without dropping existing business or record data. Existing pre-authentication businesses are intentionally not auto-assigned to the first new user. After the intended user registers, a database administrator can assign specific verified business UUIDs using `python scripts/assign_legacy_business_owner.py --email owner@example.com --business-id <UUID>`. Repeat `--business-id` for each explicitly verified business; unknown IDs abort the operation. Do not assign legacy records based on email alone without verifying the intended owner.

## Tests

From the backend directory:

```powershell
python -m pytest
```

The test suite uses isolated SQLite databases for API tests and does not require a live PostgreSQL server. The production app still uses the configured PostgreSQL database.

## AI business analysis and supplier invoices
Apply all migrations before using the supplier-invoice endpoints: `alembic upgrade head`. The business analyst reads the selected business's server-calculated report snapshot and passes only aggregated values to Gemma; it never executes model-generated SQL. Supplier invoices are persisted only after authenticated human confirmation.

For fresh setup, copy `.env.example` to `.env` and configure `DATABASE_URL` and `GEMMA_API_KEY` locally. Never commit `.env`.
