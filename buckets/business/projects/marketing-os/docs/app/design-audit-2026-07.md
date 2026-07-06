# Design Audit — Full App vs. Design System (2026-07-02)

**Baseline:** the canonical design system = `Papandi Brand Identity` (standalone) + the Claude Design project export (`Sandia Marketing (2).zip`): tokens (dark/light), 46-icon line set (24×24, stroke **1.75**, rounded, currentColor), Geist Sans/Mono, radii/shadows/glow, motion, and the principles — *one coral CTA per view, mono for IDs/gates, warm neutrals, no pure black/white, controlled glow, glass-box (data vs inference visibly distinct), no broken windows (no dead controls), honest states.*

**Method:** mechanical sweep (raw hex, naming, icon inventory, stroke widths) + page-by-page review of all 11 routes and app chrome.

---

## Scorecard

| Surface | Score | Verdict |
|---|---|---|
| **Estudio** (`/projects/:id/estudio`) | **10/10** | Redesigned today from `Estudio Redesign.html`. Reference implementation. |
| **Calendar** (`/calendar`) | 9/10 | Ported design (`cal-*`), token-clean. Only the `Sandi` crumb. |
| **Landing** (`/`) | 9/10 | Rebuilt on tokens; a few icons outside the canonical set (see icons). |
| **Dashboard** | 7.5/10 | Pattern ✓, spotlight ✓ — but **fake phase state** (see P0). |
| **Project hub** (`/projects/:id`) | 8/10 | Header pattern ✓, cards ✓. `Sandi` crumb. |
| **Phase 0 / 1 / 2** | 8/10 | Wizard system is spec-driven and consistent. `Sandi` copy everywhere (user-visible). |
| **AppShell** (chrome) | 7.5/10 | Brand lockup ✓, honest phase rail ✓, glass ✓ — but dead buttons + hardcoded user. |
| **Login** | **5/10** | Weakest page: naming, language, a nonexistent token, CTA hierarchy, zero brand warmth. |
| **Radar** | 6/10 | Breaks the page-header pattern (raw 20px `h1` + emoji, no eyebrow); needs the estudio treatment. |
| `dev/ux` | exempt | Demo route; its own comment says delete post-M2. |

**Token compliance is excellent** — only 3 raw hex in all TSX (`#0a0a0a` themeColor in layout — should be `#100F0D`; `#888888` editor default; `#FFFFFF` canvas overlay text) — everything else runs on `var(--token)`.

---

## Findings

### P0 — Bugs (fix regardless of any redesign)
1. **Login uses a token that doesn't exist**: `text-[var(--muted-foreground)]` (a shadcn name, not in our system) → status text silently unstyled. → `var(--text-muted)`.
2. **Dashboard shows fake state**: every project card hardcodes "Fase 0 · Conocer tu negocio" + a first-segment progress bar, regardless of the project's real phase. Direct violation of the honesty/glass-box principle ("the shell doesn't fake completion" — the AppShell comment says it; the dashboard does the opposite). → wire real phase status or show neutral until known.
3. **Dead controls in the topbar**: Search and Bell do nothing. The codebase already names this principle ("a control that does nothing is a broken window" — the removed LanguageToggle comment) and then ships two of them on every page. → hide until real.
4. **`themeColor: "#0a0a0a"`** in layout metadata → `#100F0D` (brand bg), so the mobile status bar matches the app.

### P1 — Brand consistency
5. **The Sandi→Papandi rename (the big one).** "Sandi" survives in ~40+ places, many user-visible: login title ("Sign in to Sandi"), the first crumb on every page, wizard copy ("Que Sandi investigue tu mercado", "La sugerencia de Sandi", "qué cuidó Sandi"), `SandiBeat` component. The sidebar says **Papandi.com** while the breadcrumb says **Sandi** — two brands on one screen.
   → Sweep in two passes: (a) user-visible strings (crumbs, login, buttons, wizard copy) — mechanical; (b) internal names (`SandiBeat`, comments, API docstrings) — opportunistic.
6. **Login page needs the brand treatment**: Spanish (the app's language), one coral CTA (Google → ghost/outline per "one coral CTA per view"), aurora backdrop or brand panel, "Inicia sesión en Papandi".
7. **Radar header breaks the canonical page pattern** (eyebrow + `ds-h1` + caption). Also uses emoji (📅) where the icon set exists.

### P1 — Icon discipline
8. **Stroke width**: all lucide icons render at default **2**; the spec is **1.75**. → central fix (see playbook #3).
9. **Icons outside the canonical 46**: `Radar` (→ `target`/`compass`), `Pencil`/`PenLine` (no edit icon in the set), `Eye`, `ShieldCheck`, `BarChart3` (set has `chart`), `CalendarClock` (set has `calendar` + `clock`), `Grid2X2` (fine ≈ `grid`).
   → Decision needed: swap to set members **or** deliberately extend the standalone with ~4 icons (`edit`, `eye`, `shield`, `radar`) — extending the source of truth is better than contorting the UI; do it in Claude Design so the spec stays canonical.

### P2 — Polish
10. Hardcoded identity in the shell ("Alfredo P." / "AP") → session user.
11. `#888888` default color in the palette editor → a neutral token.
12. Delete `dev/ux` once M2 review value is exhausted (its own stated plan).

---

## Maintenance playbook (how this stays a 10/10)

1. **One source of truth.** The Claude Design project (tokens.css + Brand Identity page) is canonical. Changes happen THERE first → re-export zip → mirror into `globals.css`. Never invent a hex/radius/shadow in TSX.
2. **Port pattern for new surfaces.** Design the screen in Claude Design → export → port as a namespaced CSS section (`est-`, `cal-` precedent) + real data wiring. Keep the export zip's `screenshots/` as the visual reference for review.
3. **Icon registry as a compile-time lock.** Add `components/ui/icon.tsx`: wraps lucide with `strokeWidth=1.75` default and a **typed union of allowed icon names** (the canonical set). TypeScript then rejects any random icon at build time — a candado, not a convention.
4. **Guard script** (same pattern as `check-supabase-imports`): `scripts/check-design-drift.mjs` failing the build on (a) raw `#hex` in `app/**/*.tsx` + `components/**/*.tsx`, (b) `strokeWidth` ≠ 1.75, (c) the word `Sandi` (post-rename), (d) tokens referenced that don't exist in `globals.css` (catches bugs like `--muted-foreground`). Wire into `npm run verify`.
5. **Canonical page header** (document + enforce by review): `ds-eyebrow` → `ds-h1` → `ds-caption`, then content. Radar is today's counterexample.
6. **Honest-state rule**: no hardcoded progress, counts, or identities. If the data isn't wired, show neutral (the AppShell phase rail is the good example).
7. **One coral CTA per view** — everything else ghost/outline. Quick self-check on every new screen.

---

## Suggested execution order
1. **P0 batch** (bugs: ghost tokens, dashboard fake state, dead buttons, themeColor) — small, immediate.
2. **Rename sweep** (user-visible Sandi → Papandi) + login brand treatment.
3. **Icon lock** (Icon wrapper + stroke 1.75 + swaps/extension decision) + guard script into `verify`.
4. **Radar header** to the canonical pattern.
5. P2 polish opportunistically.

---

# Addendum — Deep audit: Phases 0/1/2 + wizard chrome (3 parallel auditors, 2026-07-02)

## Revised scorecard
| Surface | Score | Headline |
|---|---|---|
| Phase 0 (terreno/mercado/personas/puerta/cancha) | **7.5/10** | Soul excellent; 1 raw `#fff`, 8 visible "Sandi", stage switches without motion classes |
| Phase 1 (equation/offer/paquete) | **6/10** | Ghost tokens ×4 + glass-box gaps in pricing/cost views |
| Phase 2 + wizard chrome | **6.5/10** | Ghost token `--text` ×2, mute-spinner fallback (P3), missing header caption |

## Ghost tokens — full app sweep (systematic, all TSX vs globals.css)
Silent visual bugs: the browser ignores the declaration (or uses a fallback), so these render wrong TODAY.

| Token (doesn't exist) | Where | Fix |
|---|---|---|
| `--muted-foreground` | login | → `--text-muted` |
| `--danger` (×2) | equation-step, paquete-thread | → `--error` |
| `--surface-subtle` (×2) | equation-step | → `--surface-elevated` |
| `--bg-subtle` | phase-2 page (has rgba fallback) | → `--surface-elevated` or define the token |
| `--surface-1` (many) | **estudio page + overlay-composer** — all panel/input backgrounds | → `--surface-elevated` |
| `--text` (×2) | phase2-thread (hook edit/regen hover) | → `--text-primary` |

## What the deep audit CONFIRMED is excellent (keep, and protect)
- **SourceChip discipline in Phase 0** — every researched number wears `dato` or `inferencia` (mercado/personas/puerta/cancha). Nothing disguises inference as fact.
- **Narrated waits** — ThinkingNarration on every long mutation in Phase 0/1, with honest time notes ("~3 min"). One exception below.
- **ProposalCard / GateSignature** — reversibility ("¿Cambiaste de opinión?"), two-step signing, mono gate IDs, celebrate-pop. Reference-quality co-creation UI.
- **wizard-shell** uses `step-enter-fwd/back` correctly; `step-conversation` respects `prefers-reduced-motion` and caches seen-state.
- **Amendment doctrine** (enmienda re-opens, never silent-edits) implemented cleanly in all three phases.

## New findings (beyond the ghost tokens)
1. **Glass-box gaps in Phase 1's paquete-thread**: the price study and cost breakdown render researched figures with NO SourceChip (`PriceStudyView`, `CostEditor`) — the one place in the wizard where money data appears unlabeled. Phase 2's editors have the same gap in lighter form.
2. **Mute spinner fallback** in `step-thread.tsx`: when a step doesn't pass `busyLines`, the wait falls back to silent thinking-dots — violates "espera narrada" (P3). Fix: default narration lines.
3. **Stage switches inside Phase 0/1 steps have no motion** (the shell animates between steps; the stages within a step just reflow). Add `step-enter-fwd` to stage wrappers.
4. **wizard-shell header lacks the caption line** ("Paso N de M" is aria-only) — the canonical pattern is eyebrow → h1 → caption.
5. **"Sandi" in wizard copy is bigger than the first pass showed**: ~20 user-visible strings across the phases ("Que Sandi investigue/proponga/mapee/sugiera/la escriba", "La lectura de Sandi", "Propuesta de Sandi" in ProposalCard, SourceChip tooltip).
6. Phase 0 uses emoji semantically (🟢🟡🔴 verdicts, 🔵🔴 oceans) — consistent with the design's own emoji usage; keep.

## Consolidated P0 (updated)
1. Ghost tokens (6 tokens, ~40 usages) — mechanical replace.
2. Dashboard fake phase state.
3. Dead Search/Bell buttons.
4. `themeColor` → `#100F0D`.
5. Mute-spinner fallback → default narration lines.
