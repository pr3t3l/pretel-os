# Inteligencia Temporal — el radar de fechas (ofensiva + higiene)

**Project**: business/marketing-os
**Status**: **BORRADOR v0.2** (diseño capturado; **5 decisiones** de fondo cerradas — ver §10. **▶ SIGUIENTE paso del proyecto: la trinity propia, justo antes de arrancar producción** — §11). **Cambios v0.2 (mandato 2026-06-29):** (1) **+ Capa 3 — fechas propias declaradas por el usuario** (era pendiente, ahora de primera clase); (2) **§8 vuelto un mapa de migración accionable** (qué campo cambia en cada spec / en lo ya construido); (3) **fuente de la capa civil decidida (D-IT5): librería/API de holidays por país**.
**Last updated**: 2026-06-29
**Origen:** mandato del operador 2026-06-29, durante la sim de Fase 2 (Paso 6, ganchos). Al regenerar un gancho salió *"You had a great November. Then January hit…"* y luego *"…they drop in February…"* — anclados a una temporada que **ya pasó** (era junio). El operador lo identificó como patrón, no como gancho feo: *"que el sistema sepa qué fechas especiales se aproximan y cómo explotarlas va a ser un gran factor diferenciador… algo agnóstico del proyecto y que se mantiene a lo largo del tiempo."*
**Decisión de alcance:** sub-spec **APARTE** (decisión D-IT4, §10). Referenciado por el Estudio (§6 calendario + §3.1 modelo de pieza), por Fase 2 §2.5 (ganchos) y por Fase 4 (medición). La tabla base de eventos vive en **`lookup_event_calendar_2026.md`** (como `lookup_posting_cadence_2026.md` es a la cadencia, esta es a las fechas).
**Consumidores:** el calendario del Estudio (ofensiva), el modelo de pieza/gancho (atributo de temporalidad + higiene), los generadores de contenido (producir consciente de la fecha).

---

## 0. Promesa — por qué existe

Una herramienta de marketing genérica te da un **calendario estático**: tú decides qué publicar y cuándo. La nuestra es **consciente del tiempo** — y eso es el diferenciador:

- **Ve venir las fechas** que tu mercado vive (Black Friday, día del padre, temporada de bodas, cierre fiscal, vuelta al cole…) — **y las que TÚ marcas** (tu aniversario de marca, tu lanzamiento) — y te las pone **enfrente con anticipación**, con la pieza lista.
- **Retira el contenido cuyo momento ya pasó** — nunca más un gancho de Navidad publicándose en junio.

En una frase: **el sistema conoce tu calendario mejor que tú** — y convierte cada fecha en una oportunidad antes de que llegue, y en higiene cuando se va.

Esto no es un adorno: las fechas-momento son los ganchos de **mayor disparo** que existen (son del *ahora* del lector), pero son **perecederos** — y nadie más los gestiona por ti.

## 1. Las dos caras de un mismo motor

| Cara | Qué hace | Cuándo actúa |
|---|---|---|
| 🎯 **Ofensiva (radar)** | detecta las fechas que se aproximan y **las explota**: avisa con tiempo + genera/sugiere la pieza para ese momento | *antes* de la fecha (con su lead time) |
| 🧹 **Higiene (vencimiento)** | marca el contenido de temporada como **"vencido"** cuando su fecha pasa y **ofrece refrescarlo** | *después* de la fecha |

La biblioteca de ganchos (Fase 2 §2.5) ya prometía *"los que no convierten se jubilan con datos, no con opiniones"*. La inteligencia temporal añade la otra jubilación: **los que ya pasaron de fecha** — la biblioteca aprende por **rendimiento Y por tiempo**.

## 2. El espinazo de capas (lo que lo hace agnóstico + persistente)

El motor **nunca hardcodea el calendario de un producto**: toma entradas (geo, nicho, avatar, datos propios) y produce las fechas relevantes. Mismo principio que todo el sistema — el motor es el producto, los datos son por-proyecto; **semilla → mide → afina** (Pattern B, igual que la cadencia §6.5 del Estudio).

| Capa | Qué es | De dónde sale | En v1 |
|---|---|---|---|
| **1 · Base universal + geo** | festivos civiles/religiosos por país (recurrencia + variantes regionales) + momentos **comerciales** (Black Friday, Small Business Saturday, vuelta al cole, temporada fiscal, bodas, cierres de Q) | **librería/API de holidays** para la capa civil (recurrencia + geo ya resueltas — D-IT5) + tabla curada `lookup_event_calendar_2026.md` para los comerciales que las librerías NO traen | ✅ |
| **2 · Overlay por nicho/avatar** | los momentos propios del *mercado* (florista→bodas/San Valentín; consultor→cierre fiscal/Q4; fitness→propósitos de año nuevo) | **derivados por LLM** desde el ICP + el avatar (nicho + `forces_of_progress`); operador-revisable (glass-box) | ✅ |
| **3 · Fechas propias del negocio** *(declaradas por el usuario)* | las que **solo el usuario sabe**: aniversario de la marca, sus lanzamientos, su temporada idiosincrática, la feria a la que va cada año | **el usuario las añade a mano** (UI); entran al radar como cualquier evento (`source: user_added`, lead_time + ofensiva + higiene). **La IA trabaja con ellas.** Glass-box total — son SUYAS | ✅ |
| **4 · Datos propios medidos** | qué fechas de verdad movieron *ventas* | **Fase 4** mide → el radar prioriza esas el año siguiente | ✅ (cuando haya datos) |
| **5 · Tendencias vivas** *(MÓDULO FUTURO)* | lo que explota ESTA semana (memes, noticias, trends de formato/audio) | feed externo de tendencias (dependencia de terceros) | ❌ diferido (§11) |

**Prioridad entre capas (son aditivas, no compiten):** dos eventos en la misma fecha se suman, no chocan. Para *rankear* qué oportunidad mostrar primero pesan la **cercanía del lead time** + la **autoridad de la fuente** — lo **declarado por el usuario** (capa 3) y lo **medido** (capa 4) mandan sobre lo derivado (capa 2) y la base (capa 1).

> **Decisión del operador (D-IT1, ampliada 2026-06-29):** v1 = capas **1+2+3+4** (base/geo, nicho derivado, **fechas propias declaradas**, datos medidos). La **capa 5 (tendencias vivas)** queda **marcada como módulo futuro** — alto valor pero necesita feed externo; no bloquea el v1.

## 3. El modelo de datos — la temporalidad como atributo

### 3.1 El evento (lo que el radar conoce)
```
event = {
  id,             // 'us_black_friday', 'us_fathers_day'
  name,           // "Black Friday"
  kind,           // holiday | commercial | cultural | niche | personal (fechas propias del usuario — capa 3)
  geo,            // ['US'] | ['MX'] | ['*'] universal
  recurrence,     // annual | one_off
  date_rule,      // "4º viernes de noviembre" | regla derivable a la fecha del año
  lead_time,      // con cuánta anticipación arrancar (Black Friday: 3-6 semanas)
  decay,          // cuánto sigue siendo relevante DESPUÉS (normalmente 0)
  source          // base_table | niche_derived | user_added | user_measured
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

- **Capa 1 (base):** dos fuentes, una sola salida:
  - **Festivos civiles/religiosos** → **librería/API de holidays por país** (recurrencia + variantes regionales ya resueltas — D-IT5). No los curamos a mano: día del padre/madre, Pascua (móvil), Thanksgiving por país… los resuelve la librería, **siempre al día** (requisito explícito del operador).
  - **Momentos comerciales/marketing** que las librerías NO traen (Black Friday, Small Business Saturday, Cyber Monday, vuelta al cole, temporada fiscal, bodas, cierres de Q) → tabla curada `lookup_event_calendar_2026.md`. La tabla **deja de ser la fuente de las fechas civiles** y pasa a ser la **inteligencia de marketing por evento** (`lead_time` + "quién lo explota" + B2B/B2C) sobre TODOS — incluidos los que da la librería (la librería dice *cuándo* es el día del padre; la tabla dice *con 3 semanas de anticipación lo explotan regalos/handmade*).
- **Capa 2 (nicho):** un **paso de derivación** (al configurar el proyecto / construir el calendario) le pide al LLM: *"dado este nicho + geo + avatar, ¿qué fechas/momentos recurrentes explota este mercado, con qué anticipación?"* → produce un **overlay de eventos por-proyecto**, que el operador **revisa y edita** (glass-box; nada entra sin su ojo).
- **Capa 3 (fechas propias declaradas):** el usuario **añade sus propias fechas** en la UI (aniversario de marca, lanzamientos, su temporada, ferias) → entran al radar como eventos de primera clase (`source: user_added`, `kind: personal`) con su `lead_time` y `temporality`, y **la IA produce/retira contenido para ellas igual que para cualquier evento** (misma ofensiva §6 + misma higiene §7). Es la capa **más cierta**: el usuario no infiere su aniversario, lo sabe. Glass-box total — son suyas; las edita o borra cuando quiera.
- **Capa 4 (datos propios medidos):** Fase 4 atribuye ventas a campañas de fecha → el radar **sube de prioridad** las fechas que de verdad funcionaron y baja las que no. Semilla → mide → afina.

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

## 8. Cruce con otros specs — el mapa de migración (qué cambia, campo por campo)

> El operador preguntó: *"¿cómo vamos a actualizar lo que YA tenemos construido para que tome estas nuevas variables y campos?"* Este es el changelist, separado en **(A) lo ya construido** (la app `sandia-marketing` deployada: Fase 0-2 + DB Supabase) y **(B) lo que aún es spec**. **Regla de oro:** el evento próximo entra al **brief como dato de entrada** (`{ today, upcoming_events[] }`); los generadores **nunca** hardcodean una fecha. Ese es el fix de fondo del bug origen — no un parche de "inyectar hoy", sino el evento del radar como input.

### 8.1 Relación (sin duplicar)
| Spec | Relación |
|---|---|
| **Estudio §6 (calendario)** | **consume** el radar: overlaya fechas próximas como oportunidades + dispara la ofensiva. Calendario = *cuándo publicar*; radar = *qué fechas explotar* — hermanos. |
| **`lookup_posting_cadence_2026`** | hermano metodológico: aquel = *cuándo publicar* (cadencia/ventanas); este = *qué fechas explotar*. Comparten `market_geo` + el modificador B2B/B2C. |
| **Módulo C (costos)** | producir piezas de temporada cuenta como costo (cruza con el COGS, no duplica). |

### 8.2 (A) Lo YA construido — `sandia-marketing` deployado (lo que de verdad hay que migrar)
| Dónde | Cambio concreto | Migración |
|---|---|---|
| **Fase 0 / config de proyecto** | + `market_geo` (nivel proyecto, se pregunta una vez — D-IT2) · + un **store de fechas propias** del usuario (capa 3) | columna `projects.market_geo` + tabla `project_events` (o JSONB) en Supabase; backfill `market_geo` por defecto del país primario del idioma, editable |
| **Fase 2 §2.5 — ganchos (`content_json.hooks[]`)** | cada hook gana `temporality` (`'evergreen'`\|`'seasonal'`) y, si seasonal: `event_ref`, `valid_window{start,end}`, `expires_at` | **backfill seguro: todo lo ya generado = `evergreen`** (nada caduca por sorpresa) hasta que se regenere |
| **Generador 2.5 (`app/api/phase2/step-proposal`)** | recibe `{ today, upcoming_events[] }` del radar como input del brief → generación **consciente de fecha**; el ↻ regenerar-uno idem | cambia el prompt builder (`lib/wizard/phase2/canon.ts`) + el payload de la ruta; **cierra el bug origen** (Nov/Feb en junio) |
| **DB Supabase** | `project_events` (declaradas + overlay derivado, con `source`) · cache de festivos de la librería | nuevas tablas/migraciones |

### 8.3 (B) Lo que es spec (se construye en su Trinity)
| Dónde | Cambio |
|---|---|
| **Estudio §3.1 (pieza)** | la pieza gana `temporality` + (`event_ref`, `valid_window`, `expires_at`) — mismos campos que el gancho |
| **Estudio §6 (calendario)** | franja "fechas que se acercan" + botón "preparar campaña" (consume el radar) |
| **Fase 4 (medición)** | emitir atribución **fecha→ingreso** → alimenta la **capa 4** (`user_measured`) |
| **Setup Agent / Fase 0** | UI para que el usuario **añada/edite sus fechas propias** (capa 3) + el paso de derivación de nicho (capa 2) revisable |
| **Adapter de holidays** | interfaz `HolidaySource` que envuelve la librería (D-IT5) — cambiar de proveedor sin tocar el radar |

## 9. La UI (esbozo — se detalla en su trinity)
- En el **calendario** del Estudio: una franja de "fechas que se acercan" con su lead time + botón *"preparar campaña"*.
- En la **biblioteca**: filtro/etiqueta perenne vs de-temporada; los **vencidos** marcados con *"refrescar"*.
- En **producción**: al generar contenido de temporada, el evento próximo visible en el brief (glass-box: *"esta pieza está anclada a [evento]; vence el [fecha]"*).

## 10. Decisiones cerradas

| # | Decisión | Resolución (operador, 2026-06-29) |
|---|---|---|
| **D-IT1** | Alcance v1 *(ampliado 2026-06-29)* | Capas **1 (base/geo) + 2 (nicho derivado) + 3 (fechas propias declaradas por el usuario) + 4 (datos medidos)**. **Capa 5 (tendencias vivas) = módulo futuro**, marcado, no v1. |
| **D-IT2** | Cómo se conoce la geo | Campo **`market_geo` a nivel proyecto**, preguntado una vez, reusado por radar + zonas horarias. **Por-avatar = evolución futura**, anclada en el spec. |
| **D-IT3** | Higiene del contenido vencido | **Sugiere, nunca borra solo** (operador autor): marca "vencido" + ofrece refrescar. |
| **D-IT4** | Casa en los specs | **Sub-spec propio** (este doc) + tabla lookup base + referencias desde Estudio/Fase 2/Fase 4. No se infla §6 del Estudio. |
| **D-IT5** | Fuente de la capa civil (base) | **Librería de holidays por país** (recurrencia + variantes regionales ya resueltas; *siempre actualizada*), **tras un adapter `HolidaySource`** para poder cambiar de proveedor. **RESUELTO 2026-06-30 (verificado el stack): el producto deployado es 100% Next.js/TS + Supabase, CERO Python** → default **`date-holidays` (npm)** — local, in-proceso en las mismas API routes donde ya corre la generación (`app/api/phase2/*`), 200+ países, TS-native, sin API externa ni servicio nuevo. **`Nager.Date`** (API) como fallback · **`Calendarific`** si se necesita cobertura/idiomas (de pago). **`python-holidays` descartada** (requeriría un servicio Python que no existe). Los **momentos comerciales/marketing** los curamos nosotros. |

## 11. Pendientes / módulos futuros (antes de codear)

- **▶ SIGUIENTE — Trinity propia** (spec completo + plan + tasks): **decisión de secuencia del operador (2026-06-29): se construye JUSTO DESPUÉS de este refinamiento y JUSTO ANTES de arrancar la producción de contenido.** Es el siguiente paso formal del proyecto. La Trinity confirma: pick exacto de librería (D-IT5), esquema `project_events`, el paso de derivación de nicho, y el orden de migración de §8.2.
- **Derivación de nicho (capa 2):** ¿inferencia LLM pura, o un paso de research ligero por nicho? + cómo se revisa/edita el overlay. (Se cierra en la Trinity.)
- **Sembrar + validar `lookup_event_calendar_2026.md`** — ahora **solo los momentos comerciales** + sus lead times (los civiles los trae la librería, D-IT5); candidato a estudio a profundidad, como se hizo con la cadencia.
- **Capa 5 — tendencias vivas:** feed externo (trends de plataforma, noticias). Alto valor, dependencia de terceros. Su propio mini-spec cuando se aborde.
- **Geo por-avatar:** cuando un proyecto apunte a geografías múltiples (US + México a la vez). Diseñar el modelo v1 para que subir a por-avatar sea aditivo, no reescritura.
- ✅ ~~**Fuente de la tabla base**~~ → **RESUELTO (D-IT5):** librería de holidays para lo civil + curación nuestra para lo comercial.
- ✅ ~~**Eventos personales del negocio**~~ → **RESUELTO:** promovido a **Capa 3** (fechas propias declaradas), de primera clase en v1 — `source: user_added`, `kind: personal`.
