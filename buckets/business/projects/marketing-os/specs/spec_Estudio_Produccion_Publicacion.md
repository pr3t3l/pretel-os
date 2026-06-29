# El Estudio — Producción & Publicación (post-plan)

**Project**: business/marketing-os
**Status**: **BORRADOR COMPLETO v0.1** (las 12 secciones §0–11 redactadas con el operador; NO es ley, NO codear hasta firmar). Pendiente: revisión final + bajar las decisiones abiertas (§11) + trinity antes de build.
**Last updated**: 2026-06-28
**Origen:** sesión sim Papandi (2026-06-28). Tras cerrar el plan (Fase 2) el operador identificó el puente que falta: el plan dice QUÉ publicar, pero hace falta PRODUCIR las piezas reales y PUBLICARLAS. Decisión arquitectónica del operador: esto es un **workspace independiente del wizard** ("el Estudio"), no una fase más.
**Cruza con:** `spec_Production_Support_and_Pricing_PROPOSAL.md` (modos + pricing), `spec_Phase_2_Contenido.md` (el plan que alimenta), `spec_Phase_3_Distribucion.md` (publicar/medir — el Estudio es su casa/UI), `spec_Admin_Cost_Intelligence.md` (Módulo C — billing/cost admin).

---

## Mapa del documento (esqueleto)

| # | Sección | Estado |
|---|---|---|
| 0 | Propósito + La Promesa | ✅ redactada |
| 1 | Arquitectura: wizard vs Estudio | ✅ redactada |
| 2 | Contrato de datos: el plan alimenta la generación | ✅ redactada |
| 3 | Producción pieza por pieza (copy/imagen/video por su modo) | ✅ redactada |
| 4 | Endpoints + wrapper | ✅ redactada |
| 5 | Biblioteca de assets (storage) | ✅ redactada |
| 6 | Calendario de publicaciones | ✅ redactada |
| 7 | Guía de publicación (acompañamiento) | ✅ redactada |
| 8 | La UI del Estudio | ✅ redactada |
| 9 | Costos / pricing por modo | ✅ redactada |
| 10 | Cruce con specs existentes | ✅ redactada |
| 11 | Decisiones abiertas | ✅ redactada |

---

## 0. Propósito + La Promesa

**Propósito.** El Estudio convierte el **plan de contenido firmado** (Fase 2) en **piezas reales producidas y publicadas**. Es el puente entre *"sé qué publicar"* y *"lo publiqué"* — y por tanto entre el plan y la KPI (dinero). Sin el Estudio, el plan es un mapa que el usuario no sabe ejecutar y abandona en la semana 3.

**La Promesa (el contrato de honestidad — por tipo de pieza).** Lo que de verdad cumplimos, sin letra chica:

| Tipo de pieza | Qué hace Sandi | Qué pone el usuario | Costo |
|---|---|---|---|
| **Texto** (artículo, copy, email, guion, asunto, hilo) | Lo **escribe completo**, en tu voz, con tu gancho — listo para aprobar | Aprobar (o ajustar) | incluido |
| **Imagen** | (a) la **genera** desde tu foto cruda · (b) te da el **prompt** para tu IA · (c) te **guía** a tomarla | elige la ruta; sube la foto o la toma | (a) cuesta · (b)(c) $0 |
| **Video** | Escribe el **guion** + la **guía de producción** (ambiente/luz/tips); o **anima el producto con IA** (beta) | graba siguiendo la guía (si DIY) | guion incluido · IA cuesta |
| **Publicación** | Te **avisa con la pieza lista adentro** + el momento | publica en 1–2 clics (auto-publish = futuro) | incluido |

**La anti-promesa (lo que NO prometemos).** Nunca decimos *"todo te llega hecho"* cuando una parte la pones tú o cuesta extra. **Cada pieza muestra su modo, tu-parte y su costo, antes de producir.** La persona en cámara la grabas tú (con guía) — no la inventa la IA (políticas + autenticidad). Es el mismo glass-box de todo el producto, aplicado a la producción.

## 1. Arquitectura: el wizard vs el Estudio

Dos superficies distintas, con propósitos distintos:

| | **El Wizard (Fases 0–2)** | **El Estudio (post-plan)** |
|---|---|---|
| Propósito | **Planear** | **Operar** |
| Cuándo | una vez, al inicio | siempre, día a día |
| Forma | lineal, con candados, gated | workspace persistente, libre |
| Termina en | `content_plan` firmado | (no termina — es el hogar) |
| El usuario… | decide la estrategia | produce, publica, mide |

**Regla dura (mandato del operador):** una vez firmado el plan, el usuario **NO vuelve a abrir Fase 2** (pilares, voz, reparto) para publicar. Entra **directo al Estudio**. El plan firmado queda **visible en solo-lectura** (referencia), pero la operación vive en el Estudio. Enmendar el plan es una acción explícita aparte (re-abre el sub-paso, como hoy).

**Por avatar.** El Estudio es **por avatar** (cada avatar tiene su plan → su cola de producción + su calendario). Hereda el llaveado `avatar_key` (C15). El selector de avatar vive en el Estudio.

**Relación con Fases 3–5.** El Estudio es la **casa operacional** de:
- **Producción** (la capa nueva — plan → assets reales).
- **Fase 3 — Publicar** (calendario + tracking + "te aviso").
- **Fase 4 — Medir** (los resultados que el usuario VE).
- **Fase 5 — Ajustar** (señales que re-disparan producción/plan).
El usuario no piensa en "fases 3/4/5" — piensa en "producir, publicar, ver cómo va". Las fases son la plomería; el Estudio es la experiencia.

**El Estudio es un SISTEMA PERPETUO, no un one-shot (la naturaleza del motor).** El plan firmado **NO es una lista fija de N piezas** que se produce una vez y se acaba — es una **RECETA**: los pilares + la biblioteca de ganchos + las cadencias son un **motor generativo** que produce piezas **semana tras semana**. La atomización (2.4) es el **primer lote**; de ahí el Estudio sigue generando piezas nuevas desde la receta, sobre la cadencia firmada (*"N por semana"*), hasta que la medición pida refrescar o ajustar. → **la cola de producción es un stream continuo**, no una lista que se vacía.

**El Estudio es un LOOP, no lineal.** El motor corre en bucle: **producir → publicar → medir → refrescar/ajustar → producir…**. La medición (Fase 4) **re-dispara** producción: refrescar piezas viejas (freshness = señal de ranking), generar nuevos ganchos donde sube la fatiga, doblar lo que convierte. No es "planeo, produzco, publico, fin" — es un sistema que vive.

## 2. Contrato de datos: cómo el plan firmado alimenta la generación

**Principio:** nada del plan se desperdicia. **Cada pieza real se genera cruzando los artefactos firmados** — el plan es el ADN de cada pieza. Para producir UNA pieza, el generador toma:

| Input (artefacto firmado) | Qué aporta a la pieza |
|---|---|
| **2.4 Atomización** (la pieza) | su **ancla** (título) + el **kind** (canal × formato) + la nota → QUÉ es esta pieza |
| **2.3 Pilar** al que pertenece | la **fuerza** + el **modo** (reforzar/resolver) + de qué habla → el ÁNGULO/mensaje |
| **2.5 Ganchos** de ese pilar | la biblioteca de ganchos → el **primer segundo** de la pieza |
| **2.0 Voz** | arquetipo, tono, léxico, prohibidos → **cómo SUENA** |
| **2.2 Canal** | función del canal + cadencia + ventanas → DÓNDE/CUÁNDO y el formato |
| **2.1 Reparto** | el momento de conciencia que toca → el **registro** (educar/comparar/capturar) |
| **Fase 1 Oferta** | las **palabras exactas** (garantía, displacement) → lo que las piezas REFORZAR citan |
| **Fase 0** | keywords reales + `where_we_meet` + idioma del avatar → anclaje + formato + idioma |
| **Perfil de producción** | capacidades del usuario → enruta al **modo** (texto auto / imagen / video DIY-guía) |

**La fórmula de una pieza:**
> (ancla + kind) × (mensaje del pilar) × (gancho) × (voz) × (canal/momento) × (palabras de la oferta si reforzar) → **el copy real + las instrucciones de visual/video**, en el idioma del mercado, por el modo de producción que le toca.

**Implicación:** el generador de producción es un prompt CAG (como los de Fase 2) que recibe TODO esto firmado y produce la pieza terminada. Glass-box: el usuario ve de qué pilar/gancho/voz nació cada pieza. Reusabilidad total del plan.

**El brief es CHANNEL-AWARE (mejora — no one-size).** El ensamblado de arriba es la base, pero **el grounding cambia por canal**:
- **SEO (artículo):** + análisis de la **SERP del Top-10** (vía DataForSEO) → **entidades a incluir + el gap de profundidad** vs el Top-3. Esto es lo que hace rankear, no solo "usar la keyword".
- **Social (carrusel/reel):** + el ángulo **ADAS** + el gancho específico de la biblioteca.
- **Email:** + la **posición en la secuencia** (bienvenida / nurturing / ventas) → la estructura que toca.
- **Ads:** + los **límites de plataforma** + la landing destino.

**El brief es un ARTEFACTO estructurado (mejora — no solo prosa).** Vive como el objeto `brief` de la pieza (§3.1), al estilo del **JSON-Prompt** del corpus:
```
brief = {
  mensaje_del_pilar,     // el ángulo (fuerza + modo reforzar/resolver)
  pov_mecanismo,         // el diferenciador único (anti-genérico, anti-prueba-social C4)
  gancho,                // de la biblioteca (2.5)
  voz,                   // léxico + prohibidos (2.0)
  keywords, entidades,   // grounding real (DataForSEO / SERP)
  palabras_de_oferta,    // si REFORZAR (Fase 1)
  estructura_canal       // la plantilla del corpus (§3.3)
}
```
§3 recibe un brief explícito y rico — el **lever #1 anti-genérico**. *(Brief genérico → output genérico; brief con datos reales → contenido que compite.)*

---

## 3. Producción pieza por pieza

El plan (2.4) entrega la **cola de producción**: por pilar, 1 ancla + N derivados, cada uno con su `kind` (canal × formato) y su modo. **La calidad NO sale de "un prompt"** — sale de un **pipeline de 5 pasos** (proceso experto confirmado por research externo + nuestro propio corpus), donde **el plan firmado ES el brief** — el lever #1 de calidad (*un brief genérico produce contenido genérico*).

### 3.1 La unidad: la pieza
```
Pieza = {
  id, avatar_key,            // POR AVATAR (C15) — faltaba
  pillar_id, anchor_ref,     // de qué pilar / qué ancla deriva
  kind: { channel, format },
  production_mode,           // texto auto / imagen / video, por su modo
  brief,                     // §2 ensamblado: mensaje+gancho+voz+keywords+oferta
  outline,                   // la estructura (plantilla del corpus para ese canal)
  draft, asset,              // borrador → pieza final aprobada (texto + visual/video)
  qa_flags,                  // lo que el editor-IA revisó (voz, doctrina, estructura, keywords)
  status,                    // en_cola | producida | aprobada | publicada
  cost
}
```

### 3.2 El pipeline de calidad (5 pasos) — cómo §2 alimenta §3
El §2 (contrato de datos) **ES el brief**; §3 es el **pipeline** que lo convierte en una pieza de calidad:

| Paso | Qué hace | Por qué da calidad (no genérico) |
|---|---|---|
| **1. Brief** | el §2 ya ensamblado: mensaje del pilar + gancho + voz + **keywords REALES** + palabras de la oferta + dolores del avatar | el brief más rico posible, con grounding en datos reales (= RAG). El plan es el anti-genérico. |
| **2. Estructura** | se elige la **plantilla de calidad del corpus** para ese canal (no se inventa) | el oficio ya sabe cómo se estructura un buen artículo/carrusel/email/ad |
| **3. Borrador** | el LLM redacta contra el brief + la estructura (para SEO, vía el **JSON-Prompt** parametrizado) | outline-first, no one-shot |
| **4. Edición / QA** | paso SEPARADO: aplica candados de **voz + DOCTRINA + estructura del canal + keywords + gancho** | el salto de calidad vs one-shot; donde se enforce la doctrina |
| **5. Aprobación** | tu tarjeta (✓ / ✏️ / regenerar) | tu autoría |

### 3.3 Plantillas de calidad por canal (de NUESTRO corpus — el craft de los 7 cursos)
La estructura no se inventa: viene del oficio que ya sintetizamos.

| Canal | Estructura/plantilla (cita corpus) | Reglas |
|---|---|---|
| **Artículo SEO** | intro responde la intención en el §1 · H1>H2>H3 · párrafos 150–400 car · ≥5 entidades (rel >0.7) · enlaces internos · schema · más profundo que el Top 3. Parametrizado por **JSON-Prompt** (`3_seo:239`) | imágenes ≤120 KB · freshness |
| **Carrusel / Reel / video corto** | **Hook 3–5s → Cuerpo 15–45s (micro-ganchos c/5–7s) → Cierre 4–6s (CTA)** · framework **ADAS** (`7_rrss:89,206`) | filtro niño (simple) · filtro masas (universal) · 1ª persona |
| **Email** | bienvenida = **8 puntos** · ventas = **PAS o AIDA** · asuntos **<40 car** + pre-header (par A/B) (`6_email:62,252,282`) | beneficios no características · CTA con urgencia REAL |
| **Google/Meta Ads** | 20 títulos ≤30 · 20 largos ≤90 · 20 desc ≤90 · landing 7 secciones (`5_sem:88,213`) | orientado a beneficio · relevancia kw (Quality Score) |

### 3.4 La DOCTRINA filtra el craft (clave)
El corpus es el **CRAFT** (cómo estructurar); la **doctrina manda sobre la TÁCTICA**. El paso de QA (4) **quita lo que el corpus sugiere pero nuestra doctrina prohíbe**:
- el corpus de email pone *"testimonios / casos de éxito"* en la secuencia de ventas → **C4 los retira** (pre-lanzamiento sin clientes) y los reemplaza por **mecanismo**.
- el corpus de ads pone *"precio tachado vs oferta"* (urgencia/comparación) → **C12 + C1** lo retiran (sin urgencia fabricada; valor por funcionalidad, no comparación).

Combinamos lo mejor del oficio con nuestra honestidad. Glass-box: el QA reporta qué quitó y por qué.

### 3.5 Imagen — las 3 rutas + el prompt generado
El Estudio ofrece las rutas de la Promesa, y **Sandi genera el PROMPT** desde el contexto de la pieza:
- **Asistido:** subes la foto cruda → la mandamos con el prompt al endpoint → imagen estilizada → biblioteca. *(Ej. vela → "coloca esta vela en una sala acogedora, luz cálida natural, fotografía lifestyle".)*
- **Prompt-BYO:** te damos el prompt + pasos → lo corres en tu IA → subes el resultado.
- **Guía-DIY:** instrucciones de foto (escena/luz/encuadre) → la tomas → la subes.
- **Regla (C16 + fidelidad):** la IA estiliza la **escena**, NUNCA el **producto**. Para handmade auténtico, la guía-DIY a veces gana.

### 3.6 Video — guion (del corpus) + guía, o IA-producto (beta)
- **Guion (hecho):** con la plantilla del corpus — **Hook 3–5s → Cuerpo (micro-ganchos) → Cierre/CTA**, en la voz, idioma del mercado.
- **Guía de producción (DIY):** ambiente/luz/encuadre/shot-list — "con el teléfono basta". Producto o talking-head (C4).
- **IA-producto (beta):** anima la imagen del producto (image-to-video). **Nunca la persona** (políticas + autenticidad).

### 3.7 El candado de producibilidad
El modo de cada pieza se cruza con tu **perfil de producción** (capacidades). Si una pieza pide algo que no puedes (ej. video y no quieres grabar ni elegiste IA), el sistema **degrada** (a un formato que sí puedes) o **soporta** (guía / ruta IA) — **nunca te deja trabado**. Puedes cambiar el modo a mano.

### 3.8 Aprobar → biblioteca → cola de publicación
Pieza aprobada → **biblioteca de assets** (§5) → **cola de publicación** (§6). Reusable; nada se produce dos veces.

## 4. Endpoints + wrapper

**Sandi es el wrapper en medio.** Una capa que abstrae sobre múltiples endpoints de imagen y video. El usuario nunca llama un endpoint directo — pide *"genera esta imagen / video"* y el wrapper enruta. Beneficios: no nos casamos con un proveedor; enrutamos por precio/calidad/disponibilidad; endpoints nuevos enchufan sin tocar el resto.

### 4.1 Qué endpoint por tipo (del research §7 de la propuesta)
| Tipo | Default recomendado | Alternativas | Precio | Notas |
|---|---|---|---|---|
| **Imagen — estilizado de producto** | FLUX.1 Kontext · Seedream v4.5 Edit · Nano Banana | (mismo rango) | **~$0.04/img** | preservan el producto, re-estilizan la escena (C16) |
| **Video — producto (beta)** | Runway Gen-4 Turbo | Veo 3 Fast · Kling 3.0 | **$0.75–3.60 / clip 15–30s** | image-to-video, beta; **nunca persona** |

*(Precios de docs oficiales, mediados 2026 — confirmar al integrar.)*

### 4.2 Cómo elige el usuario
- **Default (todos):** Sandi usa el endpoint recomendado para el caso. Cero fricción.
- **Elige tu engine (capacidad C5-avanzada):** quien sabe puede escoger (FLUX / Kling / Veo…) — el wrapper orquesta.
- **BYO (trae tu IA):** corre el prompt en su propia herramienta/llave → **costo $0 para nosotros**.

### 4.3 Qué hace el wrapper
Enruta · normaliza formatos (entrada/salida) · **reintenta / failover** si un proveedor cae · **mide el costo** por generación (alimenta el ledger del Módulo C + el pricing §9) · guarda el resultado en la **biblioteca** (§5). Atado a la **promoción de endpoints** del Módulo C: cuando uno gana en precio/calidad, se promueve sin deploy.

## 5. Biblioteca de assets

**Todo lo producido se guarda en el proyecto del usuario, por avatar.** Es el activo que crece y **fideliza** (su biblioteca vive en Sandi).

### 5.1 Qué se guarda y dónde
| Asset | Dónde | Metadata |
|---|---|---|
| Texto (copy, artículo, guion, email) | DB (estilo `project_phase_artifacts`) | pieza, pilar, avatar, modo, status |
| Imagen / video | **Supabase Storage** (object storage), carpeta por proyecto/avatar | + costo, endpoint, prompt usado, versión |

### 5.2 Reuso (baja costo + fideliza)
Un asset producido se **reutiliza** entre piezas y semanas (una foto estilizada de la vela sirve para 3 posts) → menos generaciones = menos COGS + retención. La biblioteca se navega desde el Estudio (§8).

### 5.3 Storage — a resolver
- **Tamaño:** imágenes 1–5 MB; videos 15–30s ≈ 5–50 MB. A escala, crece.
- **Costo:** Supabase Storage ~$0.02/GB/mes (orden de magnitud — confirmar). En uso interno, trivial.
- **Retención:** ¿se guardan todas las versiones? ¿se purgan borradores no aprobados? → decisión abierta (§11).
- **Versionado:** una pieza regenerada, ¿guarda versiones o reemplaza? → §11.

Cruza con el ledger de costos ([[sandia-cost-ledger]]: `project_api_calls` ya traquea costos de API externa; la generación imagen/video es el mismo patrón) y el Módulo C.

## 6. Calendario de publicaciones

El calendario es **la línea de tiempo** del Estudio: dónde y cuándo sale cada pieza. Es **perpetuo** (§1) — se llena semana tras semana desde la receta + las cadencias.

### 6.1 De dónde sale
**Cadencias firmadas (2.2)** × **piezas de la cola (§3)**. Cada canal trae su *"N por semana"* + sus **mejores ventanas** (del estudio + `lookup_posting_cadence_2026`). El calendario agenda los slots; la cola los llena.

### 6.2 Qué tiene cada slot
```
slot = { fecha_hora, canal, formato, asset_ref (la pieza producida),
         estado: programado|publicado, utm/tracking }
```
(hereda el `publish_plan.calendar[]` de Fase 3.)

### 6.3 Cómo recibe la info por canal
- **Cadencia + ventanas** por canal (2.2 + lookup) → los slots y sus horas.
- **El mix** del oficio balancea el calendario: 25% viral / 25% captación / 50% conversión (corpus `7_rrss`) — no solo "piezas sueltas".
- **7-11-4** (multi-touch): el calendario asegura el **ecosistema sostenido**, no impactos aislados.

### 6.4 Producción ↔ calendario
El calendario es la línea de tiempo; la **cola (§3) es el "por producir"**. Dos modos:
- **Just-in-time:** la pieza se produce cuando su slot se acerca (ahorra costo si el plan cambia).
- **Por lote:** produces la semana entera de una y se agenda.
El usuario reordena/reprograma slots a mano.

### 6.5 El modelo de timing: semilla por avatar → personalización por datos (estudio 2026-06-28)
El horario **NO es genérico** — son **dos capas**:
- **Capa 1 — Semilla (calibrada por avatar):** los promedios del oficio (Sprout/Buffer 2026) **cruzados con lo que sabemos del avatar**: su **tipo (B2B/B2C) × nicho × canal × zona horaria**. El avatar de Etsy (B2C) arranca en IG/Pinterest tardes+fines de semana; el de coaches (B2B) en LinkedIn Mar–Jue 8–10h. **Arranque inteligente, no un horario genérico para todos.**
- **Capa 2 — Personalización (sus propios datos):** cuando los posts acumulan analytics (**Fase 4** — cuándo SÍ interactuó su audiencia real), el calendario **se mueve a las mejores horas REALES** de su público. El **loop perpetuo (§1)** lo hace solo: semilla → mide → afina.
- **Frecuencia** igual: semilla por canal (IG 3–5/sem · TikTok 2–5 · LinkedIn 2–5 · YouTube 1 · FB 1–2/día) → ajustada por fatiga/rendimiento medido. **Cadencia estable ≥8 semanas antes de evaluar** (el algoritmo premia consistencia).

**Diferenciador:** una herramienta genérica te da el promedio y se queda ahí; nosotros **arrancamos calibrados por avatar Y nos volvemos tuyos con tus datos**.

## 7. Guía de publicación (acompañamiento)

### 7.1 El compromiso: "te aviso con la pieza lista adentro"
Cuando un slot vence, el usuario recibe una **notificación con el asset terminado** (copy + imagen/video) **listo para publicar** — no para redactar — **en el mejor momento para su público** (calibrado por avatar → personalizado por sus datos, §6.5). (Mandato del operador, task `7493e337`; nace en Fase 3.)

### 7.2 Pasos por canal
Cada canal trae su *"cómo publicar"*: dónde pegar, qué adjuntar, el horario. Algunos canales pueden **integrarse** (blog vía CMS, email vía ESP); el resto = "copia esto, publícalo aquí". Calibrado al canal.

### 7.3 Marcar "publicado" → alimenta la medición
Al marcar una pieza publicada (o auto-detectado), **se cierra el loop**: el post publicado → Fase 4 (métricas) → señales de Fase 5. El "publicado" es el dato que arranca la medición.

### 7.4 Auto-publish = futuro (honestidad)
- **V1:** el usuario publica — lo hacemos de **1–2 clics** (el asset llega hecho).
- **V2:** un scheduler (n8n/cron) auto-publica donde la plataforma lo permite.
No prometemos auto-publish hoy; prometemos que **producir y publicar sea trivial**.

### 7.5 Acompañamiento del lado humano
Para piezas DIY (el video que grabas tú), la notificación incluye la **guía de producción** (§3.6) + un checklist. El sistema **acompaña**, no abandona en "ahora hazlo tú".

## 8. La UI del Estudio

El Estudio es un **workspace persistente** (no un wizard), **por avatar** (selector arriba, como Fase 2). El plan firmado queda en **solo-lectura** (referencia); la operación vive aquí. Cuatro superficies + una de resultados:

### 8.1 Producir (la cola)
La lista de piezas por producir (de la receta + cadencia). Cada pieza muestra **de qué pilar/gancho nació + su modo + costo**. El usuario produce (texto auto · imagen 3 rutas · video guion+guía) y **aprueba/ajusta/regenera** (patrón de tarjeta).

### 8.2 Biblioteca
Los assets producidos (texto + imagen/video), navegables, **reutilizables** entre piezas/semanas. Filtros por pilar/canal/avatar.

### 8.3 Calendario
La línea de tiempo (semana/mes): los slots con su pieza, **calibrados por avatar y personalizados por datos** (§6.5). Reordenar/reprogramar a mano.

### 8.4 Publicar
Las notificaciones "pieza lista adentro" + los **pasos por canal** + marcar **publicado** (cierra el loop → medición).

### 8.5 Resultados (Fase 4, después)
Cómo va cada pieza/canal — y lo que **re-dispara** producción y afina el timing (el loop).

**Principio UI:** operacional (dashboard), no lineal. **Glass-box** en cada pieza (origen + modo + costo). Acceso directo: el usuario no reabre Fase 2.

## 9. Costos / pricing por modo

Detalle completo en `spec_Production_Support_and_Pricing_PROPOSAL.md §5`; aquí el resumen operativo del Estudio:

| Modo | Costo nuestro | Al usuario |
|---|---|---|
| Texto (auto) | LLM (centavos) | **incluido** |
| Imagen (asistido) | ~$0.04/img | **N gratis/mes por tier** → luego medido (~$0.10–0.25) o **BYO** ($0) |
| Video (asistido, beta) | $0.75–3.60/clip | **medido/créditos** o BYO — nunca ilimitado |
| Guía-DIY / prompt-BYO | $0 | incluido |

- **Dos modos activos** (cost-plus medido + BYO) + **N gratis y después se vende** (mandato).
- El **wrapper mide el costo por llamada** → ledger de **Módulo C** (#11–13) → **COGS por usuario** → valida el margen (doctrina de margen, Fase 1).
- Storage: costo por tipo con **pesos REALES medidos** (Módulo C #12) → informa retención.

## 10. Cruce con specs existentes (sin duplicar)

El Estudio es la **experiencia/orquestación**; los demás specs son la plomería.

| Spec | Qué aporta al Estudio |
|---|---|
| **Fase 2** (`spec_Phase_2`) | el plan firmado = el **brief** (§2) que alimenta cada pieza |
| **Fase 3** (`spec_Phase_3`) | publicar + tracking; el calendario hereda `publish_plan.calendar[]` |
| **Fase 4** (`spec_Phase_4`) | medir → **alimenta el loop + la personalización de timing** (§6.5) |
| **Fase 5** (`spec_Phase_5`) | ajustar → **re-dispara** producción (refrescar, nuevos ganchos) |
| **AI Gateway** (`spec_AI_Gateway_Wrapper`) | la capa de endpoints (§4) — integración |
| **Módulo C** (`spec_Admin_Cost_Intelligence`) | costos/billing/COGS (#11–13) — admin |
| **Propuesta de producción** (`spec_Production_Support_...`) | los modos + capacidades + pricing |
| **`lookup_posting_cadence_2026`** | las cadencias + ventanas (semilla del calendario) |

## 11. Decisiones abiertas

- **Endpoint de imagen primero** → spot-test de calidad con un producto real (Kontext vs Seedream vs Nano Banana).
- **N gratis:** ¿cuántas, por tier o global? ¿créditos unificados o por tipo (imagen/video)?
- **Storage:** retención (¿purgar borradores no aprobados?), versionado (¿guardar versiones?), pesos reales (medir).
- **Avatares de persona** (HeyGen-style) — ¿en alcance con disclaimer, o fuera?
- **Auto-publish** (V2) — ¿cuándo, en qué canales lo permite la plataforma?
- **Integraciones de publicación** — ¿qué canales conectamos directo (CMS/ESP) vs "copia y publica"?
- **Producción just-in-time vs por-lote** — ¿cuál default?
- **Pendientes que ya son tareas:** escribir `spec_AI_Gateway` (`babfe7a0`) · construir Módulo C (`c027d954`) · keyword research por-avatar (`cdf66e45`).
