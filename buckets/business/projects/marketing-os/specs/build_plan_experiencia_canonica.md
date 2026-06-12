# Build Plan v2 — La Experiencia Canónica (reconstrucción de 0: cada paso ES la conversación que vivimos)

**Status:** PLAN v2 esperando aprobación del operador (mandato 2026-06-12, sesión 4: *"quiero que cada paso refleje esta estructura que ya probamos; omite lo que tenemos construido — es más difícil arreglarlo; la Fase 0 está bien, el paso 1 de Fase 1 (ecuación de valor) está bien; todo el resto reconstrúyelo de 0. Antes de seguir: haz un plan, lee toda nuestra interacción, las reglas, nuestro objetivo, piensa con detenimiento."*).
**La fuente de verdad:** `cag_transcript_fase1_fase2.md` (CAG #4) — el transcript literal que el operador pegó como contraste. Este plan se deriva de AHÍ, no del build actual.
**Supersede:** el plan v1 (este mismo archivo, en git) y la tanda T1/T1' que produjo. v1 acertó la anatomía del mensaje (el CAG de 8 movimientos) pero erró la arquitectura: trató el paso como una página que se revela con un chat anexo. El transcript muestra otra cosa.

---

## 1. El error raíz, glass-box (por qué T1 y T1' no fueron la interacción)

Lo vivido en la sim NO es "una pantalla con beats + un chat abajo". Es un **hilo entre iguales** con tres propiedades que el build nunca tuvo:

1. **La unidad es el MENSAJE largo y trabajado, no el beat atomizado.** El "mensaje 1000 de 10" es UN solo mensaje que carga los 8 movimientos juntos: instrumento + dato medido + regla + propuesta en tabla con porqué por fila + candados con margen + en-cristiano + ask. T1' lo partió en burbujas pequeñas reveladas con ritmo — teatro de chat sin la sustancia de chat.
2. **El paso tiene ETAPAS de conversación, no un render único.** El paso 2 del transcript son TRES intercambios: (a) apertura + instrumento + dato + **tres pre-decisiones** ("con esas tres, te traigo el stack completo"); (b) la propuesta completa tarjeta por tarjeta + candados + lo-descubierto + re-score propuesto; (c) la reparación cuando el operador se confundió (re-enseñar valores≠precios + el paquete COMO EL CLIENTE LO VERÍA). La decisión vive DENTRO del diálogo.
3. **El usuario responde con palabras y el sistema responde con sustancia.** "1A, 2A, 3 ninguna, 4 va" cierra cuatro decisiones. "2.1 ok" firma. Una objeción ("no estoy de acuerdo con dejar fuera TikTok") produce: glass-box del error decompuesto + re-propuesta + "la jugada que tu corrección habilitó" + la corrección convertida en regla. Una duda con datos ("¿cada cuánto se postea?") produce la variante B: corpus → estudios con cifras y escala → tabla operativa → fuentes linkeadas.

**La regla raíz sigue siendo D-018:** *Papandi : usuario :: este chat : operador.* El paso no CONTIENE un chat. El paso ES un chat.

## 2. La arquitectura: StepThread — el hilo con guion por etapas

### 2.1 El componente y su contrato

`StepThread` reemplaza a los step-components actuales. Pantalla del paso = hilo de mensajes a ancho completo (dentro del WizardShell con su stepper; HelpPanel a la derecha sigue) + **input SIEMPRE activo abajo**.

- **Mensajes de Sandi:** markdown rico — negritas, listas, **TABLAS**, links de fuentes al pie — más bloques embebidos declarativos: tarjetas ✓/✏️/✕, chips de candado vivos, vista "así lo vería tu cliente", chequeo de dominio, GateSignature, estanterías. Un mensaje largo puede renderizarse progresivamente (se recicla `StepConversation` como detalle interno), pero ES un mensaje.
- **Mensajes del usuario:** texto libre, quick-replies sugeridos (chips: "1A", "2A", "ok"), o taps en bloques (✓/✏️/✕ generan un mensaje implícito visible: "aceptaste la tarjeta 2").
- **Persistencia:** el hilo completo (mensajes + etapa + decisiones parciales) se guarda como artefacto `step_thread` del paso. El usuario vuelve mañana y su conversación está ahí, donde la dejó. Al firmar, el artefacto de negocio (offer_stack, risk_urgency…) queda como hoy; el hilo queda como memoria del paso.

### 2.2 El guion por etapas (capa 2 — la estructura JAMÁS depende del modelo)

Cada paso define en datos (`lib/wizard/phase1/threads/*.ts`, `phase2/threads/*.ts`):

```
etapas: [
  { id, compone(datosFirmados, draft) -> MensajeSandi,   // estructura en CÓDIGO; huecos LLM acotados
    espera: DecisionSchema,                              // qué decide el usuario aquí
    quickReplies: [...],
    transicion: (decisiones) -> siguiente etapa }
]
```

- **El mensaje se compone en código** (plantillas canon del transcript + datos firmados + candados calculados); el LLM rellena huecos ACOTADOS (porqués de tarjetas, redacciones, lecturas) vía las rutas existentes. El CAG (`cag.ts`) viaja en todo prompt (capa 3).
- **El intérprete de respuestas**, en orden: (1) determinista — regex/parser para "ok", "firmo", "2.1 ok", patrones "1A, 2B, 3 ninguna", taps; (2) si es pregunta/corrección libre → ruta `step-cowork` (ya reconstruida con SOUL+CAG+guion) con salida ESTRUCTURADA `{reply_markdown, decision_updates?, regla_capturada?, necesita_research?}`; las `decision_updates` pasan por schema zod + candados en código antes de tocar el draft. **La firma jamás la ejecuta el LLM** — siempre el bloque de firma con el gate en código (capa 5).
- **Variante B cableada:** si el usuario pide datos o duda de un número → primero corpus/lookups del sistema (`posting_cadence` ya existe), después web research (patrón market-research con fuentes obligatorias) → mensaje variante B: reconocimiento decompuesto + corpus primero + estudios con escala + tabla operativa + mandatos capturados como requisitos + fuentes linkeadas.
- **Corrección→regla:** cuando una corrección del usuario cambia la propuesta, el draft guarda `user_corrected` + la esencia literal, los prompts downstream la llevan (regla existente), y Sandi lo DICE ("quedó como regla de tu proyecto").
- **Costos honestos:** paso típico = 1-2 llamadas de propuesta + 2-4 réplicas de conversación (Sonnet, techo) ≈ $0.10-0.25; variante B con web = clase research (~$0.31). Cap de rondas server-side por paso se mantiene. Todo a `project_llm_calls`.

### 2.3 Las 14 leyes de la conversación (extraídas del transcript — el checklist de cada paso)

1. La fase abre con: qué decidió la fase anterior → qué responde esta → gate de entrada VISIBLE (N/N checks) → notas honestas → el mapa de paradas.
2. El paso abre heredando el diagnóstico del anterior ("el paso 1 diagnosticó X — este construye la respuesta").
3. El instrumento primero, con el **error clásico nombrado** ("el error clásico es organizarlos por tema o canal"). Nunca un número antes que su instrumento.
4. TU dato citado, con el número medido ("tu Fase 0 midió: 25 · 50 · 20 · 5").
5. **Pre-decisiones** cuando la propuesta las necesita ("con esas tres, te traigo el stack completo") — el usuario participa ANTES de ver la propuesta.
6. La propuesta completa en tarjetas/tabla: porqué + comparable REAL por fila; desviaciones glass-box ancladas a lo firmado ("como ya firmaste").
7. Candados a la vista CON margen, calculados en código.
8. **"Lo que dejo honestamente descubierto"** — lo no resuelto viaja declarado a su fase dueña, no se barre.
9. La traducción "en cristiano" — una línea física y memorable.
10. El ask con firma corta ("puede ser '2.1 ok'"), autonomía, guardarraíl visible, y el puente (qué desbloquea).
11. Corrección del usuario → glass-box del error DECOMPUESTO ("tiene dos capas") + re-propuesta + "la jugada que tu corrección habilitó" + corrección→regla. Nunca defensiva, nunca auto-flagelación.
12. Duda con datos → variante B completa (corpus → estudios con cifras y escala → tabla operativa → fuentes linkeadas al pie).
13. Pico-final: victoria al firmar ("quedó en piedra"); celebración con MARCADOR al cerrar fase ("mira lo que quedó en piedra hoy: …").
14. Capa usuario intacta: cero D-xxx, cero JSON, jerga traducida una vez entre paréntesis, estanterías para colecciones.

## 3. Qué tiene cada paso (derivado del transcript, generalizado de Priya a cualquier producto)

> El transcript es el NIVEL; el contenido se generaliza por sus movimientos. Los textos literales reutilizables van a guiones-como-datos. Donde el contenido del transcript era de Papandi-producto (Beats/créditos propios), se marca: eso es pricing NUESTRO (Módulo C / task 5953b520), no flujo del usuario.

### Fase 1 (1.1 queda como está; 1.x, 1.2, 1.3, 1.4 se reconstruyen)

**1.x — Tus estrategias** *(el transcript no lo trae; su canon viene de D-032 + lo construido hoy, que se MONTA al hilo)*
- Etapa A: apertura (nace la entidad, versionado) + instrumento demanda con ejemplos del avatar + dato (0.2 midió `offer_strategy` + esencia del avatar) + **lectura PROACTIVA de Sandi** (ruta `strategy-proposal`, ya construida: recomendación con porqué citando lo medido + lecturas por-opción) → decisión (responder "capturar"/"mixta"/tap; la recomendada marcada 💡).
- Etapa B: en-cristiano específico a la elección → firma (gate código) → puente a 1.2.
- Conversación libre en todo momento (intérprete).

**1.2 — Tu paquete** *(el paso de REFERENCIA — el transcript lo muestra entero, con reparación incluida)*
- Etapa A — pre-decisiones: qué-es heredando el diagnóstico CON score ("el paso 1 midió probabilidad 4/10 — no te cree todavía") + instrumento de candados (≥5× y ≥70%, explicados ANTES) + **tres pre-decisiones**: (1) el entregable central — Sandi lo PROPONE configurado a su caso, usuario dispone; (2) precio objetivo — confirma o ajusta la hipótesis del brief; (3) costo de servir a UN cliente — pregunta con ayuda para estimarlo honesto. Cierre: *"con esas tres, te traigo el paquete completo."*
- Etapa B — el stack tarjeta por tarjeta: **educación valores≠precios SIEMPRE antes de la primera tarjeta** (regla canon de la reparación) → centro (aprobado en A) + 3-7 refuerzos en TABLA: valor · comparable real citado (de SU 0.4) · qué fuerza de SU avatar ataca → candados calculados → **"lo que dejo honestamente descubierto"** (objeciones que viajan a 1.3/Fase 2, nombradas) → re-score propuesto si aplica (NO firmado: "espero la garantía del paso 3 y tu visto").
- Etapa C — disposición y firma: ✓/✏️/✕ por tarjeta + candados vivos con margen mientras ajusta + **vista "así lo vería tu cliente"** (el paquete como página de venta en miniatura, con la línea final "todo esto vale $X. Tu inversión: $Y/mes" — la jugada que destrabó al operador) → en-cristiano → ask → firma (gate: ratio + margen + ≥3 aceptados, EN CÓDIGO, sin bypass).
- Reparaciones esperables (guion preparado): confusión valores/precios → re-enseñar con la vista-del-cliente; "el ratio no llega" → "mejores piezas, no valores inflados".

**1.3 — Garantía, urgencia y reemplazo** *(100% del usuario — el sistema propone con chequeo de honestidad, él elige)*
- Etapa A: apertura ("aquí cambia el juego: es 100% tuyo") + educación de las 3 piezas (🛡️⏰🔄, literal del transcript) + **4 decisiones en UN mensaje**, cada una con opciones razonadas:
  - D1 garantía: A incondicional (recomendada SI el avatar viene quemado — porqué del avatar + chequeo de honestidad con costo real de honrarla + **la pregunta: "¿la honrarías sin dudar?"**) / B condicional (con su contra honesta: la letra pequeña que este avatar castiga).
  - D2 urgencia: A ventana real del avatar con **regla de retiro** ("fuera de la ventana se quita sola del copy") / B compromiso de precio (solo si SE COMPROMETE — si no, prohibida) / C ninguna ("también es honesto").
  - D3 escasez: recomendación explícita (para avatares post-quemadura: ninguna — "no apilemos presión; nuestra honestidad ES el diferenciador").
  - D4 reemplazo (obligatorio): texto propuesto desde el hábito que 1.2 dejó declarado + el costo de seguir igual ("esa frase se volverá copy central").
- Respuesta corta aceptada: **"1A, 2A, 3 ninguna, 4 va"**.
- Etapa B: confirmación de las 4 + chequeo de honestidad como conversación (no checkbox frío) + **re-score del eje débil firmado aquí** (D-036: "con el hito + tu garantía, propongo probabilidad 4→6; composite 1.440 — sale del bloqueo blando; ¿firmas?") → firma → puente: "el precio, el nombre… el cierre".

**1.4 — Precio, nombre y tu página** *(el cierre con la victoria delante)*
- Etapa A: apertura con la VICTORIA del re-score ("mira lo que pasó con tu ecuación — por diseño, no por maquillaje") + qué-es (tres piezas) + **3 tarjetas**:
  - T1 precio justificado: contra los 3 pilares (tu ecuación · tu paquete · tu competencia 0.4) + **ancla con referentes VIVIDOS del avatar** (regla USER-CORRECTED: nunca herramientas que el cliente no conoce — el ancla usa SU dolor: "X se queda con $N de cada $100…") + ROI simple de respaldo.
  - T2 el idioma de tu cliente: registro + **frases que SÍ usa (quotes literales de SU research 0.2/0.3 — método estándar D-046)** + nunca-decir (vocabulario de su quemadura + océanos rojos).
  - T3 el nombre: el test de la frase + test Alfred (¿lo pronuncian a la primera?) + **chequeo de dominio EN VIVO** + screen de conflictos (búsqueda real de marcas/competidores homónimos con tabla de hallazgos y lectura honesta "no soy abogada — esto es investigación") + recomendación glass-box + caveat trademark como GATE pre-lanzamiento, no detalle.
- Etapa B (si el usuario quiere explorar nombres): rondas de candidatos CON dominios chequeados en vivo + las 3 preguntas de dirección (¿guiño actual o corte limpio? ¿persona o significado? ¿qué debe cargar?) — el patrón Papandi.
- Etapa C: la página única generada de piezas FIRMADAS (statement) + **preview "así la vería tu cliente"** → edición → firma global de Fase 1 → **CELEBRACIÓN con marcador** (qué quedó en piedra, qué sigue).

### Fase 2 (de visor a wizard conversacional; el visor queda como vista post-firma)

**Apertura de fase** (mensaje propio antes del paso 1): F1 decidió QUÉ → F2 responde CÓMO se cuenta → gate de entrada visible (N/N checks con sus nombres en llano) → notas honestas (lo que falta y dónde se resolverá) → mapa de 6 paradas.

**2.0 — Tu voz**: instrumento (voz = personalidad hecha palabras; arquetipo = molde, los 12; "identidad no se automatiza") → propuesta en 4 tarjetas: arquetipo con porqué anclado a los trabajos emocional/social FIRMADOS de su persona · promesa central (**reescrita con la quote real del usuario si su research la trae** — la dinámica de la corrección del transcript, ofrecida proactivamente) · tono y diccionario (sí-decimos / prohibidos-para-siempre con el porqué de cada uno) · 5 reglas de consistencia TESTEABLES → dispone por tarjeta → "2.0 ok".

**2.1 — El reparto**: el beat canónico LITERAL (variante A del CAG): 4 momentos mentales con emoji+frase vivida → la foto MEDIDA de su 0.2 → la regla (el reparto no copia la foto) → tabla foto-vs-propuesta con porqué por fila + desviación glass-box anclada a su demand_type firmado → candados (suma 100 · bandas · desviación <30 con el margen visible) → cristiano ("de cada 10 piezas…") → "2.1 ok".

**2.2 — La matriz**: instrumento (canal = UNA función; el error clásico "en todos lados lo mismo") → dato propio (dónde vive SU avatar, LITERAL del research) → tabla de canales (qué se publica · ritmo "N por semana" · cómo se mide) bajo las reglas USER-CORRECTED: **grandes superficies ON por defecto** (excluir exige caso escrito) · **IG=imágenes / TikTok=video** (entregables separados) · cadencias del lookup `posting_cadence` CON fuentes linkeadas · la válvula ("si no alcanzas a producir, se degrada el formato, no se excluye el canal") · **el trigger de notificaciones visible como compromiso del producto** ("cada slot te avisará con el copy listo") → descartes CON caso escrito → candados (momentos cubiertos · métrica por fila · carga semanal anti-quemazón) → cristiano ("tu semana es…") → "2.2 ok". Variante B lista para la objeción de cadencias.

**2.3 — Los 4 pilares**: el instrumento LITERAL que el operador mandó conservar (territorio por fuerza psicológica; el error clásico tema/canal; **REFORZAR vs RESOLVER** heredado de su oferta, con los dos accidentes que evita) → tabla de pilares (fuerza · modo · de qué habla · canales) → candados (ninguna palanca huérfana · palabras de la oferta para lo reforzado · delegados con dueño · multiplicador alimentado) → cristiano → "2.3 ok".

**2.4 — La multiplicación**: DOS instrumentos (atomización 1→6 con su porqué de supervivencia; ratio dar:pedir con ajuste razonado a SU caso) → mapa por pilar (ancla en el idioma del avatar + 6 derivados, IG/TikTok separados; ventanas por EVENTO donde aplique) → candados → cristiano → "2.4 ok" → **sub-etapa de producción: la pieza ancla 1 COMPLETA** (artículo con fuentes + carrusel + guion TikTok con tiempos + email A/B + foro + quote card + stories), candados de voz pasados a la vista → disposición.

**2.5 — Los ganchos**: instrumento (el gancho decide todo; plantillas del oficio; la biblioteca aprende) → generación ≥10 por pilar (≥4 plantillas) → **estantería** (el visor M6c existente, ahora dentro del hilo — jamás JSON) con muestra en tabla por pilar → candados (voz 100% · anti-personas · en-uso marcados) → cristiano ("nunca más una pieza desde cero") → "2.5 ok" → consolidación + gate global + **CELEBRACIÓN de fase con marcador**.

## 4. Qué se conserva / qué se retira

**Se conserva (motor y plomería):** Fase 0 entera · 1.1 EquationStep · WizardShell/stepper/breadcrumbs/HelpPanel · SandiBeat/SourceChip/ProposalCard/GateSignature/ThinkingNarration · schemas zod + candados en código (`stackEconomics`, `stackGateReady`, `riskGateReady`…) · rutas LLM: `stack-proposal`, `strategy-proposal`, `offer-statement`, `step-cowork` (se vuelve el intérprete del hilo) · `guiones.ts` + `cag.ts` (se amplían con los textos del transcript) · visores post-firma (incluida la estantería de ganchos) · seeds del sim · tests (40/40) · regla nunca-JSON.

**Se retira (la capa UI que no es la interacción):** `EstrategiaStep`/`PaqueteStep`/`GarantiaStep`/`PrecioStep` (offer-steps.tsx) · el StepChat-como-anexo (el chat ya no acompaña al paso: ES el paso) · `StepConversation` deja de ser la espina (puede quedar como render progresivo interno de un mensaje largo).

**Nuevo:** `StepThread` + render markdown rico (tablas/links/fuentes) + intérprete determinista→LLM + persistencia `step_thread` + guiones-de-hilo por paso (los textos del CAG #4 como datos) + ruta de research variante B (corpus→web) + bloques embebidos (vista-del-cliente, chequeo de dominio, estantería).

## 5. Tandas de ejecución (cada una termina con revisión del operador EN la app — D-051)

| Tanda | Alcance | El test del operador |
|---|---|---|
| **R1** | El motor (`StepThread` + render rico + intérprete + persistencia del hilo) + **el paso 1.2 COMPLETO** con sus 3 etapas, reparaciones preparadas y vista-del-cliente | "¿1.2 se siente como el transcript del paso 2?" — incluida una corrección real respondida con sustancia |
| **R2** | Fase 1 completa al hilo: 1.x (montando la lectura proactiva ya construida) + 1.3 (4 decisiones "1A, 2A…" + re-score) + 1.4 (3 tarjetas + dominio en vivo + exploración de nombre + página + celebración de fase) | "¿puedo correr la Oferta de HF entera como nuestra sesión?" |
| **R3** | Fase 2 conversacional 1ª mitad: apertura de fase + 2.0 voz + 2.1 reparto + 2.2 matriz (variante B de cadencias cableada al lookup) | "¿la Fase 2 educa y propone como lo vivimos?" |
| **R4** | Fase 2 2ª mitad: 2.3 pilares + 2.4 atomización con producción de la pieza ancla + 2.5 estantería de ganchos + gate global + celebración | "¿el cierre se siente como nuestro cierre?" |

**Criterio de hecho por paso:** ¿la conversación del transcript podría haber pasado aquí, con los datos de HF? — educa con el instrumento y su error clásico · cita lo MEDIDO · pre-decide si aplica · propone completo con porqués y comparables · responde una corrección con glass-box y re-propuesta · candados a la vista · en cristiano · firma corta · victoria. Juez: el operador, contra el CAG #4.

## 6. Lo que NO cambia (el blindaje, intacto y reforzado)

Schemas duros (capa 4) · candados programáticos (capa 5) · checks deterministas y caps de rondas (capa 6) · router tarea→modelo con techo Sonnet (capa 7) · guiones como datos (capa 2 — ahora con MÁS textos canon) · CAG en cada prompt (capa 3 — ahora con el transcript íntegro como corpus) · SOUL portable (capa 1) · telemetría a project_llm_calls (capa 9) · conocimiento en retrieval (capa 10: lookups y corpus alimentan la variante B). El modelo sigue siendo un actor intercambiable ejecutando un guion blindado — ahora el guion es la conversación entera.
