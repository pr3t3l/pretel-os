# Build Plan — El Estudio de Ángulos (página NUEVA, desde cero)

**Estado:** v1 — para APROBACIÓN del operador antes de construir. **NO construir hasta el "dale".**
**Método (consejo del operador 2026-07-07):** Claude falla más EDITANDO código complejo existente que
construyendo de cero. Por eso: (1) inventario de todo lo que se REUSA del Estudio, (2) plan de la
página nueva, (3) construir de cero. **`/estudio` NO se toca NI se borra hasta la aprobación final.**
**Fuentes:** `build_plan_modelo_contenido.md` §4b (la card de ángulo) · lectura completa de
`app/projects/[projectId]/estudio/page.tsx` (1-1267) + `app/globals.css`.

---

## A. INVENTARIO — qué reúso del Estudio (sin tocarlo)

### A.1 Diseño / CSS (`app/globals.css` — compartido, riesgo CERO)
- **Cards:** `est-pcard` (+`.idea`, `.body`, `.title`, `.meta`), `est-grid`, `est-idea-top`, `est-idea-chip` (`.cd`), `est-idea-body` (`.i-title` `.i-note` `.i-foot`).
- **Grupos/tags:** `est-group-head` (`.gt` `.gc` `.rule`), `est-pillar-tag` (`.pd`), `est-status[data-s]` (`.sd`), `badge`/`badge-brand`/`badge-outline`.
- **Controles:** `est-btn-develop`, `est-btn-produce`, `est-mini-select`, `est-mini-btn`, `est-i-hint`, `est-chip[data-active]`, `est-fg-label`, `est-link-btn`, `copy-btn`, `icon-btn`, `Button`.
- **Drawer:** `est-scrim[data-open]`, `est-drawer[data-open]` (`dh`/`dh-eyebrow`/`dh-title`/`dh-meta`, `db`, `df`), `est-prog` (riel de progreso), `est-fold`, `est-hero`/`est-ph`/`est-ph-label`, `est-sec`/`est-sec-label`, `est-piece-box` (`pb-text`/`pb-foot`/`est-pb-chars`), `est-clip` (`clip-h`/`clip-n`/`clip-say`), `est-prompt-box`, `est-qa-list`/`est-qa-clean`, `est-toast`.
- **Calendario (para "Tu plan"):** `cal-*`.
- **Tokens:** `--brand`/`--secondary`/`--accent-warm`/`--info`/`--warning` + `FORMAT_META` (colores por formato).

### A.2 Helpers puros (`lib/` — compartidos; algunos ya extraídos)
- `lib/estudio/format-meta.ts` — `FORMAT_META`, `famOf`, `PILLAR_COLORS`, `pillarColorAt`, `STATUS_LABEL` *(ya extraído, Estudio-5)*.
- `lib/estudio/channel-formats.ts` — `channelFormatOptions`, `formatRotation` *(ya hecho, Estudio-2/3)*.
- `lib/estudio/estudio-choices.ts` — `coerceEstudioChoices`, `sugKey`, `withChoice`, `withSuggestions`, `EMPTY_CHOICES` *(reuso; SEAM: claves `pillar:index:goal` → `pillar:hookId:goal`)*.
- `lib/estudio/ratio.ts` — `pieceIntent` *(SEAM: +goal de la forma)*, `parseRatioPolicy`, `ratioStatus`.
- `lib/gateway/serialize.ts` — `asDesignSpec`, `serializeForGateway`, `videoClipPrompts`; `lib/gateway/video-routing.ts` — `VIDEO_MODELS`, `planGeneration`.
- **A COPIAR (puros, hoy dentro de estudio/page.tsx):** `pieceTitle`, `parseClips`.

### A.3 Componentes (COPIAR a `components/estudio/`, NO mover — `/estudio` queda intacto)
Ya son componentes autocontenidos dentro de `estudio/page.tsx`:
- **`EstudioDrawer`** (867-1253) — el drawer completo: header + `ProgressRail`; **video** (variantes con "Usar esta", cola `pending`, `failures`, selector `VIDEO_MODELS` con precio `planGeneration`, gate del Set de Rodaje, "Generar solo este clip"); **imagen** (hero/grid + `OverlayComposer` por slide + regenerar); guion/clips + `CopyButton`; **prompts de rodaje**; tips de publicación; **QA** (word_budget, removed, origen del brief, prompt técnico); barra de acciones (Aprobar/Producir/Generar · Rehacer · Eliminar).
- **`SuggestModal`** (773) — el modal de FORMA (E3) caché-primero.
- **`CopyButton`** (836), **`ProgressRail`** (853).
- Ya-shared (import directo): `AppShell`, `Button`, `OverlayComposer`, `RodajePanel`.
- **NO reuso:** `VisualIdentityPanel` — la identidad se mueve a su fase (spec Identidad); en Ángulos es read-only.

**Decisión (respeta "no tocar estudio"):** se COPIAN a archivos nuevos compartidos; `/estudio` sigue usando SUS copias inline. Duplicación transitoria → se elimina en el swap (al borrar `/estudio`). Cero riesgo sobre la página que amas.

### A.4 API routes (compartidas — cero cambio salvo el SEAM marcado)
`produce` (C17: `hookId`+`channel` — ya) · `suggest-hooks` *(SEAM: aceptar `hookId`)* · `produce-media` · `video-generate` · `video-status` · `visual-identity` · `listPieces`/`updatePiece`/`deletePiece` · `listArtifacts`/`upsertArtifact`.

### A.5 Datos / artefactos (mismo patrón de carga que el Estudio)
`personas` 0.3 (avatares) · `pillars` 2.3 · **`hook_library` 2.5 = LOS ÁNGULOS** (reemplaza a `atomization_map` 2.4 como fuente de la cola) · `channel_journey_matrix` 2.2 · `brand_visual_identity` 2.0.5 · `set_kit` rodaje · `hook_suggestions` (estChoices) · `pieces` (`listPieces`) → estado por `(hook_id, channel)`.

### A.6 Patrones a copiar tal cual
Queries (`current-user`/`artifacts`/`pieces`) · las 11 mutations (`develop`/`suggest`/`approve`/`produced`/`media`/`del`/`videoGen`/`videoStatus`+polling/`keep`/`vi`/`rodaje`) · persistencia de choices (`persistChoice`/`formSelView`/`hookSelView`) · toast/ping · scroll-lock del drawer.

---

## B. Qué es NUEVO (lo único que se diseña desde cero)

**La CARD DE ÁNGULO** (≠ la card de derivado del Estudio). Por cada gancho de 2.5:
- Shell `est-pcard idea` + el **ángulo como título** (`i-title`) + `template · hook_id` (`i-note`).
- **Badge dar/pedir** (derivado: modo del pilar, o `goal` de la forma si se eligió).
- **Chips de CANAL con ESTADO** (`channelFormatOptions` de 2.2): cada canal = un chip ○/◐/●/✓ (estado de esa pieza `hook×canal`, de `pieces`). ○ → despliega capas + Desarrollar. ◐●✓ → abre el drawer.
- **Capas condicionales por formato** (build plan §4b): 🎬 ESCENA (solo video, `VISUAL_HOOKS`) · 💬 FORMA (siempre, `SuggestModal`). Email/texto: sin selector visual.
- **Botón** `Desarrollar para «canal» →` → `produce {hookId, channel, visualHook?, hookTemplateId?, publishDate?}`.
- **Multi-canal = Etapa D integrada** (mismo ángulo → varios chips).

*(El grid por pilar, la galería de piezas y el drawer NO son nuevos — reúsan A.1/A.3.)*

---

## C. LA PÁGINA NUEVA

- **Ruta:** se reusa **`/projects/[id]/angulos`** (ya existe + ya está en el hub) → se convierte en el Estudio de Ángulos completo. `/estudio` queda como fallback intacto.
- **Estructura (client component, portado del Estudio):** `AppShell active="estudio"` → header `ds-h1` → filtros (avatar `est-chip`, opcional pilar/canal) → **ratio strip** (reuso) → **grid de ángulos por pilar** (B, agrupado con `est-pillar-tag`) → **galería de Piezas desarrolladas** (`est-pcard`, reuso) → **`EstudioDrawer`** (copiado) → **`SuggestModal`** (copiado) → `RodajePanel` (import) → toast.
- **Estado/mutations:** copiados del Estudio, adaptados al camino C17 (`hookId`+`channel` en vez de `derivativeIndex`).

---

## D. FASES DE BUILD (verificables · `/estudio` vive en cada una)

> **ESTADO 2026-07-08 — N1, N2a, N2b+N3 HECHOS y desplegados** (sandia `116eea9`, `dbe8f72`, `4425b2a`).
> `git diff` sobre `estudio/page.tsx` **vacío en cada commit** — la regla dura se cumplió.
> Falta: **N5** (paridad/pulido con el operador) y el **SWAP** (aprobación final).

- **N1 · Shared components.** Copiar `EstudioDrawer`/`SuggestModal`/`CopyButton`/`ProgressRail` a `components/estudio/piece-drawer.tsx` (+ `pieceTitle`/`parseClips` a `lib/estudio/`). `verify` verde; `/estudio` intacto (usa sus copias).
- **N2 · La card de ángulo.** El grid de ángulos por pilar con chips de canal-estado + capas condicionales + badge dar/pedir. Sin drawer aún (Desarrollar → toast).
- **N3 · Piezas + drawer.** La galería de piezas desarrolladas (`est-pcard`) + el drawer copiado (aprobar/producir/video/overlay). Flujo completo.
- **N4 · Los seams.** `suggest-hooks` acepta `hookId`; `pieceIntent(mode, formGoal?)`; claves de choices por-gancho; retirar contadores de "cola/multiplicar" (pozo generativo).
- **N5 · Paridad + pulido.** Comparar lado a lado con `/estudio`; ajustar hasta que se sienta igual.
- **SWAP (solo con tu APROBACIÓN FINAL):** el hub apunta aquí; `/estudio` → redirect o borrado; "Tu plan" → al Calendario (swap generativo); P5 (borrar 2.4/`AtomizationMap`/`rotateHook`/plan finito + migrar).

---

## E. REGLA DURA
**`/estudio` NO se edita NI se borra hasta que el operador apruebe la construcción final.** Cada fase N1-N5 es aditiva y deja `/estudio` corriendo como fallback. El swap es un paso separado con aprobación explícita.
