# AI Gateway / Wrapper — la capa de generación de imagen/video

**Project**: business/marketing-os
**Status**: **v0.2 — investigación fundida** (2026-06-30). Era stub; ahora con el **mapa de plataformas** + los **esquemas canónicos de prompt** (imagen/video), sacados de una investigación a fondo (docs oficiales de Replicate, Google Veo/Gemini "Nano Banana", Kling, Black Forest Labs FLUX.2, ByteDance Seedream/Seedance; verificación adversarial 3-votos). **PENDIENTE:** trinity propia antes de codear · el pase de **AvatarHype** (cero evidencia verificada) · validar los templates por-motor (medium-confidence — ver §6).
**Decisión de alcance:** spec **APARTE** de `spec_Admin_Cost_Intelligence.md` (Módulo C). El Gateway = **integración** (llamar a los proveedores + el esquema de prompt); el **costo/billing/catálogo-al-día** = Módulo C. Se cruzan, no se duplican.
**Consumidor:** el Estudio (`spec_Estudio §4/§8`) — al **Desarrollar idea** se produce el `design_spec`; el Gateway es el **P5** del build de producción (ÚLTIMO: tras *desarrollar → aprobar*, "Producir media" llama aquí).

> **C17 (2026-07-09):** «el Estudio» consumidor = hoy el **develop de Ángulos** (`/api/estudio/produce`; el
> código `lib/estudio/*` conservó el nombre, la superficie no). «biblioteca» = **Media** (`/media`). Las §§ de
> `spec_Estudio` → `spec_Superficies_Produccion.md`. El **contrato del Gateway no cambia** (design_spec → motor
> → media); la pieza que lo dispara es `ángulo × canal`.

---

## 0. El hallazgo que lo define (investigación 2026-06-30, verificada)
**Replicate / OpenArt / fal.ai NO tienen modelos propios** — son **hosts/agregadores** que corren los modelos de terceros, atribuidos a su autor: **Google** (Veo 3.x, Imagen 4, **Nano Banana** = Gemini 2.5 Flash Image) · **OpenAI** (GPT Image, **Sora**) · **Black Forest Labs** (**FLUX.2** Max/Pro/Flex) · **ByteDance** (**Seedream** imagen, **Seedance** video) · **Kuaishou** (**Kling**) · Stability · Runway · Minimax (Hailuo) · Ideogram · Recraft. No son "wrappers puros" (añaden hosting/inference gestionado + te dejan subir tus modelos vía Cog), pero **el que manda es el MODELO, no el host**.

**Dos consecuencias de oro:**
1. **UN esquema canónico de prompt sirve para TODOS** — el shape lo define el modelo, no el host. Un prompt para FLUX/Veo se comporta igual en Replicate, fal u OpenArt. → no rediseñamos el esquema por plataforma; solo adaptamos al **motor**.
2. **El prompt es PROSA descriptiva, NO JSON estructurado** — la idea de "JSON para control preciso de cámara/luz" se **REFUTÓ** (1-2). El Gateway llena un esquema de **campos** y los **serializa a prosa**.

**Posicionamiento (decisión del operador, 2026-06-30):** Papandi es su **propio router** — el Gateway va **directo a los modelos** (o vía un host barato), sin markup de intermediario, engine-agnóstico, eligiendo motor por precio/calidad/disponibilidad. **NO** competimos como agregador genérico (eso es commodity, carrera al precio). El **moat** es la inteligencia de marketing (el brief + la doctrina + el `design_spec` correcto para ESE avatar/canal/beat); la generación es un **costo que optimizamos**, no el producto.

## 1. El esquema canónico de prompt — IMAGEN (el `design_spec`)
El Estudio llena estos campos al **Desarrollar idea**; el Gateway los serializa a prosa para el motor.

| Grupo | Campo | Qué es | Ejemplo |
|---|---|---|---|
| **Sujeto** | `subject` | foco + atributos clave | "artesana, 30s, delantal, manos con arcilla" |
| **Escena** | `scene` | setting + fondo | "su taller, estantes de cerámica, luz de ventana" |
| **Cámara** | `camera.angle` | eye-level / picado / contrapicado / cenital / holandés | "contrapicado leve" |
| | `camera.shot` | gran plano / general / medio / primer plano / macro | "plano medio" |
| | `camera.lens_dof` | focal + profundidad de campo | "85mm, profundidad corta, fondo desenfocado" |
| **Iluminación** | `lighting` | dirección + calidad + hora del día | "luz cálida de ventana, hora dorada, suave" |
| **Estilo** | `style` | medio/acabado | "foto editorial realista" |
| **Composición** | `composition` | regla de encuadre | "regla de tercios, sujeto a la izquierda" |
| **Atmósfera** | `mood`, `palette` | mood + paleta | "cálido, artesanal · terracota y crema" |
| **Salida** | `output` | ratio · resolución · imagen de referencia | "4:5 · alta res · ref de la marca" |

## 2. El esquema canónico de prompt — VIDEO (= imagen + estos)
Todos los campos de imagen aplican, **más**:

| Grupo | Campo | Qué es | Ejemplo |
|---|---|---|---|
| **Cámara · movimiento** | `camera.movement` | tipo + dirección + suavidad | "dolly lento adelante + tilt arriba, suave" |
| **Acción** | `motion` | qué hace el sujeto | "moldea una pieza, mira a cámara" |
| **Ritmo** | `pacing`, `duration_s` | velocidad + segundos | "lento · 4 s" |
| **Transiciones** | `transitions` | entre planos (multi-shot) | "corte directo" |
| **Audio** | `audio` | ambiente + SFX + música | "torno girando, música suave" |
| **Diálogo** | `dialogue` | líneas habladas | *(solo motores con audio nativo: Veo/Sora/Seedance)* |

> Movimientos de cámara confirmados (guía oficial de Kling): **pan · tilt · zoom · dolly** (básicos) + **orbital · grúa** (avanzados), cada uno con dirección + suavidad.

## 3. Qué cambia por motor (los adapters — un esquema, N motores)
1. **Version churn = la mayor variable.** Los catálogos rotan rápido (Kling v2→v3, Seedream 4→5, FLUX Kontext→2). El **slug del motor es config**, nunca hardcode.
2. **Audio nativo varía.** Veo/Sora/Seedance generan sonido y diálogo **desde el prompt** → los campos `audio`/`dialogue` son significativos ahí; los modelos de imagen-a-video viejos los ignoran.
3. **Referencia / consistencia de personaje varía.** Para mantener el personaje entre clips: **Kling 3.0 Omni** o **Seedance 2.0** (reference-based). El campo `refs` solo aplica donde el motor lo soporta.
4. **Prosa universal; JSON no.** El adapter serializa el `design_spec` a prosa natural; algún motor pide orden de tokens (sujeto primero) o gramática propia — eso vive como **micro-regla opcional del adapter**, no en el esquema canónico.

## 4. La interfaz única
`generate({ asset_type: 'image'|'video', design_spec, engine?, refs? }) → asset` — el Estudio pasa el `design_spec` (§1/§2) sin saber del proveedor; el Gateway **serializa a prosa → elige/llama el motor → normaliza la salida → entrega a la biblioteca** (Estudio §5) y **mide el costo** (→ Módulo C).

## 5. La mecánica de integración (a desarrollar en la trinity)
- **Catálogo de motores** + cómo se mantiene al día (slugs = config; promoción desde Módulo C).
- **Adapter por motor:** auth, request/response, params, límites, watermark, latencia, políticas, micro-reglas de prompt (§3).
- **Routing:** default por caso de uso + "elige tu motor" (C5-avanzada) + BYO/BYOK.
- **Failover / reintentos / timeouts** entre motores.
- **Normalización de salida** (formatos/tamaños) → biblioteca.
- **Medición de costo por llamada** → ledger de Módulo C (COGS + pricing del Estudio §9).
- **Políticas por motor** (contenido, caras de personas, uso comercial) — el Gateway las conoce y enruta/avisa.

## 6. Fuentes + caveats (de la investigación)
- **Verificado (alta confianza):** el modelo host-vs-aggregator + el mapa de modelos + la portabilidad del esquema + prosa-no-JSON + el taxonomy de movimiento de cámara de Kling (guía oficial). Fuentes: [Replicate official models](https://replicate.com/docs/topics/models/official-models) · [Replicate text-to-video](https://replicate.com/collections/text-to-video) · [Kling camera guide](https://kling.ai/blog/ai-camera-control-movement-prompts-guide) · [OpenArt models](https://openart.ai/models) · [fal.ai models](https://fal.ai/explore/models).
- **Medium-confidence (no refutado, sin votar por rate-limits — corroboran el esquema, no probados):** los templates de [Gemini/Nano Banana](https://ai.google.dev/gemini-api/docs/image-generation) ("A photorealistic [shot] of [subject] in [setting]. [light]. Shot from [angle] with [lens]."), [Veo 3 prompt guide](https://deepmind.google/models/veo/prompt-guide/) (7 componentes), [Seedream 4.5](https://docs.byteplus.com/en/docs/ModelArk/1829186) (5 componentes), [FLUX.2](https://docs.bfl.ml/guides/prompting_guide_flux2). **Validar al construir el adapter de cada motor.**
- **Sin responder:** **AvatarHype** (cero evidencia verificada) · **Sora** solo confirmado como modelo hosteado, no su guía propia. Un pase dedicado si se prioriza el avatar/UGC.

## Tareas
- Registrada en pretel-os (`babfe7a0`). El build es **P5** del `build_plan_estudio_produccion.md` (último, tras desarrollar+aprobar).
