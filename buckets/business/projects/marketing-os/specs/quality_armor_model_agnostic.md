# El blindaje de calidad agnóstico al modelo (cómo Papandi mantiene la misma calidad con CUALQUIER LLM)

**Status:** doctrina consolidada (mandato del operador 2026-06-12: "debes blindar para que tengamos la misma calidad agnóstico al LLM... quiero entender cómo lo estás haciendo, cómo lo has hecho en todas las fases y lo seguirás haciendo").
**Tesis (D-017 + D-020):** el modelo es un **actor intercambiable ejecutando un guion blindado**. La calidad NO vive en el modelo — vive en el sistema: guiones + ejemplos + esquemas + candados + checks deterministas + evals + telemetría. "El prompt es artefacto de software" (BP LIDR).

---

## Las 10 capas del blindaje (qué existe, dónde, y qué falta)

| # | Capa | Cómo funciona | Estado |
|---|---|---|---|
| 1 | **SOUL portable** | El carácter de Papandi (sage/mentor, los NUNCA, ruptura-reparación) vive en `SOUL_setup_agent.md` — capa de sistema, no del modelo. Cambiar de proveedor NO cambia la personalidad. | ✅ vivo (D-017) · ⏳ character evals al cambiar proveedor: diseñados, sin correr |
| 2 | **Guiones como datos** (patrón B1) | Los flujos, preguntas, educaciones y aperturas son DATOS versionados en git (`terreno-script.ts`, `value-equation-education.ts`, `phase-intros.ts`), no improvisación del modelo. El LLM rellena huecos ACOTADOS (puntuar, proponer, redactar variantes); la estructura, el orden y el copy educativo están escritos. | ✅ vivo desde M2 — toda fase nueva DEBE entrar así |
| 3 | **CAG — ejemplos canónicos en el prompt** | El nivel esperado se ENSEÑA con ejemplos trabajados dentro del prompt: `cag_step_beat_canonical.md` (variantes A y B), los 3 ejemplos del setup agent, y el run fundacional completo como caso de referencia. Cualquier modelo competente imita un patrón explícito mucho mejor que una instrucción abstracta. | ✅ canon LOCKED · ⏳ empacar el run como CAG #4 formal (pre-código D-024) |
| 4 | **Esquemas duros** | Cada artefacto tiene schema (zod en la app, seeds versionados en el run) con campos obligatorios, enums y rangos. El output del modelo se VALIDA al entrar; lo que no parsea se rechaza/repara — nunca entra silencioso. | ✅ vivo (+ reparador JSON tolerante en todas las rutas LLM, sesión 2) |
| 5 | **Candados (gates) programáticos** | Las reglas de calidad son CÓDIGO, no juicio del modelo: suma 100±2, ratio ≥5×, margen ≥70%, ≥3 filtros, composite 1-10.000, VR-1..VR-5 del brand voice (regex/term match/length). El modelo no puede aprobarse a sí mismo. | ✅ vivo (8 tests del guion 0.1 cazaron un bug real; 9 tests de la ecuación) · ⏳ check engine V2 (hoy VR rules se evalúan manual) |
| 6 | **Checks deterministas SIN LLM** | El filtro de anti-personas es un algoritmo (no LLM) — corre igual en V1 que en V3. Los presupuestos de tokens, los caps de rondas (tope duro 3 en cowork), los límites server-side: todo determinista. | ✅ vivo |
| 7 | **Router tarea→modelo con techo** | `models.ts` asigna modelo POR TAREA (beats baratos, estrategia con techo Sonnet — nunca Opus). Cambiar la asignación no toca el código de los pasos: es config. | ✅ vivo (multi-proveedor desde sesión 2) |
| 8 | **Evals como aduana de modelos** | Un modelo nuevo entra SOLO si pasa el harness: golden set (run fundacional + HF real) + juez ciego + **regla del 95%**: iguala ≥95% de la calidad del incumbente a menor costo, o no entra. Diseño completo en `docs/model-selection.md` (sandia). | ⏳ diseñado, SIN CORRER — el cabo suelto #2 del proyecto; sesión dedicada pendiente |
| 9 | **Telemetría de calidad continua** (Módulo C) | Cada tarjeta aceptada/ajustada/descartada se registra por modelo + prompt_version (`project_llm_calls` + C-D3). Si un modelo degrada en producción, los datos lo delatan y el routing se revierte — la calidad se VIGILA, no se asume. | ⏳ plomería existe (tablas), vista/alertas = Módulo C (task 156e9c29) |
| 10 | **Conocimiento en retrieval, no en el modelo** | La expertise (corpus de 7 cursos + BMC + lookups como `posting_cadence`) se INYECTA en el contexto — nunca se asume que el modelo "la sepa". CAG hoy, RAG cuando dispare un trigger LIDR; la costura (`get_relevant_examples`) está diseñada desde el día 1. | ✅ doctrina viva (D-020/D-021) · build del índice RAG pendiente |

## Cómo se ha aplicado fase a fase (el historial)

- **Phase 0 (build M1-M5):** guiones como datos (0.1 con flags por REGLAS, no por juicio del modelo) + schemas zod + gates con tests + filtro anti-persona determinista + research con fuentes obligatorias (lo no-verificado se ETIQUETA, regla de sistema).
- **Phase 1 (sim + 1.1 in-app):** educación del instrumento como canon LITERAL (datos, no prompt), convención 10=óptimo LOCKED, umbrales en código, candados ratio/margen aritméticos, comparables CITADOS o no entran.
- **Phase 2 (sim en curso):** brand voice con 5 reglas TESTEABLES (VR-1..5 — el lexicon prohibido es un string-match, no una opinión), heurísticas de mix LOCKED (Caso A/B con bandas), lookup tables persistidas (channel_function, posting_cadence), pilares con herencia LITERAL del offer_statement (REFORZAR = reusar palabras exactas — anti-disonancia por diseño).
- **Siempre:** decisiones del usuario MANDAN sobre inferencias (marcadas USER-CORRECTED en prompts downstream), firmas se enmiendan visiblemente, y el operador es el evaluador V1 de todo (BP-001: manual ≥3 runs antes de automatizar nada).

## La prueba ácida (cómo sabremos que el blindaje funciona)

Cuando corra el harness de evals (capa 8): el mismo paso, mismo guion, mismo CAG, mismos candados — ejecutado por Sonnet vs Kimi vs DeepSeek — debe producir salidas que el juez ciego no distinga en calidad ≥95%. Si un modelo barato pasa, baja el costo sin bajar la calidad (eso es el blindaje pagándose). Si ninguno pasa, el incumbente se queda y la telemetría (capa 9) lo confirma en producción con tarjetas reales.

## Pendientes honestos (en orden de impacto)

1. **Correr el harness de evals** (capa 8) — sesión dedicada; el golden set ya existe (run + HF).
2. **Módulo C** (capa 9) — convierte el blindaje en vigilancia permanente.
3. Check engine V2 (capa 5) — automatizar VR-1..5.
4. Character evals (capa 1) + CAG #4 formal (capa 3).
