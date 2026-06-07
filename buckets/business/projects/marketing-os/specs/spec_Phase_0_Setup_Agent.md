# Phase 0 — Setup Agent (capa conversacional guiada)

**Project**: business/marketing-os
**Phase ID**: phase-0-setup-agent
**Status**: spec drafted v1.0 (guion 0.1 perfilado; 0.2–0.4 stub)
**Last updated**: 2026-06-07
**Implementation correction:** Targets `C:\Users\prett\Documents\sandia-marketing`. La plomería ya existe en M0 (`setup_agent` prompt versionado, `ProjectFoundationBrief` schema, `renderDraft` single shaper, 3 ejemplos anonimizados). Esto es el **contrato de comportamiento**, no código.

**Reference**: `Overall_WF.md` §"Two extension patterns" + §"Flag Registry". Validado contra el corpus LIDR (tag `LIDR`) en pretel-os: best practices "Espectro de interfaces", "El prompt es artefacto de software", "Educational pre-flight + Step N of M"; lessons "transaccional vs conversacional" (clase 08), memoria conversacional tipada, CAG 3-7 ejemplos, costos multi-turno, prompt-inglés/salida-español.

---

## 0. Contexto y propósito

El Setup Agent es **la entrega conversacional y guiada de Phase 0 para usuarios NO expertos en IA.** No es un entrevistador que extrae y corrige — es un **socio de pensamiento que co-desarrolla la idea CON el usuario** (igual que este spec se construyó: operador + Claude intercambiando ideas hasta que el resultado superó lo que cualquiera tenía al empezar). Ver `Overall_WF.md` §"Generative Co-Creation". El **espejo meta**: *Sandi : la idea del usuario :: Claude : la idea del operador.*

**Decisión de modo e interfaz (validada contra LIDR):**
- **Modo: conversacional** — el usuario itera (reformular → confirmar → corregir → avanzar). Pasa el test de la lección "transaccional vs conversacional": hay ≥3 casos reales de iteración.
- **Interfaz: wizard guiado** (no chat libre). Por la BP "Espectro de interfaces": el default sano para features verticales es formulario/acción + chat-con-parámetros; chat libre solo como escape.
- **Profundidad: adaptativa** — idea clara → camino corto; idea borrosa → guiado completo (lección "intake interactivo para casos complejos, auto para simples"). Una respuesta vaga dispara una sub-pregunta de aclaración.
- **Inteligencia en el backend** — por la BP "El prompt es artefacto de software": el usuario da respuestas/parámetros, NUNCA escribe prompts. La calidad no depende de su habilidad de prompting.

**Anti-meta:** si conservas la estructura del wizard pero pierdes los 6 movimientos —sobre todo el 6º (co-crear)— construiste Typeform, no Sandi. La estructura es el envase; los movimientos son el producto.

---

## 1. Principios de ingeniería heredados de LIDR (no re-derivar)

- **System prompt = rol + tarea + uso del contexto + formato** (clase 11). El "rol" del Setup Agent: **socio de pensamiento (estratega de marketing) que co-desarrolla la idea** — reformula, **aporta ideas nuevas, construye sobre las del usuario, empuja la idea más lejos**, señala puntos ciegos, y siempre deja al usuario como autor.
- **Memoria tipada** — `ProjectFoundationBrief` (Pydantic), nunca string libre; `history` y `project_metadata` separados desde día 1. Asumir SIEMPRE que el modelo no recuerda entre llamadas.
- **CAG-first, RAG-later (con la costura lista hoy)** — 3 ejemplos semilla (M0 ya tiene DTC físico, SaaS B2B, servicio), sube a 5-7 si hace falta. **Migración a RAG** cuando se dispare cualquier trigger LIDR: KB > 70% del contexto útil, datos cambian >1×/semana, o volumen de queries lo encarece. Para Sandi los disparadores llegarán por (a) el research de mercado/competencia por proyecto y (b) el corpus de aprendizaje cross-usuario del loop. **Hoy:** dejar la **capa `context/`** con `get_relevant_examples(input)` desde el primer commit (lesson LIDR) — así CAG→RAG es un cambio local, sin reescribir servicios. NO construir RAG aún; solo el seam.
- **Contexto ordenado** — instrucciones al inicio, input del usuario al final ("lost in the middle"); capa `context/` desde el día 1.
- **Costo** — multi-turno crece cuadráticamente → sliding window + turnos ancla + `ProjectFoundationBrief` como resumen vivo. Prompt en inglés / salida en español (-20-40% tokens). Output cuesta 3-6× input → brevedad.

---

## 2. Los 4 movimientos (contrato de comportamiento)

Cada turno del Setup Agent ejecuta, en orden:

1. **Capturar / Reformular** — toma la respuesta cruda y la reformula en términos verificables ("esto es lo que entendí…").
2. **Reflejar y confirmar** — la devuelve para validación ("¿voy bien?") antes de avanzar.
3. **Señalar punto ciego (CALIBRADO)** — marca el tradeoff o riesgo no obvio. **No en cada paso** — solo cuando hay una decisión real en juego. Over-flag = lecturear = mala UX.
4. **Preguntar lo siguiente** — una sola pregunta, la que desbloquea el avance, con opciones sugeridas (reconocer > recordar) y "Paso N de M".
5. **Mostrar el trabajo y enseñar (glass-box + educación)** — en toda conclusión: **de dónde viene** (fuente/método), **cómo razoné**, y **qué significa la jerga en simple**, al nivel del `user_knowledge_profile`. Si fue inferencia, decirlo; decir lo que NO se pudo verificar. Esto es lo que da la sensación de "trabajar con alguien", no un bot que escupe verdades sin respaldo (ver `Overall_WF.md` §"Portable Human Connection").
6. **Co-crear / aportar (la esencia)** — no solo extraer y corregir: **proponer ideas que el usuario no tenía, construir sobre las suyas (yes-and), empujar la idea más lejos.** Toda propuesta va **etiquetada como propuesta** (no como hecho), con su porqué (glass-box) + un accept/reject fácil. El usuario **siempre es el autor**; Sandi propone, el usuario dispone (autonomía/SDT). Seguro para no-expertos solo porque va sobre glass-box + educación + autonomía (ver `Overall_WF.md` §"Generative Co-Creation"). *Sin este movimiento, Sandi es un formulario inteligente, no un socio.*

**Calibración de la intervención (movimiento 3):** pesa el flag cuando la respuesta esconde un tradeoff caro (segmento híbrido, modelo de créditos, "todos" como nicho). Sé ligero cuando la respuesta es limpia. Si el usuario se auto-corrige (como "internacional… pero foco US"), **reconoce el instinto en vez de lecturear.**

---

## 3. El esquema es VIVO — [Evolving Schema] (requisito del operador)

**El JSON que produce este sistema (`business_context.json`, etc.) es la SEMILLA v1 de ESTE build de referencia, no un contrato congelado.** Otros modelos/clientes traerán enfoque distinto y mejoras. El esquema debe mejorar con el uso, en **todas las fases** (ver `Overall_WF.md` §"Pattern C — Evolving Schema").

- Cada artefacto lleva `schema_version` + `metadata` jsonb (ya en M0). Los campos nuevos no anticipados se capturan en `metadata` primero.
- Promoción: un campo/pregunta que recurre ≥N veces + pasa review → se vuelve campo de primera clase y sube `schema_version`. Mismo lifecycle que el Flag Registry.
- Loop de aprendizaje: cada interacción escribe lessons; los resultados downstream (Phase 4 `results_summary`) revelan qué preguntas/campos predicen buenas estrategias → se refuerzan; los inútiles se deprecian.
- Tenancy: extensiones locales del cliente (`metadata`) vs core promovido global. Versionado y reconciliado, nunca una forma única impuesta.

**Implicación para el guion:** las preguntas del wizard tampoco son fijas. El banco de preguntas es semilla + se mejora con el mismo loop (qué preguntas, en qué orden, qué opciones).

---

## 4. Guion de Phase 0.1 — Business Context Gate

Captura `business_context.json` (seed v1). Las **preguntas son en lenguaje llano; la jerga (B2B/B2C, sales_cycle, etc.) queda oculta.** Mapeo pregunta→artefacto abajo.

**Pre-flight (orientación ANTES de preguntar):**
> "Antes de empezar: te haré unas preguntas cortas para entender el *terreno* de tu negocio. No necesitas saber de marketing — yo traduzco. Esto define cómo te hablo después. Son 4 preguntas; al final tendrás claro el marco de tu negocio."

| Paso | Pregunta llana | Opciones sugeridas | Artefacto (oculto) | Condición de flag |
|---|---|---|---|---|
| 1 | "¿Quién saca la tarjeta cuando alguien paga?" | persona / empresa / las dos | `business_type` (B2C/B2B/hybrid) | si "las dos" → **flag**: B2C vs B2B no son dos avatares, son dos terrenos (Foundation distinta) → sub-pregunta adaptativa "¿cuál lidera?" |
| 1b | (adaptativa) "¿Cuál lidera el lanzamiento?" | individuos / empresas / las dos con razón | `lead_segment` + `parked_segment` | si "las dos día 1" sin razón → exigir justificación |
| 2 | "¿Cómo piensas cobrar?" | suscripción / pago único / freemium / por uso / no sé | `monetization_model` | si "freemium" o "por uso" en producto con IA → **flag**: los usuarios cuestan dinero por llamada; el medidor de créditos = tu costo de IA (dependencia → Phase 1 Pricing + modelo de costo) |
| 3 | "¿Cómo deciden comprar — de una o se lo piensan?" | impulso / se lo piensan / depende | `sales_cycle` | si "impulso" en compra cara/recurrente → frenar (incoherente) |
| 4 | "¿Dónde están y en qué idioma?" | ciudad-país / hispanos / global + idioma | `market_scope` + `geographies` + `language_primary` | si "internacional día 1" → **flag** (multiplica trabajo + costo tokens es/multimodal); proponer foco de lanzamiento |

**Sub-pasos adaptativos** se disparan por respuestas vagas/híbridas (profundidad adaptativa). `channel` se infiere (SaaS → `online_only`) y se confirma, no se pregunta en frío.

### 4b. Naming + dominio (concern que cruza Phase 0 → Phase 1.4)

Hueco detectado: Phase 1.4 nombra la *oferta* y Phase 2.0 hace brand voice, pero **nadie nombra la empresa/producto ni chequea dominio/competencia.** No es una phase nueva — es un concern de dos tiempos:

- **En Phase 0 (aquí):** capturar un **`working_name`** + un **chequeo temprano de disponibilidad** (dominio + competencia + trademark básico). Objetivo: no construir marca sobre un nombre muerto. Campos: `name_status: working|final`, `working_name`, `domain_available`, `name_conflicts[]`.
- **En Phase 1.4 (finalizar):** el **buen** nombre depende del posicionamiento (avatar + diferenciación), que recién se conoce tras Phase 0–1. Ahí se decide el nombre final junto al `offer_name`, y `name_status` pasa a `final`.

Regla: el `working_name` **nunca bloquea** el avance de Phase 0 (puedes seguir con un nombre provisional); el chequeo de dominio sí se registra como **dependencia** para no llegar a lanzar con un nombre indisponible. (Implementación: un chequeo de dominio real — p.ej. el tool de disponibilidad de dominios — corre en este paso; en el spec solo se registra el resultado.)

Ejemplo Sandi: `working_name="Sandi"` (aleatorio), el operador duda por competencia/dominio → `name_status=working`, finalizar en 1.4.

**Output:** `business_context.json` (seed v1) con `implications_acknowledged` (≥2) y dependencias parqueadas explícitas (ej. modelo de costo de créditos → Phase 1). **Gate G-Phase-0.1** = todos los campos poblados + evidencia real + ≥2 implicaciones (heredado de `spec_Phase_0` §3).

**Ejemplo real (Sandi-onboarding-Sandi):** ver el `business_context.json` consolidado en la simulación — `hybrid` con `lead_segment=B2C`, `sales_cycle=reflexivo`, `monetization=subscription+usage(credits)`, `market_scope=internacional` foco US/inglés, `multimodal` parqueado como capacidad de producto.

---

## 5. Memoria y estado

- `ProjectFoundationBrief` (tipado) = estado vivo del brief; crece pregunta a pregunta.
- `renderDraft` (M0) = un solo shaper → **lo que el usuario ve en el panel == lo que el modelo ve.**
- `history` (turnos) separado de `project_metadata` (hechos que deben sobrevivir). Sliding window + turnos ancla para decisiones clave.
- **Memoria de agente por proyecto (espejo de pretel-os — ver `Overall_WF.md` §"Per-Project Agent Memory"):** cada proyecto/run tiene su cerebro = doc del proyecto + **plan de acción interno (mutable, no visible por defecto, disponible si se pide)** + lessons + best_practices + decisions + estado tipado + `user_knowledge_profile`. El plan de acción es lo que el modelo "sigue": dónde vamos, qué sigue, qué cambió. Mutable (loop Phase 5 / foundation_drift / Pattern C). Todo tipado/persistido, nunca blob.
- **`user_knowledge_profile`** (nivel por concepto: novato/intermedio/experto) — escala las explicaciones (movimiento 5) y sube de nivel con cada interacción/proyecto.
- **Carácter portable:** la voz/persona vive en `specs/SOUL_setup_agent.md` (capa A) — independiente del modelo. Correr character evals al cambiar de proveedor.

---

## 6. Stub — guiones de 0.2–0.4 (pendientes)

- **0.2 El Mercado** — cambia de tono: el sistema **trae datos** (tamaño de mercado US, qué busca en Google, awareness) más que preguntar. Mostrar-y-confirmar > preguntar.
- **0.2.5 El Segmento (ICP)** — pocas preguntas de filtro.
- **0.3 Persona + Avatares** — el más conversacional/exploratorio (aquí nacen los avatares, la joya).
- **0.4 Competencia** — el sistema investiga y presenta huecos.

Cada uno se perfila con el mismo formato de la sección 4 (pregunta llana → artefacto → condición de flag) cuando lleguemos.

---

## 7. Decisiones cerradas

| # | Decisión | Resolución |
|---|---|---|
| D1 | Modo/interfaz | Conversacional + wizard guiado + profundidad adaptativa + prompt en backend. Validado contra corpus LIDR. |
| D2 | 6 movimientos | Capturar/reformular → reflejar/confirmar → señalar punto ciego (calibrado) → preguntar siguiente → mostrar trabajo y enseñar → **co-crear/aportar**. |
| D6 | Co-creación generativa (la esencia) | Sandi co-desarrolla la idea (propone, construye sobre, empuja más lejos), no solo extrae/corrige. Rol = socio de pensamiento. Seguro para no-expertos vía glass-box + educación + autonomía; el usuario siempre es el autor. Ver `Overall_WF.md` §"Generative Co-Creation". |
| D3 | Esquema vivo | Los artefactos JSON son semilla + `schema_version` + loop de aprendizaje (Pattern C). Aplica a todas las fases. |
| D4 | Jerga oculta | El usuario nunca ve "buyer persona", "awareness level", "TAM". Pregunta llana → artefacto experto internamente. |
| D5 | Calibración de flags | No flag por paso; pesado solo en tradeoffs reales; reconocer auto-correcciones del usuario. |
