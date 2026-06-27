# Capa de Producción de Contenido + Modos & Pricing — PROPUESTA

**Project**: business/marketing-os
**Status**: **PROPUESTA v0.1** (no es ley; capturada para revisión del operador — uso INTERNO por ahora, sin módulo de pagos/admin construido). NO codear hasta firmar.
**Last updated**: 2026-06-27
**Origen:** sesión sim Papandi (2026-06-27). El operador identificó el hueco más grande del sistema: producimos un *plan* de contenido (Fases 0–2) pero no la *producción/ejecución* real. Sin ejecución no hay publicación; sin publicación no hay dinero (la KPI). Esta propuesta diseña el puente.
**Cruza con:** `spec_Phase_2_Contenido.md` (la atomización declara el modo por pieza), `spec_Phase_3_Distribucion.md` (ejecuta), `spec_Admin_Cost_Intelligence.md` (Módulo C — dueño de la vista admin/billing; aquí va lo de cara al usuario).

---

## 0. El problema (la brecha promesa–realidad)

Papandi promete *"te llega hecho"*. Es **verdad para texto** (artículo, copy, guion, email, ganchos) pero **falso para visual/video**: ahí hoy entregamos un guion y decimos *"ahora hazlo tú"*. Si no se resuelve, el cliente firma un plan precioso, choca con *"no sé/no puedo producir"*, y abandona en la semana 3 (lo que el propio sistema advierte). **Un plan calibrado a lo que el cliente PUEDE hacer vence a un plan perfecto que no puede ejecutar.**

## 1. El modelo: "modo de producción" por entregable

Cada pieza de la atomización (Fase 2.4) lleva un **`production_mode`**. En vez de lógica a medida por canal, un set chico de modos cubre todo:

| Modo | Quién produce | Costo IA | Ejemplos |
|---|---|---|---|
| `auto_text` | Sandi 100% | incluido | artículo, copy, guion, email, asuntos, ganchos |
| `guided_diy` | el usuario, con NUESTRA guía | $0 | foto del producto (escena/luz/encuadre); grabar (guion + shot-list + ambiente + tips) |
| `prompt_byo` | el usuario, en SU herramienta de IA | $0 a nosotros | le damos el prompt + pasos → genera en su ChatGPT/Gemini |
| `assisted_image` | Sandi vía endpoint de imagen | **~$0.04/img** | sube foto cruda del producto → la colocamos en un ambiente con IA |
| `assisted_video` | Sandi vía endpoint de video (BETA) | **~$0.75–12/clip** | image-to-video / animación del producto (NO persona) |
| `byo_endpoint` | Sandi como **wrapper**; el usuario ELIGE el endpoint | medido | "genera con FLUX / Kling / Veo…" — nosotros orquestamos |

**"Qué ofrecemos realmente" = el plan + una RUTA de producción honesta por pieza.** Cada pieza muestra su modo + tu-parte + costo (el contrato de honestidad — el mecanismo de confianza).

## 2. Capacidades requeridas por modo + el "perfil de producción"

El perfil NO pregunta rasgos crudos ("¿sale en cámara?"); mide **capacidades**, y cada modo tiene su gate. El sistema enruta cada pieza al modo cuya capacidad el usuario tiene, con el de menor esfuerzo que dé buena calidad.

**Las 8 dimensiones del perfil (capability-based):**

| # | Capacidad | Habilita |
|---|---|---|
| C1 | ¿Tiene producto/objeto físico mostrable? | rutas de foto/video de producto |
| C2 | ¿Puede capturar foto/video básico (teléfono)? | DIY en general |
| C3 | ¿Dispuesto a producir **siguiendo guías** (tiempo/esfuerzo)? | `guided_diy` |
| C4 | ¿Dispuesto a salir **EN CÁMARA** (su cara)? *(separado de C3 — el artesano graba su PRODUCTO, no su cara)* | talking-head DIY |
| C5 | ¿Sabe/quiere usar IA? **simple** (ChatGPT/Gemini con prompt) vs **avanzada** (FLUX/Kling/elegir engine) | `prompt_byo` / `byo_endpoint` |
| C6 | ¿Prefiere pagar para que lo hagamos vs hacerlo él? + presupuesto | `assisted_*` vs DIY/BYO |
| C7 | ¿Cuánto tiempo/semana? | calibra la carga del calendario |
| C8 | ¿Ya tiene assets hechos (fotos/videos previos)? | reutilizar (baja producción) |

**Gate por modo:**
- `auto_text` → ninguna capacidad (todos).
- `assisted_image` → C1 + C2 (tiene producto + 1 foto básica; lo demás lo hacemos). **El de menor barrera para buen visual.**
- `guided_diy` (foto) → C1 + C2 + C3. (video producto) → C2 + C3. (talking-head) → C2 + C3 + **C4**.
- `prompt_byo` → C5-simple. `byo_endpoint` → C5-avanzada.
- `assisted_video` → C1 (tiene imagen del producto). Calidad BETA.

## 3. El wrapper de endpoints (el usuario elige; nosotros abstraemos)

Sandi es el **wrapper en medio**: una capa que abstrae sobre múltiples endpoints de imagen y video. El usuario ve un **default recomendado** (el que mejor precio/calidad da para su caso) y, si tiene C5-avanzada, un modo **"elige tu engine"** (FLUX, Kling, Veo, Seedream…). Beneficio: no nos casamos con un proveedor, y podemos enrutar por costo/calidad/disponibilidad. (Atado a la promoción de modelos del Módulo C §2.)

## 4. La biblioteca de assets del proyecto (reusabilidad + fidelización)

**Todo lo generado (imágenes y videos) se guarda en el proyecto del usuario** → reusable entre piezas (una foto estilizada de la vela sirve para 3 posts) y **aumenta la fidelización** (su biblioteca vive en Sandi). Implicaciones a resolver:
- **Storage (Supabase Storage):** los videos pesan (15–30s ≈ 5–50 MB; imágenes 1–5 MB). Definir: carpeta por proyecto, política de retención, y **costo de storage** (~$0.02/GB/mes orden de magnitud — confirmar). A escala, pasar el costo o limpiar; en uso interno, trivial.
- **Reuso baja costo:** reutilizar un asset = 0 generaciones nuevas = menos COGS + el beneficio de retención.
- Cruza con el ledger del Módulo C (un nuevo tipo de costo: generación de imagen/video por usuario, como ya se hace con `project_api_calls` de DataForSEO).

## 5. Modelo de costo / precio por modo

**Dos modos de pago ACTIVOS + N gratis (mandato del operador):**
1. **Medido cost-plus** (estilo Stripe Billing / AI Gateway): markup % sobre el costo real del proveedor. Para `assisted_*` / `byo_endpoint`.
2. **BYO** (trae tu suscripción/llave): el usuario corre el prompt en su herramienta o conecta su API key; paga al proveedor directo; nosotros cobramos fee de plataforma. **Costo IA = $0 para nosotros.**
3. **N gratis y después se vende:** cada usuario recibe N generaciones gratis (por tier/mes) y luego se cobran (medido o créditos).

**Implicación de márgenes (cruza con la doctrina de margen de Fase 1):**
- **Imágenes (~$0.04):** tan barato que se puede **incluir N/mes por tier** (o vender a $0.10–0.25 c/u). Margen sano.
- **Video ($0.75–12/clip):** **medido/créditos sí o sí** (vender a costo + markup ~$3–8/clip), o BYO. **Nunca ilimitado** — se come el margen.

> **Restricción importante (políticas):** generar **video de una PERSONA real** (su cara) está bloqueado/restringido en los endpoints (Sora rechaza caras; otros restringen). Por eso: video de IA = **producto/animación**, NO persona. Si el usuario quiere salir él, va por **`guided_diy`** (copy + guía + ambiente + luz + tips) o avatar tipo HeyGen (detectable — ofrecer con disclaimer).

## 6. Qué integramos primero (faseado por madurez/costo)

- **Fase A (ya viable):** `auto_text` (ya) + `assisted_image` (maduro, ~$0.04, fiel al producto) + `prompt_byo`. Integrar **1 endpoint de imagen** (FLUX.1 Kontext **o** Seedream v4.5 Edit **o** Nano Banana — los tres ~$0.04 y hechos para "producto fiel, escena nueva").
- **Fase B:** `guided_diy` de video (guion + shot-list + guía de ambiente/luz) — alto valor, costo ~$0.
- **Fase C (R&D):** `assisted_video` (image-to-video / animación de producto) como BETA medido, con `byo_endpoint`.

## 7. Datos del research (mediados 2026 — fuentes primarias; verificación adversarial NO completada por rate-limit, confirmar al integrar)

**Imagen (estilizado de producto, fiel):** FLUX.1 Kontext pro $0.04/img (fal.ai) · Seedream v4.5 Edit $0.04/img (fal.ai) · Gemini 2.5 Flash "Nano Banana" $0.039 (batch $0.0195) · FLUX 2 $0.015–0.05. Los tres top preservan el sujeto y re-estilizan solo la escena.
**Video (15–30s):** Runway Gen-4 Turbo $0.05/s ($0.75–1.50) · Veo 3 Fast $0.10–0.12/s · Kling 3.0 $0.075–0.10/s (mejor consistencia) · Veo 3 Standard $0.40/s ($6–12) · Sora 2 $0.10–0.50/s **(deprecado sep-2026 + rechaza caras)**.
**Lectura honesta de video:** production-ready para clips cortos de social (5–15s, máx ~30s); arriba pierde consistencia; image-to-video muestra movimiento antinatural / deriva de personaje. **BETA para marketing.**
**Pricing/pass-through:** cost-plus medido (Stripe Billing) + BYOK validados como patrones estándar.

## 8. Cruce con specs + pendientes

- **Módulo C (`spec_Admin_Cost_Intelligence.md`)** es el dueño de la vista admin: billing (Stripe, item #8), ledger de créditos + perfiles de pago (#9) — todos marcados "falta". Esta propuesta define el **lado de cara al usuario** que el Módulo C administrará. **No duplicar:** el ledger y el cobro viven en Módulo C; aquí viven los **modos, capacidades, wrapper, biblioteca y precio-por-modo**.
- **`spec_Phase_2`:** añadir `production_mode` por derivado en la atomización (2.4) + un candado de "producibilidad" (cada pieza vs capacidad del usuario → degradar/soportar/sustituir, nunca dejar trabado).
- **`spec_Phase_3`:** ejecutar respetando el modo (notificación con la guía/asset adentro, no solo el copy).

## 9. Decisiones abiertas (para sesión dedicada)
- ¿Qué endpoint de imagen integrar primero (Kontext vs Seedream vs Nano Banana)? — spot-test de calidad con un producto real.
- ¿N gratis = cuántas, por tier o global? ¿Créditos unificados (imagen+video) o por tipo?
- Política de retención de la biblioteca (storage) y si se pasa el costo a escala.
- ¿Avatares de persona (HeyGen-style) en alcance, con disclaimer, o fuera por ahora?
