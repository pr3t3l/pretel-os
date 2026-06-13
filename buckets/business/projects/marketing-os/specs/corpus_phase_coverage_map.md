# Mapa de cobertura Corpus ↔ Fase (qué teoría DEBE vivir en cada pantalla)

**Status:** mapa de auditoría LOCKED como herramienta de la simulación-de-cero de Papandi (mandato del operador 2026-06-13: *"use `_corpus_extracted` toda la info para saber qué cargar en cada una de las fases y asegurarnos que lo tenemos todo incluido"*).
**Para qué sirve:** cada pantalla del wizard se audita contra su fila aquí — si un concepto del corpus que le toca a esa fase no está cubierto (ni en el spec, ni en el guion, ni en la propuesta del producto), es un hueco a llenar. Es el checklist de completitud, pantalla por pantalla.
**Fuente:** los 7 cursos + BMC en `_corpus_extracted/` (mapeados 2026-06-13). El corpus es el cuerpo de teoría; este doc dice dónde aterriza cada pieza.

---

## Cómo leerlo

Por cada fase: (1) **cursos que la alimentan**, (2) **los conceptos del corpus que la pantalla DEBE cubrir**, (3) **el artefacto del producto donde aterriza**, (4) **prompts/plantillas del corpus reutilizables**. En la sim-de-cero, cada paso se firma SOLO cuando su fila está cubierta — o el hueco queda declarado.

> Regla de oro del corpus (Curso 7, RRSS): **7-11-4** — ~7 horas de exposición · 11 interacciones · 4 impactos directos al dolor antes de que alguien confíe y compre. Gobierna las cadencias de Fase 2/3.

---

## FASE 0 — Research + ICP (`product_brief_v2.json`)

**Cursos:** 1 Fundamentos · 2 Análisis de Mercado (el núcleo) · BMC (bloques Customer Segments + Value Proposition como semilla).

| Concepto del corpus | Dónde aterriza (pantalla / artefacto) | ¿Cubierto hoy? |
|---|---|---|
| **Definición de objetivo** (qué resultado de negocio) | 0.1 Tu negocio · `business_context` | ✅ idea + diferenciadores + monetización |
| **Análisis de la demanda con IA** (volumen, intención de búsqueda, saturación) | 0.2 Tu mercado · `demand_quantification` (math gate, semáforo) | ✅ research web real |
| **Bases de un buen análisis** (datos demográficos/psicográficos/conductuales/económicos) | 0.2 + 0.3 | ⚠️ verificar que las 4 capas de datos se piden |
| **Buyer Persona vs Avatar** (modelo semi-ficticio vs representación humanizada) | 0.3 Tu cliente ideal + Tus avatares · `personas` | ✅ persona primario + avatares (distinción explícita) |
| **Análisis de activadores de la compra** (triggers que mueven a la decisión) | 0.3 (triggers del avatar) → insumo de Fase 1 urgencia | ⚠️ verificar que los triggers se capturan POR avatar |
| **Análisis de punto de dolor** (barreras emocionales y racionales) | 0.3 (pains con fuente real) | ✅ 6 dolores con fuente en el run |
| **Análisis de la competencia con IA** (qué hacen, huecos, posicionamiento) | 0.4 Tu competencia · `cancha` (rivales con precio + huecos + veredicto rojo/azul) | ✅ web search real |
| **Propuesta de valor: relevancia · diferenciación · credibilidad** | 0.4 (hueco elegido = semilla de posicionamiento) → Fase 1 | ⚠️ los 3 tests de la PdV deben aparecer explícitos |
| **BMC bloque 1-2** (Customer Segments + Value Proposition) | se arma detrás (Módulo A entretejido) | ⚠️ confirmar que 0.x alimenta el BMC invisible |

**Decisiones humanas obligatorias (no algorítmicas):** negative_personas + avatar de primer ciclo (spec Phase 0).

## FASE 1 — Oferta (`offer_spec.json` + `offer_statement.md`)

**Cursos:** 2 Análisis de Mercado (propuesta de valor) · BMC (Revenue Streams + Cost Structure) · 1 Fundamentos (value equation, objeciones).

| Concepto del corpus | Dónde aterriza | ¿Cubierto hoy? |
|---|---|---|
| **Value equation** (sueño × probabilidad ÷ tiempo ÷ esfuerzo) | 1.1 La ecuación de valor · `value_equations` | ✅ por avatar encendido (D-039) |
| **Propuesta de valor afinada** (relevancia/diferenciación/credibilidad probada) | 1.2 El paquete · `offer_stack` | ✅ stack con comparables citados |
| **Activadores de compra → urgencia honesta** | 1.3 Garantía y urgencia · `risk_urgency` | ✅ urgencia real con regla de retiro |
| **Manejo de objeciones / punto de dolor → garantía** | 1.3 (risk reversal) | ✅ garantía honrable + honesty check |
| **BMC Revenue Streams** (bait-hook, tiered, subscription) | 1.4 Precio · `offer_spec.pricing` | ✅ suscripción + Beats; **estudio de precio real (cazado 2026-06-12)** |
| **BMC Cost Structure** (fijo vs variable, escalabilidad) | 1.2 (costo de servir) · **desglose de costo por patrón** | ✅ cost-estimate (marginal + pasarela en código) |
| **Posicionamiento** (el hueco del 0.4 → ángulo) | 1.x estrategias + 1.4 statement | ✅ separate_strategies + statement |
| **Language pack** (frases literales del research del cliente) | 1.4 (key_phrases) — método estándar | ✅ USER-CORRECTED como regla |

## FASE 2 — Contenido (`content_plan.json` + `content_assets/`)

**Cursos:** 1 Fundamentos (customer journey, AIDA) · 3 SEO · 6 Email · 7 RRSS (el núcleo de contenido).

| Concepto del corpus | Dónde aterriza | ¿Cubierto hoy? |
|---|---|---|
| **Bases de marca / identidad** (RRSS: voz, pilares de mensaje, tono) | 2.0 Tu voz · `brand_voice` (arquetipo + promesa + léxico + reglas testeables) | ✅ |
| **Customer journey / niveles de conciencia** (awareness → consideration → decision) | 2.1 El reparto · `content_mix` (4 momentos mentales + reparto) | ✅ |
| **Estrategia de contenido** (valor antes de vender; educar/entretener/inspirar) | 2.1 + 2.3 | ✅ ratio dar:pedir + pilares |
| **Arquitectura de canal** (SEO captura · RRSS marca · Email nurturing · SEM inmediato) | 2.2 La matriz · `channel_journey_matrix` | ✅ grandes superficies ON por regla |
| **Cadencias por plataforma + 7-11-4** (Curso 7 + lookup) | 2.2 (cadencias "N por semana" con fuentes) · `lookup_posting_cadence_2026` | ✅ corpus + estudios |
| **Plataforma-específico** (YouTube long-form · TikTok 3seg/video · IG visual) | 2.2 + 2.4 (IG=imágenes / TikTok=video) | ✅ entregables separados |
| **Pilares de contenido** (territorios por fuerza psicológica) | 2.3 Los 4 pilares · `pillars` (REFORZAR/RESOLVER) | ✅ |
| **Atomización / repurposing** (1 pieza → N derivados; YouTube→shorts) | 2.4 La multiplicación · `atomization_map` (1→6) | ✅ |
| **SEO: intención de búsqueda + keyword clustering + E-E-A-T** | 2.x (pilar SEO + ancla larga) | ⚠️ **verificar:** intención de búsqueda y E-E-A-T explícitos en el pilar SEO |
| **Email: lead magnets + flujos (onboarding/nurturing/sales)** | 2.2 (canal email) + Fase 3 | ⚠️ **verificar:** los 3 flujos de email + lead magnet declarados |
| **Ganchos / primeras 3 frases (3seg)** | 2.5 La biblioteca · `hook_library` (≥10/pilar, ≥4 plantillas) | ✅ |
| **Análisis de competencia en RRSS** (qué postean, huecos) | hereda de 0.4 | ⚠️ ¿se reusa el scan de 0.4 para el tono de contraste? |

## FASE 3 — Publicar / Distribuir (`distribution_plan.json`)

**Cursos:** 3 SEO + 4 SEO Avanzado · 5 SEM · 6 Email · 7 RRSS (ejecución + automatización).

| Concepto del corpus | Dónde aterriza | ¿Cubierto hoy? |
|---|---|---|
| **Tracking / atribución** (UTM, conversión) | 3.1 · `tracking_manifest` | ✅ (D-050: conversion=subscription_started) |
| **Exclusiones + targeting** (negative keywords, públicos) | 3.2 (pendiente sim) | ⏳ |
| **Calendario** (≥4 semanas, ratio por canal, ventanas) | 3.3 (pendiente) + notificaciones-con-copy | ⏳ task 7493e337 |
| **SEM: estructura de campaña + copys + landing** (Curso 5 + prompts) | 3.x paid (en pausa hasta post-beta) | ⏳ diferido |
| **Email: secuencias automáticas** (Curso 6 flujos) | 3.x | ⏳ |
| **SEO Avanzado: clustering, scraping, N8N** (Curso 4) | ejecución/automatización | ⏳ futuro |
| **Protocolo de ventanas** (landing que espera el evento) | 3.x | ⏳ |
| **Go-live** (gate humano SIEMPRE) | 3.4 | ⏳ |

## FASE 4 — Medir (`metrics_snapshot.json`)

**Cursos:** 5 SEM (informes, KPIs) · 4 SEO Avanzado (monitoreo) · 6 Email + 7 RRSS (métricas por canal).

| Concepto del corpus | Dónde aterriza | ¿Cubierto hoy? |
|---|---|---|
| **KPI primario = dinero** (revenue_attributed) | 4.x | ⏳ spec existe |
| **Métricas por canal** (SEO: posición/tráfico · Email: apertura/CTR · RRSS: guardados/compartidos · SEM: CPA/ROAS) | 4.x | ⏳ cada fila de la matriz ya declara su métrica |
| **Análisis de informes con IA** (Curso 5 C10) | 4.x | ⏳ |

## FASE 5 — Ajustar / Optimizar (`optimization_plan.json`)

**Cursos:** 5 SEM (A/B, pujas) · 4 SEO Avanzado · 6/7 (refinamiento).

| Concepto del corpus | Dónde aterriza | ¿Cubierto hoy? |
|---|---|---|
| **A/B testing + refinamiento** | 5.x | ⏳ |
| **Recalibración de cadencia/ratio por fatiga** | 5.x → re-trigger Fase 2 | ⏳ |
| **Re-triggers hacia atrás** (drift → Fase 0) | 5.x | ✅ doctrina (re-triggers en spec) |
| **Ganchos: jubilar perdedores con datos** | 5.x → `hook_library` performance | ✅ diseñado (perf_status) |

---

## Prompts / plantillas del corpus listos para reutilizar (capa 3 — CAG)

El corpus trae plantillas de prompt probadas — candidatas a alimentar los prompts del producto (no reinventar):
- **SEM:** generador de títulos/descripciones · creador de landing · analista senior de Google Ads · propuestas Meta.
- **Email:** ideación de ebook · índice de webinar · optimizador de asuntos (GPT-BIG-Asuntos) · variantes de copy. + ejemplos de buena/mala respuesta.
- **RRSS:** creación de script viral · análisis de competencia · conversión YouTube→shorts · cualificación de lead potencial · prompts Claude-específicos.
- **Análisis de mercado:** prompts de análisis de demanda (C3) · workflow completo.

## Huecos a auditar en la sim-de-cero (lo ⚠️ de arriba, consolidado)

1. **Fase 0:** las 4 capas de datos (demo/psico/conductual/económico) · triggers POR avatar · los 3 tests de la propuesta de valor explícitos · que 0.x alimente el BMC invisible.
2. **Fase 1:** (ya robusto tras las cazadas del 2026-06-12 — estudio de precio + desglose de costo).
3. **Fase 2:** intención de búsqueda + E-E-A-T en el pilar SEO · los 3 flujos de email + lead magnet · reuso del scan de competencia para el tono de contraste.
4. **Fases 3-5:** existen como spec, no como build — se construyen al ritmo de la sim (regla D-051).

> Este mapa es vivo: a medida que la sim-de-cero pasa pantalla por pantalla, cada ⚠️ se cierra (cubierto) o se documenta como diferido con su razón.
