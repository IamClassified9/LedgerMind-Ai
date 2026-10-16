# LedgerMind AI — Controlled Frontend Amendment

## Changes in this delivery

- Overview now has its own **LedgerMind Business Analyst** question panel, with independent question, answer, loading, and error state.
- Invoice/payment-note extraction and review/save workflow moved from Overview to **Records** and renamed **LedgerMind Investigator**.
- Reports retains its separate **LedgerMind Business Analyst** panel for analysis of calculated records and the selected reporting period.
- AI analysis output in Overview and Reports now renders Markdown headings, bold text, inline code, and bullet lists as readable UI content.
- Textareas and related form controls use the existing dark-green workspace palette to prevent the bright white input-bar appearance.
- Existing voice-note input, invoice review fields, save action, export controls, record summaries, and report calculations were not intentionally changed.

## Validation

- `tsc -b`: passed in the supplied project environment.
- `npm run build`: not fully verified in this Linux validation environment because the uploaded `node_modules` tree is platform-specific and is missing Rollup's Linux native optional dependency `@rollup/rollup-linux-x64-gnu`. The Vite build therefore could not run here. Reinstall dependencies on the target machine with `npm ci` (or `npm install` if needed), then run `npm run build`.
- No live API, database, or AI provider integration tests were run as part of this frontend-only amendment.

## Packaging and secrets

- `.env` files, dependency directories, Python bytecode/cache folders, pytest cache, and generated frontend `dist` output are excluded from the delivery archive.
- Keep local credentials in your local `.env` files; use the included `.env.example` files for configuration reference.

## Follow-up amendment — 2026-10-15

- Renamed the Overview general-inquiry assistant to **LedgerMind Assistant**. The Reports page retains **LedgerMind Business Analyst**.
- Cleared the Reports analyst's prefilled question so the instructional text is a placeholder and disappears when the user types.
- Added a separate **Speak question** voice-input control to the Overview assistant, keeping the existing Records voice-note behavior unchanged.
- Updated Records empty-state guidance to point to LedgerMind Investigator within Records.
- Receipt-photo extraction is intentionally not included in this amendment: it needs a dedicated upload and backend image-processing path, followed by review-before-save and integration tests. No nonfunctional upload control has been added.

### Verification

- ZIP contents and source changes inspected.
- `npm run build` attempted in the isolated environment but could not complete because the archive's partial `node_modules` tree lacks TypeScript type definition packages (including React types). This is an environment/dependency limitation; the build is not claimed as passed.
- Browser runtime, microphone permissions, and live backend integration have not been verified in this environment.
