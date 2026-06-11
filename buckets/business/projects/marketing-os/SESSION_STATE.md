# Sandi / Marketing-OS — SESSION STATE (handoff)

**Última actualización:** 2026-06-10
**Propósito:** doc de retoma. Si una sesión futura (o Claude tras perder contexto) llega aquí, esto dice qué es el proyecto, qué specs existen, qué se decidió, y qué falta. **El trabajo real vive en git (`pretel-os/main`); este doc es el índice.**

---

## 1. Qué es

**PROD: https://sandia-marketing.vercel.app** (Vercel git-integration: cada push a main despliega solo; env vars + Supabase Auth URLs configurados por el operador 2026-06-10). **Sandi** = SaaS AI-first que guía a NO-expertos de "tengo una idea" a "tengo estrategia de marketing accionable". Implementación en `C:\Users\prett\Documents\sandia-marketing` (Next.js + Supabase; M0 AI-first rebuild + migración avatars/strategies).

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
  - ✅ **M3a HECHO** (sandia `87d7571`): 0.2 "Tu mercado" end-to-end — route `/api/phase0/market-research` (RLS como usuario, exige gate 0.1, Claude sonnet + web_search server tool, 503 honesto sin llave), `demand_quantification` seed v1 (verified-con-fuente SEPARADO de inferencias etiquetadas, math gate a la vista, semáforo), MercadoStep (ThinkingNarration → cards con SourceChips → firma G-0.2 → re-run), enrutamiento real de pasos por estado de artifacts en la página. **BLOQUEADOR del operador: falta `ANTHROPIC_API_KEY` en `.env.local`** — sin ella el research muestra el estado honesto y no inventa.
  - ✅ **Multi-proveedor (mandato operador 2026-06-10, sandia `f647794`):** llaves Anthropic+OpenAI+Google+OpenRouter en .env.local (ojo: `OPENROUTE_API_KEY` sin R — soportada igual). Router en el swap-point: claude-*→Anthropic directo (caching+web_search), resto→OpenRouter. `models.ts` = tarea→modelo (defaults conservadores + candidatos: Kimi K2.5 $0.60/M para beats/copy, DeepSeek V4 Flash $0.14/M para extraction). `docs/model-selection.md` = benchmarks jun-2026 con fuentes + **diseño del experimento** (golden set del run + juez ciego + costo de project_llm_calls + regla 95%-calidad). Pendiente: correr el harness de evals (sesión dedicada) y formalizar ganadores como decisión.
  - ✅ **M3b HECHO** (sandia `0a63864`): 0.2.5 "Tu puerta" — route `icp-proposal` (exige 0.1+0.2 firmados, usa `modelForTask("strategy")` vía el router), `icp.ts` seed v1 (filtros con estado por-tarjeta; gate ≥3 MH + ≥2 DB aceptados + evidence_basis), PuertaStep (Sandi propone / usuario dispone tarjeta por tarjeta con Ajustar inline SIEMPRE funcional, contadores vivos vs mínimos, firma G-0.2.5), enrutado en página + educación "todos no es un nicho". **Corrección del operador aplicada: techo de strategy = Sonnet, NUNCA Opus** (créditos = costo variable; calidad extra via prompts/retrieval — en models.ts + doc). 19/19 tests.
  - ✅ **IDEA CO-WORK (sandia `5cdb87a`) — D-018 cableado a pedido del operador:** la idea ya no se extrae, se co-desarrolla. Flujo: idea → ¿nueva o en marcha? (+pegar material si camina) → 2-3 preguntas profundas ADAPTIVAS (Sandi infiere el tipo: SaaS→funciones, craft→qué hace al tuyo distinto, servicio→especialidad, marketplace→por qué seguirte fuera) → tarjetas de diferenciadores (✓/✏️/✕) + refined_idea + why_now. Gate 0.1 exige ≥1 diferenciador aceptado. **Research 0.2 y Puerta 0.2.5 consumen los diferenciadores firmados** (el estudio busca TU cancha). Briefs firmados pre-cowork se RE-ABREN explícitamente (status→draft + beat de Sandi + re-firma — enmienda, no edición silenciosa: cierra gap (a) para este camino). 21/21 tests. REFINADO (sandia `3845174`): doc-paste FUERA del flujo base (bomba de contexto/costos; candidato premium), extracción ITERATIVA con juicio de suficiencia del modelo (a-d: qué es/funciones, para quién, qué lo hace distinto, cómo gana) + TOPE DURO 3 rondas server-side (control de costos); al juzgar sólida → auto-encadena diferenciadores. Pendiente operador: evaluación de rentabilidad/costos operativos por plan.
  - ⏭️ **SIGUIENTE:** operador reinicia server (`npm run dev`) → dogfood HF completo: co-work de idea (pegar specs de hf_v3) → re-firma 0.1 → research 0.2 real → puerta 0.2.5 → M4 "Tus personas" + 0.4 → gate global → evals multi-modelo.
  - Pendientes que siguen: (b) formalizar guiones 0.2–0.4 + CAG/evals; (c) sim Phase 1.
- Sirve de ejemplo CAG + fixture de eval.

## 5. Corpus de conocimiento (en `docs/`, copia worktree `C:\Users\prett\Pretel-OS\...`)
- **7 cursos** "Marketing Documentacion Teorica": 1 Fundamentos (+glosario), 2 Análisis de mercado (→Phase 0), 3 SEO, 4 SEO Avanzado, 5 SEM (paid), 6 Email, 7 RRSS. ~110 archivos (PDF/docx + prompts + .zip blueprints).
- **BMC** (3 PDFs): Osterwalder "Generación de modelos de negocio" (~285p) + Business Model Canvas + ed. 2010. → Módulo A.
- Binarios NO en git (copyright + bloat); solo texto procesado entra a la KB.

## 6. Trabajo abierto
- [x] **HECHO:** pase autónomo de corpus — validado (specs = superset, 8.0–9.0, cero contradicciones; `corpus_validation_report.md`) + aplicado (Tanda 0 + enriquecimientos + 10 flags aprobados, D-021). Síntesis en `specs/corpus_knowledge/` (local, IP).
- [x] **HECHO 2026-06-11:** Phase 1 validada contra corpus (8.5, superset, cero contradicciones; spec v1.6 con E1-E6; D-030; addendum en `corpus_validation_report.md`). Siguen sin decidir (sin presión): FLAG-7 (test 2-de-5) + FLAG-8-activo.
- [x] **HECHO:** 0.2.5 ICP cerrado en v2 (D-023 supersede D-022, gate re-firmado): `own_craft_offer_monetized` + `multi_audience` + `diy_going_online`; 2 deal-breakers; B2B parked; cierra BMC bloque 1.
- [ ] **RETOMAR:** simulación 0.3 (persona + avatares — la joya); incluye `negative_personas` (claims-incompatibles) y priorización de primer ciclo (2 decisiones humanas per spec). Ver `HANDOFF.md`.
- [ ] **BUILD (`C:\Users\prett\Documents\sandia-marketing`):** doble carril — la sim valida specs Y prepara el build. **Trigger LOCKED (D-024 / DB `7100edf0`):** codear el slice "Phase 0 wizard" cuando la sim cierre Phase 0 completa (0.3 + 0.4 + gate global); luego pipeline con un paso de desfase (codear N mientras se simula N+1). Pre-código: formalizar guiones 0.2–0.4 + ejemplo CAG #4 + fixtures de eval (caso D-023). PhaseHandlers (V2+) gateados por `8b32a77b` + BP-001. Dogfood propuesto (no decidido): apps propias del operador como runs #2–#3.
- [ ] Spec completo del Módulo A (BMC) tras la simulación.
- [ ] Build: extracción→estructura→validación→índice del corpus (RAG); especialistas por fase; evals.

## 7. Cómo retomar
1. Lee este doc + `Overall_WF.md` (§decisiones).
2. Mira `run/sandi/run_log.md` para dónde va la simulación.
3. Si hay un reporte de validación del corpus, aplícalo respetando el boundary.

## 8. Prod dogfood nocturno 2026-06-10/11 (resumen rapido)
- Operador corrio EN PRODUCCION (sandia-marketing.vercel.app) el flujo completo: cowork de idea (HF: "cuida el grafo entero" - posicionamiento real co-creado) -> re-firma 0.1 -> research 0.2 con web search REAL firmado -> puerta 0.2.5 firmada.
- 6 fixes mismo dia via pipeline push->autodeploy (sandia 6af4f9a..221ea9a): haiku id invalido, errores visibles, ids-numericos (Postel), Ajustar en diferenciadores, correcciones-del-usuario MANDAN en prompts downstream (original preservado), reparador JSON tolerante en las 3 rutas LLM + brevedad research.
- M4a SHIPPED (221ea9a): 0.3 "Tus personas" in-app - persona primario + avatares 2-de-3 + anti-personas + eleccion de primer ciclo + gate G-0.3. Falta: dogfood de 0.3 por operador + M5 (0.4 Tu cancha) + rollup gate global in-app.
- M5a SHIPPED (sandia 7e8d4d1): 0.4 "Tu cancha" in-app - rivales con precios y fuentes via web search, sustitutos, veredicto rojo-azul, huecos como tarjetas, eleccion del hueco (semilla de posicionamiento Phase 1), gate G-0.4. Operador firmo G-0.3 (personas de HF) en prod. PHASE 0 IN-APP COMPLETA al firmar 0.4. Proxima sesion: dogfood 0.4 + rollup/celebracion Phase 0 + arranque Phase 1 (Oferta) + evals multi-modelo + costos.
- 2026-06-11: OPERADOR CONFIRMO PHASE 0 IN-APP COMPLETA (los 5 gates firmados en prod con Healthy Families). Rename 0.4 -> "Tu competencia" (sandia 3d14252). SIGUIENTE SESION = PHASE 1 OFERTA, en este orden (pipeline D-024): (1) SIM de Phase 1 en pretel-os (formato wizard Sandi como Phase 0: value equation desde anxieties de avatares del run, offer stack, pricing creditos con el modelo de costo IA parqueado desde 0.1, naming 1.4 = nombre definitivo de Sandi; spec_Phase_1_Oferta.md v1.5 + corpus pendiente de validar - cabo suelto #1 del HANDOFF); (2) de la sim salen los guiones -> build del step Oferta en sandia (nace la entidad strategies, D-009/010: per-avatar). Tambien pendientes: rollup/celebracion Phase 0 in-app, evals multi-modelo, sesion de costos.
- 2026-06-11 (sesion 3, en curso): Phase 1 validada vs corpus (v1.6, D-030 - cabo R5 cerrado). SIM Phase 1 abierta: G-PRE 10/10; 1.1 Priya FIRMADA 960/debil con bloqueo blando sancionado (D-031, weakest=likelihood); batch Dana 1260 / Marcus 1680 / Hector 672 + multi_avatar_decision (separate_strategies - la evidencia confirma D-009) + strat_priya_v1 (demand_type=mixed, 1er uso E1) PROPUESTOS esperando firma del set. Insight estructural: likelihood debil x3 = el stack 1.2 se construye alrededor de PRUEBA. Luego: 1.2 stack + pricing creditos (costos reales de project_llm_calls) + 1.3 + 1.4 naming.
