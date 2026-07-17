# Spec — Campañas (el pico finito sobre el evergreen generativo)

**Estado:** v1.1 borrador — DISEÑADO, no construido. Para firma del operador antes de construir. Reemplaza
la §3 borrador de `docs/research/campanas-marketing-real.md` (escrita sobre el modelo MUERTO:
`buildCampaignSlots`/`mergePlans`/`PlanSlot`/`rotateHook`/`kit_variant`/derivados 2.4). Este spec conserva
las **decisiones de marketing** de esa investigación (sólidas, con fuentes) y re-expresa el **mecanismo**
sobre C17.
**UI/UX (decisión del operador 2026-07-09):** Campañas es un **módulo con ventana propia** (`/campanas`), NO
un cajón de la Agenda; el **EVERGREEN es el default** (`campaign_id = NULL`); una pieza se **ata desde su
creación** en Ángulos con **inyección completa** de contexto (concepto + oferta + fase); v1 soporta **ambas**
formas de llenado — proponer (arriba→abajo) **y** etiquetar (abajo→arriba). Detalle en §6.
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
1. **Una FECHA dura** (una fecha del calendario — evento comercial o fecha propia de lanzamiento) con deadline real.
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
- **Evento / estacional** — nace de una **fecha comercial del calendario** (4 de Julio, Black Friday…; el motor
  radar la calcula, la Agenda la muestra). Default **2 semanas**.
- **Lanzamiento / promo propia** — nace de una fecha del **usuario** (un `project_event` personal). Default
  **4 semanas**. Editable 1–6 semanas en ambos.

**NO se soporta v1**: awareness siempre-on como campaña, presupuesto/atribución, A/B, fases custom,
amplificación pagada (R1 §2 «Qué NO hacer v1» — sobredimensionado para solopreneur).

**Una campaña se asigna a 1..N avatares** (revisión del operador 2026-07-10 — el borrador original decía «UN
avatar»; en el testeo el operador pidió multi-avatar: «una campaña como 4-Jul es un momento del PROYECTO, no
de un avatar»). El **SHELL es compartido** (nombre, concepto, oferta, ventana, color, `avatar_keys`); el **ARCO
y las PIEZAS son POR-AVATAR** — `arcos = { avatarKey: CampaignArcItem[] }` — porque los ángulos 2.5 son
por-avatar, así la diferencia por avatar se mantiene. `avatar_keys` (lista; `[]` = toda la marca). Desarrollar
una campaña de N avatares = desarrollar sus piezas por cada avatar (en Ángulos la campaña aparece para
cualquiera de sus avatares; el tablero tiene un selector de avatar). CONSTRUIDO (migración `20260710120000`).

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

-- ADITIVA sobre project_pieces (el HOGAR de la pieza — la FUENTE DE VERDAD de su campaña):
--   campaign_id NULL = EVERGREEN (el default). Con valor = la pieza pertenece a esa campaña y HEREDA su
--   contexto (concepto+oferta+fase) al desarrollarse. Una pieza pertenece a ≤1 campaña (regla HubSpot).
alter table public.project_pieces
  add column campaign_id    uuid references public.project_campaigns(id) on delete set null,
  add column campaign_phase text check (campaign_phase in ('teaser','peak','close'));

-- ADITIVA sobre scheduled_posts (denormalizado para pintar el calendario sin join; deriva de la pieza):
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
- **EVERGREEN es el default**: `project_pieces.campaign_id = NULL`. La mayoría de las piezas son evergreen.
- Una pieza pertenece a **≤1** campaña (regla HubSpot). Se ata de **dos formas** (ambas fijan `campaign_id`):
  (a) **abajo→arriba** — se desarrolla en Ángulos con la campaña elegida en el selector; (b) **arriba→abajo** —
  un hueco del `arco` se desarrolla. Re-etiquetar una pieza evergreen a una campaña es válido (solo cambia la
  membresía/color; no re-desarrolla). El `arco` guarda los huecos **por desarrollar** (sin pieza aún); las
  piezas reales viven en `project_pieces` con su `campaign_id` — el tablero muestra la UNIÓN de ambos.
- `slug` único y estable por proyecto: es el futuro `utm_campaign` (no se construyen UTMs en v1).
- Los `hooks` propios expiran con `ends_on` (temporalidad = ventana).
- `cast_override.*.aprobado` obligatorio antes de generar video/imagen de campaña (contrato del cast).
- Campañas solapadas: permitidas, con **warning** (surface, no reconciliar) si comparten canal y día.
- **Pura, sin LLM**: `proposeCampaignArc(campaign, matriz2.2, hooks2.5)` reparte fases × canales con rampa y
  fechas explícitas (la campaña NO usa cadencias — cada pieza tiene su fecha). Determinista, testeable.
  **No resucita `buildPublicationPlan`**: no calcula el evergreen, solo el arco finito de ESTA campaña.

## 6. Las superficies y el flujo UI (Campañas = módulo propio)

> **Decisión de UI/UX del operador (2026-07-09).** La campaña **NO vive en el cajón de la Agenda** — tiene su
> **ventana propia** (`/campanas`) y **orquesta** los otros tres módulos vía `campaign_id`. El «radar» **no es
> una superficie**: es el motor (`lib/radar`) que calcula las fechas que la Agenda pinta como marcadores
> (nunca «clic en el radar», siempre «clic en una fecha del calendario»).
>
> **Refinamiento del operador (2026-07-10) — el modelo TALLER / PLAN / CALENDARIO (CONSTRUIDO).** Tras testear,
> las superficies se separan nítido: **Ángulos = el TALLER** (el ÚNICO sitio donde se desarrolla — ahí viven el
> estilo de apertura + la apertura visual + la apertura APROBADA, y ahí se elige el **canal**; no se duplica en el
> tablero). **Campañas = el PLAN** (NO se desarrolla aquí): cada hueco del arco es **ÁNGULO + FECHA** (sin canal);
> se ve el arco por fase, ordenado por fecha. **Agenda = el CALENDARIO** (cuándo se postea; pinta la banda). El
> **puente** es la fecha del hueco: «Desarrollar en Ángulos» **abre y RESALTA ese ángulo** (lleva
> avatar+hook+arc+fecha+fase); al **generar**, la pieza (a) **llena el hueco** — se escribe su `piece_id` en el
> arco (lazo REAL, no la coincidencia frágil canal+hook) — y (b) **se agenda sola** en la fecha del plan
> (`scheduled_post` con `campaign_id`) → sale en Campañas por fecha **y en el Calendario**. La **FASE**: **da valor
> → teaser** (auto); **pide → toggle Pico|Cierre** (se hereda del salto). El **selector de campaña es POR TARJETA**
> en Ángulos (default Evergreen). El botón **«Programar»** del tablero queda solo para piezas **fuera del plan**
> (evergreen suelto). Esto AJUSTA §6.1-6.3.

**EVERGREEN es el default.** Toda pieza nace evergreen (`campaign_id = NULL`): sin caducidad, sin arco, se
agenda cuando el operador quiera — la base always-on. Una campaña es un contenedor con fecha que se **ata** a
una pieza; atarla inyecta su contexto (concepto + oferta + fase).

### 6.1 El módulo Campañas (`/campanas`) — la cabina
- **Lista:** cada campaña con color, ventana, oferta y progreso (X/Y piezas listas) + estado (borrador ·
  activa · cerrada). Botón **«＋ Nueva campaña»**. Una nota fija: *«Todo lo que no está en una campaña es
  Evergreen — tu base siempre-activa.»*
- **Tablero** (abrir una): concepto · oferta · la ventana con el **arco teaser → pico → cierre** · las piezas
  por fase con su estado (◐ por desarrollar → ● lista → ✓ publicada) · el **medidor de ratio** del mes. **No
  se desarrolla ni se agenda aquí**: el tablero **SALTA** a Ángulos (desarrollar), a Agenda (agendar) o a Media
  (ver). Un solo lugar de detalle por cosa.

### 6.2 Qué gana cada superficie existente (cambio mínimo — `campaign_id` hace el trabajo)
- **Ángulos** (`/angulos`): al desarrollar, un **selector de contexto `Evergreen (default) | Campaña ▾`**. Si
  se elige campaña, el develop **ya inyecta** su concepto/oferta/fase (glass-box: se ve qué contexto entra). Las
  piezas que pertenecen a una campaña llevan un **chip de color** en su tarjeta. → la pieza se ata **desde su
  creación** (la decisión del operador).
- **Media** (`/media`): **filtro por campaña** + **chip de color** por pieza. Lo evergreen no lleva chip.
- **Agenda** (`/agenda`): **banda de color** de la ventana (patrón CoSchedule/HubSpot) + **chips** en las piezas
  agendadas de la campaña. Los marcadores de fecha del calendario (que el motor radar calcula) siguen ahí.

### 6.3 Las DOS formas de atar una pieza (ambas en v1)
1. **Abajo→arriba (etiquetar):** en Ángulos desarrollas y eliges la campaña en el selector → `piece.campaign_id`
   se fija y la pieza aparece en el tablero bajo su fase.
2. **Arriba→abajo (proponer):** en el tablero, `proposeCampaignArc` propone un hueco (fase × canal × ángulo) →
   clic → saltas a Ángulos con todo pre-elegido → desarrollas → el hueco fantasma pasa a pieza real.

### 6.4 Crear una campaña — 2 entradas, 1 wizard
- **Entrada A (principal):** `/campanas` → **«＋ Nueva campaña»**.
- **Entrada B (atajo):** en la Agenda, clic en una **fecha del calendario** → **«Montar campaña sobre esta
  fecha»** → prefill (`name` = evento + año, `starts_on = fecha − lead_time_days` vía `lib/radar/holidays.ts`,
  `peak_on` = la fecha).

**El wizard (3 pasos, igual desde A o B):**
1. **Concepto:** nombre · la big idea (1–2 frases) · oferta opcional (+ si termina con «día después») · ventana
   editable (default 2 sem evento / 4 sem lanzamiento). Glass-box: qué hará cada fase.
2. **Arco:** `proposeCampaignArc` propone el reparto fase × canal (canales de 2.2, rampa al pico, `intent`
   marcado) con su ángulo (2.5 estacional primero; opción de ≤5 ganchos propios) y su nota accionable. El
   operador quita/añade/edita. Se muestra el ratio del mes CON la campaña, desglosado.
3. **Look (opcional):** `CastOverride` — elegir personaje/set del cast o generar una variante temática (se
   añade al cast, se aprueba). Si se salta, kit base.

Al **firmar** → `status → activa`: la Agenda pinta la banda + los **chips fantasma** del arco; al desarrollar un
hueco → pieza real (con `campaign_id`) → chip real; al agendarla → fila `scheduled_posts` con `campaign_id`. Al
pasar `ends_on` → `status → done` (automático) y los ganchos propios expiran.

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

1. **CM1 — Datos.** Migración `project_campaigns` + `project_pieces.campaign_id`/`campaign_phase` +
   `scheduled_posts.campaign_id` (todo aditivo) + RLS espejo + accesor `lib/api/campaigns.ts`.
   `proposeCampaignArc` puro + tests.
2. **CM2 — El módulo `/campanas`.** Lista + tablero (arco por fase, estados, medidor de ratio, saltos a
   Ángulos/Agenda/Media) + wizard de creación (concepto → arco → look) desde «＋ Nueva campaña». El look reusa
   `CastOverride`/`resolveCast` (cero código de resolución nuevo).
3. **CM3 — Atar desde las superficies.** (a) Ángulos: selector `Evergreen | Campaña ▾` al desarrollar + chip de
   campaña en las tarjetas (fija `piece.campaign_id`). (b) Media: filtro + chip por campaña. (c) Agenda: banda de
   ventana + chips + atajo «Montar campaña sobre esta fecha».
4. **CM4 — Develop con contexto (inyección completa).** El MISMO `/api/estudio/produce` recibe el contexto de la
   campaña de la pieza: concepto = capa ESCENA/tema; oferta = pedir de pico/cierre con **deadline real** para la
   guardia C12; `campaign_phase` marca el intent. `arco.piece_id` ↔ pieza real; el chip fantasma pasa a real.
5. **CM5 — Ciclo.** `status → done` automático al pasar `ends_on`; ganchos propios expiran; medidor de ratio del
   mes con desglose evergreen/campaña.
6. UX bajo `spec_UX_Experience` (P1 una cosa a la vez · P5 glass-box · P6 co-creación con autoría).

## 9. Verificación

- Crear campaña desde `/campanas` («＋ Nueva») y desde una fecha del calendario en la Agenda → prefill correcto
  (`starts_on = fecha − lead_time_days`).
- Atar una pieza en Ángulos (selector `Campaña ▾`) → `piece.campaign_id` fijado; aparece en el tablero y con chip
  en Media/Agenda. Evergreen por default cuando no se elige campaña.
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
