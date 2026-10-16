# LedgerMind AI — Business Onboarding

This milestone adds the first persisted product workflow: create a restaurant or supermarket and provision that business's starter record templates.

## API endpoints

- `GET /api/v1/business-types` — list supported types.
- `POST /api/v1/businesses` — create a business and its starter templates in one transaction.
- `GET /api/v1/businesses/{business_id}` — retrieve a business.
- `GET /api/v1/businesses/{business_id}/templates` — list its starter templates.

The initial business types are deliberately limited to `restaurant` and `supermarket`. Template field definitions are stored as JSON so they can be made customizable later. This milestone does not yet implement authentication, record-entry endpoints, OCR, or AI analysis.

## Apply the database migration

From the `backend` directory, with the existing virtual environment activated and `.env` configured:

```powershell
python -m alembic upgrade head
```

## Run tests

From the `backend` directory:

```powershell
python -m pytest
```

The onboarding tests use an isolated in-memory SQLite database. They do not modify the configured PostgreSQL database.
