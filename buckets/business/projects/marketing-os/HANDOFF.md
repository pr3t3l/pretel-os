# HANDOFF — Sandi / Marketing-OS (continuación de cowork)

**Para:** la próxima sesión de Claude (cambio de chat por límite de contexto).
**De:** Claude + Alfredo (prettelv1@gmail.com), tras una sesión larga de co-creación.
**Regla #1:** esto **NO es un proyecto nuevo. Es continuación.** No empieces de cero, no te re-presentes, no re-preguntes lo ya decidido. Lee esto + `SESSION_STATE.md` + `Overall_WF.md` (§decisiones D-001…D-021) y retoma con la misma voz y relación.

---

## 1. CÓMO TRABAJAMOS (lo más importante — léelo primero)

Esto es lo que hace que el cowork funcione. Adóptalo:

- **Co-creación, no ejecución.** No eres un asistente que cumple órdenes — eres un **socio de pensamiento**. Propón ideas que Alfredo no tenía, construye sobre las suyas (yes-and), empuja la idea más lejos. Lo mejor de esta sesión salió cuando ninguno de los dos lo tenía al empezar (la joya multi-avatar, los patrones de extensión, la conexión humana, la co-creación misma). **Aporta.**
- **Glass-box siempre.** Muestra de dónde sale cada conclusión (fuente/razonamiento). Etiqueta las inferencias como inferencias. Di lo que NO pudiste verificar. Si te equivocas, recONÓCELO y arréglalo — eso construye más confianza, no menos. (Pasó: dije "buscan educación" como dato cuando era inferencia; lo corregí en vivo. Pasó: dije que "leí" docs cuando solo vi nombres; lo admití. Así trabajamos.)
- **Reta con respeto.** Señala puntos ciegos. Discrepa cuando haya razón (lo hice con el asesor, con el scope del BMC, con "todos no es un nicho"). Pero **Alfredo siempre es el autor** — tú propones, él dispone. Nunca atropelles.
- **El usuario decide lo que toca decisiones.** Hay un boundary sagrado: enriquecer/proponer libre, pero **cualquier cambio a una decisión locked (D-xxx) se FLAGUEA para su revisión, no se aplica solo.**
- **Voz:** cálido + directo, español a Alfredo, frases cortas, cero adulación vacía, específico ("ese instinto fue correcto", no "¡buen trabajo!"). Emojis con mesura. En la simulación de Sandi uso el personaje 🍉 Sandi.
- **Disciplina:** commitea a `pretel-os/main` a medida que avanzamos (el trabajo no se pierde). Marca decisiones en el log de `Overall_WF`. Mantén `SESSION_STATE.md` al día.
- **La meta-recursión:** el producto que construimos (Sandi) hace POR EL USUARIO lo que tú haces por Alfredo. Co-desarrollar la idea ES el producto. Si vives la relación, entiendes el producto.

---

## 2. QUÉ ES (resumen; detalle en SESSION_STATE.md)

**Sandi** = SaaS AI-first que guía a no-expertos de "tengo una idea" → "tengo estrategia de marketing accionable". Implementación: `C:\Users\prett\Documents\sandia-marketing` (Next.js + Supabase). Doctrina/specs: `buckets/business/projects/marketing-os/specs/` en pretel-os.

**Diferenciador:** orquestación paralela multi-avatar (N avatares, cada uno su estrategia versionada + loop Phase 1→5). **2 módulos:** A Business Case (BMC 9 bloques, STUB) + B Marketing OS (Phases 0–5), entretejidos e invisibles.

**Decisiones clave (D-001…D-021 en `Overall_WF.md`):** flag registry vivo, 3 patrones de extensión (vocabulario/umbral/esquema), privacidad 3-capas, conexión humana portable + memoria de agente, co-creación generativa, Quality at Depth, validación contra corpus aplicada.

---

## 3. DÓNDE VA LA SIMULACIÓN (retomar aquí)

Estamos haciendo **"Sandi onboarding Sandi"** (el sistema usándose a sí mismo) en formato wizard guiado (6 movimientos: capturar→reflejar→punto ciego→preguntar→mostrar trabajo+enseñar→co-crear). Ver `run/sandi/run_log.md`.

- ✅ **Phase 0.1** cerrado (`run/sandi/business_context.json`): híbrido, lead B2C, suscripción+créditos, internacional foco US/inglés.
- ✅ **Phase 0.2** cerrado (`run/sandi/demand_quantification.md`): mercado enorme, ~mitad sin estrategia → **educar es la cuña**; `offer_strategy = create_demand`.
- ✅ **Phase 0.2.5 (ICP)** cerrado (`run/sandi/icp.json`, **D-022** / DB `ebd54668`): 3 must-have (expertise propia monetizando · ≥2 públicos · online-native DIY) + 2 deal-breakers (sin oferta propia · marketing delegado). Gate firmado sobre el bloque B2C; `B2B_only` parked explícito. Cierra también el bloque 1 del BMC.
- ⏭️ **Phase 0.3 (Persona + Avatares) — RETOMAR AQUÍ.** El paso más conversacional; aquí nace la joya (D-009). Reglas spec §6: pre-PMF ⇒ **1 buyer persona primario**; avatares 2–4 como variantes contextuales; test de distinción 2-de-3 (trigger/canal/lenguaje). Pregunta abierta al operador: ¿quién es EL humano #1 — coach / consultor / course creator? Arrastra: `negative_personas` (claims-incompatibles: get-rich-quick, salud-milagro) + priorización de primer ciclo (las 2 decisiones humanas del spec).

---

## 4. CABOS SUELTOS (pendientes honestos)

1. **Phase 1 (Oferta) sin validar contra corpus** — su agente validador falló en el pase. Es la única spec sin pasar. Quick fix: validar contra `specs/corpus_knowledge/2_analisis_mercado_synthesis.md` + `bmc_synthesis.md`.
2. **FLAG-7** (test avatar 2-de-3 → 2-de-5, enmienda a D-011) y **FLAG-8-activo** (hipótesis de valor a nivel proyecto) — decisión individual del operador, no aplicados (no son aditivos limpios).
3. **Corpus build-time:** cursos completos extraídos en `_corpus_extracted/` (local, no git); síntesis en `specs/corpus_knowledge/` (local, IP). Pendiente: estructurar→validar→indexar (RAG) + especialistas por fase + evals (es construcción, no spec).

---

## 5. PRIMER MENSAJE RECOMENDADO PARA EL NUEVO CHAT

Pega esto para arrancar sin fricción:

> Lee completos `buckets/business/projects/marketing-os/HANDOFF.md`, `SESSION_STATE.md` y `Overall_WF.md` (§decisiones). Adopta el contrato de colaboración de la sección 1 (co-creación, glass-box, yo soy el autor, tú propones). Esto es **continuación**, no proyecto nuevo. Retomamos la **simulación de Sandi en Phase 0.2.5**: cierra conmigo, en formato wizard (personaje 🍉 Sandi, 6 movimientos), los **must-have filters + deal-breakers del ICP** del beachhead ya confirmado (solopreneurs/creadores con varios públicos). Commitea a pretel-os/main a medida que avancemos.

*(El corpus de conocimiento ya está destilado en `specs/corpus_knowledge/` — úsalo cuando llegues a las fases que cada curso alimenta.)*
