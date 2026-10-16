# LedgerMind AI — Part 1: Trucking workspace

This is a targeted patch, not a full project archive. It contains only the files changed/added for the trucking business type. It does not contain or modify `.env` files.

## What it adds

- A `Transport / Trucking` option when creating a business workspace.
- Six data-driven starter templates: Trip Register, Truck Fleet, Trip Expenses, Money In and Out, Service and Maintenance, and Drivers and Staff.
- A database migration that expands the business-type check constraint to allow `trucking` while preserving existing restaurant and supermarket rows.
- Backend regression tests for the supported business types and trucking template provisioning.
- A trucking icon and description in the workspace selector.

## Apply on Windows

1. Stop the backend and frontend development servers.
2. Back up the project folder or commit your current work.
3. Extract this ZIP into `C:\Users\User\Desktop\ledgermind-ai`, preserving the folder paths and allowing the listed files to be replaced. Do not replace or edit any `.env` file.
4. Open PowerShell and apply the database migration:

```powershell
cd C:\Users\User\Desktop\ledgermind-ai\backend
.\.venv\Scripts\python.exe -m alembic upgrade head
```

5. Run backend regression tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

6. Check the frontend TypeScript and production build:

```powershell
cd C:\Users\User\Desktop\ledgermind-ai\frontend
npm run build
```

## Manual acceptance check

1. Start the backend and frontend as usual and sign in.
2. Open the workspace selector and create a business with type `Transport / Trucking`.
3. Open Record templates and confirm the six trucking templates appear.
4. Create a trip record with a trip reference, customer, driver, truck registration, pickup/delivery locations, trip status, fare, amount received, payment method and payment status. Confirm the saved record appears in the records list.
5. Create a Service and Maintenance record and confirm next service date and service cost can be saved.
6. Switch to an existing restaurant workspace and verify its six original templates remain. Create/open a daily sales record and check reports.
7. Switch to an existing supermarket workspace and verify its eight original templates remain. Open/create a product or sales record and check reports.

## Verification status from the patch authoring environment

- Python syntax compilation: passed for changed Python files.
- Backend automated tests: 30 passed using an in-memory SQLite test setup and a temporary `DATABASE_URL` environment override; no `.env` file was changed.
- Alembic migration history: the new migration is the single head after `0004_supplier_invoices`.
- Template sanity check: restaurant 6, supermarket 8, trucking 6 templates.
- Frontend TypeScript build step (`tsc -b`): passed.
- Full Vite production build: could not be completed in this Linux environment because the archive's `node_modules` lacks the Linux Rollup optional dependency. Run `npm run build` on your Windows machine to verify with your platform's dependencies.
- Live PostgreSQL migration and manual browser workflow: not run here; verify using the commands and acceptance steps above.
