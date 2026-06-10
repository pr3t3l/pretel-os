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
- **SIGUIENTE (3 carriles):** (a) build slice "Phase 0 wizard" en `sandia-marketing` (chat nuevo per Overall_WF §How-To-Start); (b) pre-código en pretel-os: formalizar guiones 0.2–0.4 en §6 Setup Agent + run→CAG #4 + eval fixtures; (c) sim Phase 1 (Oferta: value equation desde anxieties de avatares, pricing créditos con dependencia parqueada del modelo de costo IA, naming 1.4).
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
