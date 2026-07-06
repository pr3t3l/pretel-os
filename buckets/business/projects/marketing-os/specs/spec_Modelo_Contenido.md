# Spec — El modelo de contenido: PILAR → ÁNGULO → PIEZA

**Estado:** v1 borrador — para firma del operador.
**Decisión de arquitectura (2026-07-06, esta sesión):** el **derivado** (2.4 "La multiplicación": idea `note` + canal `kind`) se **elimina como capa**; el **ángulo (gancho, 2.5) es la unidad de producción**; la **pieza = ángulo × canal**. El operador aceptó explícitamente rehacer lo ya construido si mejora el sistema.
**Decide:** cuál es la unidad de contenido, cómo se relacionan pilares/ganchos/piezas, cómo se genera contenido sin límite finito, y cómo el sistema aprende (la cascada de diagnóstico).
**Supersede (se ratifica como C17 en `_audit_change_ledger.md` al firmar):** el concepto de "atomización / derivados como unidad" de `spec_Phase_2_Contenido.md` **§7 (Atomization)** — el paso 2.4 del wizard deja de emitir derivados. **§8 (Hook Library)** se mantiene pero el gancho pasa a ser la UNIDAD, no una biblioteca de aperturas. La ratio dar:pedir se reubica (§5); el ancla sobrevive (§3). **Afecta (deben actualizarse al firmar):** `Overall_WF.md` (Lifecycle Fase 2), `spec_Estudio_Produccion_Publicacion.md` (input del develop), `spec_Inteligencia_Temporal.md` + su build_plan (calendario finito→generativo), `spec_Phase_Identidad.md` §1.5 (calendario generativo).
**Fuentes:** doctrina del Cerebro de Ganchos (3 capas, operador 2026-07-02) · `docs/research/doctrina-por-canal.md` (formato/gate por canal) · decisión del operador esta sesión · schema actual `lib/schemas/content-plan.ts`.

---

## 0. La tesis

Hoy conviven **dos listas de "qué decir"** generadas por llamadas LLM separadas y casadas **por índice**:
- **Derivados** (2.4): `{ kind: "Reel de Instagram", note: "el desglose de por qué caen las ventas" }` — traen su propia idea + un canal.
- **Ganchos** (2.5): `{ template: "problem_agitate", text: "You had a great November", pillar: "A" }` — cero canal, sustancia pura.

`rotateHook(pilar, índice, fecha)` los pega por posición ([`brief.ts:66`], [`plan.ts:253`]): el gancho #3 del pilar A cae sobre el derivado #3 **por accidente, no por significado**. La card dice *«Abre con: You had a great November»* pero el cuerpo salió del `note` — que puede no tener nada que ver. Esa es la incoherencia de raíz.

La doctrina ya dictó el ganador: **"El DOLOR (sustancia) = los ganchos + pilares. Sagrado: ninguna plantilla lo reemplaza."** El gancho ES la sustancia; el derivado es una segunda idea redundante encima.

**Decisión: el derivado muere. El ÁNGULO (gancho) es la unidad. La pieza es ángulo × canal.**

---

## 1. El árbol

```
PILAR (territorio del dolor — una de las 4 fuerzas del avatar)
  ├─ 1 ANCLA        → la pieza cornerstone del pilar (típico: blog/SEO largo). Rol especial (§3).
  └─ N ÁNGULOS      → los ganchos (2.5): la biblioteca de "qué decir", agnóstica de canal.
        └─ PIEZA = ÁNGULO × CANAL×FORMATO
              · el CANAL decide formato / reglas / media-gate (toda la investigación por canal)
              · el ÁNGULO decide la sustancia (el dolor, sagrado)
              · el PILAR es el substrato que da profundidad al ángulo (§4) y la raíz del diagnóstico (§6)
```

Cada nivel existe por una razón distinta:

| Nivel | Qué es | Unidad de… |
|---|---|---|
| **Pilar** | cobertura del dolor (garantiza atacar las 4 fuerzas del avatar) | ESTRATEGIA |
| **Ángulo (gancho)** | una manera concreta de entrar a ese dolor | PRODUCCIÓN + APRENDIZAJE |
| **Canal** | dónde y en qué formato se publica | DISTRIBUCIÓN |
| **Ancla** | el activo profundo al que las piezas apuntan (cross-link / CTA) | AUTORIDAD |

---

## 2. Qué muere y qué sobrevive

**Muere:**
- La capa **derivados** de 2.4 (la lista de ~28 piezas pre-horneadas con `note` propio).
- **`rotateHook` como casamiento por índice**: el gancho ya no "rota sobre" un derivado — se **ELIGE** un ángulo para desarrollar.
- El **plan finito de 28** ("el plan se acaba"). Ver §4.

**Sobrevive intacto:**
- 2.3 **Pilares** — ahora MÁS centrales (substrato + raíz diagnóstica).
- 2.5 **Ganchos** — ahora LA unidad; el candado ≥10 por pilar sigue garantizando la productividad del pilar.
- 2.2 **Canales** — la dimensión de formato/gate.
- Toda la **doctrina por canal** (C3), los **gates de media** (Identidad), los **ganchos visuales** y la **doctrina de video** — aplican al desarrollar, sin cambio.
- El **ancla** (§3).

---

## 3. El ancla: el único pre-designado

El ancla se queda porque hace algo que un ángulo suelto no hace: es el **activo cornerstone** del pilar (la página pilar de SEO), el destino profundo al que las piezas cortas enlazan (el cross-link que da autoridad). Es un **ROL, no una cuarta lista**: **un ancla designada por pilar** (típicamente blog/SEO largo), refrescable. Sigue siendo ángulo × canal, solo marcada como ancla.

---

## 4. Generación infinita, no finita (el punto del operador)

El modelo viejo era una **cola finita**: 28 derivados = el plan, con principio y fin (`plan.ts` lo dice literal: *"el calendario dice honestamente cuándo se acaba el plan"*). El operador lo rechazó: *"podemos usar esos mismos pilares para generar contenido durante 3 años si queremos."* Correcto.

El nuevo modelo es un **motor renovable**: `pilares × biblioteca-de-ángulos × canales-habilitados` es un espacio que no se agota. No existe "se acabaron las 28".

**El "set inicial" reemplaza a los 28:** al firmar, el sistema **pre-dibuja una primera tanda** de piezas (ángulo × canal) repartidas sobre las cadencias/ventanas de 2.2 — para que no mires un calendario en blanco — pero se entiende como *un primer sorteo del pozo*, extensible siempre, **NO** como el plan completo y final. La disciplina de mezcla (no 40 Reels) vive en **cómo se pesa ese sorteo** (investigación por canal: carrusel=educar, Reel=alcance, imagen=relleno…).

**Reconciliación con `spec_Phase_Identidad.md §1.5` (ronda 4):** ahí se escribió *"el calendario se llena COMPLETO al firmar (las 28)… el plan se acaba"*. Esto lo **REVISA**: el calendario se llena con el **set inicial** (mismo beneficio de "qué toca hoy", mismos estados ○◐●✓), pero **no se acaba** — se re-alimenta desde la biblioteca de ángulos. Se elimina la honestidad incómoda del "plan finito"; el motor es renovable. *(Pendiente: actualizar Identidad §1.5.)*

---

## 5. El ratio dar:pedir — nuevo hogar

Vivía en la AtomizationMap (2.4: `ratio_policy_plain`). Se reubica: es una **política** (default 3:1) evaluada ahora sobre los **ángulos/piezas que eliges desarrollar**, por su `intent` (value/cta/hybrid; los pilares en modo *reforzar* = pedir). Más limpio: el ratio siempre fue sobre lo que PUBLICAS, y lo que publicas ahora son piezas ángulo×canal. Sin cambio de comportamiento (**avisar, no bloquear**).

---

## 6. La cascada de diagnóstico (el insight del operador)

El operador: *"podríamos detectar si todos los ganchos de un pilar están fallando → sabríamos que el pilar está malo → re-plantearlo."* Es la clave del loop de automejora, y **resuelve el "matiz honesto"** (un gancho es una semilla delgada de 1-2 frases): el pilar es a la vez el **substrato** que da profundidad al ángulo al desarrollar Y la **raíz** de la que cuelga el diagnóstico. El gancho nunca está solo — siempre se expresa a través de su pilar (dolor/fuerza/mensaje) y un canal (formato).

Jerarquía de aprendizaje, de abajo a arriba:

| Nivel | Pregunta | Tag que lo aísla |
|---|---|---|
| Pieza | ¿esta ejecución concreta funcionó? (1 dato, ruidoso) | `piece_id` |
| **Ángulo (gancho)** | ¿este ángulo convierte across canales? → **multiplicar la ganadora** | `hook_id` |
| Forma | ¿esta forma retórica abre mejor (contrarian vs question)? | `template` |
| Canal | ¿este pilar rinde en carrusel vs Reel? | `channel` |
| **PILAR** | **¿TODO el territorio del dolor está muerto? → re-planear (volver a 2.3)** | `pillar_id` |

**Regla de rigor (aislar la variable — surface, don't reconcile):** un pilar se declara malo **SOLO si falla across canales Y formas Y ángulos**. Si solo fallan los Reels → es el canal. Si solo fallan los ganchos "contrarian" → es la forma. Si un ángulo falla pero otros del mismo pilar ganan → es el ángulo, no el pilar. El diagnóstico corta por cada dimensión antes de acusar al pilar (lo más caro de estar mal).

Esto exige que cada pieza nazca etiquetada con todas las dimensiones (§7). Sin eso la atribución es imposible — y hoy, con el casamiento por índice, **ES imposible**: por eso el loop no podía funcionar.

---

## 7. La taxonomía que lo habilita

Cada pieza nace con: `pillar_id` × `hook_id` × `template` (forma) × `channel` × `visual_hook` × `intent` (value/cta/hybrid) × `origin` (inicial/ángulo/campaña) × `campaign_id`+phase × `utm_*` × personaje/set usados. (Extiende lo aprobado en R3.) El loop de §6 son GROUP BY sobre estas columnas.

---

## 8. Qué se re-hace en código (honesto)

- **`lib/wizard/phase2/canon.ts` (2.4)** → deja de emitir derivados; emite (a) el **ancla por pilar** + (b) la **política de ratio**. El candado "1 ancla + ≥5 derivados" se retira; la productividad la garantiza el candado de **≥10 ganchos por pilar**.
- **`lib/schemas/content-plan.ts`** → `AtomizationMap` se reduce (ancla + ratio) o se pliega en `PillarSet`; `derivatives[]` se retira/repurpone.
- **`lib/estudio/brief.ts`** → el brief de develop toma: **ángulo elegido (hook) + contexto del pilar + canal elegido**. Deja de depender de `derivative.note`/`kind` y del `rotateHook`-por-índice.
- **`lib/calendar/plan.ts`** → `buildPublicationPlan` llena desde selecciones (ángulo × canal) y el **set inicial**, no desde los 28 derivados; deja de ser "finito por diseño".
- **Estudio UI** → "28 ideas por pilar" (C1) pasa a **"biblioteca de ángulos por pilar, cada uno desarrollable a cualquier canal habilitado"**. C1 ya agrupaba por pilar → parte se reusa.
- **Migración de datos:** proyectos con `AtomizationMap` firmada → el **ancla se conserva**; los derivados se descartan (su sustancia ya vive en los ganchos). Sin pérdida real: el `note` era redundante.

---

## 9. Fuera de alcance de esta spec

- El detalle del "set inicial" (cuántas piezas, cómo se pesa el sorteo por canal) → spec de Producción/Estudio.
- **Campañas** (spec R1) — una campaña es un **sorteo dirigido del mismo pozo** (ángulos elegidos por evento/ventana), sin cambio a este modelo.
- La UI de la **biblioteca de ángulos como superficie de producción** (era "Etapa D") → ahora es EL grano del sistema; su build se especifica aparte.

---

## 10. Los tipos de "cosa" que 2.4 mezclaba mal (destapado por el operador)

La lista vieja de derivados mezclaba tres naturalezas y las trataba a todas como piezas agendables con gancho rotado. Se separan:

| Naturaleza | Ejemplos | ¿Pieza (ángulo×canal, con gancho, develop, slot)? |
|---|---|---|
| **PIEZA publicable** | pin, carrusel, Reel, video TikTok, **post de Reddit** (self-post que TÚ escribes: el título ES el gancho), **newsletter** (el asunto ES el gancho) | ✅ Sí |
| **ACTIVIDAD de comunidad** | responder hilos ajenos en Reddit/grupos, curar un **tablero de Pinterest** (contenedor, no imagen) | ❌ No — guía de participación recurrente, sin slot ni gancho |
| **LIFECYCLE / automatización** | "secuencia de bienvenida, pieza 2 de 5" (drip disparado por suscripción, no por fecha) | ❌ No — dominio de automatización de email, futuro |

Correcciones de naturaleza confirmadas con `docs/research/doctrina-por-canal.md`:
- **Pinterest:** el **pin** es pieza y su gancho es el **texto overlay** (§1.3/§3.1: bold, breve, keyword en primeros 40 chars). El **tablero** es un contenedor, no se desarrolla.
- **Reddit:** el formato nativo es el **self-post que el operador escribe** (§1.7: título 18+ palabras, 1ª persona, pregunta final, disclosure "I built this"). Es pieza planificable; su gancho es el título. La regla 9:1 es de historial de cuenta, no un veto al post.
- **Email:** el **newsletter** es pieza (asunto = gancho). La "secuencia de bienvenida" es lifecycle → fuera.
