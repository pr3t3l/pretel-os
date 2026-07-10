# Build Plan — Campañas (el módulo `/campanas` + el hilo `campaign_id`)

**Estado:** v1 propuesto (2026-07-09) — **para aprobar antes de codear.** Trinity: spec = `spec_Campanas.md` (v1.1) ·
plan = este doc · tasks = se atomizan en `task_create` al aprobar.
**Gate de arranque:** `spec_Campanas.md` firmado. Depende de: `project_pieces` + `scheduled_posts` (existen),
`lib/estudio/cast.ts` (`CastOverride`/`resolveCast`, existe), `lib/radar` (existe), `/api/estudio/produce` (existe).
**Doctrina que gobierna:** `spec_Campanas.md` (autoridad) · `spec_Superficies_Produccion.md` (las 3 superficies) ·
`spec_Phase_Identidad §2.2` (cascada de cast) · reglas duras de sandia (UI nunca llama `supabase.from()`; data por
`lib/api`; DB por `supabase/migrations`; `npm run verify` es el gate — gatear por EXIT code, no por grep).
**Alcance:** el módulo Campañas + el enganche con Ángulos/Media/Agenda + la inyección de contexto al develop. **NO**
incluye: presupuesto/atribución, A/B, multi-avatar, plantillas, UTMs, reporting (todos v2 — ver `spec §10`).

---

## 0. El modelo en una frase (recordatorio del spec)
EVERGREEN es el default (`campaign_id NULL`). Una campaña = contenedor con fecha (concepto+oferta+ventana+arco 3
fases). `campaign_id` en la pieza es el hilo que cose los 4 módulos. La pieza se ata desde su creación (Ángulos) con
inyección completa (concepto+oferta+fase). Dos formas de llenar: proponer (arriba→abajo) + etiquetar (abajo→arriba).

## 1. La decisión de diseño: datos-primero, módulo, superficies, develop, ciclo
El orden respeta la dependencia real: sin `campaign_id` en la pieza, ninguna superficie puede pintar nada; sin el
módulo, no hay dónde crear la campaña; el develop con inyección es lo último porque consume todo lo anterior. **Todo
aditivo** (nada rompe el evergreen que ya funciona).

## 2. Milestones (cada uno cierra verde: `npm run verify` EXIT 0 + e2e del slice)

### CM1 — Datos + el proponer puro (la foundation) — ✅ HECHO (2026-07-09)

> **✅ Aplicado a prod** (`qxhfmsojpjmnlzaduzao`, vía Supabase MCP): `project_campaigns` (4 RLS policies) +
> `project_pieces.campaign_id/campaign_phase` + `scheduled_posts.campaign_id`. Verificado: las 18 piezas
> existentes siguen evergreen (`campaign_id NULL`), cero advisories de seguridad nuevos. Código en sandia
> `5d29761`, `npm run verify` EXIT 0 (371 tests, 10 de `arc.test.ts`).
1. Migración `supabase/migrations/<ts>_campaigns.sql`:
   - `project_campaigns` (campos de `spec §5`: id, project_id, avatar_key, name, slug, kind, concept, offer,
     event_id, starts_on, peak_on, ends_on, policy_overrides, cast_override, hooks, arco, color, status, signed_at,
     timestamps; `unique(project_id, slug)`).
   - `project_pieces.campaign_id` (uuid null → `project_campaigns` on delete set null) + `campaign_phase` (check
     teaser|peak|close). **null = evergreen.**
   - `scheduled_posts.campaign_id` (uuid null, denormalizado para el calendario).
   - RLS espejo de `scheduled_posts` (`is_project_member` select · `project_role_for_user in owner/editor` write) +
     trigger `set_updated_at` + `INSERT INTO schema_migrations`.
   - **Probar en un branch de Supabase ANTES de tocar `qxhfmsojpjmnlzaduzao`.**
2. `lib/schemas/campaign.ts` — zod `Campaign`, `CampaignArcItem` (shape de `spec §5`), `CampaignPhase`. Tolerante.
3. `lib/campaigns/arc.ts` — `proposeCampaignArc(campaign, matrix2.2, hooks2.5): CampaignArcItem[]` **puro**: reparte
   fase×canal con rampa (teaser ~2-3 / pico ~3-4 / cierre ~2), solo canales encendidos, `intent` por fase, fechas
   explícitas dentro de la ventana, ángulo = 2.5 estacional primero. NO cadencias, NO `buildPublicationPlan`.
4. `lib/api/campaigns.ts` — accesores CRUD (list/get/create/update/sign) + `tagPiece(pieceId, campaignId, phase)` +
   `pieceCampaign(pieceId)`. UI nunca toca `supabase.from()`.
**Done:** migración aplicada (branch→prod); evergreen intacto (piezas viejas siguen con `campaign_id NULL`); `arc.test.ts`
verde (rampa, canales de 2.2, fechas en ventana, intent por fase); `verify` EXIT 0.

### CM2 — El módulo `/campanas` (la cabina)
1. `app/projects/[projectId]/campanas/page.tsx` — **lista**: cards (color, ventana, oferta, progreso X/Y, estado) +
   nota fija «Evergreen es tu base» + «＋ Nueva campaña».
2. **Tablero** (abrir una): header (color·nombre·estado·ventana·editar) + concepto + oferta + el **arco** (3 columnas
   teaser/pico/cierre) con las piezas por fase (chip canal + ángulo + estado ◐●✓ + badge dar/pedir) + **medidor de
   ratio** del mes + botones de salto (Ángulos/Agenda/Media). Lee `campaigns.ts` + piezas por `campaign_id`.
3. **Wizard de creación** (`components/campanas/wizard-*.tsx`): paso Concepto → paso Arco (`proposeCampaignArc`,
   editable) → paso Look (`CastOverride`, reusa `resolveCast` — cero código de resolución nuevo). Firmar → `status=activa`.
4. Nav: añadir «Campañas» al `app-shell.tsx` + card en el hub «Tu camino».
**Done:** crear una campaña completa desde el wizard; el tablero muestra su arco con chips fantasma; los saltos abren
Ángulos/Agenda/Media; `verify` EXIT 0; verificación visual del operador.

### CM3 — Atar desde las superficies (el hilo se vuelve visible)
1. **Ángulos** (`app/projects/[projectId]/angulos/page.tsx`): al desarrollar, selector `Evergreen (default) | Campaña ▾`
   → fija `piece.campaign_id` + `campaign_phase` vía `tagPiece`. Chip de color de campaña en las tarjetas de piezas ya
   atadas. Re-etiquetar permitido (solo membresía; no re-desarrolla).
2. **Media** (`app/projects/[projectId]/media/page.tsx`): filtro por campaña + chip de color por pieza (evergreen sin chip).
3. **Agenda** (`app/projects/[projectId]/agenda/page.tsx`): banda de color de la ventana (lee `project_campaigns`) +
   chips de campaña en lo agendado (`scheduled_posts.campaign_id`) + atajo «Montar campaña sobre esta fecha» en el
   panel del día (prefill desde `lib/radar/holidays.ts`).
**Done:** desarrollar una pieza eligiendo campaña la pinta en el tablero + con chip en Media + (al agendar) chip+banda
en Agenda; evergreen por default cuando no se elige; `verify` EXIT 0.

### CM4 — Develop con inyección completa (lo que hace distinta a una campaña)
1. `app/api/estudio/produce/route.ts`: si la pieza tiene `campaign_id`, cargar la campaña y pasar su contexto a
   `buildBrief`/`buildDevelopSystem`.
2. `lib/estudio/brief.ts` + `prompts.ts`: **concepto** = capa ESCENA/tema compartida; **oferta** = sustancia del pedir
   en pico/cierre con **deadline real** (`ends_on`) para que la guardia C12 (`hooks-brain.ts`
   `addsFabricatedUrgency`) reconozca el «last-call» como legítimo; `campaign_phase` marca el `intent`.
3. `arco.piece_id` ↔ pieza real: al desarrollar un hueco del arco, enlazar; el chip fantasma pasa a real.
**Done:** una pieza de cierre con oferta produce un CTA con la oferta + deadline real, y la guardia NO la marca como
urgencia fabricada (test); una pieza evergreen (sin campaign) desarrolla igual que hoy (no-regresión); `verify` EXIT 0.

### CM5 — El ciclo (cerrar honesto)
1. `status → done` automático al pasar `ends_on` (check al cargar la campaña o job ligero) → los ganchos propios
   (`hooks`) expiran (fuera de la biblioteca evergreen).
2. Medidor de ratio del mes con desglose evergreen/campaña (reusa la política `ratio_policy_plain` de 2.3, ya en la Agenda).
**Done:** al pasar `ends_on` la campaña cae a `done` y sus ganchos no aparecen en Ángulos evergreen; el medidor muestra
el mes combinado desglosado; `verify` EXIT 0.

## 3. Orden y dependencias
**CM1 bloquea todo.** CM2 → CM3 (las superficies necesitan el módulo para elegir campaña). CM4 depende de CM1 (necesita
`campaign_id` en la pieza). CM5 cierra. Paralelizable: CM3-Media y CM3-Agenda son independientes de CM3-Ángulos.

## 4. V1 cuts (lo que NO entra — `spec §10`)
Presupuesto/atribución, A/B, multi-avatar por campaña, fases custom, amplificación pagada, UTMs (el `slug` queda listo),
plantillas de campaña, reporting del conjunto (se enciende con la fuente de medición, `spec_Phase_4_Medir`).

## 5. Riesgos / cuidados
- **No revivir el plan computado**: `proposeCampaignArc` es finito y explícito por pieza; NUNCA calcula el evergreen
  (`buildPublicationPlan`/`plan.ts` murieron con C17 — [[papandi-calendario-plan]]).
- **Aditivo de verdad**: toda pieza existente debe seguir siendo evergreen (`campaign_id NULL`) sin tocarla.
- **Cast**: `cast_override.*.aprobado` obligatorio antes de generar media de campaña (contrato del cast).
- **Design drift**: chips/bandas usan tokens (`--phase-*`, color de campaña por variable), nunca hex crudo — `check-design-drift` lo bloquea.

## 6. Trinity — qué falta para cerrarla
- **spec:** ✅ `spec_Campanas.md` v1.1.
- **plan:** este doc.
- **tasks:** atomizar CM1-CM5 en `task_create` de pretel-os (una tarea por migración/función/slice) al aprobar.
