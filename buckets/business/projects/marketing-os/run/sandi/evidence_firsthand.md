# Sandi — Evidencia de primera mano (input del operador, 2026-06-10)

**Qué es:** casos reales del entorno personal del operador, aportados al abrir el retrato del persona (0.3). Anecdótico, no estadístico — vale como evidencia cualitativa (`evidence_basis`) y como banco de caras para los avatares. **Privacidad:** roles sin nombres; dato del operador (no entra a contenido público ni a aprendizaje global sin des-identificar).

## Casos

| # | Caso (rol) | Situación | ¿Pasa la puerta v2 (D-023)? | Avatar candidato |
|---|---|---|---|---|
| 1 | **El propio operador** | 2 apps PROPIAS terminadas (realtor; healthy families), cero ventas, no sabe cómo venderlas | ❌ hoy — oferta lista pero sin ingresos (falla `own_craft_offer_monetized`) | Cluster **"pre-launch"** (fuera de 1ª ola) |
| 2 | Amigos diseñadores en Amazon | Venden productos de diseño PROPIO en Amazon; les va regular; no saben vender fuera del marketplace | ✅ | **Estancado** — variante "enjaulado del marketplace" |
| 3 | Jardinero (servicio local) | Monetiza informal; intenta formar empresa; no sabe posicionarse | ✅ (borde: formalización en curso) | **Lanzador digital** |
| 4 | Hermano del operador (nutriólogo) | Empleado/dependiente; quiere independizarse; no sabe conseguir clientes propios | ❌ hoy — su oferta independiente aún no monetiza | Cluster "pre-launch" |
| 5 | Pareja del hermano (politóloga) | Misma situación que #4 | ❌ hoy | Cluster "pre-launch" |
| 6 | Repostera (entorno familiar) | Vende tortas, ya monetiza, cero marketing | ✅ | **Lanzador digital** (caso canónico — "la velera" real) |

## Lectura (glass-box)

1. **La puerta v2 se sostiene:** 3 de 6 casos entran limpio y encarnan los dos avatares hipótesis (repostera/jardinero → Lanzador digital; diseñadores Amazon → Estancado). La repostera es literalmente el ejemplo canónico que motivó D-023.
2. **Flag honesto — el cluster "pre-launch" insiste:** 3 de 6 casos (incluido el fundador) son "oferta lista/casi lista, cero ingresos" — fuera de la puerta firmada hace horas. **NO se reabre la puerta** (D-023 fresca; el boundary `idea_stage_boundary` los cubre): queda **flagueado** como patrón a vigilar en 0.4/research. Si el research de competencia muestra que ese segmento está igual de desatendido y alcanzable, será decisión del operador abrirlo como 2ª ola (o atenderlo vía Módulo A dentro del producto).
3. **Sub-variante detectada en Estancado:** "enjaulado del marketplace" (vende online pero en jardín ajeno: Amazon/Etsy; quiere canal propio). Trigger y lenguaje propios ("fees", "algoritmo de Amazon", "no controlo nada") → candidata a pasar el test 2-de-3 como variante o tercer avatar. Se evalúa en 0.3 con el retrato.
4. **Propuesta dogfood (no decidida):** las 2 apps del operador como **runs manuales #2 y #3** de la metodología (BP-001 exige ≥3 corridas reales antes de automatizar; generalización vía `product_brief.json` — nunca hardcodear para un producto). Mataría dos pájaros: valida la metodología fuera de Sandi-sobre-Sandi Y resuelve el marketing de las apps propias.
