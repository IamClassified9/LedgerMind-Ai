# LedgerMind AI: Gemma, Sentry and Render

## What is implemented in this build

- Registration, login/logout, profile editing and password changes using revocable bearer sessions. Passwords are hashed; raw session tokens are not stored in PostgreSQL.
- Server-side business membership checks for business, template, record, report, intelligence and AI endpoints. Apply Alembic migration `0003_authentication` before starting the updated app. Existing pre-authentication businesses are preserved but require controlled ownership assignment before authenticated users can access them. After the verified owner registers, an administrator can use `backend/scripts/assign_legacy_business_owner.py` with the owner email and each verified business UUID.

- `POST /api/v1/ai/interpret-record`: sends a business note to hosted Gemma, validates the JSON shape and numeric amounts, and returns a **review-required suggestion**. It never saves records or declares payment confirmed.
- Optional Sentry SDK initialization and a `gen_ai.request` span around model inference. Set `SENTRY_DSN` to enable it; never enable PII collection for this workflow.
- `render.yaml` describing an API service, static frontend and managed PostgreSQL database.
- Dashboard panel to submit a supplier/invoice note and inspect the model's proposed structured extraction.

## Local configuration

1. Keep your existing `backend/.env` and database credentials private. Add these values to it (do not commit `.env`):

   ```dotenv
   GEMMA_API_KEY=your_provider_key
   GEMMA_MODEL=gemma-3-4b-it
   GEMMA_API_BASE=https://generativelanguage.googleapis.com/v1beta
   SENTRY_DSN=your_sentry_project_dsn
   ```

2. Create a provider key with access to the chosen Gemma model. Verify that the model is available to your account before assuming inference works. Provider quotas and terms apply.
3. Install backend dependencies in the existing virtual environment from `backend` with `pip install -e ".[dev]"`.
4. Run migrations and the API from `backend`:

   ```powershell
   alembic upgrade head
   python -m uvicorn app.main:app --reload
   ```

5. From `frontend`, set `VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1` in a local `.env` file, then run `npm install` and `npm run dev`.
6. Open the dashboard's **AI record investigator** and try: `Invoice from Frank: NGN 50000. Paid NGN 40000. Balance remains unpaid.` Confirm that the model extracts the facts and that a human must review the result.

The API uses a direct HTTP request to the Google Generative Language API to avoid adding a large model runtime to the user's computer. This is hosted inference, not local inference. Verify current Gemma model access and licence/terms for the selected version before submission. Do not send real customer financial records to a third party without informed authorization.

## Render deployment

1. Push this project to a Git repository you control.
2. In Render, create a **Blueprint** from that repository and select `render.yaml`.
3. Supply `GEMMA_API_KEY` and `SENTRY_DSN` as secrets in the API service's environment. Never commit them.
4. Check the generated frontend/API hostnames. If Render assigns different URLs, update `CORS_ORIGINS` on the API service and `VITE_API_BASE_URL` on the static frontend, then redeploy the frontend.
5. Confirm `/api/v1/health/live`, `/api/v1/health/ready`, onboarding, record creation, reports and the AI interpretation endpoint. The AI endpoint must return a clear configuration/provider error if Gemma is unavailable.
6. Confirm migrations run successfully against the managed database before using production data. Back up any existing database before applying production changes.

Render blueprint hostnames and external provider credentials cannot be verified from this source package alone. Do not claim the app is deployed until the public URLs have been tested.

## Sentry

Create a Sentry project for the Python/FastAPI API and copy its DSN into `SENTRY_DSN`. The integration captures API performance traces and adds a model-inference span. It does not deliberately attach request bodies or customer financial notes. Confirm a test event/trace appears in Sentry before claiming the partner integration is verified.

## Current limitations

- AI output is not automatically saved; there is no model-driven write to financial records.
- Invoice/payment balances and duplicate/stock discrepancy rules are not yet implemented by this AI patch.
- Model output needs review; the application does not verify that money actually moved.
- No live model call, Render deployment, or Sentry dashboard verification was possible from this build environment. Run the above acceptance checks before claiming these work.
