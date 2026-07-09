# _INDEX — El mapa de TODA la documentación de marketing-os

**Qué es:** el índice maestro del árbol documental completo (`specs/` + `docs/` + raíz). UNA línea por
documento: especie · qué es · estado. Si buscas algo, empieza aquí — no abras 43 archivos.
**Regla de mantenimiento:** todo doc nuevo, renombrado o archivado actualiza su línea aquí **en el mismo
commit**. Un doc que no está en el índice no existe.
**Última revisión completa:** 2026-07-09 (se leyeron los 58 docs para clasificarlos).

**Leyenda de estados:** 🟢 ley (autoridad vigente) · ✍️ para firma · 💡 propuesta (no es ley) ·
📊 dato vivo · ✅ ejecutado · ⏳ pendiente de build · 📚 fundacional (rara vez cambia) · ⚰️ archivado.

---

## 0. Si vas a leer poco, lee esto (orden)

1. `Overall_WF.md` — el ciclo completo (fases 0-5, jerarquía proyecto→avatar→estrategia).
2. `spec_Modelo_Contenido.md` — **C17 firmado**: PILAR → ÁNGULO → PIEZA (la unidad de todo).
3. `spec_Superficies_Produccion.md` — dónde se produce/vive/agenda (Ángulos · Media · Agenda).
4. `_audit_change_ledger.md` — C1–C18: cada cambio de doctrina con su porqué.

---

## 1. 🟢 LA LEY — specs vigentes (13)

| Doc | Qué decide |
|---|---|
| `Overall_WF.md` | El workflow maestro: fases 0-5, strategy lifecycle, flags, patrones de extensión. Living doc, al día C17. |
| `spec_Modelo_Contenido.md` | **C17 FIRMADO 2026-07-06** — el ángulo es la unidad; pieza = ángulo × canal; plan generativo; cascada de diagnóstico. |
| `spec_Superficies_Produccion.md` | Autoridad de las 3 superficies (`/angulos` `/media` `/agenda`) + `scheduled_posts` + pipeline de calidad. |
| `spec_Phase_0_Setup_Agent.md` | El contrato conversacional del wizard (6 movimientos, co-crear, wizard guiado ≠ chat libre). |
| `spec_Phase_0_Research_ICP.md` | Fase 0: contexto de negocio + mercado medido + ICP (v1.6 + doctrina v1.8). |
| `spec_Phase_1_Oferta.md` | Fase 1: economía, ecuación de valor, paquete, garantía, precio/statement (v1.8 — residuos C1 anotados en ledger). |
| `spec_Phase_2_Contenido.md` | Fase 2 v2.0 C17: voz, mix, matriz, pilares (con ancla+ratio), ÁNGULOS. El más gordo (97K). |
| `spec_Phase_3_Distribucion.md` | Fase 3 publicar/distribuir (pre-C17 + nota: la superficie es la Agenda). |
| `spec_Phase_4_Medir.md` | Fase 4: métricas por estrategia (`results_summary`, funnel por awareness, unit economics). |
| `spec_Phase_5_Ajustar.md` | Fase 5: el loop — no edita, emite Strategy #N+1 con la anterior superseded. |
| `spec_UX_Experience.md` | Los 7 principios UX (P1 una-cosa … P7) con ciencia + tokens de motion. |
| `spec_Inteligencia_Temporal.md` | El radar de fechas (5 capas, ofensiva+higiene). Motor EN PRODUCCIÓN; superficies remapeadas C17. |
| `spec_Admin_Cost_Intelligence.md` | Módulo C: la vista admin (costos LLM/media/storage, billing) — backlog de 13 capacidades. |

## 2. ✍️ PARA FIRMA — borradores esperando al operador (2)

| Doc | Qué propone |
|---|---|
| `spec_Phase_Identidad.md` | La fase Identidad: identidad visual con firma + bibliotecas vivas de personajes/sets (cast) + gates. |
| `spec_Campanas.md` | Campañas C17: pico finito sobre el evergreen (concepto+oferta+arco 3 fases; `campaign_id`; cascada de cast). |

## 3. 💡 PROPUESTAS — capturadas, NO son ley (3)

| Doc | Qué propone |
|---|---|
| `spec_AI_Gateway_Wrapper_PROPOSAL.md` | La capa de generación imagen/video: `generate()` único, esquemas canónicos, dialectos por motor (v0.2). |
| `spec_Production_Support_and_Pricing_PROPOSAL.md` | `production_mode` por pieza + pricing por modo (v0.1; re-expresado a ángulo×canal). |
| `spec_Business_Case_BMC.md` | STUB del Módulo A (BMC/Osterwalder 9 bloques) — spec completo en pase dedicado. |

## 4. 📊 LOOKUPS — datos vivos, semilla→medición (3)

| Doc | Qué cura |
|---|---|
| `lookup_posting_cadence_2026.md` | Cadencias, topes/día y ventanas por canal (B2B/B2C). |
| `lookup_event_calendar_2026.md` | Momentos comerciales + `lead_time` + quién los explota (lo civil lo da la librería de holidays). |
| `lookup_visual_hooks_2026.md` | Los 13 ganchos visuales de apertura (espejo/razón de `visual-hooks.ts`). |

## 5. 🔧 BUILD PLANS — el registro de ejecución (9)

| Doc | Estado |
|---|---|
| `build_plan_modelo_contenido.md` | ✅ P1-P5 ejecutados (P3/P4 superados por Agenda — banner). |
| `build_plan_estudio_angulos.md` | ✅ ejecutado — la página `/angulos`. |
| `build_plan_media_calendario.md` | ✅ ejecutado — Media + Agenda + `scheduled_posts` (Fase C). |
| `build_plan_inteligencia_temporal_calendario.md` | ✅ M1-M5 ejecutados (M4 superficie jubilada por Agenda — banner). |
| `build_plan_phase0_wizard.md` | ✅ ejecutado — el wizard de Fase 0. |
| `build_plan_produccion_v3_motor_coherencia.md` | 🟡 F1 ✅ (StyleID+Gateway); F2+ pendiente. Banner C17. |
| `build_plan_fase_identidad.md` | ⏳ pendiente (B1a `cast.ts` hecho; B1b/B2/B3 tras la firma del spec). |
| `build_plan_etapa_G_video.md` | ⏳ backlog output-side (8 botones + post-producción; aprobado 2026-07-06). |
| `build_plan_experiencia_canonica.md` | 📚 doctrina de interacción del wizard (v2, del transcript CAG) — base del build actual. |

## 6. 📚 METODOLOGÍA & CORPUS — fundacional (8 + carpeta)

| Doc | Qué es |
|---|---|
| `quality_armor_model_agnostic.md` | Las 10 capas de blindaje de calidad agnóstico al LLM (guiones, CAG, schemas, gates, evals). |
| `SOUL_setup_agent.md` | El carácter de Papandi (sage/mentor, valores, never-dos) — portable entre modelos. |
| `cag_step_beat_canonical.md` | LOCKED — la anatomía de 8 movimientos del beat de paso («el mensaje 1000 de 10») + variante B. |
| `cag_transcript_fase1_fase2.md` | LOCKED — el transcript literal fuente de la experiencia canónica (61K). |
| `corpus_phase_coverage_map.md` | LOCKED — mapa corpus→fases (qué curso alimenta qué paso; divergencias intencionales anotadas). |
| `corpus_validation_report.md` | Validación specs↔corpus (2026-06-25; el corpus es piso, no autoridad). |
| `corpus_audit_and_retrieval.md` | Auditoría v1 del corpus + diseño del pipeline de retrieval (2026-06-07). |
| `corpus_knowledge/` | Las 8 síntesis destiladas (7 cursos + BMC) — el conocimiento ya procesado. |

## 7. docs/app — CÓMO está construida la app (5 + archive)

| Doc | Qué es |
|---|---|
| `ensamblador-de-prompts.md` | El compilador de 2 etapas (firmado→brief→prompt→media): inventario campo-a-campo + 10 fixes. Snapshot 2026-07-02 reconciliado C17 (banner). |
| `design-system.md` | Tokens/reglas visuales. ⚠️ dice «Sandi» — pendiente del sweep de renombrado a Papandi. |
| `design-audit-2026-07.md` | Auditoría de diseño de las 11 rutas (2026-07-02 + nota C17: falta auditar las 3 superficies nuevas). |
| `model-selection.md` | Ruteo tarea→modelo (multi-proveedor, benchmarks, regla del 95%). |
| `README.md` | Índice de docs/app. |
| `archive/` | Notas de ejecución históricas (declassified-execution, overnight-progress, pipeline-de-ideas ⚰️). |

## 8. docs/research — INVESTIGACIONES con fuentes (5)

| Doc | Qué responde |
|---|---|
| `campanas-marketing-real.md` | R1: cómo funcionan las campañas reales (tipos, arco, ratio, herramientas). §1/§2 vigentes; §3 superseded por `spec_Campanas`. |
| `doctrina-por-canal.md` | Formato/estructura/gates de media POR canal (fuentes oficiales + estudios grandes). |
| `doctrina-video-2026.md` | Qué retiene en video: 8 personalizaciones, captions, safe zones, costos. |
| `2026-07-01_market_strategy_scope.md` | El scope estratégico: el mercado rechaza lo no-verificable; motor de coherencia ≠ playground. |
| `2026-07-01_video_field_of_action.md` | El campo de acción de video (qué pueden los generadores, qué permiten las plataformas, qué retiene). |

## 9. FUENTES CRUDAS — el corpus de origen

| Ruta | Qué es |
|---|---|
| `docs/Marketing Documentacion Teorica/` | Los 7 cursos fuente (PDF/DOCX, ES). |
| `docs/BMC/` | 3 PDFs de Osterwalder (BMC) — fuente del Módulo A. |
| `_corpus_extracted/` | Los .txt extraídos de los PDFs (derivados, regenerables con `_extract_corpus.py`). |

## 10. META — el registro del proyecto

| Doc | Qué es |
|---|---|
| `_audit_change_ledger.md` | **C1–C18**: cada cambio de doctrina con su porqué y dónde aterrizó. El registro madre. |
| `_INDEX.md` | Este mapa. |

## 11. ⚰️ specs/archive/ — muertos y cerrados (se conservan, no se leen como vigentes)

| Doc | Por qué está aquí |
|---|---|
| `spec_Estudio_Produccion_Publicacion.md` | SUPERSEDED por `spec_Superficies_Produccion` (C17; doctrina buena ya cosechada). |
| `build_plan_estudio_produccion.md` | SUPERSEDED — construía el Estudio viejo. |
| `_c17_doc_reconciliation.md` | Work-order de la reconciliación C17 — ✅ COMPLETADO 2026-07-09 (registrado como C18). |
| `_audit_report_2026-06-25.md` | Reporte puntual de la auditoría C1-C14 (su contenido vive en el ledger). |
| `HANDOFF.md` · `HANDOFF_SIM_PAPANDI_DESDE_CERO.md` | Handoffs de sesión (jun-2026) — históricos. |
| `SESSION_STATE.md` | El «índice» viejo (2026-06-12) — reemplazado por este _INDEX. |
| *(en docs/app/archive/)* `pipeline-de-ideas.md` | SUPERSEDED — describía las ~28/derivados 2.4. |

## Raíz del proyecto

| Doc | Qué es |
|---|---|
| `CLAUDE.md` | Instrucciones de sesión para Claude en este proyecto. |
| `README.md` | Auto-generado por la capa de awareness (L2) — **no editar las secciones auto a mano**. |
| `_extract_corpus.py` | Script que regenera `_corpus_extracted/` desde los PDFs. |
