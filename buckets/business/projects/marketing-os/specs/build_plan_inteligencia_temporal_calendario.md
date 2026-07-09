# Build Plan — Calendario + Inteligencia Temporal en `sandia-marketing`

**✅ EJECUTADO (2026-07, `sandia` main) — M1-M5 + calendario construidos, probados y desplegados:** M1 migración (`80d98da`) + accesores (`b8e83d0`) · M2 `date-holidays` (`be5a7bb`) · M3 radar lógica (`c77ae75`) + UI (`e0bc5c9`) · M4 calendario lógica (`2aaafc0`) + UI diseño Papandi (`476d413`) · M5 generación date-aware (`be150b8`) + flag "vencido" (`2c61031`) · nav (`7554ec2`). **145 tests + `next build` verdes.** Fase 2 firmada 100% (4 avatares). Validado en vivo: el Freelance regeneró con 2 ganchos seasonal anclados a Jul-4 + back-to-school.

**Status:** v1.0 propuesto (2026-06-30) · **Gate de arranque:** Fase 2 FIRMADA (voz 2.0 · reparto 2.1 · canales+cadencias 2.2 · pilares 2.3 · ~~multiplicación 2.4~~ (C17: murió) · ganchos 2.5, los 4 avatares Papandi). El operador cierra planning y pide, en orden: **calendario → migrar lo ya construido/firmado → módulo de Producción.**
**Doctrina que gobierna:** `spec_Inteligencia_Temporal.md` (v0.2 — el radar) + `spec_Estudio_Produccion_Publicacion.md §6` (el calendario) + `lookup_posting_cadence_2026.md` (cadencias/ventanas) + `lookup_event_calendar_2026.md` (eventos base) + reglas duras del repo sandia (UI nunca llama `supabase.from()` directo; data solo vía `lib/api`; DB solo por `supabase/migrations`; `npm run verify` es el gate).
**Alcance:** el **calendario** + el **motor temporal** + la **MIGRACIÓN** de lo ya construido/firmado. **NO** incluye el módulo de Producción completo — ese viene después y *llena* los slots del calendario.

> **⚠️ RECONCILIACIÓN C17 (2026-07-09).** M1-M3 + M5 (el **motor temporal**: migración, `date-holidays`,
> radar, generación date-aware, higiene) **sobreviven y están en producción**. Lo que C17 + el swap
> (2026-07-08) cambiaron: **M4 (el calendario) construyó un plan CALCULADO de cadencias 2.2** vía
> `buildPublicationPlan` — esa superficie la **jubiló el swap** y la reemplazó la **Agenda** (`/agenda`,
> `scheduled_posts`: lee lo que el operador agenda, no un plan computado). El radar que M4 estrenó
> (`/api/radar/upcoming`) lo consume hoy la Agenda. La **«2.4 multiplicación»** del gate murió (el ángulo 2.5
> ES la unidad; plan **generativo**). El motor NO se toca; solo la superficie de destino cambió de nombre
> (ver `spec_Superficies_Produccion.md` + `spec_Campanas.md`).

---

## 0. Estado real (lo ya construido y firmado)

- **App:** `sandia-marketing` — Next.js App Router + TS + Tailwind + Supabase (proyecto `qxhfmsojpjmnlzaduzao`) + TanStack Query. Deployada en Vercel desde `main`.
- **Firmado en DB** (`project_phase_artifacts`, `content_json.status='signed'`, llaveado por `avatar_key`): Fase 0/1 + **Fase 2 completa** (2.0 voz · 2.1 reparto · 2.2 matriz canal×avatar con `how_measured` + cadencias · 2.3 pilares [C17: +`anchor`+`ratio_policy_plain`] · ~~2.4 multiplicación~~ (C17: murió) · 2.5 ganchos —40/avatar, = los ÁNGULOS). 4 avatares Papandi.
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

### M2 — Adapter de holidays (capa civil)
1. **Librería (RESUELTO §4): `date-holidays` (npm)** — instalar + envolver tras `HolidaySource`. Local, in-proceso, 200+ países, TS-native. *Cuidar:* trae data de todos los países → lazy-load por `market_geo` (bien para serverless Node).
2. Interfaz `HolidaySource.getHolidays(geo, year) → events[]`; cache en `project_events` o `holidays_cache`. Adapter swappable (Nager.Date/Calendarific si algún día hace falta).
**Done:** para un `market_geo` dado, el sistema lista los festivos civiles del año con su fecha real + `lead_time` (de la tabla curada), sin hardcodear.

### M3 — El radar (capas 1-4) + las fechas propias del usuario (capa 3)
1. Ensamblar `radar(project) → upcoming_events[]`: base (holidays + comercial curado) + nicho (derivación LLM revisable, glass-box) + **fechas propias** + datos medidos (placeholder Fase 4).
2. **UI capa 3:** el usuario añade/edita sus fechas (aniversario, lanzamientos, su temporada) → `project_events` con `source=user_added`.
**Done:** el radar devuelve `upcoming_events[]` para un proyecto (geo + nicho + propias), con su fuente visible (glass-box).

### M4 — El calendario (consumidor del radar)

> **C17:** esta superficie (plan CALCULADO de cadencias vía `buildPublicationPlan`) la **jubiló el swap
> 2026-07-08**. La reemplaza **Agenda** (`/agenda`, `scheduled_posts` — lee lo agendado, no un plan
> computado). El **radar** que M4 estrenó sobrevive y lo consume la Agenda (`/api/radar/upcoming`). Lee lo
> de abajo como historia de M4; la superficie viva es `spec_Superficies_Produccion.md §3`.

1. Línea de tiempo: slots desde cadencias 2.2 firmadas × ventanas (`lookup_posting_cadence`) calibradas por avatar/`market_geo`.
2. Franja **"fechas que se acercan"** (radar) con lead time + **"preparar campaña"**.
**Done:** calendario navegable por avatar; muestra cadencia + las fechas próximas; reprogramable a mano.

### M5 — Generación consciente de fecha (cierra el bug origen) + higiene
1. El generador de ganchos (2.5) recibe `{ today, upcoming_events[] }`; los `seasonal` ganan `event_ref/valid_window/expires_at`; el ↻ regenerar-uno date-aware.
2. **Higiene:** ganchos/piezas con `hoy > expires_at` → "vencido" + ofrecer refrescar (**sugiere, nunca borra** — D-IT3).
**Done:** regenerar un gancho de temporada en junio apunta al beat actual (no Nov/Feb); un vencido se marca y ofrece refresh.

## 3. Orden y dependencias
**M1 bloquea todo** (foundation). M2 → M3 (el radar necesita la capa civil). M3 → M4 (el calendario consume el radar). M5 cierra. Paralelizable: M2 con la UI de capa-3 de M3.

## 4. ✅ RESUELTO (2026-06-30) — dónde corre el radar + qué librería
**Verificado el stack de sandia:** 100% Next.js 16 + React 19 + TS + Supabase + `@anthropic-ai/sdk` (JS). **CERO Python.** La generación ya vive en **API routes** (`app/api/phase2/step-proposal`, `app/api/phase2/hook-regen`, vía `lib/api/llm/complete.ts`). El radar/calendario corren **ahí mismo, in-proceso**.
→ **Default D-IT5 = `date-holidays` (npm)** — local, donde ya corre la generación; 200+ países; TS-native; sin API externa ni servicio nuevo. `Nager.Date` (API) = fallback; `Calendarific` si se necesita cobertura/idiomas. **`python-holidays` descartada** (no hay servicio Python). El `marketing-os/CLAUDE.md` que dice "runtime Python" describe una arquitectura previa que el build en sandia ya superó — anotado, no es la realidad operante.

## 5. V1 cuts (lo que NO entra)
- Capa 5 — tendencias vivas (futuro).
- Geo por-avatar (v1 = a nivel proyecto).
- Atribución fecha→ingreso real (Fase 4 — placeholder en M3).
- El **módulo de Producción** completo (llena los slots — viene después de este plan).

## 6. Trinity — qué falta para cerrarla
- **spec:** ✅ `spec_Inteligencia_Temporal.md` v0.2 + `spec_Estudio §6` (calendario).
- **plan:** este doc.
- **tasks:** atomizar M1-M5 en `task_create` de pretel-os (una tarea por migración/función/slice) al aprobar el plan. Tarea madre: `77ed379a`.
