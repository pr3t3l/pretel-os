# Spec — Campañas (el pico finito sobre el evergreen generativo)

**Estado:** v1 borrador — DISEÑADO, no construido. Para firma del operador antes de construir. Reemplaza
la §3 borrador de `docs/research/campanas-marketing-real.md` (escrita sobre el modelo MUERTO:
`buildCampaignSlots`/`mergePlans`/`PlanSlot`/`rotateHook`/`kit_variant`/derivados 2.4). Este spec conserva
las **decisiones de marketing** de esa investigación (sólidas, con fuentes) y re-expresa el **mecanismo**
sobre C17.
**Trinity:** spec = este doc · plan = `build_plan_campanas.md` (pendiente) · tasks = pendientes.
**Decide:** qué es una campaña, qué AÑADE que el evergreen no tiene, cómo encaja en el modelo ángulo × canal,
y cómo se pinta en la Agenda — sin resucitar el plan calculado muerto.
**Fuentes:** `docs/research/campanas-marketing-real.md` (R1 — investigación web jul-2026, decisiones §2) ·
`spec_Superficies_Produccion.md` (Ángulos/Media/Agenda + `scheduled_posts`) · `spec_Phase_Identidad.md §2.2`
(cascada de cast) · `spec_Modelo_Contenido.md` (C17, firmado 2026-07-06) · `lib/estudio/cast.ts`
(`CastOverride`/`resolveCast` — el enganche ya existe).

---

## 0. La tesis

**Una campaña es un PICO finito y con fecha encima del plan evergreen generativo.** El evergreen (Ángulos →
Media → Agenda) es la base always-on: mismos pilares, años de contenido, sin caducidad. La campaña es
«una ráfaga de alta intensidad, acotada en el tiempo, con un solo objetivo» (R1 §1.1) — el modelo por
capas que usa el marketing real: base continua + picos en momentos clave.

**Lo que la campaña AÑADE que el evergreen no tiene** (las cuatro cosas — R1 §1.2/§1.3):
1. **Una FECHA dura** (un evento del radar, o una fecha propia de lanzamiento) con deadline real.
2. **Un CONCEPTO compartido** (la «big idea»): una sola idea creativa que atraviesa canales — la capa
   **ESCENA/tema** del Cerebro de Ganchos, común a todas las piezas de la ventana.
3. **Una OFERTA** (opcional): la capa que **hoy no existe en el sistema** — es LO que distingue una campaña
   de venta del flujo de valor evergreen (R1 §1.3: «la oferta es una capa nueva… es LO que la campaña añade»).
4. **Un ARCO de tres fases** (teaser → pico → cierre): el ratio dar:pedir se **reordena por fases**, no
   desaparece (R1 §1.2).

**El evergreen NO es la campaña.** «Awareness siempre-on» = el plan generativo, no una campaña (R1 §2).
Una campaña sin fecha ni ventana no es una campaña: es contenido evergreen con etiqueta.

---

## 1. Qué es una campaña (2 tipos, una ventana, un concepto, una oferta opcional)

**Dos tipos v1** (R1 §2 — el mismo objeto, distinto origen de la fecha):
- **Evento / estacional** — nace de una fecha del **radar** (4 de Julio, Black Friday…). Default **2 semanas**.
- **Lanzamiento / promo propia** — nace de una fecha del **usuario** (un `project_event` personal). Default
  **4 semanas**. Editable 1–6 semanas en ambos.

**NO se soporta v1**: awareness siempre-on como campaña, presupuesto/atribución, A/B, multi-avatar por
campaña, fases custom, amplificación pagada (R1 §2 «Qué NO hacer v1» — sobredimensionado para solopreneur).

**Una campaña = UN avatar** (C15): hereda sus canales encendidos (2.2), sus pilares con ancla (2.3), y sus
ángulos (2.5). No cruza avatares en v1.

## 2. El arco: tres fases con rampa

Todas las fuentes convergen en 3 fases (R1 §1.2). Fijas en v1:

| Fase | Cuándo | Intención | Intensidad (sobre el evergreen) |
|---|---|---|---|
| **teaser** | `starts_on` → víspera del pico | **dar** (valor temático, expectativa) | ~2–3 piezas, rampa creciente |
| **pico** | `peak_on` (día del evento/lanzamiento) | **pedir** (la oferta, visual potente + CTA) | ~3–4 piezas, el día más denso |
| **cierre** | pico+1 → `ends_on` (el «día después») | **pedir** (urgencia REAL: last-call del deadline) | ~2 piezas |

- **Rampa documentada** (R1 §1.1/§2): 4/sem → diario → 3–4/día en pico (patrón BFCM); +25% sobre baseline
  como techo de temporada. La campaña **añade** piezas sobre el evergreen; **nunca inventa canales nuevos**
  (solo los encendidos en 2.2).
- **«El lanzamiento se gana en el cierre»** (PLF, R1 §1.2): el cierre concentra la urgencia. Por eso el
  «día después» (`ends_on = peak_on + 1` si hay oferta) es parte del arco, no un extra.

## 3. Cómo encaja en C17 (la reconciliación — esto es lo nuevo del spec)

**Una pieza de campaña ES una pieza C17: ángulo × canal.** No hay un objeto `CampaignPiece` con su propio
`kind` (eso era el modelo muerto de derivados 2.4). Una pieza de campaña es una fila real de `project_pieces`
(desarrollada por el MISMO `/api/estudio/produce`), que además lleva un `campaign_id`, una `phase` y un
`intent`. **La campaña no tiene su propio pipeline de generación** — superpone contexto al develop existente:

- **El concepto** (§0.2) entra al develop como **capa ESCENA/tema compartida** (contexto temático del prompt,
  común a toda la ventana) — es la big idea «estirada por todos los canales sin encerrarse en uno» (R1 §1.3).
- **El ángulo** de cada pieza sale de: (a) los **ganchos 2.5 estacionales primero** (un `ORDER BY temporality`,
  no una rotación — `rotateHook` está muerto; en C17 el operador ELIGE), o (b) los **ganchos propios de la
  campaña** (≤5, frases del concepto — mismo shape que 2.5, R1 §2). Los ganchos propios **expiran con
  `ends_on`**: viven solo en las piezas de la ventana, nunca contaminan la biblioteca evergreen.
- **La oferta** es la sustancia del **pedir** en pico/cierre. Además **legitima la urgencia C12**: la guardia
  `addsFabricatedUrgency`/`fabricatesUrgency` (`lib/estudio/hooks-brain.ts`) filtra la urgencia *inventada* en
  el evergreen — pero una pieza de cierre con **oferta real + deadline real** (`ends_on`) tiene urgencia
  **legítima**. El develop de cierre pasa el deadline real como contexto para que la guardia reconozca el
  «last-call» como verdadero, no fabricado. (Sin oferta, no hay pedir duro: el cierre degrada a recordatorio.)

**El ratio dar:pedir** (R1 §1.2/§2): se **reordena por fases** (teaser da, pico/cierre piden), el agregado de
la campaña queda ~1:1 o 2:1, y **no rompe el 3:1 firmado**: el ratio del proyecto se mide sobre el **mes
completo** (evergreen + campaña), no pieza a pieza dentro de la ventana. El medidor dar:pedir de la Agenda
(`spec_Superficies §3`, política `ratio_policy_plain` de 2.3) cuenta ambos orígenes y los **desglosa** —
transparencia, no candado.

## 4. Overrides (la cascada de Identidad §2.2 — sin código de resolución nuevo)

- **Personaje / set de campaña** — la campaña lleva un `CastOverride` (`{personaje_id?, set_id?}` — el tipo
  YA existe en `lib/estudio/cast.ts`). El develop llama `resolveCast(cast, campaign.cast_override)` y la
  cascada **pieza > campaña > default de marca** ya está implementada. La **variante temática** (ej. el
  personaje con bandera del 4 de Julio, R1 §1.3) es un **nuevo elemento AÑADIDO al cast vivo** (Identidad §2.2:
  la biblioteca se cura, no se congela — sin re-firmar) al que la campaña apunta. `aprobado` obligatorio antes
  de generar cualquier video/imagen (contrato del cast). Sin override → kit base de marca.
- **Tope/día por canal** — `policy_overrides` (`{"Email":2,"Instagram":3}`) que sube el tope **solo dentro de
  la ventana** (3–4 envíos/día en pico es práctica real, R1 §1.1). Fuera de la ventana, el default.
- **Ratio: NO se override en v1** (R1 §2). El 3:1 firmado no se toca; solo cambia dónde se mide (mes completo)
  y la UI lo transparenta.

## 5. Modelo de datos (C17 — re-expresado)

```sql
-- Una campaña = un pico finito sobre el evergreen: evento + ventana + concepto (+ oferta).
create table project_campaigns (
  id               uuid primary key default gen_random_uuid(),
  project_id       uuid not null references public.projects(id) on delete cascade,
  avatar_key       text not null,                 -- v1: UNA campaña = UN avatar (C15); denormalizado
  name             text not null,                 -- "4 de Julio 2027"
  slug             text not null,                 -- kebab, utm_campaign-ready: "4-de-julio-2027"
  kind             text not null default 'evento' check (kind in ('evento','lanzamiento')),
  concept          text not null,                 -- la big idea en 1-2 frases (capa ESCENA/tema)
  offer            text,                          -- la oferta ("15% con código JULY4") · null = sin promo
  event_id         text,                          -- RadarEvent.id / project_event ancla · null = fecha propia
  starts_on        date not null,                 -- default: event.date - lead_time_days
  peak_on          date not null,                 -- el día del evento / lanzamiento
  ends_on          date not null,                 -- default: peak_on (+1 si offer — el "día después")
  policy_overrides jsonb not null default '{}',   -- {"Email":2} tope/día SOLO en la ventana
  cast_override    jsonb not null default '{}',   -- CastOverride {personaje_id?,set_id?} → resolveCast()
  hooks            jsonb not null default '[]',   -- ganchos propios de la campaña (≤5, shape 2.5); expiran con ends_on
  arco             jsonb not null default '[]',   -- CampaignArcItem[] — el PLAN propuesto (NO piezas reales)
  color            text not null default '#E63946',
  status           text not null default 'draft' check (status in ('draft','signed','done')),
  signed_at        timestamptz,
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now(),
  unique (project_id, slug)
);
-- RLS espejo de scheduled_posts: is_project_member (select) · project_role_for_user in ('owner','editor') (write).

-- ADITIVA sobre scheduled_posts (el ENGANCHE — spec_Superficies §7):
alter table public.scheduled_posts
  add column campaign_id uuid references public.project_campaigns(id) on delete set null;
```

```ts
// El ARCO propuesto — el PLAN de la campaña, NO piezas reales. Cada item se desarrolla bajo demanda
// (nada se genera solo — doctrina C17) → cuando se desarrolla, piece_id apunta a la project_pieces real,
// y agendarlo crea una fila en scheduled_posts (campaign_id + target_date).
export type CampaignArcItem = {
  arc_id: string;
  phase: "teaser" | "peak" | "close";
  channel: string;                                    // solo canales encendidos en 2.2
  angle_ref:                                          // el DOLOR: 2.5 estacional o gancho propio
    | { kind: "hook25"; hook_id: string }
    | { kind: "own"; hook_index: number };
  intent: "dar" | "pedir";                            // teaser→dar, pico/cierre→pedir (editable)
  note: string | null;                                // el QUÉ HACER (accionable, sin jerga)
  target_date: string;                                // YYYY-MM-DD dentro de la ventana
  piece_id: string | null;                            // null = por desarrollar; con valor = project_pieces.id
};
```

**Reglas del modelo** (espejo de R1 §3.1, re-expresadas):
- Una pieza pertenece a **UNA** campaña (regla HubSpot). Los ángulos evergreen no se re-etiquetan a campañas;
  una pieza de campaña nace con su `campaign_id`.
- `slug` único y estable por proyecto: es el futuro `utm_campaign` (no se construyen UTMs en v1).
- Los `hooks` propios expiran con `ends_on` (temporalidad = ventana).
- `cast_override.*.aprobado` obligatorio antes de generar video/imagen de campaña (contrato del cast).
- Campañas solapadas: permitidas, con **warning** (surface, no reconciliar) si comparten canal y día.
- **Pura, sin LLM**: `proposeCampaignArc(campaign, matriz2.2, hooks2.5)` reparte fases × canales con rampa y
  fechas explícitas (la campaña NO usa cadencias — cada pieza tiene su fecha). Determinista, testeable.
  **No resucita `buildPublicationPlan`**: no calcula el evergreen, solo el arco finito de ESTA campaña.

## 6. Flujo UI (desde la Agenda)

1. **Entrada A (principal):** clic en un marcador del **radar** en la Agenda → el drawer del día gana
   **«Montar campaña sobre esta fecha»**. Prefill: `name` = evento + año, `starts_on = fecha − lead_time_days`
   (`lib/radar/holidays.ts`), `peak_on` = fecha del evento. **Entrada B:** botón **«＋ Campaña»** → fecha
   propia (crea el `project_event` si no existe).
2. **Paso 1 — Concepto:** nombre, la big idea (1–2 frases), oferta opcional (texto + si termina con «día
   después»), ventana editable. Glass-box: se explica qué hará cada fase.
3. **Paso 2 — Arco:** `proposeCampaignArc` propone el reparto fase × canal (solo canales encendidos, rampa al
   pico, `intent` marcado): cada item con su ángulo (2.5 estacional primero; opción de generar ≤5 ganchos
   propios) y su nota accionable. El operador quita/añade/edita. Se muestra el ratio del mes CON la campaña
   (desglosado evergreen / campaña).
4. **Paso 3 — Look (opcional):** `CastOverride` — elegir personaje/set del cast, o generar una variante
   temática (se añade al cast, se aprueba). Si se salta, kit base.
5. **Firmar:** `status → signed`. La **Agenda** pinta la **banda** del rango con el `color` (patrón
   CoSchedule/HubSpot) + **chips fantasma** («por desarrollar») de los items del `arco`. Al desarrollar un
   item → pieza real + fila `scheduled_posts` (campaign_id) → el chip fantasma pasa a **chip real**. Al pasar
   `ends_on`, `status → done` (automático) y los ganchos propios expiran.

## 7. Convivencia con el evergreen (los slots)

- **La Agenda pinta tres cosas** dentro de la ventana: (a) la **banda** de color del rango (de
  `project_campaigns`), (b) **chips fantasma** de `arco` items sin `piece_id` («por desarrollar» — glass-box:
  nada se generó solo), (c) **chips reales** de `scheduled_posts.campaign_id`. Fantasma → real al desarrollar.
- **Prioridad:** en un día lleno la pieza de campaña gana el hueco; la evergreen espera (mecanismo de la cola
  de agendado). El conflicto se reporta en warnings, **nunca en silencio** (R1 §3.3).
- **Finito y honesto:** la campaña es **finita** (tiene principio y fin); el **evergreen es generativo**. Al
  cerrar (`ends_on`), la Agenda vuelve al plan base sin residuos. (La afirmación «plan finito / nada de
  contenido infinito» de R1 §3.3 se aplica a la CAMPAÑA, no al evergreen — ahí R1 quedó en el modelo viejo.)
- **Reposteo** (`spec_Superficies §3`): las piezas de campaña también honran la doctrina de reshare — cross-canal
  = piezas distintas; repost idéntico = solo re-share con gap.

## 8. Implementación (fases del build, tras la firma)

1. **CM1** — Migración `project_campaigns` + `scheduled_posts.campaign_id` (aditiva) + RLS espejo + accesor
   `lib/api/campaigns.ts`. `proposeCampaignArc` puro + tests.
2. **CM2** — Flujo de creación (Agenda drawer → «Montar campaña» + «＋ Campaña») + wizard 3 pasos (concepto →
   arco → look). El look reusa `CastOverride`/`resolveCast` (cero código de resolución nuevo).
3. **CM3** — Develop de campaña: el MISMO `/api/estudio/produce` con contexto de campaña (concepto = capa
   ESCENA; oferta = pedir de pico/cierre con deadline real para la guardia C12). `arco.piece_id` ↔ pieza real.
4. **CM4** — Agenda: banda + chips fantasma/reales + medidor de ratio del mes con desglose. `status → done`
   automático al pasar `ends_on`.
5. UX bajo `spec_UX_Experience` (P1 una cosa a la vez · P5 glass-box · P6 co-creación con autoría).

## 9. Verificación

- Crear campaña desde un evento del radar → prefill correcto (`starts_on = fecha − lead_time_days`).
- `proposeCampaignArc`: reparto por fase con rampa, solo canales de 2.2, fechas dentro de la ventana (test puro).
- Cascada de cast: pieza de campaña sin override de pieza usa el `cast_override` de la campaña; sin él, el
  default de marca (test puro contra `resolveCast`).
- Develop de cierre con oferta: la urgencia «last-call» NO la marca la guardia como fabricada (deadline real).
- Agenda: banda pintada, chip fantasma → real al desarrollar+agendar, ratio del mes desglosado.
- Al pasar `ends_on`: `status → done`, ganchos propios fuera de la biblioteca evergreen.
- `npm run verify` verde por sub-fase; deploy continuo.

## 10. Fuera de alcance v1

- Presupuesto, atribución multi-touch, A/B, multi-avatar por campaña, fases custom, amplificación pagada
  (R1 §2 — sobredimensionado para solopreneur).
- Construcción de UTMs (el `slug` queda listo; no se construyen v1).
- Plantillas de campaña (HubSpot las tiene; v2 — nace de los 2 tipos con sus defaults).
- Reporting del conjunto por campaña (se enciende con la fuente de medición — `spec_Phase_4_Medir`).
