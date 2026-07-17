# build_plan — Admin Console & Cost Intelligence (Módulo C)

**Project**: business/marketing-os
**Spec padre**: `spec_Admin_Cost_Intelligence.md` (v0.2)
**Status**: Fase A CONSTRUIDA y en producción (2026-07-17, commit sandia `784b187`); Fases B–E para firma del operador
**Origen**: mandato del operador 2026-07-17 — aplicar el diseño `Admin Console.html` (handoff Claude Design) con máxima fidelidad + ver TODAS las llamadas LLM con sus prompts + plan para volver Papandi un sistema cobrable multi-cliente.

---

## Doctrina transversal (rige TODAS las fases)

1. **C-D2 — ningún número inventado.** Toda cifra pintada es medida. Donde falta plomería, la vista muestra el layout del diseño con el `seedtag` «plomería pendiente · Fase X» — jamás data de mentira.
2. **§5 — privacidad 3-capas.** Agregados por defecto; contenido de tenant solo en modo soporte auditado (Fase C). Payloads de LLM = admin-only, sin grants a `authenticated`.
3. **El orden importa: A alimenta D.** El pricing de créditos se calibra con el costo real por clase de acción que A ya mide — el operador no firma precios sobre estimaciones.
4. **Candados de código de sandia**: tokens solo de `globals.css` (check-design-drift), stroke 1.75, marca Papandi, `.from(` solo en lib/supabase|lib/api.

---

## Fase A — El Console con datos reales ✅ CONSTRUIDA (2026-07-17)

Registro as-built:

- [x] Migración `20260717000000_admin_observability.sql` (aplicada en prod):
  - `project_llm_call_payloads` (call_id FK → project_llm_calls, system, messages jsonb, tools, response; RLS sin policies = solo service role).
  - `admin_audit_log` (actor_email, action, target, reason, meta).
- [x] Captura de payloads en `lib/api/llm/complete.ts::logCall` — ambas rutas (Anthropic + OpenRouter), también en error (response null); imágenes = conteo, nunca bytes; toggle `LLM_PAYLOAD_CAPTURE=off`; best-effort (jamás bloquea el turno).
- [x] `lib/admin/telemetry.ts` puro + 12 tests: percentile, kpisOf, spendSpark (24/7/30 cubetas), costByPhase (min/avg/p95/max), statsByModel (share), statsByPromptVersion (cleanRate = sin error/truncar), providerHealth, cogsByProject, costQualityScatter (muestra mínima ≥3), computeAlerts (umbrales: proveedor ≥20% crit / ≥8% warn con ≥5 llamadas; trunc ≥15%; fallback ≥10%).
- [x] Server: `admin-telemetry.ts` (ensamble por ventana, cap 20k filas con aviso), `admin-llm-calls.ts` (lista cursor + detalle con payload), `admin-accounts.ts` (auth.listUsers + COGS mes por dueño), `admin-audit.ts` (log + lista).
- [x] APIs admin-only (requireAdmin en cada una): `/api/admin/telemetry?win=`, `/llm-calls` (+`[callId]`), `/accounts`, `/audit`, `/router`; `settings` POST ahora escribe `admin_audit_log`.
- [x] Shell del diseño (`components/admin/shell.tsx` + `app/admin/admin.css` prefijo `adm-`): sidebar 5 grupos, topbar (migas · live pill · ventana 24h/7d/30d persistida vía useSyncExternalStore · export JSON), drawer, toast.
- [x] 13 rutas: `/admin` (Panorama), `salud`, `costos`, `calidad`, `cogs`, `llamadas`, `router`, `prompts`, `video` (la página anterior integrada — selector de proveedor intacto), `usuarios`, `ingresos`, `aprendizajes`, `auditoria`.
- [x] Verify verde (530 tests) + build + push + migración aplicada.

**Deuda honesta que A deja marcada en la UI** (cada una es tarea de su fase): margen por cuenta (D), storage real (B), accept/adjust/reject (B), evals/promoción (E), modo soporte (C), ledger de créditos (D).

---

## Fase B — Señal de calidad + alertas (siguiente natural)

Objetivo: que Costo×Calidad mida calidad PERCIBIDA (no limpieza técnica) y que el sistema avise solo.

- [ ] B1. Telemetría de tarjetas: tabla `card_feedback` (project_id, phase, prompt_version, card_kind, action accept|adjust|reject, created_at) + hook en el wizard donde ya existe ✓/✏️/✕. Sin UI nueva de usuario.
- [ ] B2. 👍/👎 explícito en outputs largos (research/statements) → misma tabla, card_kind='thumb'.
- [ ] B3. `statsByPromptVersion` gana acceptRate real; el scatter cambia y = aceptación; la vista Calidad retira el disclaimer v1.
- [ ] B4. Storage real: job que recorre buckets de Supabase Storage (bytes por tipo de asset y proyecto) → tabla `storage_ledger`; la tarjeta de COGS pinta asumido vs real + factor.
- [ ] B5. Agrupación por ejecución completa (runs): conversation_id o run_id en las llamadas → costo por fase POR RUN (lo que el diseño ya dibuja).
- [ ] B6. Motor de alertas persistente: reglas de computeAlerts + margen (cuando D exista) evaluadas por cron; tabla `admin_alerts` con estado atendida/silenciada; badge del sidebar sale de ahí.
- [ ] B7. Aprendizajes: tablas `system_lessons/decisions/best_practices` a nivel Papandi + sembrar C-D1…C-D5; la vista deja el estado vacío.

## Fase C — Cuentas de cliente (multi-tenant operable)

Objetivo: recibir clientes de verdad con soporte seguro.

- [ ] C1. Roles en BD: `profiles.role` (user|support|admin) — ADMIN_EMAILS queda como bootstrap; requireAdmin lee rol.
- [ ] C2. Modo soporte (§5, no negociable): drawer del diseño (razón OBLIGATORIA + duración) → sesión read-only sobre la cuenta objetivo; todo acceso a `admin_audit_log` con `support.enter/exit` + visible al titular en su panel.
- [ ] C3. Pausar cuenta (detiene facturación cuando exista) + flujo GDPR de borrado: export → purga programada (nunca DELETE inmediato).
- [ ] C4. Onboarding de clientes: invitaciones/registro abierto controlado por platform_settings (`signups_open`).
- [ ] C5. Botones «Soporte»/«Gestionar» de la vista Usuarios se activan (hoy disabled con honestidad).

## Fase D — Cobrar (el sistema que se puede pagar)

Objetivo: cada cliente con su cuenta, su plan, su bolsa de créditos y su uso — margen visible por cuenta.

- [ ] D1. Modelo comercial (decisión del operador, calibrada con telemetría de A): planes Free/Pro/Studio con créditos incluidos + topups (híbrido del diseño). Precio por CLASE DE ACCIÓN (develop, keyframe, clip-segundo, research) = costo real medido × margen objetivo.
- [ ] D2. Tablas: `plans`, `subscriptions` (cuenta→plan, estado), `credit_ledger` (consumo/compra/ajuste/reembolso, razón auditada, saldo derivado).
- [ ] D3. Enforcement: middleware de acciones facturables — sin saldo, la acción NO corre (mensaje llano al usuario con costo de la acción). El tope MEDIA_BUDGET_USD pasa a ser por-plan.
- [ ] D4. Stripe: checkout (suscripción + topup), webhooks (invoice paid/failed → subscriptions/credit_ledger), portal de cliente para cambiar plan.
- [ ] D5. Vista Ingresos cobra vida: MRR por plan, ARPU, churn, LTV real vs estimado (cierra ECONOMICS-001) + ledger visible con ajustes manuales auditados desde el drawer «Gestionar».
- [ ] D6. COGS gana margen real por cuenta (cobrado − COGS) + alerta de margen negativo (regla del diseño).
- [ ] D7. Capa usuario (doctrina 3-capas): el cliente ve SU saldo/uso en lenguaje llano en su panel — la maquinaria técnica jamás sale de /admin.

## Fase E — Router dinámico + evals

Objetivo: promover ganadores sin deploy, con evidencia.

- [ ] E1. Routing en `platform_settings` (override de TASK_MODELS); `modelForTask` lee el override con caché + invalidación; la vista Router se vuelve editable (selects del diseño) + cada cambio a `admin_audit_log`.
- [ ] E2. Harness de evals corriendo contra candidatos declarados (golden set + juez ciego + costo); resultados a tabla `eval_runs`.
- [ ] E3. Botón «Promover + log» (regla 95%-calidad): aplica el override + decision log. El techo Sonnet (mandato 2026-06-10) se mantiene como candado.

---

## Riesgos y decisiones abiertas

| # | Tema | Estado |
|---|---|---|
| R1 | Retención de payloads (crecen con el uso; texto ≈ KBs/llamada) | Propuesta: retención 90 días + purga cron (decidir en B) |
| R2 | Consentimiento de captura cuando haya clientes reales | La captura es del PROPIO sistema (nuestros prompts); el contenido del usuario viaja dentro → al abrir signups (C4), declarar en términos + evaluar redacción/anonimización para soporte |
| R3 | Pesos de crédito por clase de acción | Se firman con ≥2 semanas de telemetría A (no antes) |
| R4 | Stripe en la entidad del operador (país/impuestos) | Decisión del operador antes de D4 |
