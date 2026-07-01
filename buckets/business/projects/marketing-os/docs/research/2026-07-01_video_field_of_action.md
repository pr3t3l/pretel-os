# Papandi — El campo de acción de VIDEO (reels)

**Fecha:** 2026-07-01 · **Método:** workflow multi-agente (4 frentes: generadores de video IA, reglas de plataformas, qué retiene, pipelines de ensamble → crítica adversarial → síntesis). Precios verificados en fal.ai salvo marca contraria; fuentes inline.

> Hallazgos crudos + crítica completa en `2026-07-01_video_raw_findings.json`.

---

# EL CAMPO DE ACCIÓN DE VIDEO
**Reporte de decisión — Papandi / Producción (Motor de Coherencia) — 2026-07-01**
Basado en 4 streams de research (generadores, reglas de plataforma, qué retiene, pipelines reales) + crítica adversarial. Precios verificados en fal.ai salvo marca contraria. Donde los streams se contradicen, se dice explícitamente.

---

## 1. La matriz del campo de acción

| Eje | Lo que hay (jul-2026) | Fuente clave |
|---|---|---|
| **Qué PUEDEN los generadores** | Clips de 3–15s máx por generación (Veo 8s; nada GA pasa de 15s) → **un reel ES una composición de 3–8 clips**. 9:16 nativo (en Kling i2v lo fija la imagen inicial). Audio nativo con lipsync solo EN/ZH (Kling $0.168/s, Wan $0.10/s, Seedance $0.30/s, Veo $0.40/s); **español nativo no existe en los baratos**. Consistencia vía referencias: Seedance hasta 9 imágenes + 3 videos; Veo 3 imágenes; Kling "elements"; Wan clona apariencia+voz desde video de 3–8s. Rango de precio 13x: $0.03/s (Ray 540p draft) a $0.40/s (Veo con audio). **No pueden:** rostros de personas reales (Veo lo bloquea; el resto es territorio consentimiento/deepfake), yield garantizado, clips >15s. | [fal.ai/pricing](https://fal.ai/pricing), [fal.ai/veo3.1](https://fal.ai/models/fal-ai/veo3.1), [fal.ai/seedance-2.0](https://fal.ai/seedance-2.0), [fal.ai/wan-2.6](https://fal.ai/wan-2.6) |
| **Qué PERMITEN las plataformas** | 9:16 1080×1920 HD (low-res se deprioriza). Recomendación viva hasta ~90s; techo 3 min (IG deja de recomendar; YouTube saca de Shorts — oficial). IA permitida **con etiqueta**: obligatoria si es realista (TikTok oficial), auto-label C2PA no removible, y las 3 grandes declaran oficialmente que el label **no castiga reach**. Música de negocio: solo catálogos comerciales (TikTok CML — oficial) o licencia propia; Content ID bloquea Shorts >1min globalmente. Cero watermarks ajenos (supresión oficial IG + TikTok). | [TikTok CML](https://support.tiktok.com/en/business-and-creator/creator-and-business-accounts/commercial-use-of-music-on-tiktok), [TikTok AIGC](https://support.tiktok.com/en/using-tiktok/creating-videos/ai-generated-content), [YouTube](https://support.google.com/youtube/answer/14328491), [IG originality](https://creators.instagram.com/blog/recommendations-and-originality) |
| **Qué RETIENE al humano** | Gancho como **TEXTO en el frame 1** (0–3s deciden — doctrina oficial TikTok; valida §2.7). Diseño mute-first: captions quemados (+12% watch time, dato interno FB). Sweet spot 15–35s. **Cara real para confianza:** 78% confía más en personas reales; 36% baja percepción de marca si detecta IA; gestos robóticos = delator #1 (Animoto 2026, n=460). Producto EN pantalla: +65% brand affinity (TikTok oficial). UGC-crudo gana top-funnel; pulido convierte bottom-funnel. Cadencia sostenible: 3–5/semana. | [TikTok creative](https://ads.tiktok.com/help/article/creative-best-practices), [Animoto 2026](https://www.businesswire.com/news/home/20260121875037/en/), [Buffer](https://buffer.com/resources/social-media-frequency-guide/) |

**La intersección — el espacio real de juego de Papandi:**

> Reels 9:16 de **15–35s** (techo duro 90s), compuestos de **3–5 clips IA de escena/producto/atmósfera — nunca de rostro** —, con la **cara real del dueño reservada a los formatos de confianza**, gancho como **texto-overlay en la banda central segura**, **captions quemados**, música **añadida al publicar desde el catálogo comercial de la plataforma**, y **label de IA activado** (no penaliza y evita remoción).

Fuera del campo: clips >15s en una pasada (Seedance 2.5 con 30s nativos está en beta enterprise — vigilar, no prometer), talking head sintético del founder, diálogo en español con lipsync barato, y Sora (API muere 24-sep-2026 según [dos fuentes terciarias](https://www.mindstudio.ai/blog/openai-shutting-down-sora-what-happened) — pendiente ancla oficial de OpenAI, pero nadie construye sobre un moribundo).

---

## 2. Restricciones NO negociables

Ordenadas por severidad de la consecuencia:

1. **Música (riesgo legal #1 del solopreneur business).** El audio trending general NO está licenciado para cuentas de negocio: solo TikTok CML / Meta Sound Collection / licencia propia (oficial TikTok; Meta por anclar). Un Short >1min con claim de Content ID queda **bloqueado globalmente** (oficial YouTube). Consecuencia de producto: **Papandi nunca promete un track comercial ni renderiza música dentro del archivo final** — la música se añade in-app al publicar, desde el catálogo comercial.
2. **Etiquetado IA.** TikTok obliga a etiquetar AIGC realista; el auto-label por C2PA no se puede quitar; no etiquetar = remoción posible (oficial). Las 3 plataformas declaran que el label no reduce distribución. Regla: **etiquetar proactivamente siempre; jamás vender "sin label" como feature**. Pendiente de test: si los archivos de fal traen C2PA y si un re-render lo destruye — hasta entonces, el disclosure es instrucción manual en el checklist.
3. **Watermarks.** Watermark visible de otra plataforma o herramienta = supresión de recomendaciones (oficial IG) e inelegible para For You (oficial TikTok). Export siempre limpio; ojo con el free tier de JSON2Video (lleva watermark).
4. **Zonas seguras del texto.** Regla conservadora multi-plataforma sobre canvas 1080×1920: nada crítico en ~14% superior (~270px), ~25% inferior (~480px), ~13% derecho (~140px). Son mediciones de terceros que cambian con la UI: **configuración versionada** (tabla `platform_rules`), no constantes en prompts.
5. **Duraciones.** Master único 9:16: objetivo 15–35s, techo 90s, nunca >3min. 16:9 jamás clasifica como Short (oficial YouTube).
6. **Resolución.** Export 1080p+; low-res se deprioriza. **Conflicto abierto:** el cost model barato es a 720p — falta decidir 1080p nativo vs 720p+upscaler (costo del upscaler: sin investigar).
7. **Rostros reales sintéticos.** Veo los bloquea outright (más SynthID invisible en todo output). Clonar cara/voz del cliente vía Wan reference-to-video es territorio consentimiento/deepfake y las plataformas exigen disclosure — **bloqueado hasta leer ToS y diseñar flujo de consentimiento**.
8. **UX asíncrona.** Renders de 1–5 min y Kling con concurrencia 1 por usuario en fal: cola con polling, nunca síncrono. Con token compartido (ledger sandia), un cliente rendereando puede bloquear a los demás — diseñar la cola desde el día 1.

---

## 3. Formatos ganadores para el solopreneur — y qué puede producir la IA hoy (honesto)

| # | Formato | ¿Funciona? (evidencia) | ¿La IA lo produce publicable HOY? |
|---|---|---|---|
| 1 | **Talking head real del founder** | El activo de conversión más fuerte: confianza, parasocial (78% confía más en personas reales) | **NO — y no debe.** 36% de castigo de marca al detectar IA; gestos robóticos y voz = delatores #1 y #2. Rol de la IA: guion por intervalos + teleprompter + captions + b-roll de apoyo. **El usuario graba su cara con el teléfono.** |
| 2 | **B-roll educacional + VO + captions (faceless)** | Validado como lane de volumen/educación; el algoritmo no discrimina faceless | **SÍ — el lane publicable hoy.** Clips i2v (Wan/Kling) + VO ElevenLabs ($0.02–0.05/reel) + captions. Caveat honesto: no existe medición neutral de reach de b-roll IA vs stock/real — es la apuesta central sin dato, medir con las cuentas reales. |
| 3 | **Producto en pantalla (demo/showcase)** | +65% brand affinity, +25% recall (oficial TikTok) | **SÍ con red de seguridad:** foto REAL del producto como start frame i2v, movimientos cortos. Los generadores alucinan features (queja documentada en Icon.com) — nunca t2v puro del producto. |
| 4 | **Escena narrativa/atmosférica con diálogo** | Útil para "despertar" (educar al dormido) | **BORDERLINE.** En inglés sí: Kling audio $0.168/s, Seedance multi-shot, Veo premium. **En español NO hay lipsync nativo barato** (Kling auto-traduce a inglés; Wan es ZH/EN) — la ruta es VO ElevenLabs sobre b-roll sin bocas visibles. |
| 5 | **UGC-crudo / testimonio** | CTR 2–4x top-funnel (agregado de agencias, direccional) | **NO.** La gracia del formato es la autenticidad; fingirla con IA es exactamente la zona roja del consumidor. Humano o nada. |
| 6 | **Avatar sintético del founder** | — | **NO por default.** El research trae dos direcciones (Hedra/Wan lo permiten vs. 36% de castigo medido); este reporte la resuelve: el lane no existe en V1. Ver Decisión 1. |

**Traducción de producto:** la IA de Papandi produce los formatos 2, 3 y 4-sin-diálogo con calidad publicable hoy; asiste (pero no reemplaza al humano) en 1 y 5. Un plan semanal coherente de 3–5 piezas mezcla ambos mundos — y eso es defendible con datos ([Buffer](https://buffer.com/resources/social-media-frequency-guide/): +12–17% reach/views vs 1–2/semana).

---

## 4. VEREDICTO: (c) HÍBRIDO a→b — con (a) como V1 y (b) solo como "primer corte" opt-in

**El paquete es el producto; el ensamble server-side es un accesorio posterior, nunca el default.**

Razonamiento con evidencia:

1. **El costo NO es el diferenciador — la confianza sí.** El ensamble por API cuesta $0.17–0.35/reel (JSON2Video/Shotstack, verificado) sobre $2.5–8 de clips: <10% del costo total. Elegir (a) vs (b) no es una decisión de margen; es de posicionamiento.
2. **El "reel terminado" es la promesa rota de la competencia.** Creatify, Icon y Predis venden terminado y sus reviews convergen en la misma queja: *pagan terminado, reciben borrador opaco que igual editan* (lip-sync pobre, re-renders que queman créditos, 1 de 3 intentos usable). Papandi no gana siendo un Creatify más pobre; gana vendiendo exactamente lo contrario: **paquete verificable + borrador que TÚ terminas en CapCut en 10–15 min** — la debilidad convertida en promesa glass-box.
3. **La música mata la ruta (b) como default.** Un reel terminado server-side no puede incluir legalmente la música que el algoritmo premia (catálogos comerciales viven DENTRO de las plataformas). La ruta CapCut/in-app resuelve la licencia gratis y sin riesgo: el usuario añade el track del catálogo al publicar. El terminado saldría mudo de fondo o con costo de licencia extra sin resolver.
4. **Glass-box y C17.** El entregable accionable es "el prompt exacto que pegas" y "el paso exacto que das" — el paquete ES eso. Un MP4 caja-negra viola la doctrina que el research de mercado validó como moat (el mercado rechaza lo no-verificable).
5. **El yield sin medir hace peligroso el server-side.** Nadie midió tasa de reintentos por modelo (la crítica lo marca como el número que más mueve el presupuesto). En modo paquete, el usuario regenera solo el clip fallido con presupuesto visible; en modo terminado, los reintentos se esconden y se comen `MEDIA_BUDGET_USD=20` sin que nadie firme el gasto.
6. **WTP desconocido (Fase 0 pendiente).** Con costo real $2.5–8/reel y precio al usuario sin validar, comprometerse a entregar terminados es fijar el COGS antes de conocer el ingreso.

**Costo por reel por ruta (25s final, ~22s de footage, 4 clips; reconciliando la contradicción $1.50 vs $3–6 vs $6–13):**

| Ruta | Corrida limpia | Con reintentos ×2 (realista) | Trabajo del usuario |
|---|---|---|---|
| (a0) Paquete sin clips (prompts por clip + VO + SRT + guía) | **<$0.40** (VO $0.05 + start frames $0.10–0.20 + LLM) | n/a | 30–60 min (genera clips en su herramienta + ensambla) |
| (a) Paquete con clips Wan 2.6 720p | $2.50 | **~$4.50–5** | 10–20 min (CapCut: orden, música, export) |
| (a) Paquete con clips Kling 3.0 audio | $3.90 | **~$7.50** | 10–20 min |
| (b) + primer corte server-side | +$0.17–0.35 | +$0.17–0.35 por re-render | ~0 min, cero control fino, sin música |
| Premium Veo 3.1 audio (opt-in explícito) | $9 | **$17–27** | — |

El "$1.50/reel" de un stream era corrida limpia a precios de modelos ya superados; el "$3–6" del otro usaba Kling 2.5/Wan 2.5. A catálogo vigente y con reintentos: **presupuestar $4.50–7.50 por reel con clips**. Con el tope de $20: 3–4 reels Wan, 2 Kling, 1 Veo.

**Secuencia:** V1 = paquete con VO real incluido (ElevenLabs cuesta centavos y es la mejora de mayor valor percibido por dólar). V1.5 = clips generados vía gateway con presupuesto visible por clip. V2 = "primer corte" opt-in que **siempre entrega también los assets sueltos**.

---

## 5. El pipeline V1 concreto (sobre lo que ya existe en sandia-marketing)

Piezas reales ya en el repo: gateway con router anti-lock-in (`lib/gateway/{registry,routing,fal,replicate}.ts` — video hoy en mock, "6.2b: Veo/Seedance/Kling" ya previsto en el comentario de `routing.ts`), ledger (`lib/api/server/media-ledger.ts` + `MEDIA_BUDGET_USD`), StyleID (`lib/estudio/visual-identity.ts`), design_spec canónico de pieza v2 (migración `20260630180000_estudio_pieza_v2_design_spec.sql`), capa de overlay (`components/estudio/overlay-composer.tsx`), guion por intervalos.

**Pasos del pipeline:**

1. **Brief → guion por intervalos** (existe), con campos nuevos: `hook_text_overlay` (≤8 palabras, campo de primera clase — validado por evidencia sound-off), diálogo/VO por intervalo, duración objetivo 15–35s, CTA única, validación automática de densidad 5–10 palabras/s (cifra oficial TikTok).
2. **StyleID → start frames 9:16** — el eslabón que la crítica marcó ausente y que el repo YA precia: `routeImageModel()` enruta FLUX.1 [dev] ($0.025/img) y FLUX Kontext ($0.04/img, ~92% identidad) — 4–6 frames por reel = **$0.10–0.24**. Producto: foto real como frame inicial (anti-alucinación). Esto además fija el 9:16 en Kling i2v.
3. **Prompts de video POR CLIP y POR MODELO** (dialectos: comillas dobles para diálogo en Seedance; ingredients ≤3 en Veo; start-frame en Kling; ≤2.000 chars en Wan). Este artefacto es entregable glass-box **aunque el usuario no genere con nosotros** — C17 puro.
4. **Generación vía gateway** — `routeVideoModel()` nuevo junto a `routeImageModel()`, `falHandles("video")`, cola asíncrona con polling. Tabla de enrutamiento:

| Escena (intención) | Modelo default | $/s (fal, verificado) | Notas |
|---|---|---|---|
| Draft/preview | Ray 3.2 540p o Wan Flash | $0.03–0.05 | Nunca entregable final |
| B-roll producto (i2v desde foto real) | **Wan 2.6** | $0.10 (720p) / $0.15 (1080p) | Provisional hasta bake-off |
| Escena ambiente sin diálogo | Wan 2.6 / Kling 3.0 | $0.10–0.112 | Contradicción de precio Kling 2.5 vs 3.0 sin resolver — re-verificar |
| Diálogo hablado EN (lipsync) | Kling 3.0 audio | $0.168 | Alternativa: Seedance $0.3034 solo si multi-shot reduce nº de clips (cálculo pendiente) |
| Diálogo/VO en ESPAÑOL | **VO ElevenLabs sobre b-roll** | $0.02–0.05/reel | No hay lipsync ES nativo barato — restricción de diseño, no bug |
| Coherencia multi-clip (personaje/mascota) | Seedance refs (9 imgs) / Kling elements / Kontext frames | — | StyleID → imágenes de referencia |
| Talking head founder | **No se genera.** Guion + teleprompter | $0 | Hedra/Wan ref-to-video: lane condicional, bloqueado por Decisión 1 |
| Premium opt-in | Veo 3.1 audio | $0.40 | Con presupuesto visible y firma del usuario |

5. **VO** ElevenLabs desde el guion por intervalos ($0.05–0.10/1k chars, verificado).
6. **Captions**: Whisper word-timestamps → SRT ($0.006/min) para el paquete; CapCut auto-captions como alternativa gratis.
7. **Overlay** (existe: `overlay-composer.tsx`): hook en banda central del layout-contract; safe zones desde config versionada.
8. **Guía de ensamble CapCut** (checklist ordenado: importar → ordenar clips → VO → captions → música del catálogo comercial → export 1080p limpio) + **checklist de publicación** (label IA ON, sin watermark, HD, hook visible en frame 1).
9. **Ledger**: cada clip/imagen/VO como fila en `project_api_calls` con `project_id`, gate en `MEDIA_BUDGET_USD`.

**Qué falta construir (en orden):** campos nuevos del guion (hook_text_overlay + diálogo por intervalo) → generador de start-frames desde StyleID → traductor de prompts por dialecto → tabla `platform_rules` versionada → `routeVideoModel()` + cola asíncrona + yield-ledger (intentos vs usables por modelo, alimenta el bake-off continuo) → integración ElevenLabs + Whisper → plantilla de guía CapCut. El primer bloque (hasta el traductor de prompts) no gasta un dólar de generación y ya sube el valor del entregable.

---

## 6. Riesgos y preguntas abiertas (de la crítica)

**P0 — bloquean conectar generación:**
- **ToS comerciales de Kling (Kuaishou), Wan (Alibaba), Seedance (ByteDance) y fal como intermediario:** derecho a reventa del output a clientes de un SaaS, titularidad, política de likeness real. Nadie los leyó. Riesgo legal directo.
- **Yield por modelo sin medir:** el multiplicador que más mueve el costo (¿1 usable de 2 o de 4?). Sin bake-off, la tabla de enrutamiento es una hipótesis.
- **Contradicción de precios Kling** ($0.029/$0.07/$0.112 según fuente/versión) y cost model construido sobre modelos superados: re-verificar en fal.ai el mismo día que se cablee. Ningún precio de este reporte tiene más de ~6 meses de vida útil (lección Sora).

**P1 — deciden calidad/margen:**
- 1080p nativo vs 720p+upscaler (y el costo del upscaler, sin investigar) — las plataformas exigen HD.
- C2PA end-to-end: ¿fal emite metadata? ¿el re-render la destruye? Define si el disclosure es automático o manual.
- WTP (Fase 0, el hueco maestro): sin precio validado, la elección Wan vs Kling vs Veo es prematura.
- Cero evidencia de reach de b-roll IA vs stock/real — medir con las primeras cuentas reales.
- Replicate nunca se cotizó contra fal para los mismos modelos; "fal/Replicate" se afirma equivalente sin datos.

**P2 — vigilancia:**
- Seedance 2.5 (30s nativos, 50 refs) llegando a fal ~julio: colapsaría el multi-clip a una generación — **diseñar el motor agnóstico al número de clips** y re-evaluar al aparecer en catálogo, no antes.
- Disclosure y percepción: plataformas dicen "sin castigo" (oficial), pero NIM encontró evaluación más crítica del contenido etiquetado vs IAB que ve neutral-positivo en jóvenes. No hard-codear postura; es contexto para el usuario.
- 4 reglas de plataforma sin ancla oficial (20 min de subida IG, FB video=Reel, safe zone unificada Meta mar-2026, Meta Sound Collection para business): verificar antes de codificar como regla dura.
- Confirmar shutdown de Sora en fuente oficial de OpenAI antes de purgar specs (hoy: dos blogs).
- Español: si el mercado primario es US/English (estrategia Papandi), el gap de lipsync ES es menor — pero documentarlo antes de que un usuario hispano lo descubra solo.

---

## LAS 3 DECISIONES DE VIDEO QUE DEBES TOMAR

**1. ¿Existe el lane de avatar sintético del founder? → NO en V1.**
El research trae dos direcciones incompatibles (Hedra/Wan lo habilitan; Animoto mide 36% de castigo de marca y gestos robóticos como delator #1). Resuélvelo hacia la evidencia del consumidor: **la cara del dueño la graba el dueño; la IA hace todo lo demás** (guion, teleprompter, b-roll, captions, overlay). Reabrir solo con: ToS leídos + flujo de consentimiento + evidencia de aceptación. Esto también elimina la dependencia de Hedra (API propia, créditos por suscripción — mal encaje con tu ledger).

**2. ¿Paquete, terminado o híbrido? → Híbrido a→b, con el paquete como producto y el terminado como accesorio.**
V1 = paquete CapCut-ready con VO real incluido (hook_text_overlay + prompts por clip/modelo + VO ElevenLabs + SRT + guía de ensamble + checklist de publicación). El "primer corte" server-side entra después, opt-in, siempre con los assets sueltos. La música sola justifica la decisión: el terminado no puede incluir legalmente el track que el algoritmo premia; el ensamble in-app sí. Y el terminado-caja-negra es exactamente la queja que genera tu competencia — no la heredes.

**3. ¿Qué modelo default y a qué resolución? → No se puede decidir con estos datos: corre el bake-off antes de sellar `routeVideoModel()`.**
$10–15 dentro de `MEDIA_BUDGET_USD`: mismo brief de 3 clips (b-roll producto i2v, escena ambiente, movimiento de cámara) en Kling 3.0, Wan 2.6 y Seedance 2.0 vía fal; medir yield (usables/intentos), latencia, adherencia al StyleID, y 720p+upscale vs 1080p nativo. Ese experimento convierte precio-por-segundo en **costo por clip usable** — el único número que importa — y resuelve de paso la contradicción de precios de Kling. Default provisional mientras tanto: Wan 2.6. Prerrequisito legal del mismo sprint: leer los ToS comerciales de los 3 finalistas.

---
*Rutas del repo citadas: `lib/gateway/routing.ts` (tabla de enrutamiento + precios FLUX/Kontext ya vigentes), `lib/gateway/registry.ts` (video en mock hasta 6.2b), `lib/api/server/media-ledger.ts`, `lib/estudio/visual-identity.ts` (StyleID), `components/estudio/overlay-composer.tsx`, `supabase/migrations/20260630180000_estudio_pieza_v2_design_spec.sql` — en `C:\Users\prett\Documents\sandia-marketing`.*