# LOOKUP — Cadencias y ventanas de publicación por canal (research 2026)

**Status:** referencia viva (Pattern B: defaults por estudio + calibración con datos propios del usuario en Phase 4) · **Origen:** mandato del operador 2026-06-12 ("busca en el corpus y a profundidad en internet") tras corregir la cadencia de rrss en la matriz 2.2 (D-043, DB `096d20a6`).
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

## Ventanas óptimas (SIEMPRE hora local de la audiencia)

| Canal | Mejores ventanas | Peores |
|---|---|---|
| TikTok | mar-vie 14:00-18:00 (Sprout, ~2B engagements) · **sábado mejor día** (Buffer 7.1M — videos, carruseles y text posts) | madrugadas |
| Instagram | mar 13:00-19:00 · mié 12:00-21:00 · mejor hora única: **mié 11:00** (Hootsuite) | **fines de semana** (los más débiles en casi todas las industrias — Sprout) |
| Foros | la ventana es del hilo caliente, no del reloj (responder rápido hilos de trigger) | — |
| Email | mar-jue por la mañana; calibrar con open_rate propio | — |

## Principios transversales

1. **Escalera de cadencia**: arrancar en el piso sostenible → subir a la meta cuando el flujo ruede → los datos propios calibran (Phase 4). Consistencia > rachas (3/sem sostenidas > 7 una semana y 0 la siguiente).
2. **Cross-platform por diseño**: el mismo carrusel = TikTok slideshow + IG carousel → 3 piezas alimentan 2 redes. La atomización (2.4) produce para este multiplicador.
3. **Viable solo con piezas listas**: estas cargas asumen que Papandi entrega cada pieza hecha (carrusel desde plantilla = minutos). Sin eso, son sobre-compromiso (flag de la matriz).
4. **Trigger de notificaciones (mandato, task `7493e337`)**: cada slot del calendario notifica al usuario CON el copy listo adentro; "publicado" alimenta la medición. Nace en Phase 3.

## Fuentes

- [Buffer — How often to post on TikTok (11M+ posts)](https://buffer.com/resources/how-often-should-you-post-on-tiktok/) · [Buffer — Best time to post on TikTok (7.1M)](https://buffer.com/resources/best-time-to-post-on-tiktok/)
- [Sprout Social — Best times to post 2026](https://sproutsocial.com/insights/best-times-to-post-on-social-media/) · [Sprout — Instagram](https://sproutsocial.com/insights/best-times-to-post-on-instagram/) · [Sprout — TikTok](https://sproutsocial.com/insights/best-times-to-post-on-tiktok/)
- [JoinBrands — TikTok posting schedule 2026](https://joinbrands.com/blog/how-often-to-post-on-tiktok/) · [PostEverywhere — by platform](https://posteverywhere.ai/blog/how-often-to-post-on-social-media) · [ImageWorks 2026](https://www.imageworkscreative.com/blog/how-often-post-social-media-2026)
- [ALM Corp — Reddit small business guide 2026](https://almcorp.com/blog/reddit-small-business-marketing-guide-social-media-trends/) · [Firstep — SEO small business 2026](https://firstepbusiness.com/blog/seo-best-practices-for-a-small-business-2026-guide)
