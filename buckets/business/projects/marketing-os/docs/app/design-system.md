# Sandi Design System

Use the reference package `Sandia Marketing.zip` as the visual source, but the product name is now **Sandi**.

## Permanent Rules

- Brand name in UI: `Sandi`, never `Sandia`.
- Default theme: dark; light theme is supported through `data-theme="light"` and `ThemeToggle`.
- Visual language: warm near-black surfaces, watermelon coral brand, bright watermelon green secondary, papaya progress accents.
- App shape: sidebar + sticky topbar + optional contextual right panel.
- Cards: 12px radius, subtle borders, low shadows, compact information density.
- Typography: Geist-like sans for UI, mono for IDs/gates/artifact names.
- Product workflows should look like an operational dashboard, not a marketing landing page.

## Canonical Tokens

- `--bg`: `#0f0e0d`
- `--surface`: `#1a1816`
- `--surface-elevated`: `#252321`
- `--brand`: `#ff5a6b`
- `--secondary`: `#4ade80`
- `--accent-warm`: `#ffb570`
- `--radius`: `8px`
- `--radius-card`: `12px`

## Implementation

- Global tokens live in `app/globals.css`.
- Shell primitives live in `components/app`.
- App pages should use `AppShell` unless they are auth-only pages.
- UI data access still goes through `lib/api`; visual work must not bypass architecture rules.
