# spec_Momentos — «Trae lo que está pasando» (el asistente global de Papandi)

> **Estado: 💡 PROPUESTA PARA DISCUSIÓN (2026-07-12).** Nace de la idea del operador al revisar
> Tendencias: el usuario del pasto y la ola de calor · el abogado y el cambio de ley laboral · el cambio
> de algoritmo para el propio Papandi. Contexto: `docs/research/00_CONTEXTO_MAESTRO.md` +
> `spec_Estudio_Video_v2.md` (§3.6 Tendencias) + `spec_Campanas.md` + `spec_Inteligencia_Temporal.md`.

---

## 0 · La idea en una frase

**Un MOMENTO = algo que está pasando AHORA en el mundo real del usuario** (una ola de calor, un cambio de
ley, un cambio de algoritmo, una noticia de su nicho) **que Papandi investiga con fuentes, conecta con la
marca firmada (fases 0-2) y convierte en ÁNGULOS EFÍMEROS listos para producir** — con la ventana temporal
del evento. Los ángulos firmados (2.5) son el fondo permanente; los momentos son la espuma de la semana.

**Por qué es clave (el insight del operador):** esto es lo que un consultor humano hace y ninguna
herramienta barata hace — mirar la vida real del cliente y decir "ESTO de esta semana, contado ASÍ, vende
TU negocio". Y encaja con el hallazgo maestro del research de mercado: el contenido con FUENTES es el que
la gente cree (80% prefiere la versión citada) — un momento investigado con citas es contenido verificable
de fábrica.

## 1 · Los tres casos que lo definen (del operador)

1. **El que corta pasto + la ola de calor:** alerta de calor esta semana → quiere avisar/aportar valor a
   sus clientes → Papandi investiga (qué le pasa al césped en ola de calor, qué recomiendan las fuentes
   agronómicas), lo conecta con SU negocio y SU avatar (dueños de casa) → 3 ángulos efímeros tipo «Tu
   césped no necesita más agua — necesita el agua a la HORA correcta» → piezas por el Director → la
   ventana expira sola cuando pasa el calor.
2. **El abogado + el cambio de ley laboral:** la noticia ES su momento → investigación citada de qué
   cambió y a quién afecta → ángulos educativos («Si tienes empleados por horas, esto te cambia desde el
   lunes») → además puede subir su entrevista de noticiero (modo D) y el momento la contextualiza.
3. **Papandi + el cambio de algoritmo:** nuestra propia doctrina/research (ej. «Instagram mató los
   hashtags — esto es lo que sí funciona», con las fuentes del CONTEXTO MAESTRO) alimenta NUESTROS
   momentos → contenido especializado que educa y trae clientes. **El flywheel: la investigación de
   Papandi es materia prima del marketing de Papandi.**

## 2 · Decisión de arquitectura: ¿aspecto nuevo o parte de producción?

**Las dos cosas, en capas distintas — y NO es un módulo paralelo de producción:**
- **La CAPTURA es global:** el icono de Papandi (asistente) visible en toda la app.
- **El PROCESAMIENTO es una mini-campaña:** un momento ES estructuralmente una campaña corta (ventana +
  concepto + ángulos propios) — reutiliza la maquinaria de /campanas. La feature "ganchos propios de
  campaña" (ya decidida en el research de campañas, diferida a v2) **se adelanta**: es exactamente esto.
- **La PRODUCCIÓN es la existente:** los ángulos efímeros aparecen en /angulos (agrupados bajo su momento,
  con su ventana visible) y se desarrollan por el Director como cualquier pieza. Cero flujo nuevo de
  producción.

## 3 · El flujo (4 pasos, mismas doctrinas)

```
CAPTURA → INVESTIGACIÓN (citada) → CONEXIÓN CON LA MARCA → ÁNGULOS EFÍMEROS → (producción normal)
```

1. **CAPTURA — el asistente global (el icono de Papandi):** un botón flotante en toda la app:
   *«¿Qué está pasando en tu mundo? Cuéntamelo o pídeme investigarlo.»* Acepta: texto libre («hay ola de
   calor esta semana»), un link de noticia, o una petición de investigación («¿qué cambió en la ley
   laboral de Florida?»).
   **Alcance ampliado (nota del operador 2026-07-12, se diseña EN OTRO MOMENTO — no bloquea nada de este
   spec):** el asistente global además responderá CUALQUIER pregunta del usuario — «¿qué es dar vs
   pedir?», «¿cómo uso X de la app?», «¿por qué 3:1?», consejos de marca — con la doctrina de Papandi y el
   contexto del proyecto como fuente. Requiere diseñar QUÉ información se le manda y cuál no (doctrina +
   docs de ayuda + artefactos del proyecto; jamás datos de otros proyectos). Los MOMENTOS son una de sus
   capacidades, no la única.
2. **INVESTIGACIÓN:** research web con citas (la misma capacidad del wizard de Fase 0) → informe corto
   glass-box: qué pasó, a quién afecta, datos duros CON FUENTE, ventana temporal estimada (¿cuánto dura
   este momento?). C4-compatible por construcción (todo citado, nada inventado).
3. **CONEXIÓN CON LA MARCA (el paso que lo hace Papandi y no ChatGPT):** el informe se cruza con lo
   firmado — esencia 0.1 (quién eres), oferta 1.4 (qué vendes), avatares 0.3 (a quién le duele esto y
   cómo) — y responde: *¿por qué TU marca tiene derecho a hablar de esto, y qué puerta abre?*
4. **ÁNGULOS EFÍMEROS:** 3-5 ángulos con la mecánica de 2.5 (dolor/dato/reframe + arquetipo) pero
   marcados `momento_id` + `expires_at` (la ventana). El usuario aprueba los que quiere (compuerta) →
   aparecen en /angulos bajo el momento → piezas por el Director (el contexto del momento viaja al develop
   igual que hoy viaja el de campaña, CM4). Al expirar, los ángulos se archivan solos (glass-box: "este
   momento pasó").

## 4 · La unificación (tres fuentes, UNA mecánica)

| Fuente del momento | Quién lo trae | Ejemplo |
|---|---|---|
| **El usuario** (asistente global) | él mismo | ola de calor, cambio de ley, noticia local |
| **Tendencias** (§3.6 del spec de video) | Papandi, semanal global | "este formato/mecánica está explotando" → botón «Desarrollar con tu marca» = crea un momento |
| **El radar** (Inteligencia Temporal, ya en prod) | Papandi, por calendario | ventana estacional → "Montar campaña" (ya existe) |

Tendencias deja de ser solo una pestaña informativa: **cada tendencia trae el botón que la convierte en
momento**. El radar sigue igual (fechas conocidas); los momentos cubren lo que el calendario no ve
(noticias, cambios, alertas).

## 5 · Descubribilidad (la pregunta del operador: ¿cómo se entera el usuario?)

1. **El icono global siempre visible** (la feature ES su propio anuncio — como el botón de Intercom).
2. **Momento de onboarding:** al firmar Fase 2, Papandi lo estrena: *«Tu fondo de contenido está listo.
   Cuando pase algo en tu mercado — una noticia, un cambio, un clima — tráemelo aquí y lo convertimos en
   contenido de la semana.»*
3. **Tendencias como escaparate:** la pestaña semanal muestra la mecánica funcionando (cada card =
   «Desarrollar con tu marca») — ver una tendencia convertida en ángulo ENSEÑA qué puede traer él.
4. **Empty states y la Agenda:** semana con pocos slots → *«¿Pasó algo en tu mercado esta semana?
   Cuéntamelo»*; la caja «Otro» del Director también lo sugiere.

## 6 · Modelo de datos y costos (mínimos — reutiliza lo construido)

- **Datos:** `project_campaigns` gana `kind: 'campaign' | 'momento'` + `hooks jsonb` (los ángulos
  efímeros, shape de 2.5 + `expires_at`) — la columna `hooks` ya estaba diseñada en el research de
  campañas (diferida a v2; se adelanta). El informe de investigación se guarda como artefacto del momento
  (glass-box, re-leíble). Cero tablas nuevas si esto basta.
- **Costos por momento:** 1 research con web (~$0.10-0.50) + 1 generación de ángulos (~$0.03-0.08).
  **Candado:** N momentos incluidos/mes por proyecto (propuesta: 8) con contador visible; después avisa
  (mismo patrón MEDIA_BUDGET).
- **El develop ya sabe recibir esto:** el contexto de momento viaja como hoy viaja el de campaña (CM4) —
  misma inyección, misma doctrina de fases (teaser/pico no aplican: un momento es pico corto por
  naturaleza; intent dar/pedir sí aplica y default = DAR, porque el momento es valor-primero).

## 7 · Qué NO es (guardrails)

- NO un chatbot general (todo desemboca en contenido; investigación acotada al proyecto).
- NO reemplaza los ángulos firmados (2.5 es el fondo permanente; los momentos expiran).
- NO newsjacking de tragedias/política divisiva: filtro de doctrina (mismo criterio que Tendencias §3.6 —
  lo que no usamos se explica).
- NO inventa datos: sin fuente citada, el dato no entra al ángulo (C4).

## 8 · Decisiones del operador

1. ¿Apruebas el concepto y el nombre («Momentos»)? ¿El asistente global como SU puerta de entrada?
2. ¿Adelantamos «ganchos propios de campaña» (era v2 de campañas) como base técnica de los momentos?
3. ¿Cupo de 8 momentos/mes por proyecto con contador visible?
4. Orden de construcción propuesto: DESPUÉS de V2.a+b del Director (el video encadenado primero — es tu
   prueba pendiente); Momentos entra junto a V2.c. ¿De acuerdo, o lo quieres antes?
