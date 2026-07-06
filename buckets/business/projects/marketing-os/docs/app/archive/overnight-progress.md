# Overnight Progress

Date: 2026-06-01

## Completed

- Created the first real Sandi project: `Declassified Cases`.
- Superseded the earlier generated Phase 0 and Phase 1 outputs because they assumed a finished product too early.
- Reset Declassified to an idea-only Phase 0 seed.
- Added project workspace route for organized access to generated outputs:
  - `app/projects/[projectId]/page.tsx`
- Replaced Phase 0 direction with a guided Project Setup Agent:
  - conversation-first intake
  - visible Project Foundation Draft
  - generated drafts only after review
  - Phase 1 locked until `Phase 0 Brief` is approved
- Added optional app-to-n8n automation boundary:
  - `app/api/automations/phase-artifact/route.ts`
- Added persistent dark/light theme support.
  - Component: `components/app/theme-toggle.tsx`
  - Tokens: `app/globals.css`
  - Preference: `localStorage["sandi-theme"]`
- Connected dashboard behavior to auth state.
  - Reads current user through `lib/api/auth.ts`.
  - Uses real Supabase project queries only when a user session exists.
  - Shows a login callout when unauthenticated.
- Prepared local n8n workflow exports.
  - `Sandi - Phase 0 Draft Assistant`
  - `Sandi - Phase Artifact Webhook`
  - `Sandi - Lesson Capture Webhook`
  - `Sandi - Daily Project Digest`

## Verification Targets

- `npm run verify`
- `npm run build`
- `npm run test:e2e`
- Visual QA:
  - `/`
  - `/dashboard`
  - `/projects/:id`
  - `/projects/:id/phase-0`
  - `/projects/:id/phase-1`

## Current Product Rule

n8n can support orchestration and draft assistance, but official Phase 0 persistence stays in Sandi until the user approves each section.
