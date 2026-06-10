# Sandi / Marketing-OS — SESSION STATE (handoff)

**Última actualización:** 2026-06-10
**Propósito:** doc de retoma. Si una sesión futura (o Claude tras perder contexto) llega aquí, esto dice qué es el proyecto, qué specs existen, qué se decidió, y qué falta. **El trabajo real vive en git (`pretel-os/main`); este doc es el índice.**

---

## 1. Qué es

**Sandi** = SaaS AI-first que guía a NO-expertos de "tengo una idea" a "tengo estrategia de marketing accionable". Implementación en `C:\Users\prett\Documents\sandia-marketing` (Next.js + Supabase; M0 AI-first rebuild + migración avatars/strategies).

**Diferenciador (la joya):** orquestación paralela multi-avatar — N avatares, cada uno con su estrategia versionada y su loop Phase 1→5.

**Arquitectura: 2 módulos entrelazados** (D-019) que comparten la Foundation de Phase 0:
- **Módulo A — Business Case** (BMC 9 bloques, `spec_Business_Case_BMC.md`, STUB) — ¿es viable el negocio?
- **Módulo B — Marketing OS** (Phases 0–5) — ¿cómo se vende?
Se ensamblan **entretejidos e invisibles** (el usuario solo conversa; el BMC se arma detrás).

## 2. Specs (en `specs/`, todos en git)

- `Overall_WF.md` — documento maestro: diferenciador, jerarquía, Strategy Lifecycle, Flag Registry vivo, 3 patrones de extensión (A Extensible Vocabulary, B Context-Adjusted Threshold, C Evolving Schema), privacidad 3-capas, conexión humana + memoria de agente, co-creación generativa, Quality at Depth, mapeo Phase↔artifact_phase, **log de decisiones D-001…D-020**.
- `spec_Phase_0_Research_ICP.md` · `spec_Phase_1_Oferta.md` · `spec_Phase_2_Contenido.md` · `spec_Phase_3_Distribucion.md` · `spec_Phase_4_Medir.md` · `spec_Phase_5_Ajustar.md`
- `spec_Phase_0_Setup_Agent.md` — capa conversacional guiada (6 movimientos, wizard, glass-box, educación, memoria).
- `SOUL_setup_agent.md` — carácter Sage/Mentor portable (model-agnostic).
- `spec_Business_Case_BMC.md` — Módulo A (STUB).
- `corpus_audit_and_retrieval.md` — auditoría del corpus + pipeline de recuperación.

## 3. Principios clave (resumen de decisiones)
- Flag registry **vivo** (semilla + diagnóstico abierto + promoción), no hardcode.
- Sin refresh por calendario; foundation se reconstruye por evidencia (`foundation_drift`).
- 3 patrones de extensión para no congelar el mundo abierto (vocabularios, umbrales, esquemas).
- Privacidad: T1 datos crudos (nunca salen) / T2 artefactos tenant / T3 aprendizaje global solo abstracto + cross-tenant.
- Conexión humana **portable** (carácter+patrones+memoria+evals), no del modelo. SDT = lealtad.
- **Co-creación generativa** = la esencia: Sandi co-desarrolla la idea (propone, construye sobre, empuja), no extrae. Usuario siempre autor.
- **Quality at Depth**: especialistas + retrieval + corpus-audit + gates + evals + profundidad adaptativa (no un mega-prompt).

## 4. Run de Sandi (`run/sandi/`)
- 0.1 Business Context ✅ (`business_context.json`) · 0.2 Mercado ✅ (`demand_quantification.md`, research web real) · 0.2.5 ICP ✅ v2 (`icp.json`, D-023 / DB `05ec4413`, supersede D-022 — beachhead: expertos en lo suyo, oferta propia ya monetizando, no saben empezar/escalar su marketing online, >1 público).
- 0.3 ✅ (D-025/026/027): persona + 4 avatares (Dana/Marcus/Priya/Héctor) + 2 negative personas + Priya 1er ciclo. 0.4 ✅ (D-028): scan 4 canales, hueco = categoría propia (multi-público core + loop guiado; ciclo 1 = "marketplace independence"; nunca "AI marketing tool").
- 🏁 **PHASE 0 CERRADA (D-029, 2026-06-10):** `product_brief_v2.json` firmado (gate global passed; LTV 500/CAC 165; 3 hipótesis refutadas, 0 críticas). **Build trigger D-024 DISPARADO.** 2 lessons auto-aprobadas (`076747df`, `d88bf6b5`). Flags abiertos no bloqueantes: pre-launch cluster, Ad Library manual, keyword volumes Capa 3.
- **BUILD EN CURSO (carril a — decisión del operador 2026-06-10):** mandato = UX como goal principal ("como los iPhone"). Specs: `spec_UX_Experience.md` (7 principios + patrón canónico + motion tokens) y `build_plan_phase0_wizard.md` (M1–M6; B1 híbrido guion+LLM, B2 CSS-first, B3 dogfood realtor app — las 3 aprobadas).
  - ✅ **M1 HECHO** (sandia-marketing `5648d15`, pusheado): motion system completo + WizardShell (stepper endowed, Paso N de M, draft chip) + HelpPanel glass-box + 5 componentes del alma (SandiBeat/SourceChip/ProposalCard/GateSignature/ThinkingNarration) + `lib/wizard/config.ts` (mapa Phase 0, labels llanos: terreno/mercado/puerta/personas/cancha) + demo `/dev/ux` verificada visualmente (preview: flow, firma 2 pasos, transición direccional, chips dato-vs-inferencia). Fixes pre-existentes: themeColor→viewport, hydration warning del theme script. `npm run verify` verde.
  - ✅ **M2 HECHO** (sandia-marketing `f110780`, pusheado): **Supabase smoke passed** — proyecto Cloud `qxhfmsojpjmnlzaduzao` ACTIVE_HEALTHY; **migración `avatars_strategies` aplicada vía MCP** (faltaba — drift cazado); tipos TS des-driftados (`ArtifactPhase` no tenía phase_0..5). Slice 0.1 completo: `business-context.ts` (schema seed v1 espejo del run), `terreno-script.ts` (guion validado como datos: 4 preguntas llanas + flags por reglas: hybrid→líder, freemium→patrón nombrado, impulso→inferencia etiquetada, internacional→propuesta de foco), `TerrenoWizard` (6 movimientos funcionando, draft persistente por respuesta, firma de gate → artifact signed), ruta `/projects/[id]/phase-0` con HelpPanel, dashboard des-roto (links /setup muertos → /phase-0). 8 tests del guion — **cazaron bug real del gate** (impulsivo+one_shot+nacional daba <2 implicaciones). 14/14 verde.
  - ✅ **DOGFOOD 0.1 COMPLETADO (2026-06-10):** el operador corrió el wizard real con **Healthy Families** (su app real — ¡run manual #2 de BP-001 arrancado orgánicamente!) y **firmó el primer gate humano del producto** (G-Phase-0.1 passed, verificado en DB: idea + B2C/reflexivo/subscription/internacional + foco "Estados Unidos, inglés" + 3 implicaciones). El recorrido cazó 3 bugs reales, todos arreglados mismo día (sandia `ee8ceff`+`bb595d2`): (1) RLS INSERT...RETURNING vs policy de membership-por-trigger (lesson `08ebe0bb` auto-aprobada — aplica a healthy-families repo también); (2) faltaba pedir LA IDEA del negocio (etapa nueva al inicio, gate la exige); (3) "Ajustar" de la propuesta de foco no hacía nada (ahora captura país/idioma → metadata.launch_focus, Pattern C).
  - ⚠️ **Gaps conocidos para M3:** (a) editar respuestas DESPUÉS de firmar no re-abre el gate (viola "decisión firmada se enmienda, no se edita" — añadir re-open o lock post-firma); (b) `flags_raised` es append-only (rastro de conversación, no estado final — documentar semántica o limpiar al cambiar respuesta).
  - ⏭️ **SIGUIENTE (M3):** 0.2 "Tu mercado" — show-and-confirm con ThinkingNarration + research real del territorio capturado (Healthy Families: apps de bienestar familiar, US/EN) + 0.2.5 "Tu puerta" con ProposalCards. El primer cliente del research ya existe y es real.
  - Pendientes que siguen: (b) formalizar guiones 0.2–0.4 + CAG/evals; (c) sim Phase 1.
- Sirve de ejemplo CAG + fixture de eval.

## 5. Corpus de conocimiento (en `docs/`, copia worktree `C:\Users\prett\Pretel-OS\...`)
- **7 cursos** "Marketing Documentacion Teorica": 1 Fundamentos (+glosario), 2 Análisis de mercado (→Phase 0), 3 SEO, 4 SEO Avanzado, 5 SEM (paid), 6 Email, 7 RRSS. ~110 archivos (PDF/docx + prompts + .zip blueprints).
- **BMC** (3 PDFs): Osterwalder "Generación de modelos de negocio" (~285p) + Business Model Canvas + ed. 2010. → Módulo A.
- Binarios NO en git (copyright + bloat); solo texto procesado entra a la KB.

## 6. Trabajo abierto
- [x] **HECHO:** pase autónomo de corpus — validado (specs = superset, 8.0–9.0, cero contradicciones; `corpus_validation_report.md`) + aplicado (Tanda 0 + enriquecimientos + 10 flags aprobados, D-021). Síntesis en `specs/corpus_knowledge/` (local, IP).
- [ ] **PENDIENTE:** validar Phase 1 contra corpus (su agente falló); decidir FLAG-7 (test 2-de-5) + FLAG-8-activo.
- [x] **HECHO:** 0.2.5 ICP cerrado en v2 (D-023 supersede D-022, gate re-firmado): `own_craft_offer_monetized` + `multi_audience` + `diy_going_online`; 2 deal-breakers; B2B parked; cierra BMC bloque 1.
- [ ] **RETOMAR:** simulación 0.3 (persona + avatares — la joya); incluye `negative_personas` (claims-incompatibles) y priorización de primer ciclo (2 decisiones humanas per spec). Ver `HANDOFF.md`.
- [ ] **BUILD (`C:\Users\prett\Documents\sandia-marketing`):** doble carril — la sim valida specs Y prepara el build. **Trigger LOCKED (D-024 / DB `7100edf0`):** codear el slice "Phase 0 wizard" cuando la sim cierre Phase 0 completa (0.3 + 0.4 + gate global); luego pipeline con un paso de desfase (codear N mientras se simula N+1). Pre-código: formalizar guiones 0.2–0.4 + ejemplo CAG #4 + fixtures de eval (caso D-023). PhaseHandlers (V2+) gateados por `8b32a77b` + BP-001. Dogfood propuesto (no decidido): apps propias del operador como runs #2–#3.
- [ ] Spec completo del Módulo A (BMC) tras la simulación.
- [ ] Build: extracción→estructura→validación→índice del corpus (RAG); especialistas por fase; evals.

## 7. Cómo retomar
1. Lee este doc + `Overall_WF.md` (§decisiones).
2. Mira `run/sandi/run_log.md` para dónde va la simulación.
3. Si hay un reporte de validación del corpus, aplícalo respetando el boundary.
