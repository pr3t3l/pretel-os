# Inteligencia Temporal — el radar de fechas (ofensiva + higiene)

**Project**: business/marketing-os
**Status**: **BORRADOR v0.1** (diseño capturado; las 4 decisiones de fondo cerradas — ver §10. PENDIENTE: trinity propia spec+plan+tasks antes de codear, + sembrar/validar la tabla base de eventos).
**Last updated**: 2026-06-29
**Origen:** mandato del operador 2026-06-29, durante la sim de Fase 2 (Paso 6, ganchos). Al regenerar un gancho salió *"You had a great November. Then January hit…"* y luego *"…they drop in February…"* — anclados a una temporada que **ya pasó** (era junio). El operador lo identificó como patrón, no como gancho feo: *"que el sistema sepa qué fechas especiales se aproximan y cómo explotarlas va a ser un gran factor diferenciador… algo agnóstico del proyecto y que se mantiene a lo largo del tiempo."*
**Decisión de alcance:** sub-spec **APARTE** (decisión D-IT4, §10). Referenciado por el Estudio (§6 calendario + §3.1 modelo de pieza), por Fase 2 §2.5 (ganchos) y por Fase 4 (medición). La tabla base de eventos vive en **`lookup_event_calendar_2026.md`** (como `lookup_posting_cadence_2026.md` es a la cadencia, esta es a las fechas).
**Consumidores:** el calendario del Estudio (ofensiva), el modelo de pieza/gancho (atributo de temporalidad + higiene), los generadores de contenido (producir consciente de la fecha).

---

## 0. Promesa — por qué existe

Una herramienta de marketing genérica te da un **calendario estático**: tú decides qué publicar y cuándo. La nuestra es **consciente del tiempo** — y eso es el diferenciador:

- **Ve venir las fechas** que tu mercado vive (Black Friday, día del padre, temporada de bodas, cierre fiscal, vuelta al cole…) y te las pone **enfrente con anticipación**, con la pieza lista.
- **Retira el contenido cuyo momento ya pasó** — nunca más un gancho de Navidad publicándose en junio.

En una frase: **el sistema conoce tu calendario mejor que tú** — y convierte cada fecha en una oportunidad antes de que llegue, y en higiene cuando se va.

Esto no es un adorno: las fechas-momento son los ganchos de **mayor disparo** que existen (son del *ahora* del lector), pero son **perecederos** — y nadie más los gestiona por ti.

## 1. Las dos caras de un mismo motor

| Cara | Qué hace | Cuándo actúa |
|---|---|---|
| 🎯 **Ofensiva (radar)** | detecta las fechas que se aproximan y **las explota**: avisa con tiempo + genera/sugiere la pieza para ese momento | *antes* de la fecha (con su lead time) |
| 🧹 **Higiene (vencimiento)** | marca el contenido de temporada como **"vencido"** cuando su fecha pasa y **ofrece refrescarlo** | *después* de la fecha |

La biblioteca de ganchos (Fase 2 §2.5) ya prometía *"los que no convierten se jubilan con datos, no con opiniones"*. La inteligencia temporal añade la otra jubilación: **los que ya pasaron de fecha** — la biblioteca aprende por **rendimiento Y por tiempo**.

## 2. El espinazo de 3 capas (lo que lo hace agnóstico + persistente)

El motor **nunca hardcodea el calendario de un producto**: toma entradas (geo, nicho, avatar, datos propios) y produce las fechas relevantes. Mismo principio que todo el sistema — el motor es el producto, los datos son por-proyecto; **semilla → mide → afina** (Pattern B, igual que la cadencia §6.5 del Estudio).

| Capa | Qué es | De dónde sale | En v1 |
|---|---|---|---|
| **1 · Base universal + geo** | festivos por país + momentos comerciales (Black Friday, San Valentín, día madre/padre, rebajas, vuelta al cole) | tabla `lookup_event_calendar_2026.md`, mantenida por nosotros; **geo-aware** (el día del padre cae distinto por país) | ✅ |
| **2 · Overlay por nicho/avatar** | los momentos propios del negocio (florista→bodas/San Valentín; consultor→cierre fiscal/Q4; fitness→propósitos de año nuevo) | **derivados por LLM** desde el ICP + el avatar (nicho + `forces_of_progress`); operador-revisable (glass-box) | ✅ |
| **3 · Datos propios** | qué fechas de verdad movieron *ventas* | **Fase 4** mide → el radar prioriza esas el año siguiente | ✅ (cuando haya datos) |
| **4 · Tendencias vivas** *(MÓDULO FUTURO)* | lo que explota ESTA semana (memes, noticias, trends de formato/audio) | feed externo de tendencias (dependencia de terceros) | ❌ diferido (§11) |

> **Decisión del operador (D-IT1):** v1 = capas 1+2+3. La **capa 4 (tendencias vivas)** queda **marcada como módulo futuro** — alto valor pero necesita feed externo; no bloquea el v1.

## 3. El modelo de datos — la temporalidad como atributo

### 3.1 El evento (lo que el radar conoce)
```
event = {
  id,             // 'us_black_friday', 'us_fathers_day'
  name,           // "Black Friday"
  kind,           // holiday | commercial | cultural | niche | (personal, futuro)
  geo,            // ['US'] | ['MX'] | ['*'] universal
  recurrence,     // annual | one_off
  date_rule,      // "4º viernes de noviembre" | regla derivable a la fecha del año
  lead_time,      // con cuánta anticipación arrancar (Black Friday: 3-6 semanas)
  decay,          // cuánto sigue siendo relevante DESPUÉS (normalmente 0)
  source          // base_table | niche_derived | user_measured
}
```

### 3.2 La temporalidad (lo que gana cada pieza/gancho)
```
temporality = 'evergreen' | 'seasonal'
// si 'seasonal':
event_ref,        // event.id
valid_window,     // { start, end } derivado de (fecha del evento − lead_time … fecha + decay)
expires_at        // = valid_window.end → cuándo se marca "vencido"
```

- **Perenne (evergreen):** el dolor **sin fecha** — *"Your busy season ended and the drop-off feels like starting over"*. Nunca caduca. **La mayoría de la biblioteca.**
- **De temporada (seasonal):** anclado a un `event` — dispara fuerte pero **se pudre**. Pocos, los más potentes.

**Stale = `hoy > valid_window.end`.** De ahí sale la higiene (§5).

## 4. De dónde sale cada capa (sourcing)

- **Capa 1 (base):** la tabla `lookup_event_calendar_2026.md` — eventos recurrentes con `date_rule` + `lead_time`, por geo. Se siembra una vez y se **mantiene** (los eventos recurren cada año; se añaden momentos comerciales nuevos). *A resolver (§11): ¿curada a mano o respaldada por una librería de holidays por país?*
- **Capa 2 (nicho):** un **paso de derivación** (al configurar el proyecto / construir el calendario) le pide al LLM: *"dado este nicho + geo + avatar, ¿qué fechas/momentos recurrentes explota este mercado, con qué anticipación?"* → produce un **overlay de eventos por-proyecto**, que el operador **revisa y edita** (glass-box; nada entra sin su ojo).
- **Capa 3 (datos propios):** Fase 4 atribuye ventas a campañas de fecha → el radar **sube de prioridad** las fechas que de verdad funcionaron y baja las que no. Semilla → mide → afina.

## 5. Geo — `market_geo`

> **Decisión del operador (D-IT2):** un campo **`market_geo` a nivel proyecto**, preguntado **una vez** al configurar el proyecto, reusado por todo el sistema (el radar de fechas **y** las zonas horarias del calendario §6.5). Explícito, sin ambigüedad (inglés ≠ un solo país: US/UK/AU tienen festivos distintos).

**Nota de evolución (anclada por mandato):** `market_geo` será **por-avatar más adelante** — cuando un proyecto apunte a geografías múltiples a la vez (ej. US + México), cada avatar trae su geo. En v1 es de proyecto; el modelo de datos se diseña para que subir a por-avatar sea aditivo, no una reescritura. *(Mismo trato que la capa 4: marcado en el spec, no construido aún.)*

## 6. La ofensiva — cómo se explota una fecha

1. **Lead time:** cada evento sabe con cuánta anticipación arrancar (Black Friday: semanas; un festivo simple: días). El radar **avisa con tiempo**, no el día de.
2. **El calendario del Estudio (§6) la overlaya** como oportunidad: *"El día del padre llega en 3 semanas — ¿armamos campaña?"* → entra a la cola de producción (§3) la(s) pieza(s) para ese momento.
3. **Generación consciente de la fecha:** al producir una pieza/gancho de temporada, el generador recibe **el evento próximo + la fecha de hoy** como input → escribe para el momento **correcto** (en junio: *"Father's Day just passed and the calendar went quiet"*, no Nov/Enero). Esto es *"que el generador sepa qué día es"* — pero **bien hecho**: no un parche de inyectar la fecha, sino el **evento del radar** como dato de entrada del brief (§2 del Estudio). Cierra el bug que originó este spec.

## 7. La higiene — el vencimiento

> **Decisión del operador (D-IT3): sugiere, nunca borra solo.** El operador siempre es el autor.

- Cada contenido de temporada lleva su `expires_at`. Cuando `hoy > expires_at` → estado **"vencido"**.
- Acción: el sistema **marca** el contenido vencido y **ofrece refrescarlo** (regenerar para el próximo evento equivalente, o convertirlo en perenne) — **nada se mueve sin la mano del operador**. Ni auto-borrado ni auto-archivo.
- Aplica a: ganchos (Fase 2 §2.5), piezas del Estudio (§3). En la biblioteca, los vencidos se filtran/etiquetan; no contaminan la vista activa.

## 8. Cruce con otros specs (sin duplicar)

| Spec | Relación |
|---|---|
| **Estudio §6 (calendario)** | **consume** el radar: overlaya las fechas próximas como oportunidades + dispara la ofensiva (§6 de este doc). El calendario es *cuándo publicar*; el radar es *qué fechas explotar* — hermanos, no duplicados. |
| **Estudio §3.1 (modelo de pieza)** | la pieza gana `temporality` + (`event_ref`, `valid_window`, `expires_at`). |
| **Fase 2 §2.5 (ganchos)** | el gancho gana `temporality`; el ↻ regenerar-uno se vuelve **consciente de fecha** (hoy lo desconoce — es el bug origen). |
| **Fase 4 (medición)** | alimenta la **capa 3** (qué fechas movieron ventas). |
| **`lookup_posting_cadence_2026`** | hermano: aquel = *cuándo publicar* (cadencia/ventanas); este = *qué fechas explotar*. Comparten `market_geo` y el modificador B2B/B2C. |
| **Módulo C (costos)** | producir piezas de temporada cuenta como costo (cruza con el COGS, no duplica). |

## 9. La UI (esbozo — se detalla en su trinity)
- En el **calendario** del Estudio: una franja de "fechas que se acercan" con su lead time + botón *"preparar campaña"*.
- En la **biblioteca**: filtro/etiqueta perenne vs de-temporada; los **vencidos** marcados con *"refrescar"*.
- En **producción**: al generar contenido de temporada, el evento próximo visible en el brief (glass-box: *"esta pieza está anclada a [evento]; vence el [fecha]"*).

## 10. Decisiones cerradas

| # | Decisión | Resolución (operador, 2026-06-29) |
|---|---|---|
| **D-IT1** | Alcance v1 | Capas **1 (base/geo) + 2 (nicho derivado) + 3 (datos propios)**. **Capa 4 (tendencias vivas) = módulo futuro**, marcado, no v1. |
| **D-IT2** | Cómo se conoce la geo | Campo **`market_geo` a nivel proyecto**, preguntado una vez, reusado por radar + zonas horarias. **Por-avatar = evolución futura**, anclada en el spec. |
| **D-IT3** | Higiene del contenido vencido | **Sugiere, nunca borra solo** (operador autor): marca "vencido" + ofrece refrescar. |
| **D-IT4** | Casa en los specs | **Sub-spec propio** (este doc) + tabla lookup base + referencias desde Estudio/Fase 2/Fase 4. No se infla §6 del Estudio. |

## 11. Pendientes / módulos futuros (antes de codear)

- **Capa 4 — tendencias vivas:** feed externo (trends de plataforma, noticias). Alto valor, dependencia de terceros. Su propio mini-spec cuando se aborde.
- **Geo por-avatar:** cuando un proyecto apunte a geografías múltiples. Diseñar el modelo v1 para que sea aditivo.
- **Fuente de la tabla base:** ¿curada a mano o respaldada por una librería/API de holidays por país (recurrencia + geo ya resueltas)? — candidato a research/decisión.
- **Derivación de nicho (capa 2):** ¿inferencia LLM pura, o un paso de research ligero por nicho? + cómo se revisa/edita el overlay.
- **Eventos personales del negocio** (aniversario de la marca, lanzamientos propios) — ¿el usuario los añade a mano al radar? (kind `personal`).
- **Trinity propia** (spec completo + plan + tasks) cuando se decida construir; prioridad relativa vs producción = decisión del operador.
- **Sembrar + validar `lookup_event_calendar_2026.md`** con los eventos y lead times reales (candidato a estudio a profundidad, como se hizo con la cadencia).
