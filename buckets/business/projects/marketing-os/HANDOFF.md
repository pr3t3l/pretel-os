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
- ✅ **Phase 0.2.5 (ICP)** cerrado en **v2** (`run/sandi/icp.json`, **D-023** / DB `05ec4413`, supersede D-022): beachhead = **expertos en lo suyo** (velera, gym, n8n, coach) con **oferta propia ya monetizando** (local/marketplace/online cuentan) que **no saben empezar o escalar su marketing online**, >1 público. Filtros: `own_craft_offer_monetized` · `multi_audience` · `diy_going_online`; deal-breakers: `no_own_offer` · `marketing_delegated`. `B2B_only` parked. Cierra BMC bloque 1. (D-022 cayó el mismo día por malentendido semántico de "expertise" — destapado al abrir 0.3.)
- ✅ **Phase 0.3 (Persona + Avatares)** cerrado (**D-027**; persona D-025, priorización D-026). Persona: "el experto en lo suyo que ya vende y está perdido en el marketing online" (6 dolores con fuente). 4 avatares signed: Dana (Lanzadora digital) / Marcus (Estancado) / Priya (Enjaulada del marketplace) / Héctor (Ruta local — agregado por el operador). **Priya enciende el primer ciclo.** 2 anti-personas (claims-imposibles, delegador total). Evidencia de primera mano del operador en `run/sandi/evidence_firsthand.md` (cluster pre-launch flagueado ≠ anti-target).
- ⏭️ **Phase 0.4 (Competencia) — RETOMAR AQUÍ. Último paso de Phase 0.** Trabajo de Sandi (research): `competitor_scan.md` con 4 tipos (SEO / RRSS / Ads / Substitutos, ≥3 c/u, `price_point_usd` poblado, fuente citada por dato — Meta Ads Library, Google Ads Transparency, SimilarWeb free), síntesis cross-canal con **veredicto ERRC Red/Blue Ocean**, `pricing_tiers[]` para Phase 1, y `decision_record` del hueco a atacar. El scan se enfoca primero en el terreno de **Priya** (herramientas de marketing AI + tools de sellers + sustitutos: agencias, freelancers, cursos, "hacerlo a mano"). Al cerrar 0.4: gate global G-Phase-0 → **se dispara el build trigger D-024** (codear Phase 0 wizard en sandia-marketing mientras la sim sigue con Phase 1).

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
