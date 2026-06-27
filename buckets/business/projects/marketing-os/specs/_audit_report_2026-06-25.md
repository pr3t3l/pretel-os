# Informe de auditoría de consistencia — Fase 0/1 → Fase 2 (2026-06-25)

Ancla: [_audit_change_ledger.md](./_audit_change_ledger.md) (C1–C14). 11 targets auditados, 71 hallazgos.

## Veredicto
La doctrina v1.8 (valor por funcionalidad, candado único = margen por delivery_format, ataque al eje débil por mecanismo + reversión de riesgo) **ya está en los intros y en el código del build**, pero NO bajó a los schemas, gates, algoritmos y artefactos históricos de los specs.

- **Focos rojos:** M1 spec (`spec_Phase_1_Oferta.md`) y `corpus_validation_report.md`. El M1 aún calcula contra `ratio_target`/`perceived_value_usd` y publica "Valor total $X"; el corpus **endosa activamente** el modelo viejo en vez de marcarlo como divergencia.
- **Build:** casi 100% alineado. Fase 1 UI/routes = limpio. Prompts/schemas = residuos cosméticos. **3 huecos reales en el build de Fase 2** (DataForSEO/C10, idioma/C14, anti-prueba-social/C4).

## Estado por target
| Target | Estado |
|---|---|
| M1 spec | 🔴 residuos críticos masivos (ratio/perceived_value en schema, gates, statement, pricing) |
| Corpus (validation + coverage map) | 🔴 contradice el registro; endosa el modelo viejo; falta marcar divergencia intencional |
| Build Fase 2 | 🟠 3 huecos críticos de código (DataForSEO, idioma, anti-prueba-social) |
| M0 spec | 🟡 1 crítico (prueba social en Forces) + DataForSEO V2→V1 + notas |
| M2 spec | 🟡 1 crítico (PILLAR_C testimonios) + C5/C14 notas |
| Overall_WF | 🟡 2 críticos C5 (strategies "mirrors offer_spec" + unified-vs-separate) + decisiones legacy |
| CLAUDE.md marketing-os | 🟢 falta regla híbrida C5 + punteros de versión |
| Build prompts / schemas | 🟢 casi limpio (docstrings, comentarios, defaults) |
| Build Fase 1 UI/routes | 🟢 100% limpio |
| Build docs (sandia) | 🟢 alineado por omisión |

## Plan de arreglo (6 tandas, orden = menos retrabajo)
1. **Sanear M1 spec** (la fuente canónica): limpiar schema `offer_stack` (quitar perceived_value/ratio, margen por delivery_format + proposed_rescore), reescribir el algoritmo offer-stack-builder, propagar a gates/signals/checklist/pricing/anchor/plantilla statement, quitar prueba social del value-equation-optimizer.
2. **Cerrar los 3 huecos de código de Fase 2** (paralelizables): C10 inyectar `keyword_intents` DataForSEO en `step-proposal/route.ts`; C14 pasar `statement.language` al system/dataBlock; C4 candado anti-prueba-social en `buildP2System` + retirar testimonios de PILLAR_C.
3. **Eliminar oferta-por-avatar a nivel datos (C5)**: Overall_WF L298 + L309-314, M2 `unified_C_avatar_specific_bonuses`, CLAUDE.md regla híbrida, docs/model-selection.
4. **Reescribir corpus_validation_report**: corregir L164/307 (críticos), añadir las 2 divergencias intencionales (C1, C4), freshness header; coverage map notas de divergencia.
5. **Alinear M0 + residuos cosméticos del build**: prueba social en Forces (crítico), DataForSEO V2→V1, math_gate≠precio; docstrings/comentarios/defaults.
6. **Decisiones históricas** (Overall_WF + CLAUDE): marcar D-031/032/034/035/036/038 superseded; D-006; punteros de versión a v1.8.

Los críticos están en las tandas 1, 2, 4. Las tandas 3-6 son normales/minor (trazabilidad).

> Informe sintetizado por el flujo `audit-fase-0-1-2` (run wf_132e8d90-328).
