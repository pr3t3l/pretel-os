# Build Plan — Calendario + Inteligencia Temporal en `sandia-marketing`

**Status:** v1.0 propuesto (2026-06-30) · **Gate de arranque:** Fase 2 FIRMADA (voz 2.0 · reparto 2.1 · canales+cadencias 2.2 · pilares 2.3 · multiplicación 2.4 · ganchos 2.5, los 4 avatares Papandi). El operador cierra planning y pide, en orden: **calendario → migrar lo ya construido/firmado → módulo de Producción.**
**Doctrina que gobierna:** `spec_Inteligencia_Temporal.md` (v0.2 — el radar) + `spec_Estudio_Produccion_Publicacion.md §6` (el calendario) + `lookup_posting_cadence_2026.md` (cadencias/ventanas) + `lookup_event_calendar_2026.md` (eventos base) + reglas duras del repo sandia (UI nunca llama `supabase.from()` directo; data solo vía `lib/api`; DB solo por `supabase/migrations`; `npm run verify` es el gate).
**Alcance:** el **calendario** + el **motor temporal** + la **MIGRACIÓN** de lo ya construido/firmado. **NO** incluye el módulo de Producción completo — ese viene después y *llena* los slots del calendario.

---

## 0. Estado real (lo ya construido y firmado)

- **App:** `sandia-marketing` — Next.js App Router + TS + Tailwind + Supabase (proyecto `qxhfmsojpjmnlzaduzao`) + TanStack Query. Deployada en Vercel desde `main`.
- **Firmado en DB** (`project_phase_artifacts`, `content_json.status='signed'`, llaveado por `avatar_key`): Fase 0/1 + **Fase 2 completa** (2.0 voz · 2.1 reparto · 2.2 matriz canal×avatar con `how_measured` + cadencias · 2.3 pilares · 2.4 multiplicación · 2.5 ganchos —40/avatar). 4 avatares Papandi.
- **La 2.2 ya dejó la semilla del calendario:** matriz canal×avatar con cadencias (`lookup_posting_cadence_2026`).
- **Lo que el esquema AÚN no tiene:** `market_geo` (proyecto) · `temporality` en ganchos/piezas · `project_events` (el radar) · cache de holidays.

## 1. LA decisión de diseño: migración-primero · motor agnóstico · calendario consumidor

1. **Migración PRIMERO** (foundation). Sin `market_geo` + `temporality` + `project_events`, ni el radar ni el calendario tienen de qué agarrarse. Es lo que el operador llamó *"actualizar lo ya construido y firmado"*. **Backfill SEGURO:** los ganchos firmados → `temporality='evergreen'` (nada caduca por sorpresa).
2. **El motor temporal es agnóstico** (spec IT §2): capas 1-4, nunca hardcodea el calendario de un producto. Capa civil = librería de holidays tras adapter `HolidaySource` (D-IT5); comercial = tabla curada; nicho = derivación LLM revisable; **fechas propias = las añade el usuario**.
3. **El calendario CONSUME el radar** (Estudio §6.6): línea de tiempo (cadencias 2.2 × piezas) + franja *"fechas que se acercan"* (lead time) + *"preparar campaña"*. Cadencia = *cuándo* publicar; radar = *qué fechas* explotar.
4. **Generación consciente de fecha:** el generador (2.5 hoy; piezas después) recibe `{ today, upcoming_events[] }` en el brief → cierra el bug origen (Nov/Feb en junio). El evento entra como **dato del brief**, no un parche de "inyectar hoy".

## 2. Milestones (cada uno cierra verde: `npm run verify` + e2e del slice)

### M1 — Migración del esquema + backfill (la foundation)
1. Migración Supabase: `projects.market_geo` (text) · `project_events` (`id, project_id, avatar_key?, name, kind, geo, recurrence, date_rule, lead_time, decay, source, valid_window, expires_at`) · `temporality` (+`event_ref, valid_window, expires_at`) en el `content_json` de los ganchos (y piezas, a futuro).
2. **Backfill:** `market_geo` = país primario del idioma (`US` para Papandi, editable) · **todos los ganchos firmados → `temporality='evergreen'`**.
3. `lib/api`: accesores de `project_events` + `market_geo` (UI nunca toca `supabase.from()`).
4. **Probar en un branch de Supabase ANTES de tocar `qxhfmsojpjmnlzaduzao`.**
**Done:** migración aplicada (branch → prod); los 4 avatares firmados intactos, ahora `evergreen`; `verify` verde; e2e: abrir Fase 2 y ver los ganchos sin cambios visibles.

### M2 — Adapter de holidays (capa civil) — **incluye LA decisión de runtime**
1. **DECIDIR dónde corre el radar** (ver §4): el producto deployado es sandia (Next.js/Supabase) → favorece **`date-holidays`** (npm, local, 200+ países, recurrencia+regiones) o **Nager.Date** (API). `python-holidays` solo si se levanta un servicio Python de pretel-os.
2. Interfaz `HolidaySource.get_holidays(geo, year) → events[]`; implementación default según (1); cache en `project_events` o `holidays_cache`.
**Done:** para un `market_geo` dado, el sistema lista los festivos civiles del año con su fecha real + `lead_time` (de la tabla curada), sin hardcodear.

### M3 — El radar (capas 1-4) + las fechas propias del usuario (capa 3)
1. Ensamblar `radar(project) → upcoming_events[]`: base (holidays + comercial curado) + nicho (derivación LLM revisable, glass-box) + **fechas propias** + datos medidos (placeholder Fase 4).
2. **UI capa 3:** el usuario añade/edita sus fechas (aniversario, lanzamientos, su temporada) → `project_events` con `source=user_added`.
**Done:** el radar devuelve `upcoming_events[]` para un proyecto (geo + nicho + propias), con su fuente visible (glass-box).

### M4 — El calendario (consumidor del radar)
1. Línea de tiempo: slots desde cadencias 2.2 firmadas × ventanas (`lookup_posting_cadence`) calibradas por avatar/`market_geo`.
2. Franja **"fechas que se acercan"** (radar) con lead time + **"preparar campaña"**.
**Done:** calendario navegable por avatar; muestra cadencia + las fechas próximas; reprogramable a mano.

### M5 — Generación consciente de fecha (cierra el bug origen) + higiene
1. El generador de ganchos (2.5) recibe `{ today, upcoming_events[] }`; los `seasonal` ganan `event_ref/valid_window/expires_at`; el ↻ regenerar-uno date-aware.
2. **Higiene:** ganchos/piezas con `hoy > expires_at` → "vencido" + ofrecer refrescar (**sugiere, nunca borra** — D-IT3).
**Done:** regenerar un gancho de temporada en junio apunta al beat actual (no Nov/Feb); un vencido se marca y ofrece refresh.

## 3. Orden y dependencias
**M1 bloquea todo** (foundation). M2 → M3 (el radar necesita la capa civil). M3 → M4 (el calendario consume el radar). M5 cierra. Paralelizable: M2 con la UI de capa-3 de M3.

## 4. Pendiente clave a decidir EN M2 — ¿dónde corre el radar? (⚠️ contradice mi D-IT5)
El `marketing-os/CLAUDE.md` dice *runtime = Python PhaseHandlers en pretel-os*, **pero la realidad de la sesión es que TODO el wizard (Fase 0-2) se construyó en `sandia-marketing` (Next.js/Supabase)** — no en PhaseHandlers Python. El radar/calendario son user-facing → muy probablemente viven en **sandia (Next API + Supabase)**.
→ Si es así, el **default de D-IT5 cambia de `python-holidays` (Python) a `date-holidays` (npm) o Nager.Date (API)**. **Conflicto doctrina-vs-realidad: lo dejo SIN reconciliar en silencio — decisión del operador.** Afecta el pick de M2 + corrige la fila D-IT5 del spec.

## 5. V1 cuts (lo que NO entra)
- Capa 5 — tendencias vivas (futuro).
- Geo por-avatar (v1 = a nivel proyecto).
- Atribución fecha→ingreso real (Fase 4 — placeholder en M3).
- El **módulo de Producción** completo (llena los slots — viene después de este plan).

## 6. Trinity — qué falta para cerrarla
- **spec:** ✅ `spec_Inteligencia_Temporal.md` v0.2 + `spec_Estudio §6` (calendario).
- **plan:** este doc.
- **tasks:** atomizar M1-M5 en `task_create` de pretel-os (una tarea por migración/función/slice) al aprobar el plan. Tarea madre: `77ed379a`.
