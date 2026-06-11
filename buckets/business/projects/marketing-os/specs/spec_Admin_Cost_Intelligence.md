# Módulo C — Admin & Cost Intelligence

**Project**: business/marketing-os
**Module ID**: module-c-admin
**Status**: spec v0.1 (requisitos del operador capturados + brainstorm inicial; PENDIENTE: lluvia de ideas dedicada + investigación de mercado + trinity propia antes de codear)
**Last updated**: 2026-06-11
**Origen:** mandato del operador en sesión 3 (sim Phase 1), al converger el modelo de costo de IA: "necesitamos un perfil de administrador… esto vendría siendo todo un spec completo… este módulo de los costos de Sandi no lo hemos tocado y me parece fundamental." Tema cargado por el operador desde antes, abierto formalmente aquí (D-033).

---

## 0. Contexto y propósito

Sandi tiene dos módulos de cara al usuario (D-019: A = Business Case, B = Marketing OS). **Módulo C es el tercero y NO es user-facing: es el sistema nervioso operacional** — lo que el dueño del negocio (el operador como admin) necesita para operar, soportar, cobrar y MEJORAR Sandi con datos reales.

**La tesis (del operador, verbatim en esencia):** los costos y la calidad no se estiman — se miden continuamente, con todos los usuarios, y se entregan al admin "de manera que sea sencillo descubrir patrones". La medición por fase no es un ejercicio de build-time: es telemetría viva que responde cuánto cuesta cada fase (mín/máx/promedio), cómo los rangos de costo afectan calidad y satisfacción, y cómo se relacionan con el LLM seleccionado — para encontrar **el punto óptimo dinero-calidad**.

**Por qué es fundamental ahora:** el pricing de créditos (Phase 1.4 del run) depende del modelo de costo; el modelo de costo hoy mezcla 1 run medido + estimaciones de Claude — y el operador, con razón, no firma sobre estimaciones que no puede auditar. Módulo C convierte "confía en mi estimación" en "míralo tú mismo".

## 1. Capacidades del admin (requisitos del operador — lista fundacional)

| # | Capacidad | Estado de plomería |
|---|---|---|
| 1 | **Métricas de consumo** por usuario / proyecto / fase / modelo | `project_llm_calls` ya captura cost/tokens/modelo/fase/latencia/errores — falta la VISTA |
| 2 | **System prompts**: ver versiones activas e históricas | `project_prompt_versions` ya existe — falta la VISTA |
| 3 | **Info de models.ts + selección**: ver el router tarea→modelo y PODER CAMBIARLO desde admin (promover ganadores de evals sin deploy) | hoy hardcoded en `lib/api/llm/models.ts` — falta config dinámica + UI |
| 4 | **Soporte por cuenta**: entrar a ver la cuenta de un usuario para ayudarlo | falta modo soporte (read-only, AUDITADO — ver §5) |
| 5 | **Gasto actual de IA** por sistema y por fases, en vivo | datos existen; falta agregación + dashboard |
| 6 | **Costo promedio por fase** (y mín/máx/p95 — ver §3) | ídem |
| 7 | **Pausar / eliminar cuentas** | falta (estado de cuenta + flujo GDPR-safe de borrado) |
| 8 | **Ver ingresos** (MRR, por plan, churn) | falta billing (Stripe) — cruza con M11-style billing |
| 9 | **Manejar perfiles de pago** (planes, créditos, comps, reembolsos) | falta ledger de créditos + integración de pagos |
| 10 | **Lessons / decisions / best-practices del SISTEMA** — lo aprendido operando Sandi, visible y accionable para mejorarla | patrón pretel-os; falta instancia propia en Sandi (admin-level, no por-proyecto-de-usuario) |

## 2. Brainstorm inicial (propuestas de Claude — el operador dispone; se completa en sesión dedicada)

- **Alertas y umbrales:** usuario cuyo COGS supera su plan (margen negativo) · spike de errores/fallbacks por proveedor · latencia degradada · modelo caído → kill-switch / reroute desde admin.
- **Salud del sistema:** error rate, fallback rate, latencia p50/p95 por proveedor y por prompt_version (columnas ya existen en `project_llm_calls`).
- **Funnels de producto:** drop-off por sub-paso del wizard (la métrica norte de `spec_UX_Experience.md` §4) — el admin es DONDE se ve.
- **Ledger de créditos:** saldo, consumo por clase de acción, ajustes manuales (comp/reembolso) con razón auditada.
- **Cohortes económicas:** LTV real vs estimado (cierra el loop con ECONOMICS-001 — Sandi midiendo su propio negocio con su propia Phase 4: la meta-recursión completa), CAC por canal cuando haya marketing propio.
- **Promoción de modelos:** integración con el harness de evals (`docs/model-selection.md`): cuando un candidato gana (regla 95%-calidad), el admin promueve el routing con un click + decision log.
- **Export/BI seam:** todo dashboard exportable (CSV/JSON) para análisis externo.
- **Feature flags** por cohorte (probar un prompt nuevo con 10% de usuarios).

## 3. Telemetría de costos continua (mandato: medir SIEMPRE, no solo al construir)

Cada fase/acción reporta SIEMPRE, con todos los usuarios — las estimaciones del `ai_cost_model.json` son semilla que la realidad reemplaza:

- **Por fase y sub-paso:** costo mín / máx / promedio / p95 por ejecución completa; distribución (no solo el promedio — los rangos importan: el operador quiere ver "cómo los rangos afectan la calidad").
- **Por clase de acción** (beat / propuesta_estratégica / research_web — las clases medidas del run): costo unitario real por modelo.
- **Por modelo:** costo vs calidad vs latencia — el triángulo que decide el routing.
- **Por usuario/cohorte:** COGS mensual vs plan (la distribución que valida o rompe el pricing de créditos).

## 4. Señales de satisfacción y calidad (mandato: likes/dislikes + tasas de tarjeta en TODAS las etapas)

El wizard YA produce la señal más honesta sin pedir nada extra: **cada tarjeta de propuesta se acepta (✓), se ajusta (✏️) o se descarta (✕)** — eso es feedback de calidad revelado, no declarado. Se persiste como telemetría:

- **% accept / adjust / reject por tarjeta**, por prompt_version, por modelo, por fase. Una propuesta con 80% de ajustes = prompt o modelo flojo; 95% accept = candidato a modelo más barato.
- **👍/👎 explícito** en outputs largos (research, statements) donde no hay tarjeta.
- **Cruce costo×calidad:** scatter por modelo y clase de acción (costo unitario vs tasa de aceptación) → el **punto óptimo dinero-calidad** se VE, no se argumenta. Diseño del dashboard: pattern-discovery-first (el patrón salta a la vista en <10 segundos o el dashboard está mal).
- Las señales alimentan: evals multi-modelo (golden set se enriquece con casos reales), routing (modelo por tarea), prompts (versiones que pierden se retiran), y el pricing (si la calidad cae al bajar de tier, el ahorro era falso).

## 5. Privacidad y auditoría (no negociable — hereda la doctrina 3-capas)

- El admin ve **agregados** por defecto (T3-style). El contenido de un tenant (T1/T2) solo en **modo soporte**: read-only, con razón declarada, **todo acceso queda auditado** (`project_audit_log` ya existe) y es visible para el usuario afectado. Sin esto, la capacidad #4 es una puerta trasera.
- Roles: `admin` (todo) vs `support` (soporte auditado sin billing/borrado). Borrado de cuenta = flujo GDPR (export + purga programada), no un DELETE.
- **Capas de audiencia (doctrina USER-CORRECTED, mismo origen que este módulo):** la maquinaria técnica (nombres de tablas, archivos, modelos, costos por llamada) vive AQUÍ, en admin — **nunca en la capa de usuario**. El usuario ve lenguaje llano en el flujo + profundidad opcional en su panel ("¿Qué es esta fase?", "¿De dónde sale?", "¿Cómo se calcula?"). Tres capas: flujo llano → panel de apoyo → admin técnico.

## 6. Relación con otros módulos y trabajos

- **Phase 1.4 (pricing créditos):** Módulo C es quien CALIBRA los pesos de crédito con distribución real (la semilla 1/5/60 viene del run medido).
- **Módulo A (BMC):** el Cost Structure deja de ser hipótesis — se llena con esta telemetría.
- **Evals multi-modelo (cabo suelto #2):** §4 les da el flujo de datos permanente y §2 el botón de promoción.
- **pretel-os:** lessons/decisions/BPs del sistema (capacidad #10) siguen el patrón pretel-os — el cerebro que el producto ya replica por-proyecto, instanciado a nivel sistema.

## 7. Pendientes (antes de codear NADA de esto)

1. **Lluvia de ideas dedicada** con el operador (su lista tiene "se me escapan más cosas" explícito).
2. **Investigación de mercado:** referentes de LLM-ops/observabilidad (Langfuse, Helicone, LangSmith, Portkey — el patrón de telemetría LLM ya está maduro) + admin consoles de SaaS comparables. Candidato a deep-research.
3. **Decidir build vs integrar** para la capa de observabilidad LLM (¿tabla propia + dashboards vs herramienta externa self-hosted?). El costo de construir dashboards es real; el de regalar datos de tenants a un tercero también — pasa por la doctrina de privacidad.
4. Trinity propia (spec completo + plan + tasks) cuando se decida construir; prioridad relativa vs terminar Phase 1-5 del producto = decisión del operador (la sim de Phase 1 NO se bloquea por esto).

## 8. Decisiones cerradas

| # | Decisión | Resolución |
|---|---|---|
| C-D1 | Módulo C existe como tercer módulo (operacional, no user-facing) | D-033, 2026-06-11. Spec v0.1 ancla requisitos; build después de su propia trinity. |
| C-D2 | Telemetría continua, no build-time | Costos y calidad se miden SIEMPRE con todos los usuarios; estimaciones solo como semilla etiquetada. |
| C-D3 | Señal de calidad primaria = decisiones de tarjeta (accept/adjust/reject) | Feedback revelado del wizard existente; 👍/👎 explícito solo donde no hay tarjeta. |
| C-D4 | Capas de audiencia | Flujo llano → panel de apoyo → admin técnico. Maquinaria técnica nunca en capa usuario. |
| C-D5 | Soporte auditado | Acceso a cuentas: read-only + razón + audit log visible al usuario. |
