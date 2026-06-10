# Reporte Maestro — Validacion de Specs vs. Corpus (7 cursos + BMC)

**Fecha:** 2026-06-09
**Alcance:** 8 specs de Marketing OS / Sandi validados contra el corpus de marketing (7 cursos: fundamentos, analisis de mercado, SEM, SEO/BigSEO, SEO avanzado, email, RRSS + Business Model Canvas).
**Veredicto general:** los specs son un **superset** del corpus en casi todos los ejes. El corpus actua como piso (floor) que los specs superan, no como techo que rompan. **Cero contradicciones duras corpus-vs-spec.** Las unicas "contradicciones" halladas son erratas internas de un spec que el corpus ayuda a resolver.

---

## 1. Resumen ejecutivo — Alineacion por spec

| Spec | Score | Lectura |
|---|---|---|
| `spec_Phase_0_Research_ICP.md` | **9.0** | El mas alto. Replica casi campo-por-campo el "Bases del Negocio" del Curso 2 y anade JTBD, Forces of Progress, Schwartz, TAM/SAM/SOM, ICP separado, DMU, LTV:CAC gate. Superset estricto. |
| `spec_Phase_5_Ajustar.md` | **9.0** | El loop medir->diagnosticar->ajustar->iterar es el cierre universal de todos los cursos. Accion diferenciada por condicion + re-trigger al nivel minimo = leccion explicita del corpus. |
| `Overall_WF.md` | **8.5** | Backbone de 6 fases mapea 1:1 con los workflows canonicos (Curso 1: 12 pasos; Curso 2: 8 fases con dependencias). Foundation-first + viability gate + anti-vanity = fieles a la fuente. |
| `spec_Phase_2_Contenido.md` | **8.5** | Un contenido por intencion, adaptacion por Customer Journey, hooks, ratio Vaynerchuk, atomizacion 1->N. Convergencia de dos fuentes independientes en el ratio valor:venta. |
| `spec_Phase_4_Medir.md` | **8.5** | Rechazo de vanidad operacionalizado (leads sucios restados ANTES de conversion), CPA<margen, funnel por awareness, atribucion por avatar. Tiene 1 errata interna (ver seccion 4). |
| `spec_Phase_3_Distribucion.md` | **8.0** | Spine de 4 canales con funcion diferenciada, tracking-first, exclusion lists, permission marketing. Le falta la dicotomia captacion-vs-generacion de demanda a nivel arquitectura. |
| `spec_Phase_0_Setup_Agent.md` | **8.0** | Gate-before-research validado por el principio fundacional mas fuerte del corpus ("ficha antes de cualquier IA"). Question set 1:1 con las 5 dimensiones del Curso 2. |

**Promedio: ~8.5/10.** Diagnostico global: la **metodologia** esta solidamente anclada al corpus; lo que falta es **tactica de canal** (el corpus la tiene muy operacionalizada y los specs estrategicos la omiten o difieren a V2) y **dos variables modernas** que el corpus enfatiza pero el overview no nombra: (a) **captacion vs generacion de demanda** y (b) **AI Overview / zero-click**.

---

## 2. Enriquecimientos SEGUROS a aplicar (por spec, ordenados por valor)

> "Seguro" = aditivo, no toca decisiones locked, gobernado por los patrones de extension ya existentes ([Extensible Vocabulary] / [Context-Adjusted Threshold] / [Evolving Schema]). Los que SI tocan una D-xxx estan en la Seccion 5 (FLAGS), no aqui.

### 2.1 `spec_Phase_2_Contenido.md` (alto valor — 5 enriquecimientos limpios)

1. **Subject line de email como artefacto de primera clase** (es el "hook" del canal email y decide la tasa de apertura).
   *Texto:* anadir al derivative `format=email` (2.4) un sub-objeto `subject_line: { variants: [<=5, cada una <40 chars], pre_header, one_variant_with_emoji: true, spam_words_checked: true, ab_test_pair: [2 mejores] }`. **Regla dura:** un derivative de email sin `subject_line` poblado no se publica. *(Curso 6)*

2. **Limites de caracteres de ads como restriccion estructural** (un ad que excede se rechaza en plataforma).
   *Texto:* en PILLAR_B y derivatives `format=ad_copy`, declarar `char_limits_per_platform`: Google Ads headlines <=30 chars, long headlines/descriptions <=90 chars. Asi el copy nace dentro del limite y Phase 3 no rebota assets. *(Curso 5)*

3. **Estructura de guion de video por intervalos de segundos** (el formato de mayor friccion de produccion queda sin guia).
   *Texto:* anadir a derivatives de video un campo `video_script_structure`: ads paid (PILLAR_B) = 0-2s hook / 2-5s producto / 5-8s prueba-o-precio / 8-10s CTA; organico = gancho 3-5s / cuerpo 15-45s con micro-ganchos / cierre 4-6s. El `hook_id_assigned` alimenta el primer intervalo. *(Cursos 5 + 7)*

4. **Schema.org / JSON-LD en long-form SEO** (factor de Rich Results y elegibilidad para AI Overview).
   *Texto:* anadir al long_form de PILLAR_A un campo opcional `structured_data: { schema_type, jsonld_validated: true }` y la regla: todo long-form SEO declara su `schema_type` y valida el JSON-LD antes de publicar. *(BigSEO)*

5. **Re-impacto evergreen por cambio de angulo motivacional** (mismo producto, distinto beneficio; palanca barata para no-convertidores).
   *Texto:* anadir a PILLAR_C / seccion 13 una nota de estrategia: para leads que consumieron pero no convirtieron, generar derivatives de re-impacto que ataquen la MISMA fuerza con un angulo distinto (cambiar beneficio, no producto); no requiere re-build del plan. Calibrar urgencia por ticket: bajo 15min-1h, medio 48h, alto 3-7 dias. *(Curso 6)*

> Nota: `entity_coverage_checklist` (Knowledge Graph / TextRazor) queda como activable a partir del ciclo 2 / V2, no regla dura en V1.

### 2.2 `spec_Phase_0_Research_ICP.md` (alto valor — metodo y defaults)

1. **Default de conversion sourced en DEMAND-004** (hoy el math gate multiplica por una variable indefinida).
   *Texto:* en 0.2, definir `conversion_rate_optimistic` como [Context-Adjusted Threshold]: ~3% e-commerce US, ~1% e-commerce ES/LATAM (Javier Martinez, Curso 2 C4), ajustable por `business_type`/`delivery_format`; servicio/B2B usan default menor. La tasa asumida se registra en el `decision_record` para que el veredicto sea auditable. *(Curso 2 C4)*

2. **Empathy Map (XPLANE) como metodo de elicitacion de `psychographics`** (el spec define campos pero ningun metodo para llenarlos honestamente).
   *Texto:* en 0.3, anadir nota de metodo: poblar psychographics via Empathy Map de 6 preguntas (VE / OYE / PIENSA-SIENTE / DICE-HACE + incongruencias / ESFUERZOS->pain_points+Forces.anxiety / RESULTADOS->aspirations+JTBD). La incongruencia entre (3) y (4) es el input de mayor senal para copy. Queda como [Evolving Schema] seed. *(BMC)*

3. **Workflow IA de elicitacion de pain points** (dos pasos del Curso 2 C7, que ademas hace de puente a Phase 1).
   *Texto:* en 0.3, regla para `pain_points_universal`: Step 1 "Dame los puntos de dolor de [buyer_persona] al comprar [producto]"; Step 2 "Dame la solucion para cada punto." Las soluciones se llevan como mapa-semilla de objeciones a Phase 1. El output IA es brainstorm, no verdad: cada pain que sobrevive al JSON cita >=1 fuente real. *(Curso 2 C7)*

4. **Stack de herramientas + URLs para 0.2 y 0.4** (el competitor scan solo cita Meta Ad Library en prosa).
   *Texto:* en 0.4 anadir tabla "Fuentes": SimilarWeb (trafico+demografia+canales), Social Blade (evolucion RRSS), Meta Ads Library + Google Ads Transparency + TikTok Creative Center (creatividades activas), Semrush/Ahrefs (SEO competidor). En 0.2 anadir SearchVolume.com (free, 100 kw) como opcion Capa-3 de costo cero. Etiquetar cada una free/paid. *(Curso 2 §4 + Curso 5)*

### 2.3 `spec_Phase_3_Distribucion.md` (operabilidad del calendario)

1. **Campo `format` / aspect-ratio por entrada de calendario** (decision de distribucion, no de contenido).
   *Texto:* en 3.3, anadir a cada `publish_plan.calendar[]` el campo `format: "9:16 | 16:9 | 1:1 | article | email"`. Sin esto el calendario no especifica como sale el mismo asset en cada plataforma. *(Curso 7)*

2. **Reutilizacion cross-platform (1 asset madre -> N filas)** (hoy cada (asset, canal) es independiente).
   *Texto:* en 3.3, permitir `derived_from_asset_id` + `repurpose_format` para que un asset de Phase 2 genere multiples filas (mismo asset madre, distinto channel+format+utm). Refleja "video largo -> N piezas cortas" y conecta con DISTRIB-001 (cada formato derivado cuenta para el ratio de su canal). *(Curso 7 §6.6)*

3. **Secuencias de email como objetos schedulables** (el spine dice "email convierte" pero el calendario solo agenda posts).
   *Texto:* en 3.3, anadir `entry_type ∈ {one_off_post, automated_sequence}`. Para `automated_sequence`: `sequence_kind ∈ {onboarding, nurturing, sales, evergreen_reimpact}`, `trigger`, `length`. La ventana de urgencia por ticket viaja como metadata. *(Curso 6 §2.2)*

### 2.4 `spec_Phase_4_Medir.md` (senales de medicion mas finas)

1. **Diagnostico de terminos de busqueda en 4 categorias** (senal de desperdicio que el funnel agregado oculta).
   *Texto:* anadir a `metrics_snapshot.raw` un bloque opcional `per_search_term` para canales de pago: `[{term, channel, avatar_id, spend_usd, conversions, category: profitable|informational|out_of_model|non_converting}]`. Regla: clasificar cada termino con gasto>0; `non_converting` (spend>0 AND conversions==0) y `out_of_model` son desperdicio que Phase 5 acciona. `category` como [Extensible Vocabulary]. *(Curso 5 C8)* — **OJO:** si esto emite una bandera nueva (`paid_search_waste`), va a FLAGS (Seccion 5).

2. **Metricas de algoritmo en social (`completion_rate`, watch-time, saves, shares)** (indicador LIDER de fatiga; precede la caida de CTR).
   *Texto:* extender `per_pillar` con campos opcionales por canal social: `completion_rate, avg_watch_time_s, saves, shares`. Para video corto, `completion_rate` es indicador lider — su caida precede al CTR. Snapshot quincenal (alineado con "revision cada 15 dias" del Curso 7). *(Curso 7 Fase 4)* — promover nombres al seed de `kpi_primary` toca D-014 R-6: va a FLAGS.

3. **Nombrar el metodo de agregacion multi-plataforma en V2** (hoy "pull via API" abstracto; 4.1 estima 1h/snapshot manual evitable).
   *Texto:* en 4.1 columna V2, reemplazar "Sub-workflow pull via API" por "pull via conector multi-plataforma (p.ej. Windsor.ai: GA4 + Google Ads + Meta/TikTok/LinkedIn -> URL conector JSON/CSV)". Es candidato a `tracking_manifest`/V2, no contrato V1. *(Curso 5 C11)*

### 2.5 `spec_Phase_5_Ajustar.md` (anclar el diagnostico abierto a evidencia)

1. **Sensor concreto para `foundation_drift` / competitive-shift** (la condicion existe sin instrumento de deteccion).
   *Texto:* en §3b step 1 y §6, anadir fuente de evidencia recomendada: benchmark competitivo periodico (scrape -> analisis IA -> repositorio fechado acumulativo). El versionado fechado separa `foundation_drift` real del ruido de un solo avatar. Mantiene el principio evidencia-sobre-calendario (D10) pero le da un sensor. *(Curso 7 + Curso 4)*

2. **Aclaracion "revisar != reconstruir" dentro de D10** (pre-empta la tension aparente con freshness/15-dias).
   *Texto:* anadir a D10 una clausula: "Revisar es continuo (freshness SEO, revision quincenal, benchmark competitivo) y alimenta las banderas; la RECONSTRUCCION del cimiento (0.1-0.2.5) la dispara solo `foundation_drift` por evidencia. Eliminar `12_months_elapsed` no elimina el mantenimiento continuo — lo separa del versionado." *(Cursos 3 + 7 + BMC)*

3. **Comparacion de canvas BMC bloque-a-bloque para diagnostico estructural** (cuando la causa raiz es que el competidor movio su modelo).
   *Texto:* en §3b step 2, anadir metodo opcional: cuando la hipotesis es estructural, usar comparacion de canvas (propio vs competidor) y/o mini-escenario para razonar la causa, no solo metricas. Cubre anomalias que las metricas de canal no explican (ej: competidor lanza gratis el modulo avanzado -> cae el upsell). *(BMC + Curso 2)*

### 2.6 `Overall_WF.md` (arquitectura — la mayoria toca decisiones, ver FLAGS)

- El unico enriquecimiento puramente seguro a nivel overview es de **vocabulario compartido**: nombrar un **glosario canonico** (~80 terminos del Curso 1) como activo de retrieval de primera clase compartido entre sub-agentes especialistas. Barato, alto apalancamiento para consistencia de terminos cross-agent. *(Curso 1)*
- Los demas (demand_type, zero_click flag, trust_cycle 7-11-4) tocan D-010 / D-012 / D-014 -> **Seccion 5**.

### 2.7 `spec_Phase_0_Setup_Agent.md`

1. **Nombrar el patron de pricing en el flag de monetizacion** (hoy solo flaguea freemium/uso en abstracto).
   *Texto:* en Step 2, glass-box copy: "Lo que describes es un patron conocido: Freemium (1-10% paga y financia al resto) o Cebo-y-Anzuelo (entrada barata, margen en el consumible recurrente - Nespresso). En un producto con IA el medidor de creditos ES tu costo variable por llamada, asi que el patron decide tu Cost Structure (BMC bloque 9) y tu pricing de Phase 1.4." Capturar campo opcional `monetization_pattern` (seed: subscription | one-shot | freemium | bait_hook_credits | usage | other). *(BMC §4.4)*

---

## 3. Gaps reales (lo que falta cubrir)

Ordenados por criticidad estrategica.

### CRITICOS (afectan supuestos de viabilidad/trafico)

- **G1 — Captacion vs Generacion de demanda no es un primitivo de arquitectura.** Es el fork estrategico #1 del corpus (Cursos 1, 2, 5 construyen canal/copy/conversion sobre el). Ausente del strategy entity (`Overall_WF`), del Flag Registry, y de `audience_per_channel` en Phase 3. Debilita la legibilidad de seleccion de canal y del flag `cac_up_40pct`. Los canales de demanda capturada convierten MUY distinto a los de demanda generada — comparar sus CVR es un error que el spec no previene.
- **G2 — Ningun productor de zero-click / AI Overview en el Flag Registry.** BigSEO construye TODA su estrategia de contenido+medicion alrededor de que las queries informacionales pierden clics ante respuestas IA en SERP. El Flag Registry tiene productores FATIGUE/CONVERSION/CAC/AVATAR/FOUNDATION/ANOMALY pero nada para un shift de SERP-feature. Una falla real moderna (trafico informacional organico colapsa por razones ajenas al ranking) cae a `unexplained_anomaly` en vez de a una ruta determinista. **Especialmente critico para el mix Caso B (create_demand, 35-45% Problem Aware via SEO)**, cuyo supuesto de trafico puede estar erosionado.

### DE COBERTURA (el corpus lo tiene operacionalizado; el spec lo omite o difiere)

- **G3 — Subject line de email no modelado en ningun JSON.** Unico canal donde el "hook" no tiene equivalente al `hook_library`. (Phase 2)
- **G4 — Limites tecnicos de plataforma para ads** (Google Ads 30/90; formatos 9:16/16:9/1:1). Causa rebote de assets en Phase 3. (Phase 2/3)
- **G5 — Schema.org/JSON-LD en long-form SEO** ausente; el corpus lo trata como paso de produccion obligatorio con validacion. (Phase 2)
- **G6 — Estructura interna de guion de video por intervalos** ausente; el formato de mayor friccion queda sin plantilla. (Phase 2/3)
- **G7 — Secuencias de email tipadas (onboarding/nurturing/ventas, funnel->broadcast)** no schedulables; ambiguo si la secuencia vive en Phase 2 o Phase 3. (Phase 2/3)
- **G8 — Competencia tratada como monolitica a nivel arquitectura.** El corpus insiste en competencia por-canal (SEO != paid != social son actores distintos; Curso 2 §6.6, Curso 7 §2.9). `Overall_WF` Foundation lista "competitors" como salida unica; Pattern B lee `competitive_landscape` sin estructura. (Overall_WF / Phase 0)
- **G9 — Medicion a nivel termino de busqueda** (Curso 5 C8); el funnel agregado puede ocultar 10.000 terminos quemando presupuesto. La categoria "No convierten" (gasto>0, conversiones=0) no tiene equivalente. (Phase 4)
- **G10 — Metricas de algoritmo (watch-time/completion) como indicador LIDER de fatiga**; el spec solo tiene CTR (indicador tardio), asi FATIGUE-001 reacciona tarde. (Phase 4)
- **G11 — KPIs nativos por canal** (open_rate email, avg_position/impressions SEO, zona "posicion 10-13") colapsados en `kpi_primary_value` generico. (Phase 4)
- **G12 — Funnel de conversion en RRSS organico** (ManyChat comment-trigger -> DM -> lead) ausente; RRSS solo tratado como amplificacion, sin captura de lead organico. (Phase 3)
- **G13 — Reutilizacion cross-platform de assets** (1 madre -> N formatos) ausente; el repurposing es motor de distribucion a escala. (Phase 3)
- **G14 — Playbooks tacticos por canal bajo el routing de Phase 5.** El spec decide QUE fase re-triggerar pero no QUE hace esa fase al re-correr. El corpus tiene la tactica "Ajustar" totalmente operacionalizada (SEM 4-categorias, SEO 10-13 + freshness + 301 seguras, Email re-impacto, RRSS benchmark mensual) — nada referenciado. **El contenido mas grande que el corpus cubre y el spec omite** (intencional, por ser estrategico; pero deberia al menos apuntar a donde viven las tacticas). (Phase 5)

### MENORES / DIFERIBLES

- **G15 — A/B testing como primitivo nombrado de validacion** en el procedimiento de Phase 5 (3 cursos lo hacen el metodo canonico; hoy solo aparece en una columna de madurez). (Phase 5)
- **G16 — Glosario / vocabulario controlado compartido** entre sub-agentes (~80 terminos del Curso 1) no nombrado como activo de retrieval de primera clase. (Overall_WF)
- **G17 — Modelo cuantitativo 7-11-4** como fundamento de la cadencia del calendario; hoy el ">=4 semanas" es arbitrario. (Overall_WF / Phase 3)
- **G18 — Re-impacto evergreen (angle-switch)** no nombrado como movida de Phase 5. (Overall_WF / Phase 2 lo cubre como enrich)
- **G19 — Propuesta de Valor como entregable de Phase 0** (ver Seccion 4 — es contradiccion suave de ordenamiento). (Phase 0 Research)
- **G20 — Empathy Map como metodo de elicitacion psicografica** (campos sin procedimiento). (Phase 0 Research)
- **G21 — Nuance de buscador regional** (Bing mayor share en US; Google >90% EU/LATAM); ignorar Bing en US sub-cuenta demanda. (Phase 0 Research)
- **G22 — Entidades / Knowledge Graph** como senal de optimizacion semantica; aceptable diferir a V2 pero ni mencionado como diferido. (Phase 2 / Phase 0)
- **G23 — Pipeline de data multi-fuente** (Windsor.ai) para que Phase 4 mida un funnel unificado; solo tangencialmente cubierto. (Phase 3/4)
- **G24 — Make.com auto-respuestas** (5 modulos, delay 5-10s) ausente de columna V2 de Phase 3.
- **G25 — Storytelling como tecnica de conversion** a nivel asset largo (BMC lo eleva a tecnica propia); parcialmente cubierto por jtbd_anchor + before-after-bridge. (Phase 2)
- **G26 — "Trafico cualificado > volumen"** como principio explicito; el spec lo aplica implicitamente (SOM/awareness/negative-personas) pero nunca lo enuncia. (Phase 0 Research)

---

## 4. Contradicciones a resolver

**No hay contradicciones duras corpus-vs-spec.** En todos los ejes los specs son consistentes con (y mayormente superset de) el corpus. Lo que sigue son **erratas internas** y **tensiones de matiz** que el corpus ayuda a resolver.

### C1 — ERRATA INTERNA en `spec_Phase_4_Medir.md` (corregir; el corpus respalda el cuerpo, no el resumen)

La fila **D4** de la tabla de decisiones (§10) dice: `LTV:CAC < 3.0 -> red -> Phase 5 actua`.
Pero las **Reglas duras de 4.2 + ECONOMICS-LIVE-001** (§4, §8) dicen explicitamente que el umbral **NO es un 3.0 plano** sino una **tabla por modelo de negocio** (one-shot margen alto = 2.0, etc.).
El corpus (Curso 1: "CPA < margen", viabilidad atada al margen real, no a un ratio fijo SaaS) **contradice el "< 3.0" del resumen y respalda el cuerpo context-adjusted**.
**Accion:** corregir la redaccion de la fila D4 para que cite la tabla por modelo, alineandola con su propio cuerpo y con el corpus.
**OJO (va tambien a FLAGS):** el **nombre del flag** sigue siendo `ltv_cac_below_3` (literal "3" como clave canonica del registro) — eso **NO se cambia**; solo se corrige la redaccion del resumen D4.

### C2 — Contradiccion SUAVE de ordenamiento en `spec_Phase_0_Research_ICP.md` (documentar, no resolver)

El Curso 2 C7 es explicito en que los **puntos de dolor requieren 4 pilares previos**, y la **propuesta de valor + customer journey** son dos de ellos -> la propuesta de valor **debe preceder** la identificacion de pain points.
El spec **invierte/omite** esto: colecta `pain_points_universal` en 0.3 **sin producir artefacto de propuesta de valor en Phase 0** (el value framing se difiere a Phase 1, Hormozi por avatar).
**Por que NO es conflicto logico:** JTBD (`current_solution` + `frustration_with_current`) y Forces of Progress (pull/anxiety/habit) **funcionan como sustituto** del pilar propuesta-de-valor, y el customer journey SI esta presente (embebido en el avatar, 5 etapas). Es una contradiccion **estructural de ordenamiento de artefactos**, no de logica.
**Accion:** documentar explicitamente en §0 del spec que la propuesta de valor esta **intencionalmente reubicada a Phase 1**, para que la divergencia con la secuencia del Curso 2 sea una **decision trazable, no una omision silenciosa**. (Tocar esto activamente colisiona con D-009/D-010 -> FLAGS.)

### C3 — Tension de matiz en `spec_Phase_2_Contenido.md` (ya resuelta; documentar)

El spec colapsa Schwartz de **5 a 4 niveles de awareness** (Product+Most -> Most Aware), justificado porque Keyword Planner no discrimina Product de Most Aware (ambos transaccionales).
El corpus SEO trabaja con **3 intenciones** (informacional/transaccional/mixta), no con los 5 de Schwartz, por lo que **NO contradice el merge** — de hecho lo respalda indirectamente (la granularidad fina de awareness no es recuperable desde keyword data).
**Accion:** ya documentado como tension resuelta. Sin cambio.

### C4 — Tension de matiz en `spec_Phase_5_Ajustar.md` (ya resuelta implicitamente; hacerla explicita)

Remover `12_months_elapsed` y reconstruir Foundation solo ante `foundation_drift` (D10) **puede leerse** como conflicto con la insistencia del corpus en freshness continuo (SEO "freshness" obligatorio; RRSS "revision cada 15 dias"; BMC "innovar continuamente").
**No es contradiccion real** porque el spec separa *revisar* (continuo) de *reconstruir* (disparado por evidencia) — pero nunca lo enuncia en una linea, asi que un lector cruzando con el corpus podria confundirlo.
**Accion:** aplicar la clausula de aclaracion (enrich 2.5.2) para hacer el no-conflicto explicito.

---

## 5. ⚠️ FLAGS — Cambios que tocan decisiones LOCKED (D-xxx). El operador decide. NO se aplican solos.

> Regla: el corpus **enriquece**, no es autoridad para sobrescribir una decision locked. Todo lo siguiente es **aditivo y sancionado por el mecanismo de extension**, pero como modifica un schema/registro impreso y propiedad de una D-xxx, requiere **sign-off del operador**.

### FLAG-1 — D-010 (`strategies` entity; schema V1 documentado) — `Overall_WF.md`
**Propuesta:** anadir `demand_type` (capture_demand | generate_demand | mixed) al schema V1 de `strategies`.
**Naturaleza:** aditivo, cae bajo Pattern C [Evolving Schema]. NO requiere sobrescribir D-010.
**Por que se flaguea:** modifica el schema V1 canonico impreso en el overview.
**Decision del operador:** promover `demand_type` a columna de primera clase **ahora** (enum estable y cerrado: capture|generate|mixed) **vs.** dejarlo en `metadata` hasta que el uso lo justifique.
**Recomendacion del analisis:** primera clase ahora — gobierna la logica de canal desde el dia 1. No cambiar sin sign-off.

### FLAG-2 — D-012 (Living Flag Registry; seed v1 enumerado; rebuild-on-evidence) — `Overall_WF.md`
**Propuesta A:** anadir seed flag `zero_click_informational_decay` (productor AIO-TRAFFIC-001).
`| zero_click_informational_decay | Phase 4 (AIO-TRAFFIC-001: impresiones estables pero CTR/clics de query informacional cayendo, AI Overview presente en SERP) | mover mix de contenido a intencion transaccional + construir autoridad Top-10 para alimentar (no perder ante) AI Overview | Phase 2 (ese avatar) | yes |`
Mas en Phase 0 Foundation: auditar presencia de AI Overview por keyword prioritaria (keyword | intencion | AIO si/no | tipo dominio dominante | viabilidad).
**Naturaleza:** el registro esta DISENADO para crecer via adiciones producer-bound — es la ruta SANCIONADA, no un override.
**Por que se flaguea:** la tabla seed v1 esta impresa en el doc y es propiedad de D-012.
**Decision del operador:** aprobar la adicion de seed flag.
**Tension NO-conflictiva a confirmar (no resolver):** el corpus usa cadencias de REVIEW/benchmarking programadas (Curso 7 "revision cada 15 dias", benchmark mensual; Curso 3 freshness checks), compatibles con "review constantemente, rebuild solo por evidencia" (review != rebuild). **No se propone cambiar la regla no-calendar-REBUILD de D-012;** solo confirmar que la capa de review-cadence quede capturada en specs de Phase 4/5.

### FLAG-3 — D-014 R-5 (Vaynerchuk ratio per-channel ajustable por fatiga) — `Overall_WF.md` / Phase 2 / Phase 3
**Propuesta:** registrar un 8vo zona Pattern B: threshold `trust_cycle_target` sembrado de 7-11-4 (7h exposicion / 11 interacciones / 4 impactos en pain points), keyed por canal y nivel de awareness, ajustado por lag de conversion medido en Phase 4. Usado por Phase 2/3 para dimensionar el calendario.
**Naturaleza:** sibling de R-5 ya locked, usa el mecanismo exacto que D-014 establecio. Aditivo.
**Por que se flaguea:** D-014 enumero las zonas especificas que toco; anadir una 8va zona Pattern B es decision del operador, no in-scope automatico.

### FLAG-4 — D-013/D-014 R-6 (`kpi_primary` como [Extensible Vocabulary]) — Phase 2 / Phase 4
**Propuesta:** sembrar como miembros nombrados del seed: `completion_rate`, `avg_watch_time_s`, `saves`, `shares` (social); `open_rate`, `click_rate` (email); `avg_position`, `impressions` (SEO).
**Naturaleza:** el mecanismo [Extensible Vocabulary] ya lo permite via "other"; pero nombrarlos en el seed es una **promocion** del vocabulario.
**Por que se flaguea:** la promocion tiene costo gobernado por Pattern A (>=3 repeticiones + review).
**Decision del operador:** validar la promocion al seed bajo gobernanza Pattern A, **o** aceptarlos solo como `other`+descripcion por ahora.

### FLAG-5 — D-013/D-014 (mecanismo ratio) — Phase 2 / Phase 3
**Propuesta:** el corpus (Curso 7) aporta un valor concreto de referencia: **25/25/50** (viral/captacion/conversion), mas agresivo en CTA que el default **3:1** del spec.
**Naturaleza:** NO sobrescribir el 3:1 ni el mecanismo per-channel (que es superior y ya contempla ajuste por canal). NO toca el "alarm-stays-on".
**Decision del operador:** sembrar 25/25/50 como **default documentado por canal para RRSS organico B2C** dentro del marco Pattern B existente, **o** mantener 3:1 puro.

### FLAG-6 — D-014 R-7 (arquetipo Jungiano cerrado) — Phase 2
**Propuesta:** anadir a `brand_voice.json` (2.0) un campo `brand_promise` tipo CPM (Compromiso Principal de Marca: "Ayudo a [cliente] a [logro] via [metodo] sin [dolor]"), ademas del archetype.
**Naturaleza:** NO contradice ni reabre el enum cerrado de arquetipos (R-7 se mantiene). Aditivo, no reemplaza.
**Decision del operador:** extender el schema de `brand_voice` (Pattern C / schema_version) **o** dejarlo fuera de alcance de Phase 2.

### FLAG-7 — D-011 (test de distincion de avatar 2-de-3) — Phase 0 Research
**Propuesta:** extender el test de distincion con los 5 criterios de separacion de BMC Segmentos de Mercado (oferta distinta / canal distinto / tipo de relacion distinto / rentabilidad materialmente distinta / paga por cosas distintas).
**Naturaleza:** anadir rentabilidad y willingness-to-pay cambiaria la definicion del test locked (de 2-de-3 a 2-de-5); un nuevo gate de rentabilidad podria hacer "distintos" a dos avatares que el test actual fusiona, o viceversa.
**Decision del operador:** (a) mantener 2-de-3 y citar BMC solo como rationale de apoyo, **o** (b) ensanchar formalmente el test — lo cual es una **enmienda a D-011**.

### FLAG-8 — D-009/D-010 (Phase0/Phase1 boundary; Foundation avatar-agnostica; value equation en Phase 1) — Phase 0 Research
**Propuesta (derivada de C2/G19):** si se actua sobre el gap "propuesta de valor en Phase 0" jalando un artefacto de propuesta de valor a Phase 0, colisiona con el limite congelado por D-009/D-010 (value framing es per-avatar y Phase-1).
**Decision del operador:** confirmar que la reubicacion-a-Phase-1 se mantiene y **solo documentarla explicitamente en §0** del spec de Phase 0, **O** decidir anadir una "hipotesis de valor" liviana a nivel proyecto, claramente distinta de la value equation de Phase 1. NO sobrescribir.

### FLAG-9 — D-019 (Blue Ocean ERRC / tecnicas BMC "en sus fases naturales") — Phase 0 Research
**Propuesta:** colocar la lente Red/Blue Ocean en Phase 0 sub-step 0.4 (sintesis competitiva), produciendo un veredicto de posicionamiento (oceano rojo -> competir en posicionamiento/precio, nombrar el unico vector de diferenciacion sostenible = conocimiento profundo del mercado; oceano azul -> nicho no disputado).
**Naturaleza:** D-019 admite la tecnica pero dejo la **ubicacion de fase sin decidir** ("en sus fases naturales").
**Decision del operador:** confirmar si Phase 0 / 0.4 es la fase natural para el veredicto Blue-Ocean, **vs.** Phase 1 (oferta/posicionamiento). Bajo riesgo, pero es una decision que D-019 difirio.

### FLAG-10 — D-012 + D-005 (Phase 4 local) — Phase 4
**Propuesta (derivada de enrich 2.4.1):** el diagnostico de terminos en 4 categorias, para accionarse en Phase 5, implicaria una **bandera metrica NUEVA** de origen Phase 4 (p.ej. `paid_search_waste` para terminos out_of_model/non_converting).
**Naturaleza:** por la regla producer-binding, toda bandera que Phase 4 emite debe declararse en el registro canonico (`Overall_WF` §Flag Registry) con producer rule y su signal rule en §8 del spec.
**Decision del operador:** promover esta bandera al registro (con su productor) **o** mantener el diagnostico de terminos como dato raw sin bandera dedicada.

### FLAG-11 — D-012 + Phase-5 D8/D9 (open-diagnosis razona la causa; cheap_validation es metodo abierto) — Phase 5
**Propuesta (derivada de G15):** nombrar A/B testing como el primitivo `cheap_validation` por defecto en 5.1.b.
**Naturaleza:** roza el diseno locked de que 5.1.b es LLM-razonado y el metodo es deliberadamente abierto. La propuesta es aditiva (concreta un campo free-text con un default fundamentado y mantiene fallback cualitativo para hipotesis no-A/B-testables) — NO cierra el registro abierto.
**Decision del operador:** revisar antes de hardcodear A/B como default nombrado, dado que la forma reasoning-first/method-open de 5.1.b esta locked.

### FLAG-12 — D-011 / Phase-5 D11 + D-013/D-014 (re-trigger semantics; nueva vocabulary layer) — Phase 5
**Propuesta (derivada de G14):** adjuntar la taxonomia SEM de 4-categorias como tactica concreta bajo el retarget de `cac_up_40pct`, y anadir una capa de vocabulario "tactica de canal".
**Naturaleza:** compatible — ES lo que "fix targeting" significa operacionalmente y se mantiene dentro del re-trigger Phase 3 de la MISMA version activa. Pero la capa de vocabulario nueva debe taggearse [Extensible Vocabulary] con seed + "other" + gobernanza de promocion >=3x, NO congelarse como lista exhaustiva.
**Decision del operador:** (a) confirmar que anadir contenido tactico a esa fila no se malinterprete como disparo de version nueva, y (b) decidir si admite un nuevo vocabulario extensible (y asume su costo de gobernanza) vs. mantener las tacticas como referencias en prosa al corpus.

---

## 6. Prioridad de aplicacion (que primero)

### Tanda 0 — Erratas y aclaraciones de coherencia (sin riesgo, hacer ya)
1. **C1** — corregir redaccion de la fila D4 en Phase 4 (citar tabla por modelo, no "< 3.0"). El nombre del flag `ltv_cac_below_3` NO se toca.
2. **C4 / enrich 2.5.2** — clausula "revisar != reconstruir" en D10 de Phase 5.
3. **C2 / G19** — nota en §0 de Phase 0 Research documentando que la propuesta de valor esta reubicada a Phase 1 (solo documentar; el cambio activo es FLAG-8).

### Tanda 1 — Enriquecimientos seguros de alto valor (aditivos, sin tocar D-xxx)
4. **Phase 2:** subject_line de email (2.1.1) + char_limits de ads (2.1.2) + video_script_structure (2.1.3). Eliminan rebotes de assets y dan plantillas al operador V1.
5. **Phase 0 Research:** default sourced de conversion en DEMAND-004 (2.2.1) — desbloquea el math gate que hoy multiplica por una variable indefinida.
6. **Phase 3:** campo `format`/aspect-ratio (2.3.1) + reutilizacion cross-platform (2.3.2) — operabilidad inmediata del calendario.
7. **Phase 5:** sensor de competitive-shift para foundation_drift (2.5.1).

### Tanda 2 — Cerrar los 2 gaps criticos modernos (requieren decision -> FLAGS)
8. **FLAG-1 (demand_type)** + **G1** — el fork estrategico #1 del corpus. Recomendacion: aprobar como columna de primera clase. Habilita G1 en Phase 3 (`demand_type` en `audience_per_channel`).
9. **FLAG-2 (zero_click flag)** + **G2** — proteger el supuesto de trafico del Caso B. Ruta sancionada por D-012.

> Tanda 2 primero entre los FLAGS porque ambos cierran **gaps criticos de viabilidad/trafico**, no solo cobertura.

### Tanda 3 — Enriquecimientos seguros de valor medio
10. **Phase 0 Research:** Empathy Map (2.2.2) + workflow IA de pain points (2.2.3) + stack de herramientas (2.2.4).
11. **Phase 2:** Schema.org/JSON-LD (2.1.4) + re-impacto evergreen (2.1.5).
12. **Phase 3:** secuencias de email schedulables (2.3.3).
13. **Phase 4:** metodo de agregacion multi-plataforma en V2 (2.4.3).
14. **Phase 5:** comparacion de canvas BMC para diagnostico estructural (2.5.3).
15. **Setup Agent:** nombrar patron de pricing (2.7.1).
16. **Overall_WF:** nombrar glosario canonico como activo de retrieval (2.6 / G16).

### Tanda 4 — FLAGS de menor urgencia (decision del operador, sin presion de tiempo)
17. FLAG-4 (KPIs por canal al seed), FLAG-3 (7-11-4 trust_cycle), FLAG-10 (paid_search_waste), FLAG-11 (A/B como default), FLAG-12 (tactica de canal Phase 5).
18. FLAG-5 (25/25/50 seed), FLAG-6 (brand_promise CPM), FLAG-7 (test 2-de-5), FLAG-9 (Blue Ocean en 0.4), FLAG-8 (hipotesis de valor liviana en Phase 0).

### Diferibles a V2 (no urgentes, ni siquiera mencionados como diferidos en algunos specs)
- G22 (entidades/Knowledge Graph), G21 (Bing en US), G12 (funnel ManyChat RRSS), G23 (pipeline Windsor.ai), G24 (Make.com auto-respuestas), G25 (storytelling como tecnica), G17 (7-11-4 como ancla de cadencia — ligado a FLAG-3).

---

### Nota de cierre

El patron es consistente: **la metodologia de los specs esta solidamente anclada al corpus** (scores 8.0-9.0, cero contradicciones de fondo). El trabajo pendiente es de dos tipos: (1) **bajar la tactica de canal** que el corpus ya tiene operacionalizada al nivel donde el spec la consume (subject lines, limites de ads, guiones de video, secuencias de email, playbooks de Phase 5), y (2) **nombrar dos variables modernas** que el corpus enfatiza y el overview no eleva a primitivo — **captacion vs generacion de demanda** y **AI Overview / zero-click**. Lo primero es seguro y aditivo; lo segundo toca schema/registro impresos y por tanto pasa por la mesa del operador (FLAG-1, FLAG-2).
