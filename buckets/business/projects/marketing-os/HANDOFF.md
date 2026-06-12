# HANDOFF — Papandi / Marketing-OS (continuación de cowork · sesión 3 → 4)

**Para:** la próxima sesión de Claude (cambio de chat por ventana de contexto llena).
**De:** Claude + Alfredo (prettelv1@gmail.com), tras TRES sesiones de co-creación. La 3ª cerró Phase 1 y Phase 2 COMPLETAS en sim, bautizó el producto (**Papandi**), y terminó con la corrección más importante del proyecto (lee §3 antes que nada).
**Regla #1:** esto **NO es un proyecto nuevo. Es continuación.** No te re-presentes, no re-preguntes lo decidido. Lee esto + `SESSION_STATE.md` + `specs/build_plan_experiencia_canonica.md` + `specs/cag_step_beat_canonical.md` y retoma con la misma voz y relación.

---

## 1. CÓMO TRABAJAMOS (el contrato — ampliado en sesión 3)

- **Co-creación, no ejecución.** Socio de pensamiento: propone con porqués, construye sobre (yes-and), reta con respeto. Alfredo SIEMPRE es el autor; sus correcciones MANDAN (van "USER-CORRECTED" en prompts/specs).
- **Glass-box siempre.** Toda cifra con fuente; inferencias etiquetadas; errores reconocidos y decompuestos (la sesión 3 tuvo varios — cada uno reconocido sumó confianza).
- **Voces marcadas:** `## 🔧 Claude` (meta/ingeniería) vs `## 🍉 Sandi — sim` (el personaje). Mandato explícito del operador.
- **El beat canónico ("mensaje 1000 de 10")** — `specs/cag_step_beat_canonical.md` variantes A y B: TODA presentación de paso sigue los 8 movimientos (apertura → instrumento → TU-dato-citado → propuesta-con-porqué → candados-con-margen → en-cristiano → ask-con-guardarraíl → conversación). El operador pidió replicarlo "exactamente en cada parte".
- **Capa usuario sin maquinaria:** cero D-xxx/códigos/JSON al usuario ("como ya firmaste"; estantería, no JSON — si la pantalla muestra llaves {}, está rota).
- **Regla sim→app (D-051):** cada paso cerrado en sim se siembra a prod + gana su vista + **se revisa EN la app antes de seguir**.
- **Disciplina:** commitea a `pretel-os/main` Y `Sandia-Marketing/main` a medida que avanzas (cada push a sandia = deploy a prod); `npm run verify` antes de cada commit; mensajes por archivo temporal; **al final de cada push: `git -C C:/Users/prett/Documents/pretel-os pull --ff-only`** (el operador navega ESA copia — se quedó atrás una vez y "perdió" archivos).
- Cadencias se escriben "N por semana" (nunca "N/sem"). Decisiones D-xxx + lessons via MCP pretel-os SIEMPRE (vamos en D-053).

## 2. QUÉ ES + ESTADO REAL

**Papandi** (ex-Sandi — D-037: nombre acuñado por el operador, papandi.com COMPRADO y sirviendo prod; historia familiar del nombre = PRIVADA, jamás en copy público) = SaaS AI-first que guía de "tengo una idea" → "estrategia accionable". **PROD: papandi.com / sandia-marketing.vercel.app** (repo `C:\Users\prett\Documents\sandia-marketing`).

**Sim (run/sandi/, la metodología validándose a sí misma):** Phase 0 ✅ (D-029) · **Phase 1 ✅ (D-030..D-038**: ecuación, estrategias separadas/strat_priya_v1, stack 11.1×/76%, garantía incondicional + urgencia-con-retiro + displacement, $30+Beats+puerta gratis, PAPANDI, statement EN) · **Phase 2 ✅ (D-040..D-049**: voz sage+caregiver, mix 15/30/40/15, matriz 5 canales con cadencias-por-estudio, 4 pilares REINFORCE/RESOLVE, atomización con pieza A_001 PRODUCIDA + guion TikTok, 40 hooks) · **Phase 3 abierta: 3.1 tracking ✅ (D-050**; conversion=subscription_started $30); faltan 3.2 exclusiones → 3.3 calendario+notificaciones → 3.4 go-live.

**Build (sandia):** Phase 0 wizard completo + hub del proyecto + Fase 1 interactiva (M7a) + T1 experiencia canónica (StepChat + guiones + pasos 2-3) + visor Fase 2 (estantería de hooks) + breadcrumbs/lifecycle navegables. Seed: 14 artefactos del sim en prod (script `.claude/seed_sim_phase2.mjs`).

**Doctrina nueva de la sesión 3 (toda USER-CORRECTED, ya en specs):** aperturas de fase 0-5 canónicas · nunca-un-número-antes-que-su-instrumento (falló 2 veces antes de ser regla) · ancla con referentes VIVIDOS del avatar (no herramientas desconocidas) · quotes literales del research = estándar de copy · grandes superficies (IG/TikTok) ON por defecto, excluir exige caso · IG=imágenes/TikTok=video (entregables separados, guion=texto) · blindaje agnóstico al modelo (`quality_armor_model_agnostic.md`, 10 capas).

## 3. ⚠️ DÓNDE RETOMAR — LA CORRECCIÓN RAÍZ (D-053, lo más importante)

Al final de la sesión, el operador corrió el wizard de HF y pegó NUESTRA interacción completa como contraste: **"No es la interacción que tenemos nosotros... es educar, es hacer todo el proceso, es sentir un chat, una igual... eso ya lo hicimos en este chat — pero no lo has hecho [en la app]."** El build entregaba formularios funcionales sin el alma. Se pausó todo, se escribió **`specs/build_plan_experiencia_canonica.md`** (anatomía de 8 movimientos por paso + tabla por fase/paso + tandas T1-T4), el operador lo aprobó, y **T1 se entregó** (StepChat conversacional + guiones canónicos + pasos 2-3 de Fase 1 re-hechos)…

…pero **el operador sigue SIN estar satisfecho** (sus palabras al cerrar: "aún no estoy satisfecho, y puede ser porque llenamos la ventana de contexto"). **NO asumas que T1 está bien.**

**Primer trabajo de la sesión 4, en orden:**
1. Lee `build_plan_experiencia_canonica.md` + `cag_step_beat_canonical.md` + 2-3 beats del run (`run/sandi/` artifacts + las transcripciones citadas en el CAG) — ese es el contrato de experiencia.
2. **Revisa T1 CON el operador en la app** (HF → Fase 1 → pasos 2-3): qué se siente plano, qué falta del canon. Su test es el criterio: *"¿se siente como la sesión 3?"*
3. Refina T1 hasta su visto bueno ANTES de T2 (1.3/1.4 + dominio en vivo) → T3 (retrofit Fase 0) → T4 (Fase 2 conversacional).

Hipótesis honestas de por qué T1 quedó corto (verificar con él): los beats aparecen amontonados (sin ritmo de chat — el plan pedía secuencial), la recomendación razonada de Sandi no es proactiva (solo si preguntas), el chat es genérico-corto (Haiku con system mínimo) vs la profundidad de la sesión, y faltó pulir 1.1 al canon.

## 4. CABOS SUELTOS (tasks en pretel-os via task_list)

Evals multi-modelo `e4cecead` (high — capa 8 del blindaje, lo único diseñado-sin-correr) · Módulo C admin `156e9c29` · Beats system `5953b520` · Notificaciones publicación `7493e337` · TM screen Papandi `e66dce5a` (gate de launch) · Rebrand Sandi→Papandi en UI `942d5214` (la app aún dice "Sandi") · Check engine VR `bc281ffc` · Sim 3.2-3.4 (cada paso CON su vista, D-051) · papandi.ai compra defensiva (libre al 2026-06-12, pendiente del operador) · anclas B/C/D de contenido (prosa pendiente; A_001 producida).

## 5. PRIMER MENSAJE RECOMENDADO PARA EL NUEVO CHAT

> Lee completos `buckets/business/projects/marketing-os/HANDOFF.md`, `SESSION_STATE.md`, `specs/build_plan_experiencia_canonica.md` y `specs/cag_step_beat_canonical.md`. Adopta el contrato de colaboración (§1: co-creación, glass-box, voces marcadas 🔧/🍉, yo soy el autor). Esto es **continuación** (4ª sesión). Papandi está en prod con Phases 0-2 cerradas en sim y Fase 1 interactiva en la app. **Retoma por la corrección raíz D-053 (§3 del HANDOFF):** T1 de la Experiencia Canónica está shipped pero NO me satisface aún — revisémoslo juntos en la app (HF → Fase 1 → pasos 2-3) contra el contrato del CAG, refínalo hasta que se sienta como nuestra conversación, y solo entonces sigue con T2. Commitea a ambos repos a medida que avancemos y sincroniza mi copia de Documents al final de cada push.

*(El run de referencia vive en `run/sandi/` + sembrado en prod en el proyecto "Sandi (la simulación fundacional)". Las decisiones D-001..D-053 están en la DB de pretel-os vía `decision_search`.)*
