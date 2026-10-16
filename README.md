# LedgerMind AI

LedgerMind AI is a configurable business-record and intelligence platform. The initial release supports **restaurants and supermarkets** through a shared backend and template-driven record engine.

## Project layout
- `backend/` — FastAPI, SQLAlchemy, Alembic, PostgreSQL, authentication and automated tests.
- `frontend/` — React, TypeScript and Vite dashboard.

## Authentication and data access
- Register with a name, email and password (minimum 10 characters), then sign in to receive a short-lived, revocable bearer session.
- Profile name and password can be updated from the account panel. Changing a password revokes existing sessions.
- Each business created by a user receives an owner membership. Business lists, records, templates, reports, intelligence and AI interpretation require authentication; business-specific endpoints also enforce membership server-side.
- Passwords are PBKDF2-HMAC-SHA256 hashes; raw session tokens are returned only at login/registration and only token hashes are stored in the database.
- The browser keeps the session token in `sessionStorage`. Sign out revokes the session and clears the browser token.

## Start the backend
Activate the existing Python virtual environment and run from `backend/`:

```powershell
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
# Set DATABASE_URL in .env, then apply the additive migration:
alembic upgrade head
python -m uvicorn app.main:app --reload
```

API documentation: `http://127.0.0.1:8000/docs`.

## Start the frontend
In another PowerShell window:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open `http://localhost:5173`.

## Verify
From `backend/` with the project's virtual environment active:

```powershell
python -m pytest
```

From `frontend/`:

```powershell
npm run build
```

## Database migration notes
Migration `0003_authentication` adds `users`, `user_sessions`, and `business_memberships`. It does not drop or rewrite the existing business, template or record tables. Existing businesses created before authentication have no owner membership and therefore remain inaccessible through authenticated endpoints until ownership is assigned through a controlled administrative process. After the intended user registers, use `backend/scripts/assign_legacy_business_owner.py` with each verified business UUID; do not automatically assign legacy business data to the first person who registers.

## Scope and interpretation
Reports are calculated from saved records. Reconciliation differences are review signals, not proof of missing money or wrongdoing. This product does not currently claim to provide audited accounts or net profit calculations.

See [`DEPLOYMENT_AND_AI.md`](DEPLOYMENT_AND_AI.md) for hosted Gemma inference, optional Sentry tracing, Render configuration and deployment acceptance checks. AI extraction is review-only; it does not save records or confirm payments.

## AI business analysis and supplier invoices
- The AI Business Analyst is available from Reports. It sends an authenticated request for the selected business and period; the backend computes a report snapshot from saved data before Gemma writes a narrative. The model cannot submit SQL or modify records through this workflow.
- Supplier invoices created from the AI investigator are persisted in the dedicated `supplier_invoices` table only after the user selects **Confirm and save invoice**. Their invoice total, amount paid, calculated outstanding amount, supplier, date, reference and source note are retained separately from generic purchase records to avoid silent double counting.
- After updating an existing database, apply the additive migration from `backend/`:

```powershell
alembic upgrade head
```

- Browser voice input uses the Web Speech API when supported by the browser and microphone permissions. Typed notes remain available as a fallback.
