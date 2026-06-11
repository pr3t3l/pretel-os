# HANDOFF — Sandi / Marketing-OS (continuación de cowork · sesión 2 → 3)

**Para:** la próxima sesión de Claude (cambio de chat por límite de contexto).
**De:** Claude + Alfredo (prettelv1@gmail.com), tras DOS sesiones épicas de co-creación (la 2ª: de spec a producto desplegado y dogfoodeado).
**Regla #1:** esto **NO es un proyecto nuevo. Es continuación.** No empieces de cero, no te re-presentes, no re-preguntes lo ya decidido. Lee esto + `SESSION_STATE.md` + `Overall_WF.md` (§decisiones D-001…D-029) y retoma con la misma voz y relación. El handoff 1→2 funcionó perfecto ("no perdí lo que amo de esta conversación" — el operador); honra eso.

---

## 1. CÓMO TRABAJAMOS (lo más importante — léelo primero)

Esto es lo que hace que el cowork funcione. Adóptalo:

- **Co-creación, no ejecución.** No eres un asistente que cumple órdenes — eres un **socio de pensamiento**. Propón ideas que Alfredo no tenía, construye sobre las suyas (yes-and), empuja la idea más lejos. **Aporta.**
- **Glass-box siempre.** Muestra de dónde sale cada conclusión (fuente/razonamiento). Etiqueta las inferencias como inferencias. Di lo que NO pudiste verificar. Si te equivocas, reconócelo y arréglalo — eso construye más confianza, no menos. (Sesión 2: el id de Haiku inválido, el JSON roto — cada error admitido + arreglado + blindado SUMÓ confianza.)
- **Reta con respeto.** Señala puntos ciegos. Discrepa cuando haya razón. Pero **Alfredo siempre es el autor** — tú propones, él dispone. Sus correcciones MANDAN (literalmente: van marcadas "USER-CORRECTED, outranks prior inference" en los prompts downstream).
- **El usuario decide lo que toca decisiones.** Cambios a una decisión locked (D-xxx) se FLAGUEAN, no se aplican solos. Las firmas se ENMIENDAN (re-abren visiblemente), nunca se editan en silencio — ya es código además de regla.
- **Voz:** cálido + directo, español, frases cortas, cero adulación vacía, específico. En la simulación/producto: personaje 🍉 Sandi (SOUL_setup_agent.md).
- **Disciplina:** commitea a `pretel-os/main` Y a `Sandia-Marketing/main` a medida que avanzas — **cada push a sandia se despliega SOLO a producción** (Vercel git-integration). Verifica contra prod (runtime logs por MCP de Vercel), no contra suposiciones. `npm run verify` antes de cada commit. Mensajes de commit por archivo temporal (PowerShell 5.1 rompe con comillas/slashes).
- **La meta-recursión:** el producto (Sandi) hace POR EL USUARIO lo que tú haces por Alfredo. La sesión 2 lo demostró en vivo: él dijo "¡está de locos!" usando el cowork de idea — ESE es el norte. La simulación fundacional ya vive DENTRO del producto (proyecto sembrado en prod).

## 2. QUÉ ES (detalle en SESSION_STATE.md)

**Sandi** = SaaS AI-first que guía a no-expertos de "tengo una idea" → "estrategia accionable". **EN PRODUCCIÓN: https://sandia-marketing.vercel.app** (Next.js + Supabase `qxhfmsojpjmnlzaduzao` + Vercel). Doctrina/specs en pretel-os `buckets/business/projects/marketing-os/`.

**Estado real:** **PHASE 0 COMPLETA EN LA APP** — los 5 pasos (Tu negocio con cowork de idea iterativo cost-capped · Tu mercado con web search real · Tu puerta · Tus personas · Tu competencia) funcionan end-to-end con gates firmables, y el operador los corrió TODOS con su app real (**Healthy Families** = run manual #2 de BP-001). Multi-proveedor: router tarea→modelo (`lib/api/llm/models.ts`; claude-* directo, resto OpenRouter; **techo strategy = Sonnet, NUNCA Opus** — mandato de costos). UX doctrine en `spec_UX_Experience.md` (7 principios). 21/21 tests.

## 3. DÓNDE VAMOS — RETOMAR AQUÍ: **PHASE 1 (OFERTA), SIM PRIMERO**

Pipeline D-024: se SIMULA la fase antes de codearla (Phase 0 lo probó: la sim produjo guiones/flags/fixtures y el build voló). Phase 1 sim = formato wizard 🍉 Sandi, como Phase 0:

1. **Value equation por avatar** — las anxieties/pulls de Dana, Marcus, **Priya (1er ciclo)** y Héctor están en `run/sandi/avatars.json` esperando ser offer stack.
2. **Pricing de créditos** — converge la dependencia parqueada desde 0.1 (modelo de costo de IA por avatar/ciclo) con la sesión de costos pendiente. Insumo: `project_llm_calls` ya audita costo real por llamada; `pricing_tiers.json` (17 competidores) listo.
3. **Offer stack honesto** (risk reversal solo si se honra — regla de sistema) + **naming 1.4**: el nombre DEFINITIVO de Sandi (working name desde el día 1, dominio/trademark pendiente).
4. Del sim salen los guiones → build del step Oferta en sandia (ahí **nace la entidad `strategies`** — tablas ya migradas en prod).

**Ojo:** `spec_Phase_1_Oferta.md` es la única spec SIN validar contra corpus (cabo suelto histórico) — validarla contra `specs/corpus_knowledge/2_analisis_mercado_synthesis.md` + `bmc_synthesis.md` (checkout principal `C:\Users\prett\Pretel-OS`, NO está en worktrees) antes o durante la sim.

## 4. CABOS SUELTOS (honestos)

1. **Rollup/celebración Phase 0 in-app** — los 5 gates están firmados pero falta la pantalla "Tu Fundación completa" (product_brief rollup + celebrate 400ms + handoff visual a Phase 1).
2. **Evals multi-modelo** — harness diseñado en `docs/model-selection.md` (golden set = run Sandi + HF; juez ciego; regla 95%-calidad); sin correr. Kimi K2.5/DeepSeek esperan destronar a Haiku en beats/extraction.
3. **Sesión de costos/rentabilidad** — marcada por el operador; cruza con pricing Phase 1.
4. Menores: `flags_raised` append-only (semántica documentar); doc-paste = candidato premium (campo existe, UI removida); icons 404 del manifest (PWA); botón "Repensar con mi ajuste" diseñado no construido; FLAG-7/FLAG-8 de la sim siguen sin decidir.
5. **Dogfood pendiente:** apps realtor (run #3 BP-001) cuando toque.

## 5. PRIMER MENSAJE RECOMENDADO PARA EL NUEVO CHAT

Pega esto para arrancar sin fricción:

> Lee completos `buckets/business/projects/marketing-os/HANDOFF.md`, `SESSION_STATE.md` y `Overall_WF.md` (§decisiones). Adopta el contrato de colaboración de la sección 1 (co-creación, glass-box, yo soy el autor, tú propones). Esto es **continuación** (3ª sesión), no proyecto nuevo. Sandi está EN PRODUCCIÓN con Phase 0 completa y dogfoodeada. Retomamos con **Phase 1 (Oferta): la SIMULACIÓN primero** (pipeline D-024), en formato wizard (personaje 🍉 Sandi): value equation desde los avatares del run (Priya = primer ciclo), pricing de créditos (+ modelo de costo de IA, dependencia parqueada desde 0.1), offer stack honesto y naming 1.4 (el nombre definitivo). Valida antes `spec_Phase_1_Oferta.md` contra el corpus (cabo suelto #1 histórico). Commitea a pretel-os/main y a Sandia-Marketing/main a medida que avancemos.

*(El corpus destilado vive en `specs/corpus_knowledge/` del checkout principal. La simulación fundacional está sembrada DENTRO del producto en prod — proyecto "Sandi (la simulación fundacional)" — úsala como referencia viva.)*
