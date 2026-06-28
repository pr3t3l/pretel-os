# El Estudio — Producción & Publicación (post-plan)

**Project**: business/marketing-os
**Status**: **BORRADOR EN DESARROLLO** (se redacta sección por sección con el operador; NO es ley, NO codear hasta firmar). Fundación §0–2 redactada; §3–11 pendientes.
**Last updated**: 2026-06-28
**Origen:** sesión sim Papandi (2026-06-28). Tras cerrar el plan (Fase 2) el operador identificó el puente que falta: el plan dice QUÉ publicar, pero hace falta PRODUCIR las piezas reales y PUBLICARLAS. Decisión arquitectónica del operador: esto es un **workspace independiente del wizard** ("el Estudio"), no una fase más.
**Cruza con:** `spec_Production_Support_and_Pricing_PROPOSAL.md` (modos + pricing), `spec_Phase_2_Contenido.md` (el plan que alimenta), `spec_Phase_3_Distribucion.md` (publicar/medir — el Estudio es su casa/UI), `spec_Admin_Cost_Intelligence.md` (Módulo C — billing/cost admin).

---

## Mapa del documento (esqueleto)

| # | Sección | Estado |
|---|---|---|
| 0 | Propósito + La Promesa | ✅ redactada |
| 1 | Arquitectura: wizard vs Estudio | ✅ redactada |
| 2 | Contrato de datos: el plan alimenta la generación | ✅ redactada |
| 3 | Producción pieza por pieza (copy/imagen/video por su modo) | ⬜ pendiente |
| 4 | Endpoints + wrapper | ⬜ pendiente |
| 5 | Biblioteca de assets (storage) | ⬜ pendiente |
| 6 | Calendario de publicaciones | ⬜ pendiente |
| 7 | Guía de publicación (acompañamiento) | ⬜ pendiente |
| 8 | La UI del Estudio | ⬜ pendiente |
| 9 | Costos / pricing por modo | ⬜ pendiente |
| 10 | Cruce con specs existentes | ⬜ pendiente |
| 11 | Decisiones abiertas | ⬜ pendiente |

---

## 0. Propósito + La Promesa

**Propósito.** El Estudio convierte el **plan de contenido firmado** (Fase 2) en **piezas reales producidas y publicadas**. Es el puente entre *"sé qué publicar"* y *"lo publiqué"* — y por tanto entre el plan y la KPI (dinero). Sin el Estudio, el plan es un mapa que el usuario no sabe ejecutar y abandona en la semana 3.

**La Promesa (el contrato de honestidad — por tipo de pieza).** Lo que de verdad cumplimos, sin letra chica:

| Tipo de pieza | Qué hace Sandi | Qué pone el usuario | Costo |
|---|---|---|---|
| **Texto** (artículo, copy, email, guion, asunto, hilo) | Lo **escribe completo**, en tu voz, con tu gancho — listo para aprobar | Aprobar (o ajustar) | incluido |
| **Imagen** | (a) la **genera** desde tu foto cruda · (b) te da el **prompt** para tu IA · (c) te **guía** a tomarla | elige la ruta; sube la foto o la toma | (a) cuesta · (b)(c) $0 |
| **Video** | Escribe el **guion** + la **guía de producción** (ambiente/luz/tips); o **anima el producto con IA** (beta) | graba siguiendo la guía (si DIY) | guion incluido · IA cuesta |
| **Publicación** | Te **avisa con la pieza lista adentro** + el momento | publica en 1–2 clics (auto-publish = futuro) | incluido |

**La anti-promesa (lo que NO prometemos).** Nunca decimos *"todo te llega hecho"* cuando una parte la pones tú o cuesta extra. **Cada pieza muestra su modo, tu-parte y su costo, antes de producir.** La persona en cámara la grabas tú (con guía) — no la inventa la IA (políticas + autenticidad). Es el mismo glass-box de todo el producto, aplicado a la producción.

## 1. Arquitectura: el wizard vs el Estudio

Dos superficies distintas, con propósitos distintos:

| | **El Wizard (Fases 0–2)** | **El Estudio (post-plan)** |
|---|---|---|
| Propósito | **Planear** | **Operar** |
| Cuándo | una vez, al inicio | siempre, día a día |
| Forma | lineal, con candados, gated | workspace persistente, libre |
| Termina en | `content_plan` firmado | (no termina — es el hogar) |
| El usuario… | decide la estrategia | produce, publica, mide |

**Regla dura (mandato del operador):** una vez firmado el plan, el usuario **NO vuelve a abrir Fase 2** (pilares, voz, reparto) para publicar. Entra **directo al Estudio**. El plan firmado queda **visible en solo-lectura** (referencia), pero la operación vive en el Estudio. Enmendar el plan es una acción explícita aparte (re-abre el sub-paso, como hoy).

**Por avatar.** El Estudio es **por avatar** (cada avatar tiene su plan → su cola de producción + su calendario). Hereda el llaveado `avatar_key` (C15). El selector de avatar vive en el Estudio.

**Relación con Fases 3–5.** El Estudio es la **casa operacional** de:
- **Producción** (la capa nueva — plan → assets reales).
- **Fase 3 — Publicar** (calendario + tracking + "te aviso").
- **Fase 4 — Medir** (los resultados que el usuario VE).
- **Fase 5 — Ajustar** (señales que re-disparan producción/plan).
El usuario no piensa en "fases 3/4/5" — piensa en "producir, publicar, ver cómo va". Las fases son la plomería; el Estudio es la experiencia.

## 2. Contrato de datos: cómo el plan firmado alimenta la generación

**Principio:** nada del plan se desperdicia. **Cada pieza real se genera cruzando los artefactos firmados** — el plan es el ADN de cada pieza. Para producir UNA pieza, el generador toma:

| Input (artefacto firmado) | Qué aporta a la pieza |
|---|---|
| **2.4 Atomización** (la pieza) | su **ancla** (título) + el **kind** (canal × formato) + la nota → QUÉ es esta pieza |
| **2.3 Pilar** al que pertenece | la **fuerza** + el **modo** (reforzar/resolver) + de qué habla → el ÁNGULO/mensaje |
| **2.5 Ganchos** de ese pilar | la biblioteca de ganchos → el **primer segundo** de la pieza |
| **2.0 Voz** | arquetipo, tono, léxico, prohibidos → **cómo SUENA** |
| **2.2 Canal** | función del canal + cadencia + ventanas → DÓNDE/CUÁNDO y el formato |
| **2.1 Reparto** | el momento de conciencia que toca → el **registro** (educar/comparar/capturar) |
| **Fase 1 Oferta** | las **palabras exactas** (garantía, displacement) → lo que las piezas REFORZAR citan |
| **Fase 0** | keywords reales + `where_we_meet` + idioma del avatar → anclaje + formato + idioma |
| **Perfil de producción** | capacidades del usuario → enruta al **modo** (texto auto / imagen / video DIY-guía) |

**La fórmula de una pieza:**
> (ancla + kind) × (mensaje del pilar) × (gancho) × (voz) × (canal/momento) × (palabras de la oferta si reforzar) → **el copy real + las instrucciones de visual/video**, en el idioma del mercado, por el modo de producción que le toca.

**Implicación:** el generador de producción es un prompt CAG (como los de Fase 2) que recibe TODO esto firmado y produce la pieza terminada. Glass-box: el usuario ve de qué pilar/gancho/voz nació cada pieza. Reusabilidad total del plan.

---

## 3. Producción pieza por pieza  ⬜
*(pendiente — el modo por pieza, el copy por canal, el prompt de imagen, la guía de video)*

## 4. Endpoints + wrapper  ⬜
*(pendiente — qué endpoint por tipo; cómo el usuario elige; la capa wrapper)*

## 5. Biblioteca de assets  ⬜
*(pendiente — dónde se guarda; reuso; storage Supabase + retención)*

## 6. Calendario de publicaciones  ⬜
*(pendiente — dónde vive; cómo recibe la info por canal; cadencias del plan)*

## 7. Guía de publicación  ⬜
*(pendiente — el acompañamiento; "te aviso con la pieza lista"; pasos por canal; marcar publicado → medición)*

## 8. La UI del Estudio  ⬜
*(pendiente — pantallas: producir · biblioteca · calendario · publicar; navegación; acceso directo)*

## 9. Costos / pricing por modo  ⬜
*(pendiente — cross-ref a la propuesta: N-gratis + créditos + BYO; el ledger del Módulo C)*

## 10. Cruce con specs existentes  ⬜
*(pendiente — Fase 3 distribución, Fase 4 medir, Módulo C admin; sin duplicar)*

## 11. Decisiones abiertas  ⬜
*(pendiente — endpoint primero, N-gratis, storage, avatares, auto-publish, etc.)*
