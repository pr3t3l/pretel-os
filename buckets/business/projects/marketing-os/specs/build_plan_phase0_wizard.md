# Build Plan — Phase 0 Wizard en `sandia-marketing` (slice D-024)

**Status:** v1.0 propuesto (2026-06-10) · **Gate de arranque:** D-024 disparado por D-029
**Doctrina que gobierna:** `spec_UX_Experience.md` (la experiencia es el producto) + `spec_Phase_0_Setup_Agent.md` (6 movimientos) + `SOUL_setup_agent.md` (carácter) + design system (`docs/design-system.md` + zip de Claude Design) + guiones validados en vivo (`run/sandi/` = el fixture CAG).

---

## 0. Estado real del repo (inventario verificado 2026-06-10)

- **Stack:** Next.js 16 App Router + React 19 + TS + Tailwind + shadcn-style local · Supabase (SSR clients en `lib/supabase`, 4 migraciones aplicables incl. `avatars_strategies`) · TanStack Query + Zustand · `@anthropic-ai/sdk` ya en deps · Playwright + Vitest.
- **Plomería M0 existente:** `lib/schemas/foundation-brief.ts` (Zod + merge-patch RFC 7396 + REQUIRED_SLOTS), `lib/prompts/setup_agent/v1` (system+examples), `lib/api/*` (projects/artifacts/decisions/lessons/auth/llm con pricing), `renderDraft` (un solo shaper), AppShell + theme + tokens.
- **Diseño (zip Claude Design):** chrome completo (rail lifecycle 0→5 + stepper de sub-pasos + topbar + panel derecho Ayuda/Signal-rules/Decisiones) + tokens watermelon dark + screenshots wizard/dashboard. **Es formulario-wizard; le falta el alma conversacional.**
- **Reglas duras del repo:** UI nunca llama `supabase.from()` directo; data access solo vía `lib/api`; cambios de DB solo por `supabase/migrations`; `npm run verify` es el gate.

## 1. LA decisión de diseño: fusión mockup + 6 movimientos ("wizard conversado")

El mockup aporta el **chrome**; el Setup Agent spec aporta el **alma**. Cada sub-paso del wizard se construye con el patrón canónico de `spec_UX_Experience.md` §2: beat de Sandi (2-3 frases, capturar/reflejar/flag calibrado) → UNA decisión (controles del mock como opciones sugeridas = reconocer>recordar) → tarjetas de propuesta accept/edit/discard (co-crear) → CTA único + draft guardado → panel derecho glass-box. Anti-meta vigilado: sin los 6 movimientos es Typeform.

**Capa de inteligencia V1 (decisión propuesta):** HÍBRIDO guion+LLM.
- Los **beats estructurales** de cada sub-paso salen del guion validado en el run (textos semilla versionados en `lib/prompts/setup_agent/`) — deterministas, baratos, evaluables.
- El **LLM entra solo donde el guion no alcanza**: reformular la respuesta libre del usuario, detectar flags adaptativos (ej. "las dos" → sub-pregunta), y el movimiento 6 (propuestas co-creadas). Vía `lib/api/llm/complete.ts` existente (Anthropic SDK), `temperature` baja, salida estructurada (merge-patch al brief).
- Razón: control de costo/latencia (P3: feedback <100ms en UI, LLM solo en momentos con narración), evals reproducibles, y el run/sandi como CAG de los prompts.

## 2. Milestones (cada uno termina verde: `npm run verify` + e2e del slice)

### M1 — Fundación UX (el chrome con física)
1. Motion tokens (`--motion-tap/step/panel/celebrate`) en `globals.css` + util `transition-step` (CSS-first; `framer-motion` SOLO si el slide direccional + shared-element lo exige — decidir en M1, no antes).
2. Wizard chrome reutilizable: `<WizardShell>` (rail lifecycle + stepper endowed + "Paso N de M" + panel derecho colapsable + chip borrador) sobre AppShell/design tokens existentes.
3. Transición entre sub-pasos: slide direccional 220/180ms, dirección = dirección del flow.
4. Componentes del alma: `<SandiBeat>` (texto con voz), `<SourceChip>` (📊 dato / 💭 inferencia), `<ProposalCard>` (✓/✏️/✕), `<GateSignature>` (ritual de firma), `<ThinkingNarration>` (espera narrada).
**Done cuando:** Storybook-less demo route con los 5 componentes + transiciones funcionando; tokens auditados vs design system.

### M2 — Slice vertical 0.1 Business Context (end-to-end real)
1. Supabase smoke (paso 1 de Overall_WF §next steps): migraciones aplicadas en el proyecto Cloud, login + create project funcionan (`.env.local` ya existe — verificar).
2. Las 4 preguntas llanas de 0.1 (guion spec §4: quién paga / cómo cobras / cómo deciden / dónde están) como 4 beats, con flags adaptativos (híbrido→cuál lidera; freemium→nombrar patrón; internacional→foco) — los MISMOS que vivimos en el run.
3. Persistencia: respuestas → merge-patch → `ProjectFoundationBrief` (schema existente) → `project_phase_artifacts` vía `lib/api/artifacts.ts`; draft permanente (P3).
4. Gate G-0.1 con `<GateSignature>` → status `approved` → victoria nombrada (P7) → desbloquea 0.2 en el rail.
**Done cuando:** un usuario real crea proyecto y cierra 0.1 completo sin tocar jerga; e2e Playwright del flow; brief en DB.

### M3 — 0.2 Mercado + 0.2.5 ICP (show-and-confirm + propuesta)
- 0.2 cambia el tono (spec §6 stub): **Sandi trae datos** — `<ThinkingNarration>` mientras corre el research (V1: server action con plantilla de research + LLM; fuentes citadas con `<SourceChip>`), presenta TAM/awareness/cuña en cards confirmables. Math gate visible y simple.
- 0.2.5: la propuesta de filtros como `<ProposalCard>`s editables (la tabla que usamos en el run, hecha UI) + deal-breakers + gate.
**Done cuando:** flow 0.1→0.2.5 corrido de punta a punta por el operador con un producto real (¡dogfood run #2: la app de realtors!).

### M4 — 0.3 Persona + Avatares (la joya en UI)
- Retrato del persona (research asistido) → cards de avatar con la historia de 60 segundos + Forces colapsables (P1: revelación progresiva).
- Test 2-de-3 visual al crear/editar avatar. Priorización de primer ciclo = decisión humana con ritual.
- Negative personas (2 tarjetas, base ética visible — honestidad arquitectónica).
**Done cuando:** los 4 avatares del run Sandi se pueden recrear en la UI y el resultado JSON ≅ `run/sandi/avatars.json`.

### M5 — 0.4 Competencia + Rollup (cierre de fase con pico)
- Scan presentado por canal (4 tabs) + pricing tiers + veredicto ERRC + decisión del hueco (ProposalCard).
- `product_brief_v2` rollup en pantalla "Tu Fundación" (la inversión visible del usuario, P6) + firma final → **celebrate 400ms** + handoff a Phase 1 ("qué sigue").
**Done cuando:** Phase 0 completo navegable; gate global reproduce las reglas del spec (≥1 refutada, ECONOMICS-001, etc.).

### M6 — Evals + pulido (la prueba de que la UX es real)
- Playwright: flow completo + drop-off instrumentado (métricas spec UX §4). Character evals del agente vs SOUL (fixture: run/sandi + caso D-023 "semantic catch"). Estados vacíos/error con voz Sandi. Perf budget: feedback <100ms.

## 3. Orden y paralelismo

M1→M2 son secuenciales (el chrome primero). M3–M5 dependen de M2 pero entre sí son mayormente secuenciales (cada fase consume la anterior). La sim de Phase 1 (carril c) puede correr en paralelo desde que M2 esté en marcha — pipeline de un paso de desfase (D-024).

## 4. Decisiones abiertas para el operador

| # | Decisión | Recomendación |
|---|---|---|
| B1 | Capa LLM V1: ¿híbrido guion+LLM (arriba) o LLM full desde día 1? | Híbrido (costo/latencia/evals; CAG listo) |
| B2 | Motion: ¿CSS-first o framer-motion desde M1? | CSS-first; framer-motion solo si el shared-element lo pide |
| B3 | ¿Dogfood del M3 con la app de realtors como run #2 (BP-001)? | Sí — mata dos pájaros (D-024 ya lo propone) |

## 5. Riesgos nombrados

- **Supabase Cloud sin smoke previo** — M2.1 lo ataca primero; si el proyecto Cloud no existe/expiró, se crea antes de cualquier UI.
- **El alma se diluye al codear** (anti-meta): cada PR de M2–M5 se revisa contra los 6 movimientos + never-dos del spec UX.
- **Scope creep del dashboard**: el mockup trae dashboard multi-proyecto rico; V1 construye SOLO lo que el flow Phase 0 necesita (proyectos list mínimo + wizard). Lo demás espera.
