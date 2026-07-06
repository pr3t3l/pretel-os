# Campañas en el marketing real — investigación

> Investigación web (julio 2026) para la spec de CAMPAÑAS de Papandi — aparcadas hasta ahora como
> "evento + ventana + piezas, spec propio al retomar". Contexto interno contra el que encaja:
> `lib/calendar/plan.ts` (plan de publicación finito, `CHANNEL_MAX_PER_DAY`, `policyOverrides` como
> gancho previsto de campañas), `lib/radar/holidays.ts` (`RadarEvent.lead_time_days` — la "ofensiva"),
> `lib/estudio/rodaje-kit.ts` (personaje/set/voz aprobados), 4 pilares por avatar, ~28 piezas (2.4),
> ~40 ganchos por avatar (2.5, con `temporality: seasonal`), ratio dar:pedir firmado (default 3:1).
>
> Método y honestidad de fuentes: cada afirmación lleva su URL inline. Se marca [opinión] cuando la
> fuente es un blog/agencia sin datos, [estudio] cuando hay datos detrás, [oficial] cuando es
> documentación de producto. Las páginas del Help Center de Hootsuite y del help de Planable no se
> pudieron leer completas (requieren JS / devolvieron 403); lo citado de ellas viene de los extractos
> del buscador y de la página de producto de Planable — está marcado.

## 1. Hallazgos

### 1.1 Tipos de campaña y cuánto duran

**Los tipos que usan los equipos reales.** La taxonomía se repite en todas las fuentes:
lanzamiento de producto, awareness de marca, estacional/evento, promocional (descuentos), y
concursos/UGC ([Indeed](https://www.indeed.com/career-advice/career-development/types-of-marketing-campaigns),
[Sprout Social](https://sproutsocial.com/insights/social-media-campaigns/)). Las estacionales
"aprovechan momentos culturales, festivos y tendencias con fecha para generar relevancia y ventas"
([Sprout Social](https://sproutsocial.com/insights/social-media-campaigns/)).

**Always-on vs burst.** El marketing "always-on" es actividad continua que sostiene presencia y
retención durante todo el ciclo de vida ([Smart Insights](https://www.smartinsights.com/conversion-optimisation/conversion-optimisation-strategy/always-on-marketing/));
la campaña es "una ráfaga de alta intensidad, acotada en el tiempo, con un solo objetivo"
([The Escape](https://www.the-escape.co.uk/insights/what-is-the-difference-between-always-on-and-campaign-based-marketing) [opinión]).
La práctica dominante hoy es **por capas**: una base continua complementada con picos de campaña en
momentos clave ([Pitch](https://www.pitchonnet.com/pitch-feature/always-on-vs-burst-campaigns-what-are-marketers-choosing-39277.html),
[Campaign del Mar](https://www.campaigndelmar.com/blog/always-on-marketing-versus-campaigns-why-you-need-both-but-not-equally) [opinión]).
El estudio clásico detrás: Binet & Field, "The Long and the Short of It" — ~60% construcción de
marca (largo plazo) / 40% activación (corto plazo) como punto de partida, no regla fija
([Growth Method](https://growthmethod.com/long-and-short/), [VXTX](https://www.vxtx.co.uk/blog/mastering-the-60-40-marketing-mix-how-peter-field-les-binets-framework-maximizes-roi) [estudio, IPA]).
Ojo: es doctrina **disputada** — Byron Sharp (Ehrenberg-Bass) la ataca y defiende alcance always-on
([Ehrenberg-Bass](https://marketingscience.info/news-and-insights/prof-byron-sharp-skewers-binet-tells-marketers-to-sack-agencies-preaching-share-of-voice)).
Traducción a Papandi: el plan evergreen finito ES el always-on; la campaña es el pico encima. Es
exactamente el modelo por capas.

**Duración típica.** Depende del objetivo, con consenso razonable:
- Campañas sociales necesitan "al menos 4–6 semanas para construir momentum; las ligadas a metas
  grandes, 3 meses de pista" ([Sprout Social](https://sproutsocial.com/insights/social-media-campaigns/)).
- "Las campañas cortas (1–2 semanas) funcionan para momentos con fecha — lanzamientos, promos
  estacionales — pero exigen **mayor cadencia de contenido**" ([Sprout Social](https://sproutsocial.com/insights/social-media-campaigns/)).
- Awareness: 3–6 meses ([Impremis](https://impremis.com/blogs/how-long-should-a-marketing-campaign-last) [opinión]);
  en ads pagados 2–8 semanas ([Your Marketing People](https://yourmarketingpeople.com/how-many-weeks-for-awareness-campaign-ads-meta-and-google/) [opinión]).
- Conversión: 4–6 semanas ([Impremis](https://impremis.com/blogs/how-long-should-a-marketing-campaign-last) [opinión]);
  consideración: 6–8 semanas para datos fiables ([Oyova](https://www.oyova.com/blog/how-many-weeks-consideration-campaign-ads/) [opinión]).

**Intensidad durante la campaña vs evergreen.** El evergreen sano (datos de Buffer sobre millones de
posts): Instagram 3–5 posts/semana + 1–2 stories/día; TikTok crecimiento real desde 3–5/semana;
LinkedIn 2–5/semana; y "la consistencia sostenible gana a publicar a diario"
([Buffer, guía de frecuencia](https://buffer.com/resources/social-media-frequency-guide/),
[Buffer, Instagram 2M posts](https://buffer.com/resources/how-often-to-post-on-instagram/) [estudio]).
Durante campaña la frecuencia **sube deliberadamente**: "si lanzas un producto, es normal un empujón
de campaña con frecuencia de publicación aumentada"
([Loomly](https://www.loomly.com/blog/social-media-posting-schedule) [opinión]). El caso extremo
documentado es BFCM en email: a principios de noviembre 4 envíos/semana → mediados-finales de
noviembre envío diario → Black Friday y Cyber Monday 3–4 envíos el mismo día (lanzamiento AM,
recordatorio mediodía, last call PM), con "+25% sobre tu volumen base" como benchmark de temporada
([Hustler Marketing, checklist BFCM](https://www.hustlermarketing.com/blog/the-complete-black-friday-cyber-monday-pre-launch-checklist/) [agencia]).
Klaviyo estructura las 3 semanas previas por temas (semana 1 gift guide + early access, semana 2
free shipping + bundles, semana 3 acceso VIP + mensaje de entrega garantizada) y cita como práctica
de experto "3 emails + 2 SMS en los días pico"
([Klaviyo, guía de envíos BF](https://www.klaviyo.com/blog/when-to-send-black-friday-emails) [oficial]).
En social, un patrón realista de "drop" mensual: semana −1 un post de preview, semana de lanzamiento
un post principal + secuencia de stories, semana +1 un follow-up de uso
([Kivopost](https://kivopost.com/glossary/strategy-growth-frameworks/posting-cadence) [opinión]).

### 1.2 El arco de una campaña: fases y reparto de piezas

**Las fases existen en todas las fuentes, con nombres distintos.** Sprout las llama pre-launch /
active / post-campaign, con revisión de rendimiento en cada una
([Sprout Social](https://sproutsocial.com/insights/social-media-campaigns/)). Las guías de
lanzamiento en social convergen en teaser → lanzamiento → sostenimiento → integración:
- Calendario a nivel de día: "Día 0–6: hype/teasers la semana previa · Día 7: LANZAMIENTO ·
  Día 8–14: contenido post-lanzamiento · Día 15–30+: integrar el producto al contenido regular"
  ([The Creative Company](https://thecreativecompany.com/7-steps-to-plan-launch-a-new-product-on-social-media/) [agencia]).
- Mínimo viable: 4 semanas — 2 de teaser, 1 de lanzamiento intensivo, 1 de momentum post
  ([MEAN blog](https://blog.mean.ceo/social-media-launch-timeline-startups/) [opinión]); los
  lanzamientos grandes estiran el pre-launch a 12 semanas (teaser → awareness → engagement →
  conversión/pre-order) ([SociallyIn](https://sociallyin.com/resources/social-media-strategy-for-product-launch/),
  [Prefinery](https://www.prefinery.com/blog/referral-programs/prelaunch-campaign/social-media-3/) [agencias]).
- Contenido por fase: teaser = expectativa/countdown/sneak peeks; lanzamiento = visual potente +
  CTA claro; post = testimonios y prueba social
  ([Metricool](https://metricool.com/social-media-product-launch/) [agencia]).

**El arco con más doctrina escrita es el de Jeff Walker (Product Launch Formula):** la "Sideways
Sales Letter" = 3 piezas de pre-launch **de valor puro** repartidas en 7–10 días, que desembocan en
la apertura de carrito; el carrito abre 5–7 días con deadline duro; y el cierre concentra la
urgencia — el último día se envían 4 mensajes (mañana deadline, tarde historia personal, noche
recordatorio, countdown final 90 min antes). "El lanzamiento no se gana en la apertura. Se gana en
el cierre" ([systeme.io, resumen PLF](https://systeme.io/blog/product-launch-summary),
[Product Launch Strategy, cart close](https://productlaunchstrategy.org/how-to-structure-your-product-launch-cart-close-sequence/),
[jeffwalker.com](https://jeffwalker.com/my-secrets-to-consistent-success-with-product-launch-formula/) [libro/práctica documentada]).
El equivalente BFCM: teasers 1–2 semanas antes, acceso VIP anticipado, día D con múltiples envíos, y
**extensión del día después** — The Honest Company envía el 5 de julio "HOURS LEFT: 20% off (almost)
everything" ([Klaviyo, 4th of July](https://www.klaviyo.com/blog/4th-of-july-marketing) [oficial]).

**Ratio dar:pedir DENTRO de una campaña.** El evergreen tiene reglas conocidas: 80/20
([Brenton Way](https://brentonway.com/social-media-80-20-rule/) [opinión]), 4-1-1 (de cada 6 posts:
4 de valor, 1 venta blanda, 1 venta dura — [The SMMU](https://www.thesmmu.com/post/social-media-marketing-content-mix-finding-the-right-balance) [opinión]),
la regla de los tercios y el 70-20-10 ([LikeMind Media](https://www.likemind.media/70-20-10-rule-in-marketing/) [opinión]),
y el jab-jab-jab-right-hook de Vaynerchuk — muchos más jabs (valor) que right hooks (CTA)
([libro](https://www.amazon.com/Jab-Right-Hook-Story-Social/dp/006227306X),
[resumen Shortform](https://www.shortform.com/summary/jab-jab-jab-right-hook-summary-gary-vaynerchuk)).
Dentro de una campaña el ratio **no desaparece: se reordena por fases**. PLF es la prueba: incluso
el arco más vendedor mete 3 piezas de valor ANTES de pedir, y concentra todo el pedir en una ventana
corta con deadline ([systeme.io](https://systeme.io/blog/product-launch-summary)). En el pico (días
de carrito abierto / BFCM) la proporción se invierte a casi todo pedir, a diario
([Hustler Marketing](https://www.hustlermarketing.com/blog/the-complete-black-friday-cyber-monday-pre-launch-checklist/)).
**Síntesis (inferencia nuestra, coherente con las fuentes):** el ratio de campaña se mide sobre el
arco completo (teaser da, cierre pide — el agregado queda ~1:1 o 2:1), y el 3:1 firmado del proyecto
se sigue midiendo sobre el mes completo (evergreen + campaña), no pieza a pieza dentro de la ventana.

### 1.3 Un tema, muchas piezas: la "big idea" y sus ejecuciones (caso 4 de Julio)

**El concepto existe con nombre propio.** Una campaña es una serie de piezas centradas en **una sola
idea creativa** ejecutada en múltiples canales durante un periodo; la big idea debe "estirarse por
todos los medios sin quedarse encerrada en un canal"
([Smart Insights](https://www.smartinsights.com/traffic-building-strategy/campaign-planning/four-steps-developing-big-idea-campaign/) [agencia]).
La versión moderna es **modular**: "un concepto núcleo que se reforma para cada plataforma y
audiencia" ([MarTech](https://martech.org/whats-big-idea-3-fundamentals-successful-digital-creative/) [opinión]);
Ogilvy lo formula como adaptar la idea a cada canal manteniendo look & feel cohesivo
([Ogilvy](https://www.ogilvy.com/ideas/five-principles-optimize-multichannel-campaigns) [agencia]).
Hay datos a favor de la integración: campañas integradas con idea central fuerte rinden mejor en
todos los KPIs de marca (+64%, y +91% en asociaciones de imagen), según datos citados por
[Creativepool](https://creativepool.com/magazine/workshop/campaign-ideas-that-actually-work-what-makes-the-best-advertising-campaigns) [secundaria].

**El 4 de Julio, desglosado en las tres dimensiones que nos importan** (todas documentadas en
[Klaviyo](https://www.klaviyo.com/blog/4th-of-july-marketing) [oficial] y guías para pequeños
negocios [Alkai](https://www.alkai.ai/post/15-independence-day-social-media-post-ideas),
[Jetpack](https://jetpack.com/resources/4th-of-july-social-media-posts/) [opinión]):
- **Visual:** "fondos, decoraciones y colores de temporada — banderas, fuegos artificiales, rojo,
  blanco y azul", BBQ y picnic; colecciones temáticas fotografiadas en contexto (Little Sleepies
  mostró su colección patriótica en un show de fuegos artificiales).
- **Verbal:** subject lines y frases del momento — "Combat your 4th of July hangover 🍻", "Best
  Dressed at the BBQ 🏆", "⏰ Don't miss out on our July 4th Sale!"; posts de "qué significa la
  libertad para mí como emprendedor".
- **Oferta:** promos limitadas con código temático — "code JULY4TH: $5 off $20+", "10% Off + Free
  Shipping! Code: FIREWORKS", "up to 45% off" — y la extensión del 5 de julio como last call.
- **Reparto por canal:** email para storytelling largo y escaparate de producto, SMS para lo
  urgente, social para UGC/concursos (foto patriótica, tag-a-friend); las promos se publican el
  2–3 de julio y el día 4 se reserva para contenido ligero y comunitario
  ([Alkai](https://www.alkai.ai/post/15-independence-day-social-media-post-ideas)).
- **Timing:** Klaviyo recomienda empezar a planear "en mayo o antes" — para una pyme real, semanas,
  no meses ([Klaviyo](https://www.klaviyo.com/blog/4th-of-july-marketing)).

Es exactamente el modelo de 3 capas de Papandi (DOLOR × FORMA × ESCENA): la big idea es la ESCENA/
concepto compartido; los ganchos y frases son la capa verbal; la oferta es una capa nueva que hoy no
existe en el sistema — **es LO que la campaña añade** que el evergreen no tiene.

### 1.4 Campañas para solopreneurs: qué es realista

- **El mínimo viable de un lanzamiento tiene ~6 tareas de carga** sin las cuales no hay lanzamiento:
  posicionamiento en una línea, anuncio con prueba, landing con un solo CTA, email a toda la lista,
  al menos un post público en cada canal donde YA está la audiencia, y un loop de respuestas el día
  D. Lo demás — ads pagados, notas de prensa, briefs de agencia, video ads — es opcional y "los
  fundadores solos fallan lanzamientos estirándose hacia la lista opcional con el núcleo a medias"
  ([Sistava](https://sistava.com/en/insights/how-to-launch-a-product-without-a-marketing-team) [opinión]).
- **Uno o dos canales, no más.** "Como solopreneur, empieza con solo 1–2 canales donde estén tus
  clientes" ([Shopify](https://www.shopify.com/blog/marketing-for-solopreneurs) [oficial]); Etsy a
  sus vendedores: "si estás empezando, elige UN solo canal" y "planea las promos de Black Friday /
  Cyber Monday con anticipación"
  ([Etsy Seller Handbook, holiday marketing](https://www.etsy.com/seller-handbook/article/22815438793) [oficial]).
- **Planificación estacional realista:** revisar cómo fue el año pasado, fijar una meta específica y
  medible, y trabajar con checklist de fechas clave — no un war room
  ([Etsy Seller Handbook, prepare your shop](https://www.etsy.com/seller-handbook/article/30953650830),
  [Seller Holiday Checklist](https://www.etsy.com/seller-handbook/article/1401252562091) [oficial]).
- **Sobredimensionado para nuestro usuario:** presupuestos/attribution multi-touch (HubSpot-style),
  campañas multi-audiencia simultáneas, amplificación pagada como requisito, calendarios de 12
  semanas de pre-launch. **Mínimo viable:** una ventana corta con fecha, un concepto, una oferta
  opcional, pocas piezas por fase en los canales ya encendidos, y deadline real
  ([Sistava](https://sistava.com/en/insights/how-to-launch-a-product-without-a-marketing-team),
  [Sprout Social](https://sproutsocial.com/insights/social-media-campaigns/)).
- La sostenibilidad manda: "los mejores resultados vienen de un calendario sostenible en el tiempo",
  no de picos heroicos ([Buffer](https://buffer.com/resources/social-media-frequency-guide/) [estudio]).

### 1.5 Cómo modelan "campaña" las herramientas líderes

| Herramienta | Modelo | Detalles verificados |
|---|---|---|
| **Buffer** | **Etiqueta + color** (la feature se llamaba "Campaigns" y fue renombrada a "Tags") | Tag = texto + color; se aplica a ideas, borradores, programados y publicados; hasta 10 tags/post (de pago); filtrado y reporting por tag ("Tag pulse": impresiones, engagement del conjunto). Las URLs del help conservan el nombre viejo: "tracking-the-performance-of-your-**campaigns**" ([Buffer Help, tags](https://support.buffer.com/article/585-creating-and-managing-tags), [Buffer Help, reporting](https://support.buffer.com/article/535-tracking-the-performance-of-your-campaigns), [Buffer Help, mobile](https://support.buffer.com/article/634-creating-and-managing-campaigns-on-the-mobile-app) [oficial]) |
| **Hootsuite** | **Dos niveles: tag + "content campaign" con fechas** | Tags = "hashtags internos" invisibles al público, para clasificar y reportar; las content campaigns "abarcan un periodo especificado y tienen atributos definidos: parámetros de link tracking, acortadores y tags" ([Hootsuite Help, organize campaigns with tags](https://help.hootsuite.com/hc/en-us/articles/1260804248950-Organize-campaigns-with-tags), [create and manage content campaigns](https://help.hootsuite.com/hc/en-us/articles/1260804251710-Create-and-manage-content-campaigns) [oficial — citado vía extractos: la página requiere JS]) |
| **HubSpot** | **Contenedor de negocio de primera clase** | Campos al crear: nombre único, **color**, owner, **fechas de inicio/fin "reflejadas en el calendario de marketing"**, goal, audiencia, moneda/presupuesto, notas; los assets (emails, landing pages, social posts, blogs, workflows) se asocian a la campaña; **un asset solo puede pertenecer a UNA campaña** (salvo workflows y listas); hay plantillas de campaña ([HubSpot KB, create campaigns](https://knowledge.hubspot.com/campaigns/create-campaigns), [associate assets](https://knowledge.hubspot.com/campaigns/associate-assets-and-content-with-a-campaign), [campaign templates](https://knowledge.hubspot.com/campaigns/campaign-templates) [oficial]) |
| **Planable** | **Etiqueta + color + filtro** | "Añade post labels para campañas, pilares de contenido o asignaciones de equipo"; labels con color, múltiples por post, filtrado del calendario por label y vistas custom ([Planable, product](https://planable.io/product/) [oficial]; [help de labels](https://help.planable.io/en/articles/1563941-labels) devolvió 403 — citado vía extractos) |
| **Later** | **Labels sobre la BIBLIOTECA de media**, no sobre posts | Labels = keywords sobre los media items "para organizar por perfil, estilo, campaña, fotógrafo"; filtrado de la biblioteca por label/estrella ([Later Help, glossary](https://help.later.com/hc/en-us/articles/360043360953-Later-Glossary), [Later, scheduler](https://later.com/social-media-scheduler/) [oficial]) |
| **CoSchedule** | **Carpeta/timeline en el calendario** | "Marketing Campaigns" agrupa múltiples proyectos/piezas en una carpeta con timeline propio visible en el calendario — "vista global de tu campaña de fiestas entera en un solo lugar" ([CoSchedule Support](https://coschedule.com/support/marketing-calendar/marketing-campaigns/marketing-campaigns), [CoSchedule blog](https://coschedule.com/blog/organize-marketing-campaigns) [oficial]) |
| **Convención transversal** | **`utm_campaign` = el nombre de campaña como clave** | El parámetro `utm_campaign` "agrupa todos tus assets bajo un paraguas" cross-plataforma; nombres tipo `spring_sale`, case-sensitive ([Google Analytics, URL builders](https://support.google.com/analytics/answer/10917952?hl=en) [oficial], [Buffer Help, UTM](https://support.buffer.com/article/518-understanding-utm-parameters-and-google-analytics)) |

**El espectro es claro:** etiqueta+color (Buffer, Planable, Later — el patrón dominante en
herramientas para pequeños equipos) → contenedor con fechas y atributos compartidos (Hootsuite,
CoSchedule) → objeto de negocio con presupuesto y atribución (HubSpot, para equipos). Dos lecciones
de producto: (1) Buffer LANZÓ "Campaigns" y lo degradó a "Tags" — para su público, el contenedor
pesado sobraba; (2) lo que sí sobrevive en todas: **color en el calendario, filtro, y reporting del
conjunto**. HubSpot aporta las dos ideas útiles de contenedor: fechas que se pintan en el calendario
y "un asset pertenece a una sola campaña".

## 2. Tabla de decisiones para Papandi

| Decisión | Recomendación | Fuente/razón |
|---|---|---|
| **Tipos de campaña v1** | Solo 2: **evento/estacional** (nace de una fecha del calendario) y **lanzamiento/promo propia** (nace de una fecha del usuario — que ya existe como evento "personal" del radar). Ambas son el mismo objeto: evento + ventana + concepto + oferta opcional. NO soportar "awareness" como campaña: eso ES el plan evergreen | El always-on ya lo cubre el plan finito; la práctica por capas = base + picos ([Pitch](https://www.pitchonnet.com/pitch-feature/always-on-vs-burst-campaigns-what-are-marketers-choosing-39277.html)); solopreneur = mínimo viable ([Sistava](https://sistava.com/en/insights/how-to-launch-a-product-without-a-marketing-team)) |
| **Duración default** | **2 semanas** para evento (teaser semana −2/−1 → pico → día después), **4 semanas** para lanzamiento propio; editable 1–6 semanas. El default nace de `RadarEvent.lead_time_days` que YA existe | Mínimo viable 4 semanas para launch ([MEAN](https://blog.mean.ceo/social-media-launch-timeline-startups/)); 1–2 semanas para momentos con fecha ([Sprout](https://sproutsocial.com/insights/social-media-campaigns/)); PLF: 7–10 días de pre + 5–7 de venta ([systeme.io](https://systeme.io/blog/product-launch-summary)) |
| **Fases** | 3 fijas: **teaser → pico → cierre** (cierre incluye el "día después" opcional). Sin fases custom en v1 | Todas las fuentes convergen en 3–4 fases ([Sprout](https://sproutsocial.com/insights/social-media-campaigns/), [The Creative Company](https://thecreativecompany.com/7-steps-to-plan-launch-a-new-product-on-social-media/)); el cierre es donde se gana ([PLF](https://productlaunchstrategy.org/how-to-structure-your-product-launch-cart-close-sequence/)); day-after documentado ([Klaviyo](https://www.klaviyo.com/blog/4th-of-july-marketing)) |
| **Intensidad default** | La campaña **añade** piezas sobre el evergreen: ~2–3 en teaser, ~3–4 en pico, ~2 en cierre (escalado a los canales encendidos de 2.2), con rampa creciente hacia el pico. Nunca inventa canales nuevos | Rampa documentada: 4/sem → diario → 3–4/día en pico ([Hustler](https://www.hustlermarketing.com/blog/the-complete-black-friday-cyber-monday-pre-launch-checklist/)); +25% sobre baseline como benchmark de temporada (misma fuente); drop realista semana −1 / semana 0 / semana +1 ([Kivopost](https://kivopost.com/glossary/strategy-growth-frameworks/posting-cadence)) |
| **Vínculo con eventos del calendario** | Crear campaña **DESDE un evento** del radar (drawer del evento → "Montar campaña"): `starts_on = date − lead_time_days`, `ends_on = date (+1 día si oferta)`. El evento sigue existiendo; la campaña lo referencia | `lead_time_days` ya es "con cuánta anticipación arrancar contenido" (`lib/radar/holidays.ts`); el calendario ya absorbió el radar (una sola interfaz temporal) |
| **Vínculo con ganchos de marca (2.5)** | Doble: (1) dentro de la ventana, `rotateHook` ya prioriza ganchos `seasonal` — la campaña se apoya en eso sin tocar la rotación; (2) la campaña puede traer **hasta ~5 ganchos propios** (frases del concepto) que viven en la biblioteca del avatar etiquetados con `campaign_id` y temporalidad = la ventana; al firmar la campaña entran, al cerrar expiran | rotateHook es la única rotación (doctrina); la capa verbal de la big idea son frases de apertura — mismo objeto que un gancho ([Klaviyo 4th July](https://www.klaviyo.com/blog/4th-of-july-marketing): subject lines temáticas) |
| **Ratio dentro de campaña** | Por fase: teaser mantiene dar (valor temático), pico/cierre son pedir. El agregado de la campaña queda ~1:1 y **no rompe el 3:1 firmado**: el ratio del proyecto se mide sobre el mes completo (evergreen + campaña) y la UI lo muestra desglosado, no lo esconde | PLF: valor antes de pedir incluso en lanzamiento ([systeme.io](https://systeme.io/blog/product-launch-summary)); 4-1-1/80-20 son reglas del flujo base, no de la ventana de venta ([The SMMU](https://www.thesmmu.com/post/social-media-marketing-content-mix-finding-the-right-balance)); surface-no-reconciliar es doctrina propia |
| **Override: tope/día** | `policy_overrides` por canal SOLO dentro de la ventana (ej. Email 1→2 en pico, Instagram 2→3). El merge usa `max(default, override)` únicamente en fechas de la campaña. Ya está previsto en `buildPublicationPlan` (`policyOverrides`) | El comentario del código ya lo dice ("una CAMPAÑA futura puede subir el tope"); 3–4 envíos/día en pico BFCM es práctica real ([Hustler](https://www.hustlermarketing.com/blog/the-complete-black-friday-cyber-monday-pre-launch-checklist/)) |
| **Override: personaje/set** | La campaña puede tener una **variante temática del kit de rodaje** (misma cara del personaje, atrezzo/escena del tema — ej. bandera para el 4 de Julio), generada desde el kit base + concepto, con aprobación previa obligatoria (mismo contrato que rodaje-kit). Si no hay variante, se usa el kit base | Visual temático documentado ([Klaviyo](https://www.klaviyo.com/blog/4th-of-july-marketing): banderas/fuegos/rojo-blanco-azul); consistencia de personaje = doctrina propia (Kling image-to-video con `start_image`) |
| **Override: ratio** | NO override del ratio en v1. El ratio firmado no se toca; solo cambia dónde se mide (mes completo) y la UI lo transparenta | Evita romper el candado firmado; coherente con "el doc gana" |
| **Modelo de datos mínimo** | Tabla `project_campaigns` (campos en §3.1) + `campaign_id` en las piezas de campaña y en los `PlanSlot` derivados. Las piezas de campaña son NUEVAS (no se re-etiquetan derivados de 2.4) y pertenecen a UNA sola campaña | Patrón HubSpot: contenedor con fechas pintadas en calendario + asset en una sola campaña ([HubSpot KB](https://knowledge.hubspot.com/campaigns/create-campaigns)); patrón Buffer/Planable: color + filtro ([Buffer](https://support.buffer.com/article/585-creating-and-managing-tags), [Planable](https://planable.io/product/)) |
| **UI en calendario** | Banda de color con el rango de fechas (patrón CoSchedule/HubSpot) + chip de color en cada slot de campaña (patrón Buffer/Planable). `slug` del nombre queda listo como `utm_campaign` para el futuro (no se construyen UTMs en v1) | [CoSchedule](https://coschedule.com/support/marketing-calendar/marketing-campaigns/marketing-campaigns); [GA URL builders](https://support.google.com/analytics/answer/10917952?hl=en) |
| **Qué NO hacer v1** | Presupuesto, atribución, A/B, multi-avatar por campaña, fases custom, campañas de awareness siempre-on, amplificación pagada | Sobredimensionado para solopreneurs ([Sistava](https://sistava.com/en/insights/how-to-launch-a-product-without-a-marketing-team), [Shopify](https://www.shopify.com/blog/marketing-for-solopreneurs), [Etsy](https://www.etsy.com/seller-handbook/article/22815438793)) |

## 3. Spec borrador de campañas para Papandi

### 3.1 Modelo de datos

```sql
-- Una campaña = un pico finito sobre el plan evergreen: evento + ventana + concepto (+ oferta).
create table project_campaigns (
  id              uuid primary key default gen_random_uuid(),
  project_id      uuid not null references projects(id) on delete cascade,
  avatar_id       uuid not null,            -- v1: una campaña pertenece a UN avatar (sus 2.2/2.4/2.5)
  name            text not null,            -- "4 de Julio 2027"
  slug            text not null,            -- kebab, utm_campaign-ready: "4-de-julio-2027"
  concept         text not null,            -- la big idea en 1-2 frases (capa ESCENA/tema)
  offer           text,                     -- la oferta si la hay ("15% con código JULY4"), null = sin promo
  event_id        text,                     -- RadarEvent.id / project_event que la ancla (null = fecha propia)
  starts_on       date not null,            -- default: event.date - lead_time_days
  peak_on         date not null,            -- el día del evento / lanzamiento
  ends_on         date not null,            -- default: peak_on (+1 si offer — el "day after")
  policy_overrides jsonb not null default '{}',  -- {"Email": 2, "Instagram": 3} solo dentro de la ventana
  kit_variant     jsonb,                    -- {character_image_url, set_image_url, prompt, approved} | null = kit base
  hooks           jsonb not null default '[]',   -- ganchos propios de la campaña (≤5), mismo shape que 2.5
  pieces          jsonb not null default '[]',   -- ver CampaignPiece; v1 jsonb (patrón artifacts), tabla hija si crece
  color           text not null default '#E63946',
  status          text not null default 'draft', -- draft | signed | done
  signed_at       timestamptz,
  created_at      timestamptz not null default now(),
  unique (project_id, slug)
);
```

```ts
// Una pieza de campaña — NUEVA (no re-etiqueta derivados de 2.4), pertenece a una sola campaña.
export type CampaignPiece = {
  piece_id: string;
  phase: "teaser" | "peak" | "close";
  channel: string;              // solo canales encendidos en 2.2
  kind: string | null;          // reel, email, pin… (mismo vocabulario que 2.4)
  intent: "dar" | "pedir";      // teaser→dar, peak/close→pedir (editable)
  hook_id: string | null;       // de 2.5 (seasonal primero) o de campaign.hooks
  note: string | null;          // el QUÉ HACER de la pieza (accionable, sin jerga)
  date: string;                 // YYYY-MM-DD dentro de la ventana
};

// PlanSlot gana un campo (retro-compatible):
//   campaign_id: string | null   — null = slot evergreen; con valor = pinta chip del color de la campaña.
```

**Reglas del modelo** (espejo de lo investigado):
- Una pieza pertenece a UNA campaña (regla HubSpot); los derivados de 2.4 nunca se anexan a campañas.
- `slug` único por proyecto y estable: es el futuro `utm_campaign`.
- `hooks` de campaña expiran con `ends_on` (temporalidad = ventana); nunca entran a la rotación fuera de ella.
- `kit_variant.approved` obligatorio antes de generar cualquier video/imagen de campaña (contrato rodaje-kit).
- Campañas solapadas: permitidas pero con warning (surface, no reconciliar) si comparten canal y día.

### 3.2 Flujo UI de creación (desde el calendario)

1. **Entrada A (la principal):** clic en un evento del calendario → el drawer del evento gana el botón
   **"Montar campaña sobre esta fecha"**. Prefill: `name` = evento + año, ventana desde
   `lead_time_days`, `peak_on` = fecha del evento. **Entrada B:** botón "＋ Campaña" → elige fecha
   propia (crea el project_event personal si no existe — mismo flujo que "＋ Tu fecha" hoy).
2. **Paso 1 — Concepto:** nombre, la big idea en 1–2 frases, oferta opcional (texto + si termina con
   "día después"), ventana editable (default 2 semanas evento / 4 lanzamiento). Glass-box: se explica
   qué hará cada fase.
3. **Paso 2 — Piezas:** Papandi propone el reparto por fase×canal (solo canales encendidos de 2.2,
   rampa hacia el pico, `intent` marcado dar/pedir): cada pieza con su gancho (seasonal de 2.5
   primero; opción de generar ≤5 ganchos propios del concepto) y su nota accionable. El usuario
   quita/añade/edita. Se muestra el ratio del mes CON la campaña (dar:pedir desglosado evergreen /
   campaña) — transparencia, no candado.
4. **Paso 3 — Look (opcional):** variante temática del kit (misma cara, escena del tema — prompt
   editable, generar → aprobar). Si se salta, kit base.
5. **Firmar:** status → `signed`; el calendario pinta la banda del rango con el color + chips en los
   slots. Al pasar `ends_on`, status → `done` (automático) y sus ganchos expiran.

### 3.3 Convivencia con el plan evergreen (los slots)

- **Cálculo puro, mismo patrón:** `buildCampaignSlots(campaign): PlanSlot[]` (fechas explícitas por
  pieza — la campaña no usa cadencias) + `mergePlans(evergreen, campaigns[])` que aplica los topes:
  dentro de la ventana el tope efectivo por canal/día es `max(CHANNEL_MAX_PER_DAY, policy_overrides)`;
  fuera, el default. Determinista, sin LLM, testeable como `plan.test.ts`.
- **Prioridad:** en un día lleno, la pieza de campaña gana el hueco y la evergreen ESPERA (usa el
  mecanismo de estiramiento que ya existe — la cola se corre a la siguiente fecha elegible) y el
  conflicto se reporta en `warnings`, nunca en silencio. Razón: la campaña es por definición el
  contenido con fecha; el evergreen es finito pero sin caducidad.
- **El plan sigue siendo finito y honesto:** la campaña añade N slots con principio y fin; al
  terminar, el calendario vuelve al plan base sin residuos. Nada de contenido infinito.
- **Ratio:** los slots de campaña llevan `intent`; la vista mensual muestra dar:pedir del mes
  combinado y por origen. El 3:1 firmado se evalúa sobre el mes completo (decisión §2).
- **Ganchos:** dentro de la ventana `rotateHook` ya prefiere seasonal; los ganchos propios de la
  campaña participan solo en sus piezas (no contaminan la rotación evergreen).

## 4. Fuentes

**Oficiales / documentación de producto**
- HubSpot KB — Create campaigns: https://knowledge.hubspot.com/campaigns/create-campaigns
- HubSpot KB — Associate assets: https://knowledge.hubspot.com/campaigns/associate-assets-and-content-with-a-campaign
- HubSpot KB — Campaign templates: https://knowledge.hubspot.com/campaigns/campaign-templates
- Buffer Help — Creating and managing tags: https://support.buffer.com/article/585-creating-and-managing-tags
- Buffer Help — Tracking tag performance (slug conserva "campaigns"): https://support.buffer.com/article/535-tracking-the-performance-of-your-campaigns
- Buffer Help — Tags en mobile (ex "campaigns"): https://support.buffer.com/article/634-creating-and-managing-campaigns-on-the-mobile-app
- Buffer Help — UTM parameters: https://support.buffer.com/article/518-understanding-utm-parameters-and-google-analytics
- Hootsuite Help — Organize campaigns with tags (vía extractos, página requiere JS): https://help.hootsuite.com/hc/en-us/articles/1260804248950-Organize-campaigns-with-tags
- Hootsuite Help — Create and manage content campaigns (vía extractos): https://help.hootsuite.com/hc/en-us/articles/1260804251710-Create-and-manage-content-campaigns
- Planable — Product (labels/filtros): https://planable.io/product/
- Planable Help — Labels (403 al fetch; vía extractos): https://help.planable.io/en/articles/1563941-labels
- Later Help — Glossary (labels de media library): https://help.later.com/hc/en-us/articles/360043360953-Later-Glossary
- Later — Social media scheduler: https://later.com/social-media-scheduler/
- CoSchedule Support — Marketing Campaigns: https://coschedule.com/support/marketing-calendar/marketing-campaigns/marketing-campaigns
- CoSchedule — Organize campaigns blog: https://coschedule.com/blog/organize-marketing-campaigns
- Google Analytics — URL builders (utm_campaign): https://support.google.com/analytics/answer/10917952?hl=en
- Klaviyo — When to send Black Friday emails: https://www.klaviyo.com/blog/when-to-send-black-friday-emails
- Klaviyo — 4th of July marketing: https://www.klaviyo.com/blog/4th-of-july-marketing
- Etsy Seller Handbook — Holiday marketing tips: https://www.etsy.com/seller-handbook/article/22815438793
- Etsy Seller Handbook — Prepare your shop: https://www.etsy.com/seller-handbook/article/30953650830
- Etsy Seller Handbook — Seller holiday checklist: https://www.etsy.com/seller-handbook/article/1401252562091
- Shopify — Marketing for solopreneurs: https://www.shopify.com/blog/marketing-for-solopreneurs

**Estudios / datos**
- Buffer — Social media frequency guide (datos propios): https://buffer.com/resources/social-media-frequency-guide/
- Buffer — How often to post on Instagram (2M posts): https://buffer.com/resources/how-often-to-post-on-instagram/
- Binet & Field explicados — Growth Method: https://growthmethod.com/long-and-short/ · VXTX: https://www.vxtx.co.uk/blog/mastering-the-60-40-marketing-mix-how-peter-field-les-binets-framework-maximizes-roi
- Contraargumento (Byron Sharp / Ehrenberg-Bass): https://marketingscience.info/news-and-insights/prof-byron-sharp-skewers-binet-tells-marketers-to-sack-agencies-preaching-share-of-voice
- Datos de integración citados por Creativepool: https://creativepool.com/magazine/workshop/campaign-ideas-that-actually-work-what-makes-the-best-advertising-campaigns

**Agencias / prácticas documentadas**
- Sprout Social — Social media campaigns guide: https://sproutsocial.com/insights/social-media-campaigns/
- Hustler Marketing — BFCM pre-launch checklist: https://www.hustlermarketing.com/blog/the-complete-black-friday-cyber-monday-pre-launch-checklist/
- systeme.io — Resumen Product Launch Formula (Jeff Walker): https://systeme.io/blog/product-launch-summary
- Product Launch Strategy — Cart close sequence: https://productlaunchstrategy.org/how-to-structure-your-product-launch-cart-close-sequence/
- Jeff Walker — PLF secrets: https://jeffwalker.com/my-secrets-to-consistent-success-with-product-launch-formula/
- The Creative Company — 7 steps product launch: https://thecreativecompany.com/7-steps-to-plan-launch-a-new-product-on-social-media/
- SociallyIn — 5-phase launch framework: https://sociallyin.com/resources/social-media-strategy-for-product-launch/
- Prefinery — Prelaunch campaign on social: https://www.prefinery.com/blog/referral-programs/prelaunch-campaign/social-media-3/
- Metricool — Product launch guide: https://metricool.com/social-media-product-launch/
- Smart Insights — Big idea (4 pasos): https://www.smartinsights.com/traffic-building-strategy/campaign-planning/four-steps-developing-big-idea-campaign/
- Ogilvy — Five principles multichannel: https://www.ogilvy.com/ideas/five-principles-optimize-multichannel-campaigns
- Smart Insights — Always-on marketing: https://www.smartinsights.com/conversion-optimisation/conversion-optimisation-strategy/always-on-marketing/

**Opinión / blogs (marcados como tal en el texto)**
- The Escape — Always-on vs campaign: https://www.the-escape.co.uk/insights/what-is-the-difference-between-always-on-and-campaign-based-marketing
- Pitch — Always-on vs burst: https://www.pitchonnet.com/pitch-feature/always-on-vs-burst-campaigns-what-are-marketers-choosing-39277.html
- Campaign del Mar — Why you need both: https://www.campaigndelmar.com/blog/always-on-marketing-versus-campaigns-why-you-need-both-but-not-equally
- Impremis — Campaign duration: https://impremis.com/blogs/how-long-should-a-marketing-campaign-last
- Oyova — Consideration campaign weeks: https://www.oyova.com/blog/how-many-weeks-consideration-campaign-ads/
- Your Marketing People — Awareness ads weeks: https://yourmarketingpeople.com/how-many-weeks-for-awareness-campaign-ads-meta-and-google/
- Loomly — Posting schedule: https://www.loomly.com/blog/social-media-posting-schedule
- Kivopost — Posting cadence: https://kivopost.com/glossary/strategy-growth-frameworks/posting-cadence
- MEAN — Launch timeline startups: https://blog.mean.ceo/social-media-launch-timeline-startups/
- Brenton Way — 80/20 rule: https://brentonway.com/social-media-80-20-rule/
- The SMMU — Content mix (4-1-1, tercios): https://www.thesmmu.com/post/social-media-marketing-content-mix-finding-the-right-balance
- LikeMind Media — 70-20-10: https://www.likemind.media/70-20-10-rule-in-marketing/
- Gary Vaynerchuk — Jab, Jab, Jab, Right Hook (libro): https://www.amazon.com/Jab-Right-Hook-Story-Social/dp/006227306X · resumen: https://www.shortform.com/summary/jab-jab-jab-right-hook-summary-gary-vaynerchuk
- MarTech — Modern big idea: https://martech.org/whats-big-idea-3-fundamentals-successful-digital-creative/
- Sistava — Launch without a marketing team: https://sistava.com/en/insights/how-to-launch-a-product-without-a-marketing-team
- Alkai — Independence Day post ideas: https://www.alkai.ai/post/15-independence-day-social-media-post-ideas
- Jetpack — 4th of July posts: https://jetpack.com/resources/4th-of-july-social-media-posts/
- Indeed — Types of marketing campaigns: https://www.indeed.com/career-advice/career-development/types-of-marketing-campaigns
