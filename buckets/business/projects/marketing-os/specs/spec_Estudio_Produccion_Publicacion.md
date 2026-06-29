# El Estudio — Producción & Publicación (post-plan)

**Project**: business/marketing-os
**Status**: **BORRADOR EN DESARROLLO** (se redacta sección por sección con el operador; NO es ley, NO codear hasta firmar). Fundación §0–2 redactada; §3–11 pendientes.
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
| 6 | Calendario de publicaciones | ⬜ pendiente |
| 7 | Guía de publicación (acompañamiento) | ⬜ pendiente |
| 8 | La UI del Estudio | ⬜ pendiente |
| 9 | Costos / pricing por modo | ⬜ pendiente |
| 10 | Cruce con specs existentes | ⬜ pendiente |
| 11 | Decisiones abiertas | ⬜ pendiente |

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

## 6. Calendario de publicaciones  ⬜
*(pendiente — dónde vive; cómo recibe la info por canal; cadencias del plan)*

## 7. Guía de publicación  ⬜
*(pendiente — el acompañamiento; "te aviso con la pieza lista"; pasos por canal; marcar publicado → medición)*

## 8. La UI del Estudio  ⬜
*(pendiente — pantallas: producir · biblioteca · calendario · publicar; navegación; acceso directo)*

## 9. Costos / pricing por modo  ⬜
*(pendiente — cross-ref a la propuesta: N-gratis + créditos + BYO; el ledger del Módulo C)*

## 10. Cruce con specs existentes  ⬜
*(pendiente — Fase 3 distribución, Fase 4 medir, Módulo C admin; sin duplicar)*

## 11. Decisiones abiertas  ⬜
*(pendiente — endpoint primero, N-gratis, storage, avatares, auto-publish, etc.)*
