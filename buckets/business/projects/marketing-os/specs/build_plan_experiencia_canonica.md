# Build Plan — La Experiencia Canónica (cada paso del producto = la interacción de este chat)

**Status:** PLAN esperando aprobación del operador (mandato 2026-06-12: "para antes de seguir, haz un plan, lee toda nuestra interacción, las reglas, nuestro objetivo... eso ya lo hicimos en este chat").
**El error que corrige (glass-box):** M7a entregó pasos *funcionales* (opciones + firma) pero NO la experiencia: el operador vivió en la sim una **conversación que educa, propone con razones, calcula candados a la vista, traduce a cristiano y responde correcciones** — y el paso de la app era un formulario con 3 tarjetas. La doctrina existía (`cag_step_beat_canonical.md`, D-041) pero el build no la encarnó. Este plan la vuelve OBLIGATORIA y ejecutable.
**La regla raíz (D-018, la meta-recursión):** *Papandi : usuario :: este chat : operador.* La interacción de la sesión 3 ES el spec de la experiencia. Si un paso del producto no se siente como esta conversación, está incompleto.

---

## 1. Anatomía OBLIGATORIA de cada paso (los 8 movimientos → componentes)

Derivada del CAG canónico (variantes A y B) — cada paso renderiza esta secuencia, no un formulario:

| # | Movimiento | En la UI | Fuente del contenido |
|---|---|---|---|
| 1 | **Apertura del paso** — qué es, por qué importa, qué decides TÚ | SandiBeat inicial (secuencial, no amontonado) | guion-como-datos por paso (canon LITERAL) |
| 2 | **El instrumento primero** — qué mide, escala, cómo se combina, umbrales | SandiBeat corto + panel "¿Cómo se calcula?" SIEMPRE | canon literal (ya existe para ecuación/stack/1.3/pilares...) |
| 3 | **TU dato citado** — "tu Fase 0 midió X", "a [avatar] le falla Y" | beat con SourceChips a los artefactos firmados | derivación en código desde artifacts (no LLM) |
| 4 | **Propuesta glass-box** — cada tarjeta con su PORQUÉ + comparable/fuente | ProposalCards (✓/✏️/✕) con `why` SIEMPRE poblado y específico | ruta LLM con guion + CAG en el prompt |
| 5 | **Candados a la vista CON margen** — "vas en 10; la alarma salta en 30" | chips vivos calculados en código (nunca el LLM se aprueba) | helpers puros (stackEconomics etc. — ya existen) |
| 6 | **"En cristiano"** — la línea física que traduce los números | cierre del beat de propuesta | guion + LLM (plantilla con slots) |
| 7 | **Ask con autonomía + guardarraíl** — firma fácil + qué pasa si te sales del riel | GateSignature + flag honesto | guion |
| 8 | **CONVERSACIÓN del paso** ← LO QUE FALTÓ | input libre en CADA paso: "ajusta esto / no entiendo / ¿y si...?" → Sandi responde EN CONTEXTO y re-propone (ruptura-reparación, como esta sesión) | NUEVA ruta genérica `step-cowork` (patrón idea-cowork generalizado): system = SOUL + canon + guion del paso + artefactos firmados + estado del draft |

**El componente nuevo que lo une: `StepConversation`** — renderiza la secuencia 1-7 como beats encadenados (con el ritmo de chat: aparecen en orden, no como página estática) + el input del movimiento 8 anclado abajo. Los pasos existentes (TerrenoWizard, idea-cowork) ya viven cerca de esto; los de M7a no.

## 2. Qué tiene cada paso (derivado de NUESTRA interacción — sesión 3)

### Fase 1 (PRIORIDAD 1 — HF la va a correr ya)

| Paso | Apertura + instrumento (canon) | TU dato citado | Decisiones del usuario | Propuesta de Sandi (con porqué) |
|---|---|---|---|---|
| 1.1 Ecuación | ✅ ya al canon | esencia del avatar + brief | scores 4 ejes + sueño + plan-si-débil | (V2: Sandi propone scores citando artefactos — hoy manual OK) |
| 1.x Estrategias | apertura "aquí nace la entidad estrategia, versionada" + educación demand_type CON EJEMPLOS DEL AVATAR ("¿buscan a [avatar] con palabras exactas? p.ej. [derivar de su where_we_meet]") — no opciones genéricas | where_we_meet + triggers del avatar firmado | tipo de demanda + firma de nacimiento | Sandi RECOMIENDA un tipo con razón (como recomendó mixed para Priya) — el usuario dispone |
| 1.2 Paquete | apertura con DIAGNÓSTICO heredado ("el paso 1 dijo: a [avatar] le falla [eje débil] — este paso construye la respuesta") + instrumento valores≠precios LITERAL + candados explicados ANTES | eje débil + anxieties/habits del avatar + precios de competencia 0.4 | disposición por tarjeta + precio + costo de servir + firma | core + 4-5 bonuses, cada uno: qué fuerza ataca + comparable REAL citado (ya en M7a, mejorar el why) |
| 1.3 Garantía | educación de las 3 piezas (canon LITERAL ya existe) + Sandi RECOMIENDA A/B con el porqué del avatar ("a tu cliente lo quemaron: lo incondicional le habla") + honesty check como pregunta, no checkbox frío | anxieties del avatar (por qué esta garantía LE habla) | A/B/none + "¿la honrarías sin dudar?" + urgencia con razón + reemplazo | opciones redactadas POR el LLM desde el avatar (las semillas del stack ya existen) — con recomendación razonada |
| 1.4 Precio+Nombre | apertura "el cierre: precio justificado, nombre, página" + precio con LOS 3 PILARES ("tu ecuación dice X, tu paquete sostiene Y, tu competencia cobra Z") + naming con el TEST ALFRED + test de la frase | ecuación + stack + pricing_tiers del 0.4 | nombre (con chequeo de dominio EN VIVO — la experiencia Papandi que vivimos) + statement editado + firma | statement generado de piezas FIRMADAS + preview "así la vería tu cliente" (la jugada que destrabó al operador) |

### Fase 0 (PRIORIDAD 2 — retrofit ligero: ya es la mejor; auditar contra anatomía)
0.1 cowork ya conversa ✓ · añadir instrumentos/aperturas donde falten (0.2 semáforo, 0.2.5 filtros, 0.3 test 2-de-3, 0.4 ERRC) + movimiento 8 en todos.

### Fase 2 (PRIORIDAD 3 — del visor al wizard conversacional)
Cada sub-paso con su educación YA VIVIDA: 2.0 voz (arquetipo en llano + 12 moldes + promesa con la quote del research DEL USUARIO) · 2.1 reparto (momentos mentales 😴😣🔍🎯 + foto-vs-estrategia) · 2.2 matriz (canal=función + hábitos del avatar mandan + cadencias del lookup CON fuentes) · 2.3 pilares (territorio por fuerza + REFORZAR/RESOLVER) · 2.4 atomización (1→6 + ratio dar:pedir per-channel) · 2.5 estantería (ya diseñada). El visor actual queda como la vista post-firma.

### Fase 3 (se construye AL RITMO de la sim — regla D-051)
3.1 tracking (instrumento UTM/conversión en llano — ya vivido) · 3.2 exclusiones · 3.3 calendario+notificaciones · 3.4 go-live.

## 3. Mecánica de implementación (blindaje intacto)

1. **Guiones-como-datos por paso**: `lib/wizard/phase1/{estrategia,paquete,garantia,precio}.ts` — aperturas, instrumentos, en-cristiano plantillas, guardarraíles (capa 2 del blindaje). Los textos = los de ESTA sesión, limpios de capa (sin D-xxx).
2. **CAG en cada prompt**: las rutas LLM (stack-proposal, statement, step-cowork) llevan el ejemplo canónico (capa 3) — el why de cada tarjeta debe sonar a esta sesión.
3. **Ruta genérica `POST /api/phase1/step-cowork`** `{projectId, step, message, draft}` → respuesta de Sandi + (opcional) draft ajustado. Tope duro de rondas server-side (control de costos, como idea-cowork).
4. **Candados/validaciones SIEMPRE en código** (capa 5) — el chat puede explicar, nunca aprobar.
5. **Educaciones completas al panel** (capas de audiencia): beat corto + panel profundo.

## 4. Tandas de ejecución (cada una termina con revisión del operador EN la app — D-051)

| Tanda | Alcance | Resultado visible |
|---|---|---|
| **T1** | `StepConversation` + guiones Fase 1 + re-hacer 1.x y 1.2 al canon (aperturas, instrumento, dato citado, recomendación razonada, en-cristiano, chat del paso) | HF corre pasos 2-3 SINTIENDO la conversación |
| **T2** | 1.3 y 1.4 al canon (+ dominio en vivo en naming) + movimiento 8 en 1.1 | Fase 1 completa con el alma |
| **T3** | Retrofit Fase 0 (aperturas/instrumentos faltantes + chat del paso) | Toda la Fundación al canon |
| **T4** | Fase 2 wizard conversacional sobre el visor | Fase 2 ejecutable, no solo visible |

**Criterio de hecho por paso (el test del operador):** ¿se siente como la sesión 3? — educa antes de pedir · cita TUS datos · propone con porqués y fuentes · candados a la vista con margen · "en cristiano" · puedes corregirla y te responde · tú firmas.

## 5. Lo que NO cambia
Schemas, rutas LLM existentes, candados como código, visores post-firma, seeds del sim, la regla nunca-JSON — todo queda. Esto añade el ALMA encima de la plomería ya construida.
