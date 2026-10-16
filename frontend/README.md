# LedgerMind AI Frontend

React + TypeScript + Vite dashboard for the LedgerMind AI API. The initial release supports restaurants and supermarkets.

## Requirements
- Node.js 20 or newer
- The LedgerMind AI backend running at `http://127.0.0.1:8000`

## Run locally (PowerShell)
```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```
Open `http://localhost:5173`.

If the API is running at a different address, change `VITE_API_BASE_URL` in `frontend/.env` to the backend's `/api/v1` URL. The backend's `CORS_ORIGINS` should include `http://localhost:5173`.

## Build check
```powershell
npm run build
```

## Current functionality
- Registration, sign-in and sign-out with API-issued bearer sessions.
- Protected account profile, profile-name updates and password changes.
- Server-enforced business membership isolation; the UI lists only authorized businesses.
- Connects to the existing health, business, template, record and report endpoints.
- Creates restaurant/supermarket workspaces.
- Creates validated records using each template's field definitions.
- Shows reporting totals, previous-period comparison, daily activity and reconciliation warnings.
- Searches recent records and filters daily/weekly/monthly/yearly summaries.

The frontend uses the API contract and does not create or modify the database schema. Authentication requires the backend migration `0003_authentication` to be applied before first use.

For fresh setup, copy `.env.example` to `.env` if the backend is not at the default API URL. The Reports page includes the database-grounded AI analyst; the Overview page includes typed and supported-browser voice invoice interpretation. AI-extracted supplier invoices are not saved until explicitly confirmed.
