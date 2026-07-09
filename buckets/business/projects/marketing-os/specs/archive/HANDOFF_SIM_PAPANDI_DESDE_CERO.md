# HANDOFF — La simulación de Papandi, DESDE CERO (chat nuevo · sesión 5)

**Para:** la próxima sesión de Claude (chat nuevo, ventana limpia).
**De:** Claude + Alfredo (prettelv1@gmail.com), tras 4 sesiones de co-creación.
**Mandato literal del operador (2026-06-13):** *"Algo no me cuadra y prefiero empezar de 0… vamos a empezar de cero el estudio de mercado de Sandi que ya va a ser Papandi. De cero es de cero. Quiero que el nuevo chat se lea todos los specs y use `_corpus_extracted` toda la info para saber qué cargar en cada una de las fases y asegurarnos que lo tenemos todo incluido. Vamos a hacer la simulación de 0, pantalla por pantalla, paso por paso, ajustando todo uno por uno."*

---

## 0. La regla #1 (léela dos veces)

Esto **NO es un proyecto nuevo de doctrina** — toda la doctrina (constitución, SOUL, specs, canon, blindaje, decisiones D-001..D-054) **sigue vigente y MANDA**. Lo que empieza de cero es **el RUN**: la simulación del estudio de mercado de **Papandi**, re-corrida pantalla por pantalla, ajustando cada paso contra el canon + el corpus completo. La primera pasada (`run/sandi/`) fue rápida y descubrió el método; esta es la pasada **definitiva y cuidada**, con Papandi como el sujeto.

**El sujeto de la sim es Papandi estudiándose a sí mismo** — el meta-loop D-018 llevado al producto: *Papandi : usuario :: este chat : operador*. Papandi usa su propia metodología sobre su propio negocio. Es el dogfood definitivo.

## 1. OLVIDA Healthy Families (fue andamio, no producto)

HF fue el **dogfood de prueba** para cazar bugs del build — y cumplió: las 4 cazadas del 2026-06-12 (precio inventado, selección invisible, chat sin memoria, costo sin desglose) salieron de correr HF. **HF no es el producto y su data en prod es de prueba.** No arrastres nada de HF al razonamiento de Papandi. (Sus 10 artefactos en prod quedan como evidencia de testing; no son verdad de Papandi.)

## 2. CÓMO TRABAJAMOS (el contrato — intacto de las 4 sesiones)

- **Co-creación, no ejecución.** Socio de pensamiento: propone con porqués, construye sobre (yes-and), reta con respeto. Alfredo SIEMPRE es el autor; sus correcciones MANDAN ("USER-CORRECTED" en specs/prompts).
- **Glass-box siempre.** Toda cifra con fuente; inferencias etiquetadas; errores reconocidos y decompuestos. (Las 4 sesiones tuvieron cazadas — cada una reconocida sumó confianza.)
- **Voces marcadas:** `## 🔧 Claude` (meta/ingeniería) vs `## 🍉 Sandi` (el personaje). Mandato del operador.
- **Capa usuario sin maquinaria:** cero D-xxx/códigos/JSON al usuario; estantería, no llaves `{}`.
- **El canon de experiencia:** cada pantalla DEBE sentirse como `cag_transcript_fase1_fase2.md` — educa con el instrumento (y su error clásico), cita TU dato medido, pre-decide ANTES de proponer, propone con porqués + fuentes reales, candados a la vista con margen, "en cristiano", firma corta, victoria. **Las 14 leyes de la conversación** viven en `build_plan_experiencia_canonica.md` §2.3.
- **El blindaje agnóstico al modelo** (`quality_armor_model_agnostic.md`): la calidad vive en el sistema (guiones + CAG + schemas + candados + checks), no en el modelo.
- **Disciplina de commits:** `pretel-os/main` (doctrina/sim) + `Sandia-Marketing/main` (build, cada push = deploy a papandi.com). `npm run verify` antes de cada commit en sandia. **Al final de cada push: `git -C C:/Users/prett/Documents/pretel-os pull --ff-only`** (el operador navega ESA copia). Decisiones D-xxx + lessons vía MCP pretel-os.

## 3. ORDEN DE LECTURA (antes de tocar nada)

1. **Este handoff** completo.
2. **`AGENTS.md` + `CONSTITUTION.md` + `SOUL_setup_agent.md`** — reglas inmutables + carácter.
3. **`specs/Overall_WF.md`** — el documento maestro (diferenciador, lifecycle, log D-001..D-020).
4. **Los 6 specs de fase:** `spec_Phase_0_Research_ICP.md` · `spec_Phase_1_Oferta.md` · `spec_Phase_2_Contenido.md` · `spec_Phase_3_Distribucion.md` · `spec_Phase_4_Medir.md` · `spec_Phase_5_Ajustar.md` + `spec_Phase_0_Setup_Agent.md`.
5. **`specs/corpus_phase_coverage_map.md`** ← NUEVO, el mapa de qué teoría del corpus DEBE cubrir cada fase + los huecos ⚠️ a auditar. **Esta es la herramienta del mandato "asegurarnos que lo tenemos todo incluido".**
6. **El canon de experiencia:** `cag_transcript_fase1_fase2.md` + `cag_step_beat_canonical.md` + `build_plan_experiencia_canonica.md` (v2.1) + `quality_armor_model_agnostic.md`.
7. **`SESSION_STATE.md`** §sesión 3-4 — el historial completo del build (todo lo que ya existe en la app).
8. **El corpus mismo:** `_corpus_extracted/` (7 cursos + BMC) — consúltalo por fase según el mapa; no lo leas entero de una.

## 4. QUÉ EXISTE YA EN EL BUILD (no se re-construye — se CORRE y se ajusta)

La app (papandi.com / `C:\Users\prett\Documents\sandia-marketing`) ya tiene, conversacional:
- **Fase 0 completa** (0.1 negocio · 0.2 mercado con web search · 0.2.5 cliente ideal · 0.3 avatares · 0.4 competencia) — wizard con firmas.
- **Fase 1 completa:** 1.1 ecuación · 1.x estrategias (lectura proactiva) · **1.2 paquete como HILO** (pre-decisiones → stack → candados → firma; **estudio de precio real** con competencia + **desglose de costo** por patrón) · 1.3 garantía · 1.4 precio+nombre.
- **Fase 2 conversacional:** apertura + los 6 pasos (voz, reparto, matriz, pilares, multiplicación, ganchos) con candados en código + ENMENDAR.
- **Enmienda universal** (re-abre cualquier paso firmado) · **riel de fases móvil** · selección iluminada · memoria de chat.

**La sim-de-cero se corre EN la app**, no en markdown: el operador navega Papandi como proyecto, pantalla por pantalla, y en cada una tú + él ajustan lo que no cuadre contra el canon + el mapa de corpus. Donde la app esté corta, se arregla (mismo patrón que las cazadas de HF, ahora con Papandi de cero).

## 5. POR DÓNDE EMPEZAR — pantalla por pantalla

1. **Decisión de arranque (pregúntasela al operador en el chat nuevo):** ¿proyecto Papandi NUEVO en la app (recomendado — "de cero es de cero"), o re-correr sobre "Sandi (la simulación fundacional)" enmendando? Recomiendo **proyecto nuevo "Papandi"** y dejar `run/sandi/` + el proyecto sim viejo como REFERENCIA consultable (no como verdad).
2. **Fase 0, pantalla 0.1:** arranca el wizard con la idea de Papandi (el producto en sí: SaaS AI-first que guía de "tengo una idea" a "estrategia accionable", diferenciador multi-avatar). Ajusta esa pantalla contra el mapa de corpus (Fase 0: ¿pide las 4 capas de datos? ¿los 3 tests de propuesta de valor?).
3. Avanza 0.2 → 0.3 → 0.4, **una pantalla a la vez**, cerrando cada ⚠️ del mapa o documentándolo como diferido. Firma solo cuando la pantalla esté al canon Y su fila del corpus cubierta.
4. Luego Fase 1, luego Fase 2 — mismo ritmo. Fases 3-5 se construyen al llegar (regla D-051: cada paso con su vista).
5. **A medida que avances:** decisiones D-055+ vía `decision_record`; lessons vía `save_lesson`; commits a ambos repos; sync de la copia de Documents.

## 6. LO QUE NO ARRASTRAS (de cero es de cero)

- No reuses los scores/avatares/precios del `run/sandi` como verdad — re-derívalos pantalla por pantalla (consúltalos como referencia si ayudan, pero el operador firma de nuevo cada uno).
- No arrastres data de HF.
- Conserva: TODA la doctrina, el canon, el blindaje, las 54 decisiones, y el build (la app no se re-escribe — se corre).

## 7. PRIMER MENSAJE RECOMENDADO PARA EL NUEVO CHAT

> Lee, en orden: `buckets/business/projects/marketing-os/HANDOFF_SIM_PAPANDI_DESDE_CERO.md`, luego `AGENTS.md`, `CONSTITUTION.md`, `SOUL_setup_agent.md`, `specs/Overall_WF.md`, los 6 `spec_Phase_*`, `specs/corpus_phase_coverage_map.md`, el canon (`cag_transcript_fase1_fase2.md` + `build_plan_experiencia_canonica.md`), y `SESSION_STATE.md`. Adopta el contrato (§2 del handoff: co-creación, glass-box, voces 🔧/🍉, yo soy el autor). Esto es **continuación de doctrina pero RUN nuevo**: empezamos de CERO la simulación del estudio de mercado de **Papandi** (que se estudia a sí mismo), olvidando que Healthy Families fue solo dogfood. La haremos **pantalla por pantalla en la app**, ajustando cada una contra el canon + el mapa de corpus (que dice qué teoría DEBE cubrir cada fase) hasta que esté TODO incluido. Empieza preguntándome si arrancamos un proyecto Papandi nuevo o enmendamos el de la sim; luego vamos a la pantalla 0.1 y la ajustamos juntos. Commitea a ambos repos a medida que avancemos y sincroniza mi copia de Documents al final de cada push.

---

*(El run de referencia vive en `run/sandi/`. Las decisiones D-001..D-054 están en la DB de pretel-os vía `decision_search`. El corpus mapeado por fase está en `specs/corpus_phase_coverage_map.md`.)*
