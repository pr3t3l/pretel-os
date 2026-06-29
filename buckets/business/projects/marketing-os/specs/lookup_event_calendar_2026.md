# LOOKUP — Calendario de eventos / fechas explotables (semilla 2026)

**Status:** **SEMILLA v0.1** (Pattern B: base curada + overlay por nicho derivado + priorización por datos propios en Fase 4). Extensible. · **Origen:** mandato del operador 2026-06-29 (ver `spec_Inteligencia_Temporal.md` — el radar de fechas). Esta tabla es la **Capa 1** (base universal + geo); la Capa 2 (nicho) se DERIVA por proyecto; la Capa 3 (datos propios) la reordena con el tiempo.
**Regla de notación:** las fechas se escriben como **regla de recurrencia** (`date_rule`), no como fecha fija de 2026 — recurren cada año y se derivan al año en curso. `lead_time` = con cuánta anticipación arrancar contenido. `geo` = dónde aplica (universal `*` o país).
**Persistencia:** este doc (referencia narrativa) + best_practice `LOOKUP-TABLE event_calendar` en pretel-os (descubrible cross-producto).
**Aviso de geo:** sembrada **US-primaria** (mercado primario de Papandi, [[papandi-language-strategy]]) con la **variación por país señalada**. NO asumir US para todos — el día del padre/madre cae distinto por país; `market_geo` del proyecto manda.

---

## Capa 1 — Eventos base (universal + comercial), US-primario con variación por país

| Evento | `date_rule` (US salvo nota) | `kind` | `lead_time` | Quién lo explota |
|---|---|---|---|---|
| **Año nuevo / propósitos** | 1 ene (arranca ~26 dic) | cultural | 1-2 sem | fitness, coaching, finanzas, "fresh start" en casi todo |
| **San Valentín** | 14 feb | commercial | 2-3 sem | regalos, handmade, hospitality, parejas |
| **Temporada de impuestos** | ~15 ene–15 abr (US) · varía por país | niche/commercial | 3-4 sem | contadores, finanzas, freelancers (deducciones) |
| **Pascua / Semana Santa** | móvil (mar–abr) | cultural | 2-3 sem | retail, familia, viajes, alimentos |
| **Día de la madre** | 2º dom de mayo (US) · **MX 10 may fijo** · **UK 4º dom de Cuaresma, mar** | commercial | 3 sem | regalos, handmade, flores, restaurantes |
| **Memorial Day** | último lun de mayo (US) | commercial | 2 sem | arranque de rebajas de verano (US) |
| **Día del padre** | 3er dom de junio (US) · **ES/parte LATAM 19 mar (San José)** · **AU 1er dom sep** | commercial | 3 sem | regalos, handmade, herramientas |
| **Verano / bajón** | jun–ago | seasonal | continuo | algunos pican (lifestyle, viajes), otros caen (B2B) — usar para "slow season" honesto |
| **Vuelta al cole** | jul–sep (US) | commercial | 4-6 sem | retail, papelería, edtech, organización |
| **Labor Day** | 1er lun de sep (US) | commercial | 2 sem | rebajas; "back to business" B2B |
| **Halloween** | 31 oct | cultural/commercial | 3-4 sem | retail, costumes, contenido lúdico |
| **Acción de Gracias** | 4º jue de nov (US) · **CA 2º lun oct** | cultural | 2-3 sem | familia; antesala de Black Friday |
| **Small Business Saturday** | sáb tras Acción de Gracias (US) | commercial | 2-3 sem | **handmade, local, makers** (alto encaje C-B2C) |
| **Black Friday** | 4º vie de nov | commercial | **4-6 sem** | el gran momento comercial; global pero más fuerte US |
| **Cyber Monday** | lun tras Black Friday | commercial | 4-6 sem | ecommerce, digital, servicios online |
| **Temporada navideña / regalos** | dic (arranca ~mediados nov) | commercial | **6-8 sem** | pico de retail; regalos, handmade, gift guides |
| **Fin de año** | 31 dic | cultural | 1-2 sem | retrospectiva, "year in review", ofertas de cierre |

## El gran modificador B2B vs B2C (igual que la cadencia)

- **B2C** (handmade, consumo, lifestyle): los **comerciales/culturales** de arriba mandan (San Valentín, día madre/padre, Black Friday, navidad, Small Business Saturday).
- **B2B** (coaches, consultores, freelancers de servicio): mandan los **ciclos de negocio** — cierres de trimestre (**fin de Q1/Q2/Q3/Q4**), cierre de año fiscal, el **arranque de enero** (presupuestos nuevos) y el **"regreso" de septiembre**. Año nuevo también pega fuerte (propósitos → demanda de coaching).

→ El tipo del avatar (B2B/B2C, de `where_we_meet` + el tipo) filtra **cuáles** de estos eventos son suyos.

## Capa 2 — Overlay por nicho (ILUSTRATIVO — se DERIVA por proyecto, no se hardcodea)

Ejemplos de lo que la derivación (LLM desde nicho + avatar) produciría — **no es una lista fija**, es muestra del *tipo* de momento:

| Nicho (avatar) | Sus momentos propios (además de la base) |
|---|---|
| Handmade / makers (B2C, Etsy) | Small Business Saturday · temporada de regalos · San Valentín · día madre/padre · temporada de bodas |
| Coaches / consultores (B2B) | propósitos de año nuevo (pico de demanda) · "regreso" de septiembre · cierre de Q4 · cierre de año fiscal |
| Servicios locales | estacional del oficio (HVAC verano/invierno · jardinería primavera) · eventos locales de su ciudad |
| Freelancers / marketplaces (B2B) | enero (clientes con presupuesto nuevo) · rampa de Q1 · fin de año fiscal del cliente |

## Variación de geo (no asumir US — `market_geo` manda)

| Evento | US | México | España / parte LATAM | UK | Australia | Canadá |
|---|---|---|---|---|---|---|
| Día de la madre | 2º dom may | **10 may (fijo)** | varía | 4º dom Cuaresma (mar) | 2º dom may | 2º dom may |
| Día del padre | 3er dom jun | 3er dom jun | **19 mar (San José)** | 3er dom jun | **1er dom sep** | 3er dom jun |
| Acción de Gracias | 4º jue nov | — | — | — | — | **2º lun oct** |
| Black Friday | 4º vie nov | sí (importado) | sí (importado) | sí | sí | sí |

## La meta-regla (igual que la cadencia)

La tabla es la **SEMILLA, no la verdad**. El óptimo real sale de los **datos del propio usuario**: **Fase 4** mide qué fechas movieron *ventas* → el radar **prioriza esas** el año siguiente y baja las que no funcionaron. Semilla (base + nicho) → mide → afina. El loop perpetuo del Estudio.

## Pendientes (de `spec_Inteligencia_Temporal.md §11`)

- **Fuente mantenida:** ¿curada a mano o respaldada por una librería/API de holidays por país (recurrencia + geo ya resueltas)? — decidir.
- **Sembrar a profundidad:** lead times y "quién explota qué" con grounding (candidato a estudio, como se hizo con la cadencia).
- **Más geos:** ampliar la tabla de variación cuando entren mercados no-US.

## Fuentes (semilla — pendiente grounding a profundidad)

- Conocimiento base de calendario comercial US + variación internacional de día madre/padre (a confirmar con fuente mantenida).
- Hermana metodológica: [[lookup_posting_cadence_2026]] (mismo Pattern B: semilla calibrada → datos propios afinan).
