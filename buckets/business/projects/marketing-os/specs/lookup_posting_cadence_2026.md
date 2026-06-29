# LOOKUP — Cadencias y ventanas de publicación por canal (research 2026)

**Status:** referencia viva (Pattern B: defaults por estudio + calibración con datos propios del usuario en Phase 4) · **Origen:** mandato del operador 2026-06-12 ("busca en el corpus y a profundidad en internet") tras corregir la cadencia de rrss en la matriz 2.2 (D-043, DB `096d20a6`). · **Ampliado 2026-06-28:** + LinkedIn/YouTube/Pinterest/Facebook, + el modificador **B2B vs B2C**, + la meta-regla — semilla del **calendario del Estudio** (`spec_Estudio_Produccion_Publicacion.md §6.5`).
**Regla de notación:** las cadencias SIEMPRE se escriben "N por semana/día" — nunca "N/sem" (la ambigüedad ya costó una ronda).
**Persistencia:** este doc (referencia narrativa) + best_practice `LOOKUP-TABLE posting_cadence` en pretel-os (descubrible cross-producto).

---

## Lo que dice el corpus propio (curso 7 — RRSS con IA)

Sin números de cadencia, pero con la doctrina que los gobierna:

- **7-11-4** (ya FLAG-3 del sistema): la confianza que compra exige ~7 horas de exposición + 11 interacciones + 4 impactos directos al dolor → **la frecuencia no es vanidad, es el mecanismo de confianza**.
- **Watch-time es la métrica rey** de los algoritmos (tiempo de visualización, tasa de finalización).
- Hábitos: calendario de contenido + revisión de métricas + montarse en tendencias de formato/audio cuando tenga sentido.
- Lógica por plataforma: YouTube = extenso/educativo · TikTok = viralidad rápida, primeros segundos decisivos · Instagram = visual versátil (Stories + Reels + feed coherente). "No estar en todas por igual, sino elegir según objetivo y audiencia" — ahora bajo la regla D-042 (grandes superficies ON por defecto; excluir exige caso escrito).
- Formatos: 9:16 TikTok/Reels/Stories · 16:9 YouTube · 1:1 feed.

## Cadencias por canal (estudios 2026)

| Canal | Piso de lanzamiento | Meta | Techo/alerta | Evidencia |
|---|---|---|---|---|
| **TikTok** | 3-5 por semana | **1 por día** (1-3/día = sweet spot) | >5 por DÍA diluye alcance + riesgo shadowban 3-14 días | Buffer (11M+ posts): 2-5/sem = +17% views/post; 11+/sem = +34% (JoinBrands) |
| **Instagram** | 3 feed por semana + Stories ligeras diarias | 4-5 feed/sem + ~4 Reels | calidad > cantidad; el engagement entrena al algoritmo, no el volumen solo | consenso 2026 (PostEverywhere, ImageWorks) |
| **Foros/Reddit** | 2-3 participaciones por semana | escucha diaria ligera (15 min + 1 respuesta con sustancia) | las comunidades castigan frecuencia-sin-valor | guía Reddit small-biz 2026: canal de ESCUCHA e intención, no de frecuencia |
| **Email** | 1 por semana (mismo día/hora — el hábito es del lector) | 1/sem + secuencias automáticas | la fatiga se mide en bajas, no en opiniones | rango sano semanal–2x/sem; consistencia > frecuencia |
| **Blog/SEO** | 1 por semana | 1-2 por semana | bursts no compensan pausas | resultados reales a 3-6 meses de constancia (Firstep 2026) |
| **LinkedIn** | 2-3 por semana | 2-5 por semana | >1 por DÍA se canibaliza (compiten por la misma audiencia) | 2-5/sem = +1,180 impresiones/post vs 1/sem (HeyOrca/Kanbox 2026, 4.8M posts) |
| **YouTube** | 1 por semana | 1/sem (o 1 c/2 sem si la calidad es alta) | — | Shorts constantes = +67% subs |
| **Pinterest** | 3 por semana | 5 por semana | — | tráfico evergreen; los pins compounden como SEO |
| **Facebook** | 1 por día | 1-2 por día | low-effort hiere el alcance | 1 post fuerte/día basta |

## Ventanas óptimas (SIEMPRE hora local de la audiencia)

| Canal | Mejores ventanas | Peores |
|---|---|---|
| TikTok | mar-vie 14:00-18:00 (Sprout, ~2B engagements) · **sábado mejor día** (Buffer 7.1M — videos, carruseles y text posts) | madrugadas |
| Instagram | mar 13:00-19:00 · mié 12:00-21:00 · mejor hora única: **mié 11:00** (Hootsuite) | **fines de semana** (los más débiles en casi todas las industrias — Sprout) |
| Foros | la ventana es del hilo caliente, no del reloj (responder rápido hilos de trigger) | — |
| Email | mar-jue por la mañana; calibrar con open_rate propio | — |
| LinkedIn | **mar-jue 8:00-10:00** (+ 11:00-17:00) — curva B2B | lun temprano · vie tarde |
| YouTube | **14:00-16:00** entre semana · 9:00-11:00 finde | — |
| Pinterest | mañanas entre semana **8:00-12:00** (fuerte toda la tarde) | madrugadas |
| Facebook | **8:00-10:00 y 19:00-21:00**, mar-jue | finde en grupos de negocio |
| General (todos) | **mar-jue 9:00-12:00**; **miércoles** el mejor día | — |

## Principios transversales

1. **Escalera de cadencia**: arrancar en el piso sostenible → subir a la meta cuando el flujo ruede → los datos propios calibran (Phase 4). Consistencia > rachas (3/sem sostenidas > 7 una semana y 0 la siguiente).
2. **Cross-platform por diseño (D-047; refinado C16 2026-06-27)**: la misma pieza ancla alimenta varias redes con entregables **SEPARADOS**, pero el formato lo decide **el canal Y el avatar**, NO un mapa fijo — IG admite Reels/video además de carrusel; *"IG=imágenes / TikTok=video"* era un **EJEMPLO, no ley** (C16). La atomización (2.4) produce cada derivado en el formato que ese canal×avatar usa.
3. **Viable solo con piezas listas**: estas cargas asumen que Papandi entrega cada pieza hecha (carrusel desde plantilla = minutos). Sin eso, son sobre-compromiso (flag de la matriz).
4. **Trigger de notificaciones (mandato, task `7493e337`)**: cada slot del calendario notifica al usuario CON el copy listo adentro; "publicado" alimenta la medición. Nace en Phase 3.

## El gran modificador: B2B vs B2C (el "tipo de usuario objetivo") — estudio 2026-06-28

El mismo producto publica en horarios **OPUESTOS** según a quién le hable:
- **B2B** (coaches, consultores, freelancers de servicio): horas laborales, entre semana, **mañanas 8-10h**; LinkedIn-pesado. (DevriX, Hashmeta 2026)
- **B2C** (compradores handmade, consumidores, lifestyle): todo el día, fuerte en **tardes/noches 18-21h + fines de semana**; IG/Pinterest. (Sprout 2026)
- **Matiz Instagram:** B2C peaks **18-21h**; B2B peaks **11-13h** (scroll de almuerzo). El MISMO canal, distinta hora según la audiencia.

→ La semilla del calendario se calibra por **tipo de avatar (B2B/B2C) × nicho × canal × zona horaria** (de `avatars[].where_we_meet` + el tipo del avatar). NO es un horario genérico para todos.

## La meta-regla (todos los estudios coinciden)

Los promedios de arriba son **la SEMILLA, no la verdad**. El óptimo real sale de los **analytics del PROPIO usuario** ("haz A/B 4 semanas con tu audiencia"). Por eso es **Pattern B**: arranca con estos defaults calibrados por avatar → **Phase 4 mide cuándo SÍ interactuó su audiencia → el calendario se mueve a las horas REALES de ese usuario**. Semilla → mide → afina (el loop perpetuo del Estudio, `spec_Estudio_Produccion_Publicacion.md §6.5`).

## Fuentes

- [Buffer — How often to post on TikTok (11M+ posts)](https://buffer.com/resources/how-often-should-you-post-on-tiktok/) · [Buffer — Best time to post on TikTok (7.1M)](https://buffer.com/resources/best-time-to-post-on-tiktok/)
- [Sprout Social — Best times to post 2026](https://sproutsocial.com/insights/best-times-to-post-on-social-media/) · [Sprout — Instagram](https://sproutsocial.com/insights/best-times-to-post-on-instagram/) · [Sprout — TikTok](https://sproutsocial.com/insights/best-times-to-post-on-tiktok/)
- [JoinBrands — TikTok posting schedule 2026](https://joinbrands.com/blog/how-often-to-post-on-tiktok/) · [PostEverywhere — by platform](https://posteverywhere.ai/blog/how-often-to-post-on-social-media) · [ImageWorks 2026](https://www.imageworkscreative.com/blog/how-often-post-social-media-2026)
- [ALM Corp — Reddit small business guide 2026](https://almcorp.com/blog/reddit-small-business-marketing-guide-social-media-trends/) · [Firstep — SEO small business 2026](https://firstepbusiness.com/blog/seo-best-practices-for-a-small-business-2026-guide)
- **Ampliación 2026-06-28:** [HeyOrca — frecuencia por plataforma 2026](https://www.heyorca.com/blog/social-media-posting-frequency-by-platform-2026) · [DevriX — B2B posting](https://devrix.com/tutorial/b2b-posting-social-media/) · [Buffer — State of Social 2026 (52M posts)](https://buffer.com/resources/state-of-social-media-engagement-2026/) · [Kanbox — LinkedIn 4.8M posts](https://www.kanbox.io/blog/best-times-to-post-on-linkedin)
