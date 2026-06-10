# Módulo A — Business Case (Business Model Canvas completo) — STUB

**Project**: business/marketing-os
**Module ID**: module-a-business-case
**Status**: **STUB** (arquitectura fijada D-019; spec completo = pase dedicado tras la simulación de marketing)
**Last updated**: 2026-06-07

**Decisión (D-019):** Sandi = **dos módulos que se entrelazan**. Este es el **Módulo A — Business Case**, que valida que el negocio sea **viable** usando el **Business Model Canvas completo (9 bloques de Osterwalder)**. El **Módulo B — Marketing OS** (Phases 0–5 en `Overall_WF.md`) valida cómo se vende. Comparten la investigación de Phase 0 (Foundation) para no duplicar.

**Origen:** análisis NotebookLM (cruce specs ↔ "Generación de Modelos de Negocio", Osterwalder) — los specs eran fuertes en el lado derecho del Canvas (cliente/valor/canal) y flacos en infraestructura/viabilidad. Este módulo cierra ese hueco.

---

## 0. Principio de diseño (el salvavidas anti-genérico)

BMC completo **NO** significa "llenador de 9 cajas". El Módulo A se entrega con el **mismo estándar de calidad que el Setup Agent** (ver `spec_Phase_0_Setup_Agent.md`):
- Los **6 movimientos** (incluido co-crear), glass-box, educación adaptativa, memoria de agente, carácter SOUL.
- **Enfocado en viabilidad**, no en completar el canvas por completarlo: cada bloque existe para responder *"¿esto hace el negocio viable o lo rompe?"*.
- **Entrelazado** con Marketing (no standalone): comparte Foundation, alimenta el pricing, y su gate de viabilidad protege al marketing de promover un negocio inviable.

Sin esto, el Módulo A sería el "generador de business plans genérico" del mercado saturado. Con esto, es un socio de pensamiento que co-desarrolla el modelo de negocio.

---

## 1. Los 9 bloques — y qué ya está cubierto por la Foundation de Marketing

| # | Bloque BMC | Estado vs Marketing OS | Dónde |
|---|---|---|---|
| 1 | **Customer Segments** | ✅ compartido | Phase 0.2.5 ICP + 0.3 persona/avatars |
| 2 | **Value Propositions** | ✅ compartido | Phase 1 (value equation, offer stack) |
| 3 | **Channels** | ✅ compartido | Phase 2/3 (channel_journey, distribución) |
| 4 | **Customer Relationships** | 🟡 parcial — falta el **tipo** (asistencia personal / autoservicio / comunidad / co-creación) | a integrar en 0.3/2 |
| 5 | **Revenue Streams** | 🟡 parcial — tenemos `monetization_model` + pricing 1.4; falta el modelo de ingresos completo | extender |
| 6 | **Key Resources** | 🔴 hueco | nuevo en Módulo A |
| 7 | **Key Activities** | 🔴 hueco | nuevo en Módulo A |
| 8 | **Key Partnerships** | 🔴 hueco | nuevo en Módulo A |
| 9 | **Cost Structure** | 🟡 parcial — gate LTV/CAC + modelo de costo de IA parqueado; falta fijos/variables/economías de escala | extender |

**Lectura:** 3 bloques ya los tiene Marketing (se reusan), 3 son parciales (se extienden), 3 son huecos reales (se crean aquí). El Módulo A **no reinventa** el lado derecho — añade el izquierdo + costos.

---

## 2. Técnicas de diseño estratégico a incorporar (del análisis Osterwalder)

| Técnica | Qué aporta | Dónde encaja |
|---|---|---|
| **Escaneo de entorno (4 fuerzas)** | tendencias tech / socioeconómicas / industria / macro — que la idea no muera contra el entorno | conecta con `foundation_drift`; sub-paso en Phase 0 |
| **Blue Ocean — Eliminar/Reducir/Aumentar/Crear (ERRC)** | innovación en valor; separación radical de la competencia | afila el `differentiation_angle`; Phase 1 |
| **Prototipos "what-if"** | 2–4 variantes de modelo de negocio/oferta antes de comprometer (patrón "judge panel") | Phase 1 |
| **DAFO por bloque** | cruzar F/D/O/A contra cada uno de los 9 bloques, no un DAFO genérico | gate de viabilidad del Módulo A |

---

## 3. Entrelace con el Módulo B (Marketing OS)

- **Foundation compartida:** Phase 0 (mercado, demanda, competencia, ICP) sirve a ambos. No se corre dos veces.
- **Costos → Pricing:** `Cost Structure` (bloque 9) + Key Resources/Activities (6/7) alimentan el pricing de Phase 1.4 y el **sistema de créditos** (resuelve la dependencia parqueada del modelo de costo de IA).
- **Gate de viabilidad → Marketing:** si el modelo de negocio no es viable (DAFO por bloque, unit economics con costos reales), se **frena** antes de gastar en marketing un negocio inviable.
- **Marketing → Business Case:** el research de demanda (0.2) valida/refuta los Revenue Streams y Customer Segments.

---

## 4. Secuencia / dependencia (a definir en el pase completo)

Pregunta abierta para el pase dedicado: ¿el Módulo A corre **antes** del marketing (sanity de viabilidad primero), **en paralelo**, o **iterativo** (BMC borrador → marketing → refinar BMC)? Hipótesis: **un sanity ligero primero + el detalle en paralelo/iterativo**, porque marketing y modelo de negocio se informan mutuamente.

---

## 5. Pendiente para el pase completo (backlog)

- [ ] Specear los 9 bloques con el formato del Setup Agent (pregunta llana → artefacto → flag), igual que Phase 0.1.
- [ ] Definir el artefacto canónico (`business_model_canvas.json`) bajo [Evolving Schema].
- [ ] El gate de viabilidad (DAFO por bloque + unit economics con costos reales).
- [ ] Los sub-workflows: escaneo de entorno, Blue Ocean ERRC, what-if prototyping.
- [ ] Secuencia/dependencia con Marketing (§4).
- [ ] Integrar lo marketing-adyacente en el Módulo B en su fase natural: Customer Relationship type (0.3/2), entorno (0.4), Blue Ocean (1), what-if (1).
- [ ] Privacidad (3 capas) + memoria de agente + carácter — heredados de Overall_WF, confirmar aplicación.

> **Status: STUB.** La arquitectura está fijada para que el resto de la simulación de marketing no la contradiga. El spec completo se hace en un pase dedicado al terminar la simulación.
