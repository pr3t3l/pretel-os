# 00 · CONTEXTO MAESTRO — Video, imágenes y contenido (Papandi)

> **Qué es este archivo.** El punto único de re-hidratación de contexto. Leerlo COMPLETO = recuperar todo lo
> que sabemos sobre producción de video/imagen/contenido en Papandi: la doctrina investigada, el método
> AvatarHype (curso), la realidad técnica verificada de las APIs, el estado real del código, y las decisiones
> vigentes. Reemplaza la relectura de los archivos fuente (mapa en §11). Si este doc contradice a otro doc
> más viejo, **gana este**; si el operador contradice a este doc, se actualiza este doc.
>
> Escrito 2026-07-12. Fuentes: todo `docs/research/`, `specs/AvatarHype Classes/`, el código vivo de
> `sandia-marketing`, y verificación web de APIs (fal) del 2026-07-12.

---

## §1 · El sistema HOY (qué está construido y funcionando en sandia-marketing)

**El producto:** Papandi, co-pilot de marketing. El usuario firma fases 0-2 (negocio 0.1, demanda 0.2,
avatares 0.3, oferta 1.4, voz 2.0, identidad visual 2.0.5, journey 2.2, pilares 2.3, ángulos/ganchos 2.5).
Producción vive en **/angulos**: la **pieza = ángulo (gancho firmado) × canal**. Módulos hermanos:
/campanas (campañas con concepto/oferta/fases/cast_override), /agenda (calendario, scheduled_posts),
/identidad (cast: personajes + sets + voz).

**Pipeline de una pieza de video (v1 — el actual):**
1. **Develop** (1 llamada LLM, `buildDevelopSystem`): capas = pilar + idea planificada + ángulo SAGRADO +
   apertura aprobada verbatim (`hookFilled`) + audiencia estructurada + personaje/voz + journey (2.2) +
   contexto temporal (radar, fecha ancla) + voz de marca + keywords + **ESENCIA (0.1)** + **OFERTA (1.4)**
   + diferenciador + **campaña (CM4: concepto/fase/oferta+deadline)** + candados C4/C12/C1 + instrucción
   por tipo + **G1 videoPrefs** + gancho visual + identidad visual. Salida: guion por clips `[CLIP N — X-Ys]`
   + `design_spec` (`video_prompts[]` uno por clip, `clip_narrations[]` narración exacta, `hook_text_overlay`)
   + tips + QA glass-box.
2. **Cast**: biblioteca N personajes (con `voz`) + N sets; `aprobado` = listo para Kling; cascada
   **pieza > campaña (cast_override) > default de marca**. El gate de video es POR-PIEZA (el override
   aprobado de una campaña desbloquea aunque el default no esté aprobado). Sin personaje aprobado NO se
   genera (evita texto-a-video = cara aleatoria).
3. **Generación** (cola async de fal, `video-generate` → `video-status`): Kling 3.0 Pro image-to-video con
   `start_image_url` = retrato del personaje + `elements.frontal_image_url` (identidad) +
   `reference_image_urls` = set. Presupuesto validado ANTES (`MEDIA_BUDGET_USD`=20/mes), anti doble-click,
   cada generación es una VARIANTE (nada se pisa).
4. **G2 post-producción** (todo fal, misma llave/cola): `video-align` (whisper `chunk_level=word` → timestamps
   POR PALABRA; EN) → `captions.ts` (beats 1-3 palabras, karaoke `.srt`/`.ass`) → `caption-png.ts` (PNGs
   client-side $0, gancho bajo el 14%) → `video-compose` (ffmpeg-api: concat en orden + overlays por
   keyframes) → re-host durable del reel (brand-assets, mp4). UI: `ReelAssembler` (① Armar ② Captions).
5. **Música: JAMÁS quemada** (legal #1) — se añade al publicar desde el catálogo de la plataforma + label IA ON.

**Doctrinas de guion vigentes (en `developTypeInstruction` caso video):** 15-35s techo (G1 lo parametriza),
clips 4-10s, movimiento obligatorio (nada de sujeto quieto), cámara con golpe (prohibido slow push-in),
micro-evento a mitad de clips >4s, la cara comunica antes de hablar, primer frame apilado (máx 3 elementos),
safe zones 14%/35%, CTA de esencia, **ARCO QUE VENDE** (ver §10), **piso de voz continua** ~2-2.5
palabras/seg sostenido (guard determinista `clipWordBudget`: `over`=acelerado, `under`=silencio),
**i2v = la imagen es el ancla** (el prompt describe SOLO movimiento; PROHIBIDO re-describir apariencia
del personaje/set — re-describir le cambia la cara), narración del clip entre comillas DENTRO del prompt
(audio nativo), voz descrita idéntica por clip, texto JAMÁS renderizado por el generador (capa editor).

**EN-FIRST:** el mercado primario es US/inglés. El lip-sync nativo de Kling funciona en EN (el hueco era
español). Ángulos/keywords en inglés → la persona HABLA a cámara.

**LA PRUEBA REAL (2026-07-12) y su diagnóstico — lo que motiva v2:** el operador generó los 5 clips de
«Someone Else's Decision». Resultado: **los 5 clips arrancan desde el MISMO retrato** (así funciona v1:
misma foto = ancla de identidad por clip) → cinco tomas sueltas SIN continuidad entre sí, no se siente
fluido ni emotivo ni real. Además: guion sobrecargado (~120 palabras habladas en 28s ≈ 4.3 w/s; lo legible
es 2-2.5), y la campaña adjunta tenía `concept` de prueba ("test de saving") → cero tema en el guion.
**Conclusión:** falta la capa de CONTINUIDAD (keyframes encadenados primer/último frame) y más
participación del usuario en compuertas. Eso es exactamente lo que resuelve el método AvatarHype (§6) +
las APIs verificadas (§7).

---

## §2 · Doctrina de video corto 2026 (research verificado, julio 2026)

Tiers de evidencia: **[OFICIAL]** plataforma · **[ESTUDIO]** independiente · **[HERRAMIENTA]** blog con
data propia · **[PRÁCTICA]** consenso sin data.

**Captions:**
- El mute es el default: 85% del video en Facebook sin sonido (Meta), 92% de móviles en mute
  (Verizon+Publicis) [ESTUDIO]. Matiz TikTok: 88% dice que el sonido es vital [OFICIAL] → **diseñar para
  ambos mundos** (audio nativo que funciona solo + captions que sostienen el mute).
- Captions = retención: +80% más propensos a TERMINAR el video [ESTUDIO]; +12% view time (Facebook interno);
  ads con captions convierten 12.5% vs 6.9%; text boxes en 86% de los ads TikTok, +64% lift [OFICIAL vía 3º].
- **El estilo que retiene: karaoke palabra-a-palabra** (estilo Hormozi): ALL-CAPS, bold, blanco, 1-4 palabras
  por golpe, UNA resaltada (amarillo); punto de fijación nuevo cada 250-400ms vs 2-4s del subtítulo estático;
  +15-40% duración media reportada [HERRAMIENTA]. Legibilidad: máx ~5-10 palabras/seg en pantalla.
- **Safe zones (1080×1920): Meta OFICIAL = 14% superior, 35% inferior, 6% lados.** TikTok conservador:
  top ≥150px, bottom ≥480px, derecha ≥120px. Regla multiplataforma: karaoke en banda central (45-65% altura),
  hook en tercio superior BAJO el 14%, nada crítico en el 35% inferior.

**Ritmo:**
- Un corte/pattern-interrupt cada **2-4s**; la atención móvil cae tras **2.7s sin cambio** (Adobe 2025).
- 50-60% del abandono ocurre en los **primeros 3s**; meta retención media ≥70%.
- Cambios de escena frecuentes retienen +32% vs plano estático. Anti-sobreedición: el cambio debe ser
  MOTIVADO (acompaña la narración), no ruido.
- Duración óptima: TikTok viral 11-18s · Reels 7-15s (valor 30-45s) · Shorts 30-60s · 15-30s logra
  retención >80%. Matiz: >1min gana watch time total en TikTok narrativo bien paceado.

**El primer segundo:**
- 63% de los ads top comunican el mensaje clave en <3s [OFICIAL]; 90% del recall y 80% del awareness se
  capturan en los primeros 6s [OFICIAL/MediaScience].
- **Persona visible en <2s: +50% hooking power, +32% reconocimiento** [OFICIAL].
- Movimiento + texto overlay en <3s: +38% retención media. El acantilado del eye-tracking: 1.5-3.5s.
- Primer frame ideal APILA: persona con expresión fuerte + acción ya iniciada + texto de gancho + alto contraste.

**Otros multiplicadores:** B-roll/cutaways superan al estático (y esconden el corte) · punch-ins disimulan
cortes · **loop** (fin = inicio): "completar el loop es el indicador #1 de éxito en TikTok" (VP Vimeo), cada
vuelta cuenta como view — funciona si el contenido lo justifica (curiosity gap, acción circular) · CTA cards
+45% recall +19% likeability; verbos de acción > pasivos; en orgánico el CTA nativo (frase hablada + overlay).

**Qué genera la IA vs qué monta el editor:** los difusores NO renderizan texto fiable → cero texto en el
prompt de rodaje, componer en el editor. El karaoke es IMPOSIBLE en generación (sincronía por-palabra) —
siempre capa de edición. Vías programáticas: Creatomate/JSON2Video/Shotstack (render por JSON), Remotion
(code-first), WhisperX+FFmpeg (DIY, timestamps ±50ms), Submagic (SaaS). **Papandi ya lo resolvió con
fal whisper + PNGs + ffmpeg compose (§1.4).**

**El catálogo G1 (botones pre-develop, ya construido):** duración (micro 7-15 / estándar 15-30 / valor
30-45) · ritmo (rápido ~2s / normal 3-4 / respirado 5-6) · cámara (punch-ins / handheld / locked) · loop
(sí/no) · CTA (hablado+texto / solo texto / sin). Cada botón con tooltip glass-box de su dato. "" = Papandi decide.

---

## §3 · Doctrina por canal (destilado completo de `doctrina-por-canal.md`, v1 2026-07-06)

**Tesis:** el formato correcto por canal lo determinan señales OFICIALES de algoritmo + estudios de muestra
grande (Buffer 45M+, Socialinsider 35M/70M, Metricool 24.3M, van der Blom 1.3-1.8M, HubSpot 500M emails).
Cada canal cae en un **gate de media**: VIDEO duro · IMAGEN duro · SIN gate (texto-nativo) · intermedio.
Los ER de estudios distintos NO se comparan entre sí (metodologías distintas).

**Los 4 gates (implicación de producto):**
- **GATE VIDEO (duro):** Reel IG, TikTok video, YouTube Short — la pieza NO se genera sin kit (personaje
  aprobado + identidad visual). No hay fallback a texto.
- **GATE IMAGEN (duro):** pin Pinterest, carrusel, post de imagen, Story — exige identidad visual firmada;
  el texto overlay = capa del editor.
- **SIN GATE (texto-nativo, media default OFF):** email, Reddit, Grupos FB, X — la media RESTA o no suma;
  el develop NO emite image_prompts (`===SPEC=== = {}`).
- **INTERMEDIO (media ON, no bloqueante):** LinkedIn, blog — el texto compite pero el default lleva visual.

**Instagram:** Reels = ALCANCE (2.25× vs imagen, único formato con ER creciendo +24.76%), carrusel =
ENGAGEMENT/saves (9× más saves que imagen, ~4× interacciones), imagen única cae en picado (ER −45.98% YoY).
Señales de ranking (Mosseri oficial): watch time, **sends per reach** ("crea algo que quieran mandarle a un
amigo"), likes per reach. Posts con pregunta +36.7% comentarios; CTA de comentario +202.78%. Duración Reel
ideal 30-90s (límite 3 min; nuestro techo interno 15-35s manda). **Hashtags muertos para alcance** (≥1 ≈
−31.7% views; 0-5 solo por búsqueda) — el peso son keywords en caption. Castiga: watermarks de otras apps,
contenido reposteado (crackdown jul-2025/abr-2026). **Stories NO descubren** (Mosseri) — profundizan con los
que ya te siguen; replies +88% YoY; 1-3 frames + UN sticker interactivo. **Trial Reels** (dic-2024): Reel
solo para no-seguidores, a las 24h decides si va al grid — A/B nativo de ganchos.

**TikTok:** video domina alcance (5× views, 6× interacciones vs imagen); foto-carrusel concentra engagement
(+81% ER) pero no escala frío. **El FYP = 7 de cada 10 views**; follower count NO es factor (cada video
compite solo); completion/watch time = señal fuerte. 63% de top videos enganchan en ≤3s. **TikTok es
buscador: el ASR transcribe el audio y lo INDEXA — lo que DICES es keyword** → la narración debe DECIR las
keywords. Caption keyword-rich (~100 chars visibles) + 3-5 hashtags. Castiga (oficial, por escrito):
watermark de otra plataforma, clips ultra-cortos, imágenes estáticas de baja calidad, **engagement bait
explícito** ("tag a 3 amigos") — preguntas genuinas SÍ.

**Pinterest:** video pin gana engagement (+83%) pero **89% de los pins virales son ESTÁTICOS** y el estático
es el formato del click saliente — **el link ES el objetivo (único canal que lo premia); 3× más tráfico de
referencia que Twitter+LinkedIn juntos.** Formato oficial 2:3 (1000×1500). SEO del pin: título ≤100 chars
pero solo ~40 visibles (keyword en los primeros 30-35) · descripción 100-232 chars ≤5 keywords · alt text
(+25% impresiones, +123% outbound). Peso estimado: título 40% > descripción 30% > tablero 20% > texto-en-
imagen 10% > hashtags ~1%. **Fresh pins > repins** (imagen nueva = pin nuevo aunque repita URL; espaciar
3-7 días). **Half-life de un pin: 3.88 MESES** (vs ~19h IG, ~50min FB) — compounde como SEO.

**LinkedIn:** **carrusel-PDF (document post) #1 en engagement en los 4 datasets** (7.00% ER; 17× más
interacciones que imagen; ER mediano 21.77% = +196% vs video). Ranking: 1º carrusel-PDF · 2º imagen CON
personas (+50%) · 3º video · 4º texto puro (en declive; 0.42× en páginas de empresa). 1ª línea ES el post
(~210 chars desktop / ~140 móvil antes del "see more"; 60-70% nunca lo pulsa). Largo 800-1.500 chars;
preguntas +77% comentarios. **Hashtags degradados: 0-3** (sin hashtags rinde 5-10% mejor; >10 = −30-50%).
Link en cuerpo = −18.8% alcance ("primer comentario" ya no da ventaja). Golden hour: 60-90 min deciden;
1 guardado ≈ 5× un like; **máx 1 post/día** (diario = −26-45%/post). Post de empleado rinde 6-8× el de la
página. Newsletters LinkedIn saltan el feed (open 30-50%).

**Email:** **texto simple GANA en todo** (HubSpot 500M+): HTML con imágenes = −25% opens, −21% CTR; incluso
UNA imagen reduce clics; Gmail castiga densidad de imagen (→ Promotions). Estándar real = híbrido ligero con
apariencia personal. Asunto 30-50 chars (33 visibles) + preheader 40-90 que EXTIENDE el asunto + cuerpo
50-125 palabras (hasta ~200) + **UN solo CTA** + P.S. (hasta +20% CTR). Segmentar: +30% opens/+50% clics.
Botón CTA +45-127% vs link de texto (la excepción pro-imagen: ecommerce visual). `===SPEC=== = {}` CONFIRMADO.

**Blog/SEO:** era AI Overviews: CTR orgánico **−61%** en queries con AIO; posición #1 pierde −58%; **ser
citado DENTRO del AIO devuelve +35% clics** → respuesta directa quotable ARRIBA + profundidad debajo; Google
usa schema markup para features de IA. Largo: promedio real 1.333 palabras; long-form 1.500-2.500 = strong
results 2×; rango dual Papandi: 800-1.200 apoyo / 1.500-2.200 ancla. ≥1 imagen = 2× tráfico, +30% shares,
+25% backlinks (correlacional) — CUSTOM, nunca stock ("stock no penaliza pero no aporta" — Mueller).
Internal links con anchor exacto = 5× tráfico. **E-E-A-T/experiencia 1ª persona = EL diferenciador** (la IA
per se NO penaliza; *scaled content abuse* sí, mar-2024).

**Reddit:** self-post de TEXTO = formato nativo en subs de nicho; gana **experiencia operativa real con
números concretos y errores admitidos**; el marketing-speak se hunde; link post de marca muere
(AutoModerator filtra dominios). **Regla 9:1 OFICIAL** (reddiquette; subs estrictos de facto 99:1); karma
mínimo + edad de cuenta = umbral invisible (la cuenta se "calienta" semanas comentando). Título LARGO
específico (**18+ palabras** = mediana 2.570 upvotes vs ~1.590; 160-180 chars) + historia 1ª persona +
pregunta genuina + disclosure "I built this"; OP que responde rápido sube. **Reddit = autopista de Google:**
visibilidad +1.328% (2023-24), 2º dominio tras Wikipedia, **5.8M citas en AI Overviews** (más que ninguna
fuente) → el hilo rankea AÑOS.

**Grupos de Facebook:** la conversación ES el ranking (meaningful social interactions, 2018; grupos rankean
sobre páginas). **Link externo = el peor formato de la plataforma** (ER 0.05%, 4× menos que texto). Dentro
del grupo: texto-pregunta rey; historia personal 2-4 líneas → pregunta abierta; promo SOLO en promo-day;
aportar antes de pedir; tono par-a-par. Alcance de grupo ≈ 10× el de página.

**X:** **única plataforma grande donde el TEXTO PURO gana** (ER 3.56% > imagen 3.40% > video 2.96% > links
2.25%). El multiplicador real = Premium (~10× alcance mediano), no el formato. Señales del ranker (código
abierto): reply ≈ 13.5× un like; **reply contestada por el autor ≈ 150×**; bookmark +10; dwell 2+ min +10;
**>1 hashtag ≈ −40%**. Desde ene-2026 Grok lee cada post para el recomendador. Hook 1ª línea; 0-1 hashtags;
sin link en cuerpo (o con descripción rica); diseñado para provocar replies que el autor contesta.

**YouTube Shorts:** señal principal **"Viewed vs Swiped Away"** + engaged views; top Shorts mantienen 70-90%
viewed rate (<60% no despega). Mejor alcance en frío para cuentas chicas (1-5K: 2.600 views/Short vs 660
TikTok / 600 Reels). Banda fuerte 20-45s; **el loop es mecánica de ranking** (desde 31-mar-2025 cada replay
cuenta como view). Watermarks de otras plataformas = NO monetizable. El final debe fluir hacia el inicio.

**CTA nativo por canal:** IG=envíalo/guárdalo · TikTok=comenta/completa · Pinterest=click al link ·
LinkedIn=pregunta · Email=1 click · Blog=link interno/lead magnet · Reddit/Grupos=conversación · X=reply.

**Half-life como metadato de planificación:** Pinterest 3.88 meses y Blog/Reddit (años) = activos
compuestos; IG ~19h, FB ~50min = consumo inmediato.

**Correcciones pendientes detectadas por el doc** (contra `lib/estudio/prompts.ts`): ①Stories mapea a `text`
(bug — debe ser `image`) ②LinkedIn "3-5 hashtags" → 0-3 ③blog corto para SEO competitivo (ya corregido a
rango dual) ④`slideCapForChannel`: falta TikTok=10, LinkedIn=8 ⑤añadir a video TikTok "la narración DICE
las keywords" ⑥tipos `text` necesitan reglas por comunidad (ya existe `channelDoctrine`) ⑦Pinterest merece
campos SEO propios (título/descripción/alt) ⑧`cta_destination` por canal al ensamblador.

## §4 · Campañas de marketing real (destilado de `campanas-marketing-real.md` + módulo construido)

**Tesis:** una campaña es un **pico finito de alta intensidad y objetivo único MONTADO ENCIMA del plan
evergreen** (modelo por capas: always-on = base; campaña = pico). Mínimo viable solopreneur: ventana corta
con fecha + UN concepto (big idea) + oferta opcional + pocas piezas por fase en canales YA encendidos +
deadline real.

**Anatomía (convergencia de fuentes):**
- **Fases:** teaser → lanzamiento/pico → cierre (+día después). Calendario típico: día 0-6 hype/teasers ·
  día 7 LANZAMIENTO · día 8-14 post · día 15-30 integración. Mínimo viable 4 semanas (2 teaser + 1
  lanzamiento + 1 momentum); evento estacional = 1-2 semanas.
- **Jeff Walker (PLF):** 3 piezas de pre-launch de VALOR PURO en 7-10 días → carrito abre 5-7 días con
  deadline duro → **"el lanzamiento se gana en el CIERRE"** (el último día hasta 4 mensajes: mañana deadline,
  tarde historia, noche recordatorio, countdown 90 min).
- **Rampa de intensidad (BFCM email):** 4/sem → diario → 3-4 envíos el MISMO día pico; benchmark de
  temporada = +25% sobre volumen base. Extensión del día después ("HOURS LEFT" el 5 de julio).
- **Ratio dar:pedir DENTRO de campaña:** no desaparece, se REORDENA por fases (teaser da, pico/cierre piden);
  agregado del arco ~1:1 o 2:1; **el 3:1 firmado del proyecto se mide sobre el MES completo** (evergreen +
  campaña), no pieza a pieza dentro de la ventana.
- **La big idea en 3 dimensiones (caso 4 de Julio, Klaviyo):** VISUAL (banderas, rojo/blanco/azul, BBQ) ×
  VERBAL (subject lines del momento: "Best Dressed at the BBQ") × **OFERTA (la capa NUEVA que el evergreen
  no tiene:** código temático "FIREWORKS", last call día 5). Promos se publican el 2-3 de julio; **el día 4
  se reserva para contenido ligero/comunitario.** Campañas integradas con idea central: +64% KPIs de marca.
- **Herramientas líderes:** el espectro va de etiqueta+color (Buffer degradó "Campaigns" a "Tags" — el
  contenedor pesado sobraba para equipos chicos) a contenedor con fechas (HubSpot: fechas pintadas en el
  calendario; **un asset pertenece a UNA sola campaña**). Lo que sobrevive en todas: color en calendario,
  filtro, reporting del conjunto. `utm_campaign` = slug como convención transversal.

**El módulo construido (/campanas, CM1-CM5 en prod):** EVERGREEN es el default; tipos v1 = evento/estacional
y lanzamiento propio (NO "awareness" — eso ES el evergreen); 3 fases fijas; `campaign_id` cose
Ángulos+Media+Agenda; se ata EN la creación (inyección de concepto+oferta+fase al develop, CM4); auto-cierre
por ventana; **cast_override por campaña** (personaje/set temáticos con aprobación previa); plan por arco =
ángulo+fecha con generación auto-agendada; solo campañas ACTIVAS seleccionables; campaña POR-CANAL en las
tarjetas. La sección §3 del doc original (SQL/UI) está SUPERSEDED por `spec_Campanas.md`; §1-§2 siguen vigentes.

**Lección de la prueba 2026-07-12:** si `concept` es placeholder ("test de saving"), el guion no puede tejer
el tema — **el concepto es el HILO**; escribirlo bien importa más que cualquier otra config.

## §5 · Estrategia, mercado y el compilador (destilado de los docs de scope 2026-07-01 + ensamblador)

**Hallazgo maestro del research de mercado:** *el comprador no rechaza el contenido de IA; rechaza el que no
puede VERIFICAR.* (80% prefiere la versión CON fuentes; solo 7% confía más al ver "hecho con IA", 31% menos;
US: 50% prefiere marcas que EVITAN GenAI — Gartner 2026.) El enemigo no es la IA, es la in-verificabilidad →
**el moat es glass-box + brief verificable + StyleID.** "AI slop": 54% de estadounidenses reportan fatiga.
- Competencia/precios: Icon.com $39 ("AI CMO", cojea en ejecución) · Copy.ai $249+ (abandonó SMB) · Jasper
  $69-250 (text-only; 4.7 G2 vs 3.4 Trustpilot — el mercado masivo castiga complejidad/billing opaco) ·
  Canva $15 (ejecución, no cerebro). Ancla de mercado: $15-49/mes. El HUECO (hipótesis a validar): CEREBRO
  (estrategia+voz) + COHERENCIA multicanal + glass-box para SMB.
- **Producción = MOTOR DE COHERENCIA, no playground** (estado del arte: Coca-Cola + Adobe Fizzion "StyleID";
  "Designers Lead, AI Follows" — Papandi lo democratiza). Dos capas: CORE inmutable (logo, paleta, voz
  cuantificada 4 dimensiones NN/g, promesa, personaje) + EXPRESIÓN de campaña (gancho, imagen, copy, canal).
- **Mandatos UX no-negociables del research:** ①NUNCA cobrar créditos por regeneración (patrón más odiado)
  ②todo output EDITABLE (no PNG plano) ③brand kit EMPUJADO como guardrail. Briefs pobres desperdician 33%
  del presupuesto (IPA/BetterBriefs).
- **Routers:** fal.ai capa primaria (~985 endpoints, 30-80% más barato, cold start <1s) · Replicate fallback.
  Regla: ningún modelo >X% del valor; degradación con gracia; la tabla de enrutamiento es un activo vivo.

**Campo de acción de VIDEO (jul-2026):** clips de 3-15s máx por generación → un reel ES composición de 3-8
clips; audio nativo con lipsync solo EN/ZH (Kling $0.168/s · Wan $0.10/s · Seedance $0.30/s · Veo $0.40/s);
**español nativo no existe en los baratos** (por eso EN-first). Rango de precio 13×: $0.03/s (Ray draft) a
$0.40/s (Veo). Plataformas: IA permitida CON etiqueta (no castiga reach — declarado por las 3); música solo
de catálogos comerciales al publicar; cero watermarks ajenos. **Qué retiene al humano:** cara real para
confianza (78% confía más en personas reales; 36% baja percepción si detecta IA; gestos robóticos = delator
#1) · producto EN pantalla (+65% brand affinity, +25% recall — TikTok oficial) · UGC-crudo gana top-funnel,
pulido convierte bottom-funnel · cadencia sostenible 3-5/semana.
- **Mapa de formatos (¿la IA lo produce publicable hoy?):** talking head del founder real = NO y no debe
  (IA da guion+teleprompter) · b-roll educacional + VO + captions (faceless) = SÍ, el lane publicable ·
  producto en pantalla = SÍ con foto REAL como start frame (nunca t2v puro — alucina features) · escena
  narrativa con diálogo EN = borderline-SÍ · UGC-testimonio = humano o nada (v1) · avatar sintético del
  founder = NO en V1.
- Costo por reel (25s, 4 clips): paquete sin clips <$0.40 · Wan ~$4.50-5 con reintentos · Kling ~$7.50 ·
  Veo premium $17-27. Presupuesto vigente $4.50-7.50/reel. **Bake-off pendiente** ($10-15: mismo brief en
  Kling/Wan/Seedance; medir yield=usables/intentos, latencia, adherencia StyleID) antes de sellar el default.
- Riesgos abiertos P0: ToS comerciales de Kling/Wan/Seedance+fal sin leer; yield sin medir. P2: Seedance 2.5
  (30s nativos, 50 refs) llegando; Sora API sunset 24-sep-2026 (sin ancla oficial).

**El ensamblador (el compilador de Papandi):** Papandi es un **compilador de decisiones firmadas a media
publicable**: fases firmadas (código fuente, 409 duro sobre 2.0/2.3/2.5) → `buildBrief()` (IR-1, puro,
persiste con la pieza) → `buildDevelopSystem()` por tipo (blog|linkedin|email|carousel|video|image|text) →
PIEZA + design_spec (IR-2) → dialectos por motor (`serialize.ts` imagen / `video-routing.ts` video). Regla
de oro: doctrina/precios/duraciones NUNCA las decide el LLM. Orden del system (19 bloques, curva de
atención: primacía + recencia): rol → pilar → gancho verbatim → apertura aprobada → audiencia → personaje →
journey → temporal → voz → keywords → esencia → oferta → diferenciador → doctrina → TIPO → gancho visual →
identidad visual → reglas visuales → contrato de salida. El moat técnico = **la cadena de suministro de
contexto firmado**, no la llamada al LLM. Tesis: el ensamblador ES el producto SI la procedencia es visible
(UI) y hay loop de rendimiento (falta: few-shot de piezas aprobadas, medición por gancho/pieza).
**C17 (la inversión del modelo):** murió la atomización 2.4/derivados/rotación — pieza = ángulo × canal; el
operador ELIGE el ángulo; plan generativo infinito. Doctrina del molde C17.1: "el molde ENMARCA el ángulo,
NO lo comprime" (guardia determinista `keepsAngle` ≥0.45).

*(§3-§5: destilado completo; los docs originales guardan las fuentes citadas una a una. El índice maestro
de TODA la documentación es `specs/_INDEX.md` — 58 docs con leyenda de estado.)*

---

## §6 · El método AvatarHype (curso — 2026-07; fuente: `specs/AvatarHype Classes/`)

### 6.0 Filosofía
> "La IA sola no hace que un creativo parezca real. Lo que lo hace parecer real es: la situación específica,
> el comportamiento humano, el lenguaje natural, la imperfección controlada, la integración creíble del
> producto. **Si parece anuncio, está mal. Si parece contenido real, está bien.**"

### 6.1 Método 6C (prompts de IMAGEN consistentes)
C1 **Character** (quién: edad, identidad, rasgos) · C2 **Context** (dónde) · C3 **Camera** (cómo está tomada:
"iPhone dump photo, harsh direct flash, 35mm natural look") · C4 **Clothing** · C5 **Cinematic Light**
(atmósfera: "high contrast shadows, slight grain") · C6 **Clean Output/Consistency** ("No text, no watermark,
no distortion, not AI-generated look"). El **6C Engine** (agente): recibe idea O IMAGEN DE REFERENCIA →
la descompone en las 6C → UNA pregunta de confirmación → devuelve UN prompt en inglés listo para pegar.
Si pides cambiar UN elemento, mantiene todo lo demás idéntico.

### 6.2 El workflow del anuncio animado (8 pasos — el corazón del método)

> **⚠️ Qué es esta sección (aclaración 2026-07-12):** esto documenta FIELMENTE cómo el CURSO hace un anuncio
> **A MANO**, con sus herramientas sueltas: ChatGPT (los prompts numerados), **NotebookLM** (herramienta
> gratuita de Google de research: le cargas fuentes/artículos y responde SOLO con ellas — ellos la usan para
> sacar datos duros con cita), NanoBanana (imágenes) y Kling/Veo (video). **NO es nuestro diseño** — es la
> materia prima. En Papandi la mayoría de estos pasos YA EXISTEN automatizados:
>
> | Paso del curso (manual) | En Papandi (ya existe) |
> |---|---|
> | 1. Avatar hiper-específico | Fase 0.3 (avatares firmados con dolores/miedos/deseos) |
> | 1-2. Research de datos duros (NotebookLM) | Fase 0.2 (demanda/keywords DataForSEO) + esencia 0.1 — con C4: datos reales o marcados |
> | 3. Ángulos | Fase 2.5 (biblioteca de ángulos firmada) — el usuario ELIGE en /angulos |
> | 4. Guion | El develop (se enriquece con los 9 patrones para modo animado) |
> | 5-8. Storyboard → keyframes → auditoría → producto real | **LO NUEVO que adoptamos** → `spec_Estudio_Video_v2` |
>
> Lo que importa del método: la TÉCNICA de continuidad (keyframes primer/último frame encadenados) y el
> nivel de exigencia visual (plan visual, money shot, pares encadenables). El resto ya lo teníamos.
1. **Avatar + research** — input: producto (3-4 frases), mercado, ESTILO (Pixar 3D / Apple realista /
   Sci-fi / Claymation / Wes Anderson). Output: avatar HIPER-específico (3 dolores OBSERVABLES —
   "se despierta con la boca seca", no "duerme mal" —, lo que ya probó y por qué falló, el miedo profundo
   que no admite, lo que quiere SENTIR) + 3 búsquedas cortas para NotebookLM Discover Sources enfocadas a
   DATOS DUROS (①estadísticas/cifras del problema ②mecanismo biológico/científico ③evidencia
   histórica/evolutiva/comparativa). El anuncio vende DEMOSTRANDO con datos, no con emoción.
2. **NotebookLM** — sobre las fuentes cargadas: **5 insights atómicos** (específico + respaldado por dato
   duro LITERAL con referencia + contraintuitivo). Si un insight no tiene dato duro → se marca "NECESITA
   REFUERZO". Se ordenan por munición.
3. **Ángulos** — avatar + insights → **3 ángulos DISTINTOS**: titular en lenguaje del cliente, dolor atacado,
   reframe ("antes piensa X → después piensa Y"), insight base, **METÁFORA VISUAL CENTRAL dibujable**
   ("una columna que se ilumina en rojo donde duele" ✅; "la sensación de pesadez" ❌), por qué para el scroll.
4. **Guion (50-60s, 140-180 palabras) — LOS 9 PATRONES:**
   1. HOOK = **verdad MÁS GRANDE que el cliente** (historia/tiempo, biología con cifra, creencia colectiva
      rota, dato contraintuitivo). PROHIBIDO empezar con "Estás/Tu/Te/No sabes" (hablar del tú).
   2. DATO técnico con CIFRA concreta (nunca "mucho"; siempre "20%", "9.000 años").
   3. PREGUNTA reflexiva (la que el cliente se hace, no la que lanza el publicista).
   4. PUNTOS SUSPENSIVOS en 3-4 momentos ("Y, de alguna forma…") — el locutor piensa en alto.
   5. FRASE PUENTE al producto ("Por eso creamos…") — nunca corte abrupto.
   6. PRODUCTO por FUNCIÓN, cero adjetivos ("innovador" prohibido).
   7. BENEFICIOS en 3-4 frases telegráficas paralelas.
   8. **BISAGRA REFLEXIVA obligatoria** antes del cierre ("Y es curioso…") — sin esto suena a anuncio.
   9. CIERRE: vuelta poética al hook + invitación / conclusión filosófica / reflexión + invitación suave.
   Estructura con timing: HOOK 0-5s (~12 palabras) · DEVELOPMENT 5-18s (~35) · INSIGHT/REFRAME 18-30s (~35)
   · PRODUCTO 30-40s (~30) · BENEFICIOS 40-48s (~20) · BISAGRA+CIERRE 48-58s (~25). Auto-verificación con
   checklist ANTES de entregar. **TEST FINAL: si leído en voz alta suena a anuncio → mal; si suena a alguien
   contándotelo en una cena → bien.** Reglas brutales: cero exclamaciones, palabras prohibidas ("descubre",
   "revolucionario", "no creerás"), si una frase no aporta dato/mecanismo/reframe → se borra.
5. **Storyboard — PASO 0 obligatorio, el PLAN VISUAL:** ①metáfora visual en 2-3 escenas (1=desperdicio,
   todas=saturación) ②**MOMENTO ICÓNICO (money shot)** — LA imagen que si la ves fija en el feed te para;
   entre la escena 2 y 4 ③ARCO visual en una frase ("empieza íntimo → conceptual → vuelve real
   transformado") ④CONTRASTE de planos (mínimo: 1 wide, 2 close-ups, 1 macro, 1 cenital, 1 conceptual)
   ⑤1-2 escenas CONCEPTUALES (MODE A) simbólicas. Reglas: UNA escena = UNA idea visual (mejor 14 claras
   que 8 cargadas) · todo DIBUJABLE ("frunce el ceño, aprieta los puños" no "siente frustración") ·
   **escena = 4-6s (el clip Kling es de 5s)** · personaje/entorno IDÉNTICOS entre escenas · transiciones
   pensadas · la escena FINAL retoma la primera TRANSFORMADA (cierre circular). Cada escena declara:
   - **MODE de referencia: A** (sin referencia) / **B** (referencia de personaje) / **C** (referencia de
     entorno) / **D** (continuidad total),
   - **FRAME TYPE: SINGLE FRAME o START + END FRAMES** (start+end si hay movimiento significativo).
6. **Prompts de imagen (NanoBanana Pro)** — inglés 100%, **STYLE LOCK** de una frase ("Pixar 3D animation
   style"), un bloque de código por escena, formato etiquetado: [STYLE LOCK]/[SUBJECT]/[ACTION]/
   [ENVIRONMENT]/[LIGHTING]/[CAMERA]/[ASPECT 9:16]/[REFERENCE]/[EXCLUDE]. **La primera aparición del
   personaje lo describe A FONDO; las siguientes = "Use image from Scene X. Keep [X] identical. Change [Y]"**
   (cadena de edits = consistencia). NanoBanana NO hace bien: texto legible (→ se añade en el editor),
   >2 caras detalladas. SÍ hace bien: split screens, mecanismos internos estilizados, composiciones simétricas.
7. **Auditoría final "nivel cortometraje"** — referencias obligatorias: Piper, Bao, Inside Out, La Luna,
   Paperman, Coin Operated, Kiwi!, Apple Underdogs/Intention, Chipotle Back to the Start. Principios: la
   cámara es narrador; los objetos cotidianos se vuelven metáfora; close-ups brutales con textura; lo
   abstracto se materializa; **la luz cuenta la mitad de la historia**; hay UN momento icónico; el final
   cierra circular. Caza el pecado capital: **"infografía disfrazada"** (producto flotante en fondo neutro,
   gráficos con cifras). Y verifica lo crítico para producción: **¿cada PAR CONSECUTIVO de imágenes es
   visualmente ENCADENABLE?** (si escena 3 es dormitorio azul y escena 4 fondo blanco abstracto, el corte
   es inanimable — se añade escena puente). Entrega: guion definitivo + 2 variantes completas distintas +
   storyboard reconstruido + prompts finales.
8. **Producto real al final** — todo el trabajo se hace con placeholder; al final entra el producto REAL
   (nombre + 1 frase) y donde aparece físicamente: `[REFERENCE IMAGE]: insert real product photo here`
   (se adjunta la FOTO REAL al generar — la IA no inventa el producto).

**Transiciones por estilo (para animar ENTRE dos keyframes):** "Create a seamless [Pixar / Claymation /
sci-fi / Apple-style / Wes Anderson] transition between the first shot and the second shot… with sound
effects (no talking)". ← Así se genera el clip que une el keyframe A (start) con el B (end).

### 6.3 La técnica de CONTINUIDAD (lo que a Papandi v1 le falta)
**Primero las IMÁGENES, después el video.** Por cada escena se generan sus keyframes; el clip N se genera
con primer frame + último frame; **el ÚLTIMO frame del clip N ES el PRIMER frame del clip N+1** → continuidad
garantizada de punta a punta. Flujo de referencia del curso: buscar una referencia en TikTok/Pinterest →
screenshot → el 6C Engine la descompone → generar la persona/escena (persona NUEVA inventada — sin derechos
de imagen) → variantes de la misma persona para las tomas (edits encadenados). Trucos documentados:
- **El truco de los dientes:** generar una variante "closer view… you can see his teeth well" — con dientes
  visibles el modelo de video imagina bien la boca (mejor lip-sync) y de paso da la toma zoom-in siguiente.
- **Podcast:** "She/he is looking to the right/left side of the frame, as if talking to someone sitting next
  to her/him" + "Flip the image horizontally" para el contraplano. "Single speaker: only the person from the
  reference image talks."
- **Talking head estático:** "(static camera, no movement) he/she's looking directly at the camera, realistic
  arm movements, clear influencer tone: '[guion]'".
- Cambiar avatar conservando escena: "make this woman/man a different one, [descripción]"; trasplantar
  persona: "replace the guy from file 1 with the guy from file 2 wearing the same outfit…".

### 6.4 UGC Prompt Engine (reels que parecen grabados por gente real)
**Reglas fijas:** ①ANTI-AD: los primeros segundos no parecen anuncio ②**MICRO-MOMENTO** concreto, jamás
idea genérica ("chica en el baño ANTES DE SALIR mirándose la frente de cerca", no "chica hablando de una
crema") ③REALISMO: móvil en mano, micro-shake, framing imperfecto, UN reajuste de agarre ~seg 6, entorno
vivido, textura de piel real, cero estudio ④LENGUAJE del mercado REAL (para US: inglés natural
conversacional; el curso lo hacía para España) ⑤DURACIÓN 12-16s sin relleno ⑥VALOR: cada guion aporta
(observación, verdad incómoda, error común, mini revelación) — "se absorbe en nada y no te deja la cara
pringosa" ✅, "esto va genial" ❌ ⑦CTA suave opcional ("yo lo estoy usando y ya", "si te pasa, míratelo");
PROHIBIDO "cómpralo ya/haz click/link en bio" salvo pedido.
**Formato de trabajo:** 3 OPCIONES (concepto + micro-momento + ángulo + hook + guion + por qué funciona) →
el usuario ELIGE → guion final + notas de comportamiento + prompt EN en un bloque. *(= compuerta humana.)*
**Anatomía del prompt UGC** (de los 6 ejemplos de la biblioteca): captura ("hyper-realistic 9:16 iPhone 15 Pro
front-camera selfie video") + identidad CREÍBLE con imperfecciones (edad, "slightly receding hair, mild eye
bags", "natural skin texture visible pores") + entorno VIVIDO ("suburban driveway, parked work truck",
"slightly messy car interior") + cámara (micro-shake, one grip adjustment at ~6s, autofocus pulse) + luz
imperfecta + tono ("frustrated but helpful, like warning a friend") + **script con timing por segundos** +
behavior (empieza mid-thought, mira fuera de cámara, risita) + audio raw (mic del móvil, viento, respiración,
NO música) + STRICT REALISM RULES (no warping, no smoothing, anatomía estable) + **one continuous take,
no cuts, no captions**.
**Trucos de biblioteca:** street interview nocturno (entrevistador off-camera, "beat: she briefly looks down
at her hand as if referencing something not shown" → **EDIT HOOK: hueco de mano vacía a los 6-8s para
insertar el producto EN POST**) · scroll nocturno iluminado solo por la pantalla · cita/baño con urgencia
privada ("lowered voice, glances toward the door") · producto sacado del bolso "que ya estaba ahí".

### 6.5 Estructura VEO 3.1 (14 bloques — para UGC hiperrealista con referencia)
①formato ("hyper-realistic 9:16 handheld iPhone front-camera selfie video") ②identidad: **"The exact same
woman from the provided reference images. Identity, face, skin texture, hair, and outfit must match perfectly
at all times."** ③entorno (lugar+hora+luz+ambiente) ④UNA acción principal + UNA micro-acción (8s no es
para 5 acciones) ⑤**física humana DEFINIDA** ("slight vertical bounce, subtle side-to-side sway, natural
shoulder movement, inconsistent micro-movements, breathing that affects motion and speech" — "natural" sin
definir no vale) ⑥idioma/acento explícito ⑦tono emocional ("calm, reflective… not performing and not
selling") ⑧script corto con pausas reales ⑨behavior (empieza mid-thought, parpadea, mira fuera, se
recoloca) ⑩cámara (handheld, off-center, autofocus shifts, rolling shutter, no stabilization) ⑪luz
(natural, cambios de exposición) ⑫audio (raw mic, viento, respiración, NO música) ⑬**negative prompt**
("studio lighting, beauty filter, perfect skin, ad-like polish, robotic delivery…") ⑭**START FRAME / END
FRAME**: "START FRAME matches the first reference image… END FRAME matches the second reference image…"
(Veo soporta primer+último frame para guiar la transición).

### 6.6 Copywriter de guiones cortos (agente del curso)
3 formatos: **Podcast** (2 personas: pregunta natural → recomendación → OBJECIÓN ("¿no será marketing?") →
dato WOW la rompe → reacción emocional → detalle técnico → CTA; 8-12 líneas) · **UGC tradicional** (gancho →
problema → empatía "yo estaba igual" → dato WOW → lo que probó y falló → descubrimiento → diferenciador
técnico → resultado concreto → CTA; 15-25 líneas) · **Voz en off** ("me he comprado esto y os tengo que
enseñar algo" → producto → por qué mola → dato → valor/precio → CTA suave). **Proceso en 2 pasos con
compuerta:** primero ANALIZA (público, ángulo más potente, 2-3 datos WOW con fuentes reales — si no está
confirmado LO DICE, tono) y PREGUNTA "¿te cuadra este enfoque?" → solo tras el OK genera los 3 guiones.
Anti-invento: cero estudios/universidades/estadísticas falsas, cero promesas médicas absolutas. Voz: "persona
recomendándole algo a un amigo", no marca.

### 6.7 ADS de IMAGEN (5 plantillas de alto CTR — Nano Banana Pro)
①**Testimonial + before/after**: comentario FB/IG falso arriba (nombre difuminado) + split ANTES(flash crudo,
imperfecto)/DESPUÉS(mejora REAL, NO perfecta — "some traces of the problem still visible for credibility") +
producto al centro superpuesto rotado + ⭐4.7 · +3.000 opiniones. ②**Chat iMessage**: before/after arriba +
burbujas azul/gris (resultado emocional → pregunta curiosa → confirmación + diferenciador) + badge de
garantía. ③**Timeline de transformación**: headline con subrayado amarillo imperfecto + timeline por semanas
+ before/after + badge rotado. ④**Facebook testimonial exacto** ("DO NOT redesign. Replicate structure.").
⑤**TikTok social-proof cards**: review card flotante + 2 tarjetas UGC before/after con flechas dibujadas a
mano, profundidades y rotaciones. **REGLA CRÍTICA DE REALISMO en todas: el DESPUÉS jamás perfecto** (poros
visibles, marcas leves) — "si parece flawless/airbrushed → FAIL". Anti-AI: no simetría perfecta, no
gradientes perfectos, no glow, alineación ligeramente imperfecta, "NOT Apple clean, NOT Canva template".
**⚠️ Matiz de doctrina:** estas plantillas SÍ incrustan texto en la imagen — Nano Banana Pro renderiza texto
bien. Nuestra regla "el texto no va en la imagen" nació de los difusores que lo garabatean; se mantiene para
KEYFRAMES de video y generadores clásicos, pero para ADS ESTÁTICOS vía Nano Banana Pro el texto-en-imagen es
válido y es el formato ganador del curso. **⚠️ Candado Papandi:** los testimonios/reviews FALSOS violan C4
para productos pre-lanzamiento — estas plantillas se adaptan (la ESTRUCTURA visual sirve; el contenido debe
ser honesto: mecanismo, comparación funcional, timeline de uso esperado — no reseñas inventadas).

---

## §7 · Realidad técnica VERIFICADA (fal, 2026-07-12)

**Kling v3 Pro image-to-video** (`fal-ai/kling-video/v3/pro/image-to-video` — el endpoint QUE YA USAMOS):
- `start_image_url` (requerido) + **`end_image_url` (opcional) — ¡soporta primer Y último frame HOY!**
- `elements[]`: `frontal_image_url` + `reference_image_urls` (identidad multi-ángulo) o `video_url` (motion
  reference); se citan como @Element1 en el prompt.
- `duration` 3-15s · `generate_audio` · `negative_prompt` · `cfg_scale` · prompt i2v ≤2500 chars ·
  `multi_prompt` solo ≤512 chars/segmento · ~$0.168/s (nuestro catálogo) · audio EN/ZH.
**Veo 3.1 first-last-frame** (`fal-ai/veo3.1/first-last-frame-to-video`): first+last+prompt; interpola entre
ambos; $0.20/s sin audio · **$0.40/s con audio** (720/1080p) · $0.60/s 4K. Lip-sync bueno; 4/6/8s.
**Sora 2 i2v Pro** (`fal-ai/sora-2/image-to-video/pro`): $0.30/s 720p · $0.50-0.70/s 1080p; **audio nativo
con diálogo lip-sync + ambiente**; 4/8/12s (hasta 25s extendido). El motor natural del formato UGC one-take.
**Nano Banana Pro** (`fal-ai/nano-banana-pro` + `/edit`): **$0.15/imagen** (generación y edición; 4K $0.30).
Renderiza TEXTO legible (único difusor confiable para ads con texto). El `/edit` = cadenas de consistencia
("keep X identical, change Y"). Nano Banana clásico ≈ $0.039/img (borradores baratos).
**video-use** (github.com/browser-use/video-use, MIT): agente (Claude Code) que edita footage REAL: ElevenLabs
Scribe (timestamps por palabra) → **lee el TRANSCRIPT, no mira frames** → corta muletillas/silencios, color
grade, subtítulos burn-in, overlays animados (Remotion/Manim/PIL), auto-evalúa el render, memoria en
project.md. FFmpeg debajo. **= El blueprint exacto del camino "el usuario trae SUS videos".**
**Lo nuestro reutilizable para ese camino:** whisper word-align (ya en prod), ffmpeg compose
(tracks+keyframes = cortes + overlays con posición/tiempo), karaoke PNGs client-side, re-host de brand-assets,
cola async, ledger de costos por proyecto.

## §8 · Los DOS caminos del usuario (decisión de producto)

**Camino A — Generación completa (avatar IA):** el usuario no tiene material. Papandi genera personaje/set
(Identidad), guion, keyframes encadenados, clips, post. El método = §6 adaptado a nuestras fases (el avatar
del paso 1 YA LO TENEMOS firmado en 0.3; el research de datos duros ≈ nuestro 0.2/keywords + radar).
**Camino B — Footage propio:** el usuario TIENE videos (el abogado con entrevistas de noticieros; la velera
que filma con nuestro guion). Papandi: ingesta → transcript por palabra → plan de edición glass-box (cortes,
captions karaoke, overlays de marca/elementos nombrados, color) → compose → reel final CON su marca (fases
0-2 gobiernan tono, paleta, CTA). Nunca destructivo (el original se conserva).
**Decisión de diseño (operador, 2026-07-12): HÍBRIDO.** Automatizar lo posible PERO el usuario participa en
compuertas: aporta referencia visual (screenshot TikTok/Pinterest/upload), elige estilo/formato, **aprueba el
guion ANTES de las imágenes, aprueba los KEYFRAMES antes del video** (regenerar uno = barato; regenerar un
clip = caro), y en Camino B aprueba el plan de edición. El asistente acompaña TODO el proceso.

## §9 · Costos de referencia (verificados 2026-07-12; re-cotizar al construir)

| Concepto | Costo |
|---|---|
| Keyframe Nano Banana Pro | $0.15/img (par start+end por clip ≈ $0.30) |
| Borrador keyframe Nano Banana clásico | ~$0.039/img |
| Clip Kling 3.0 Pro (i2v, audio) | ~$0.168/s → 5s ≈ $0.84 |
| Clip Veo 3.1 first-last (audio) | $0.40/s → 5s = $2.00 |
| Clip Sora 2 Pro (UGC one-take, audio) | $0.30-0.70/s → 15s ≈ $4.50-10.50 |
| Whisper align (palabra) | centavos |
| Compose ffmpeg + PNGs karaoke | ~$0.10 + $0 (client-side) |
| **Reel v1 actual (5 clips Kling 28s)** | **~$4.70** |
| **Reel v2 keyframes-first (10-12 imgs + 5 clips Kling + compose)** | **~$6.50-7.00** |
| Reel v2 con Veo 3.1 | ~$11-12 |
| Presupuesto vigente | `MEDIA_BUDGET_USD` = $20/mes por proyecto (gate pre-encolado) |

## §10 · Decisiones y candados VIGENTES (no re-litigar sin el operador)

1. **C4** anti-prueba-social (pre-lanzamiento: cero testimonios/casos/cifras inventadas → MECANISMO) ·
   **C12** cero urgencia fabricada (deadline real de campaña SÍ es legítimo) · **C1** valor por funcionalidad.
2. **Arco que vende** (2026-07-11): gancho/dolor → GIRO a la solución (~60%: qué es el producto y qué
   resuelve, con ESENCIA+OFERTA) → CTA de esencia. "No vender" = tono, JAMÁS ocultar el producto (aplica a
   pilares dar-valor y fase teaser; solo la intensidad del CTA cambia).
3. **Opener sagrado**: la apertura aprobada viaja verbatim y no se mutila… **tensión conocida**: un opener de
   45 palabras ≈ 18-22s hablados; en 15-30s no caben opener completo + producto + CTA (~120 palabras ≈ 48s).
   Resolución pendiente de decisión; mientras tanto el guard `under/over` avisa.
4. **i2v: la imagen es el ancla** — el prompt SOLO movimiento (re-describir apariencia cambia la cara).
5. **EN-first** (mercado US; lip-sync Kling EN OK; ES era el hueco).
6. **Música jamás quemada**; se añade al publicar (catálogo de la plataforma) + label IA ON.
7. **El texto jamás lo renderiza el generador de VIDEO** — captions/gancho = capa de edición. (Matiz §6.7:
   ads ESTÁTICOS con Nano Banana Pro sí pueden llevar texto embebido.)
8. **Dedupe de slot en el servidor** (una pieza por proyecto×avatar×pilar×ángulo×canal; `deletePieceSlot`
   antes de insertar). Campaña POR-CANAL en las tarjetas; solo campañas ACTIVAS seleccionables.
9. **Gate de video POR-PIEZA** (override de campaña aprobado desbloquea; sin personaje aprobado NO se genera).
10. **Glass-box siempre** (QA reporta qué quitó y por qué; costos visibles antes de gastar; presupuesto duro).
11. **Deploy inmediato** (sandia: todo commit → push → Vercel). **Verify con EXIT 0 real** antes de commit.
12. **Docs SIEMPRE en pretel-os** (`buckets/business/projects/marketing-os/docs`); sandia-marketing/docs es
    solo un puntero.
13. UI: **firmado es visible** (firmar bloquea EDITAR, no LEER). **"Puede" ≠ "debe"** al capturar mandatos
    (ejemplo ilustrativo ≠ regla dura). Entregables ACCIONABLES (mostrar QUÉ HACER, no cómo se hizo; "el
    prompt exacto" = el que el usuario pega en SU generador).

## §11 · Mapa de fuentes (dónde vive el detalle)

| Sección | Archivo(s) fuente |
|---|---|
| §1 estado del sistema | código `sandia-marketing` (`lib/estudio/*`, `app/api/estudio/*`, `lib/gateway/*`, `lib/video/*`) |
| §2 doctrina video | `docs/research/doctrina-video-2026.md` (43 fuentes citadas) |
| §3 canales | `docs/research/doctrina-por-canal.md` |
| §4 campañas | `docs/research/campanas-marketing-real.md` + `specs/spec_Campanas.md` |
| §5 estrategia/scope | `docs/research/2026-07-01_market_strategy_scope.md` + `2026-07-01_video_field_of_action.md` (+ raw JSONs) |
| §6 AvatarHype | `specs/AvatarHype Classes/` — `Planificacion.txt` (workflow 8 pasos + transiciones), `Metodo 6C…`, `prompts-metodo-6c Engine.md`, `UGC PROMPT ENGINE.md`, `Prompts VEO3-1.md`, `Prompts Video Samples.md` (el `.txt` es duplicado), `Referencia Visual…`, `ADS IMAGEN.md`, `copywriter especializado….md`, `Ads Visual Architect Engine.md` |
| §7 APIs | verificación web 2026-07-12 (fal endpoints + github.com/browser-use/video-use) |
| Plan de construcción | `specs/spec_Estudio_Video_v2.md` (el plan completo, mismo día) |
