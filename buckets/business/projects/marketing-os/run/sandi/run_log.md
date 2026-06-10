# Run: Sandi — log

**Qué es:** el primer run de la metodología marketing-os. Sandi (el sistema de marketing AI-first) usándose a sí mismo como caso de prueba. Sirve de ejemplo trabajado (CAG) + fixture de eval.

## Estado

| Fase | Sub-paso | Estado | Artefacto |
|---|---|---|---|
| Phase 0 | 0.1 Business Context | ✅ cerrado | `business_context.json` |
| Phase 0 | 0.2 Mercado | ✅ cerrado | `demand_quantification.md` |
| Phase 0 | 0.2.5 ICP | 🔄 en curso | `icp.json` (draft, pre-signoff) |
| Phase 0 | 0.3 Persona + Avatares | pendiente | — |
| Phase 0 | 0.4 Competencia | pendiente | — |
| Phase 1–5 | — | pendiente | — |

## Hechos clave capturados
- **Idea:** SaaS AI-first que guía a no-expertos de "tengo una idea" a "tengo estrategia de marketing accionable".
- **Diferenciador (la joya):** orquestación paralela multi-avatar — N avatares, cada uno con su estrategia versionada y su loop Phase 1→5.
- **Business context:** híbrido con lead B2C (individuos), ciclo reflexivo, suscripción+créditos, internacional con foco US/inglés, multimodal.
- **Nombre:** "Sandi" es working name (aleatorio); dudas por competencia/dominio → finalizar en Phase 1.4.
- **Mercado (0.2):** enorme (36M PYMEs, 5.6M nuevas/año, 29.8M solopreneurs); ~la mitad sin estrategia formal → **educar es la cuña**; espacio "AI marketing tool" saturado; `offer_strategy = create_demand`. Veredicto 🟢/🟡.
- **ICP (0.2.5, en curso):** beachhead confirmado por el operador = solopreneurs/creadores que venden su expertise y le hablan a >1 público (US, con ingreso, online-native — el multi-avatar les brilla). Draft de 3 must-have + 2 deal-breakers en `icp.json`, pendiente signoff + 2 flags chicos (hybrid_gate, db3_candidate).
- **Producto (principios definidos):** Setup Agent guiado (no chat libre); glass-box (no caja negra); educación adaptativa + `user_knowledge_profile`; conexión humana portable (SOUL + patrones + memoria + evals, model-agnostic); memoria de agente por proyecto (plan interno mutable + lessons/best-practices/decisions). Privacidad 3-capas.

## Dependencias parqueadas
- Modelo de costo de IA por avatar/ciclo → insumo de Phase 1 Pricing y del sistema de créditos.

## Notas
- Este run se construyó vía la simulación del Setup Agent (formato wizard guiado) — ver `specs/spec_Phase_0_Setup_Agent.md`.
