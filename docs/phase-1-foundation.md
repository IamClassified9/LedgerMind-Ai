# LedgerMind AI — Phase 1: Backend Foundation

## Scope

This bundle establishes the backend service foundation only.

Included:
- FastAPI application and API router
- Environment-based settings
- SQLAlchemy engine and session dependency
- Liveness and database-readiness endpoints
- Alembic configuration
- Initial automated tests
- Backend setup documentation

Not included yet:
- Authentication or authorization
- Restaurant or supermarket workspace creation
- Business templates or custom fields
- Transaction tables
- Document upload or AI inference
- Financial calculations or reconciliation
- Frontend implementation

## Verification

Run `python -m pytest` from `backend/`. The tests cover service identification,
liveness, OpenAPI availability, and settings defaults. They do not claim to
verify PostgreSQL connectivity; `/api/v1/health/ready` checks that at runtime.
