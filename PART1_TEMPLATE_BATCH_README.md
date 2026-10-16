# LedgerMind AI — Part 1 template batch

This batch adds template-only workspaces for Contractor, Hotel, Farm, Rental Property, School, Salon, Training / Courses, and Pharmacy. Clinic is intentionally excluded.

## Farm grouping

Every farm receives two shared templates: **Farm Operations** and **Farm Money In and Out**. During creation, select any combination of **Crops**, **Livestock**, and **Poultry**. Only the selected modules' templates are provisioned in that farm workspace. The selection is represented by the generated template set; no separate farm-module database table or domain workflow is added in this template-only phase.

## Apply on Windows

1. Back up or commit the current project first.
2. Extract this archive over the project root, preserving paths. Do not replace any `.env` files; none are included.
3. Apply the migration:

```powershell
cd C:\Users\User\Desktop\ledgermind-ai\backend
.\.venv\Scripts\python.exe -m alembic upgrade head
```

4. Run backend tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

5. Build the frontend:

```powershell
cd C:\Users\User\Desktop\ledgermind-ai\frontend
npm run build
```

## Before-and-after checks

Existing template provisioning remains unchanged: Restaurant 6 templates, Supermarket 8, Trucking 6. New template counts: Contractor 3, Hotel 3, Farm 2 shared plus 2 per selected module, Rental Property 3, School 3, Salon 3, Training 3, Pharmacy 3.

Automated regression tests assert existing restaurant/supermarket/trucking template provisioning and test each new business type plus farm module selection. Run them on Windows with the command above. The migration changes only the `businesses.business_type` check constraint and preserves existing rows.

## Scope

Template data and workspace creation only. This does not add new specialized business logic, new reporting formulas, or clinic functionality. Existing `.env` files, `node_modules`, generated `dist`, caches, and virtual environments are not included in the archive.
