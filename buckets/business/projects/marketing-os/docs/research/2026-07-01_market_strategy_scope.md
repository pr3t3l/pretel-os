# Papandi — Investigación de mercado + scope estratégico

**Fecha:** 2026-07-01 · **Método:** workflow multi-agente (7 frentes de research en paralelo → crítica de completitud → síntesis). Fuentes citadas inline.

> Los hallazgos crudos por frente + la crítica están en `2026-07-01_raw_findings.json`.

---

I now have enough grounding: Papandi (sandia-marketing) already has phase0/1/2 wizards, an estudio (production studio), a radar (temporal intelligence), a gateway (AI routing), calendar, and per-project cost ledger. The research maps directly onto this. Let me write the strategic report.

I have everything I need to write the report now.

---

# REPORTE ESTRATÉGICO — SCOPE DE PAPANDI
### Producción, coherencia de marca y el moat defendible
**Para:** el operador (decisión de scope) · **De:** estrategia de producto · **Fecha:** 2026-07-01

---

## ⚡ TL;DR (léelo aunque no leas nada más)

1. **El mercado NO rechaza la IA — rechaza lo que no puede verificar.** Ese es el hallazgo más fuerte y más cross-cultural de todo el research (80% prefiere la versión CON fuentes; solo 7% confía más por ver IA visible). **Tu glass-box ya construido es tu moat, no un detalle.**
2. **Hay un hueco real y validado:** un OS de estrategia + voz de marca + ejecución coherente para el SMB/solopreneur. Copy.ai se fue a enterprise ($249+), Icon.com valida la demanda de consolidación pero **cojea en ejecución** (renders lentos, exports al 99%). El hueco es de CEREBRO + COHERENCIA, no de otra fábrica de output.
3. **Producción NO debe ser un playground tipo Kling/OpenArt.** Debe ser un **motor de coherencia**: mismo personaje/voz/marca a través de N ganchos, con el prompt exacto y el trail de fuentes. El playground es table-stakes que ya regala fal.ai por debajo; el cerebro que decide QUÉ generar y CÓMO mantener la marca es lo defendible.
4. **Tú eres el cerebro; fal.ai/Replicate son las manos.** Integra por encima del router, nunca cablees un modelo (Sora 2 pasó de exclusiva a "discontinuado" en meses — la volatilidad de proveedor es un riesgo cuantificado).
5. **⚠️ El research tiene un hueco que invalida decidir hoy el modelo de negocio:** cero willingness-to-pay medida del ICP real, cero voz cruda del comprador, cero costo unitario calculado. **Puedes decidir el SCOPE DE PRODUCTO ahora; NO puedes fijar precio ni cerrar el caso de negocio sin dos experimentos baratos (§9).**

---

## 1. La verdad del mercado: qué esperan de la IA-marketing

### El hallazgo maestro (todo lo demás cuelga de aquí)
> **El comprador no rechaza el contenido de IA. Rechaza el contenido que no puede VERIFICAR.**
> Cuando a la gente le muestran dos versiones de un resultado, **80% prefiere la que trae fuentes humanas auténticas, fuentes creíbles y links accionables** ([Fast Company Brasil](https://fastcompanybrasil.com/ia/a-busca-por-ia-tem-um-problema-de-confianca-transparencia-e-a-solucao/)). Solo **7%** dice que ver marketing hecho-con-IA aumenta su confianza; **31%** dice que la baja ([eMarketer/Klaviyo, 8.000+ consumidores, 8 países](https://www.emarketer.com/content/shoppers-aren-t-impressed-by-ai-generated-marketing)).

Esto reencuadra todo: **el enemigo no es la IA, es la in-verificabilidad.** Y eso juega exactamente a favor de lo que ya construiste (glass-box, "el prompt exacto que pegas", entregable accionable).

### Universal vs cultural

| Dimensión | US | España | Brasil |
|---|---|---|---|
| **Transparencia + etiquetado** | 80-91% lo quiere ([Emplifi](https://www.emarketer.com/content/shoppers-aren-t-impressed-by-ai-generated-marketing)) | 90% quiere transparencia en imágenes IA | 90% igual; 69% quiere OPCIÓN de salir a sitios confiables |
| **Sesgo dominante** | Más anti-GenAI visible, más generacional (50% prefiere marcas que EVITAN GenAI — [Gartner](https://www.gartner.com/en/newsroom/press-releases/2026-03-16-gartner-marketing-survey-finds-50-percent-of-consumers-prefer-brands-that-avoid-using-genai-in-consumer-facing-content0)) | Exige **metodología/evidencia**; desconfía de "resultados extraordinarios sin método" ([Cyberclick](https://www.cyberclick.es/numerical-blog/preguntas-para-elegir-una-agencia-de-marketing-con-ia-en-espana)) | Más abierto a IA transaccional (40% acepta que la IA compre por ellos) pero igual de exigente en transparencia de fuentes |
| **Núcleo universal** | Transparencia · verificabilidad · opt-out · autoría humana · **velocidad de respuesta** (lo más valorado cross-market) | ← idéntico | ← idéntico |

**Regla de expansión:** UNA arquitectura de confianza (transparencia + verificabilidad + opt-out + autoría humana), localizar **solo el énfasis** del mensaje, no la lógica del producto.

### El JTBD por el que se contrata una herramienta/agencia de marketing
Ya no basta "campañas llamativas o más followers". El comprador de 2025-26 quiere ([Nautilus](https://nautilusmarketing.co.uk/what-modern-day-clients-expect-digital-marketing-agency/), [Whatagraph](https://whatagraph.com/blog/articles/exceeding-client-expectations)):
- **Resultados medibles**, no actividad.
- **Agilidad** (rollouts rápidos, test/iterate, recomendaciones proactivas).
- **Transparencia en tiempo real** (un espacio central para ver progreso, aprobar assets, ver costo/métricas on-demand).
- **Prueba de valor antes de pagar premium** (9 de 10 power users pagan prima SOLO con valor demostrado; 39% prefiere pay-as-you-go — [G2 Buyer Behavior 2025](https://images.g2crowd.com/uploads/attachment/file/1470753/2025-G2-Buyer-Behavior-Report.pdf)).

### La lección Jasper (el abismo G2 vs Trustpilot)
Jasper: **4.7/5 en G2** (power users que invirtieron en aprender) vs **3.4/5 en Trustpilot** (los que esperaban plug-and-play). **El mercado masivo es la población Trustpilot** — castiga la complejidad, la curva de aprendizaje y la facturación opaca. Lo más odiado: output genérico, tono sobre-entusiasta, "tengo que fact-checkear cada afirmación", suscripciones turbias con upsells ([eyesift](https://www.eyesift.com/blog/jasper-ai-review/), [G2](https://www.g2.com/products/jasper-ai/reviews?qs=pros-and-cons)).

> **Implicación #1 para Papandi:** El glass-box deja de ser footnote y pasa a ser el **feature de confianza central**. Cada deliverable sale con su trail de fuentes + el prompt/asset exacto que el usuario pega y **posee**. Eso responde el hallazgo maestro directamente.

---

## 2. Panorama competitivo + precios + el HUECO

### El tablero (ordenado por lo que revela)

| Herramienta | Qué es | Precio | Fortaleza | Hueco / debilidad |
|---|---|---|---|---|
| **Icon.com** ⭐ | "AI CMO / 14-en-1" | **$39/mes** | La señal más fuerte: mercado quiere consolidación. $0→$5M ARR en 30 días, Founders Fund | **Cojea en ejecución**: renders lentos, exports al 99%, glitches. Vende ejecución de ADS, no estrategia |
| **Copy.ai** | Pivotó a "GTM AI Platform" | **$249+/mes** | Orquestación GTM, "elimina el bloat" | **Abandonó el SMB** → se fue a enterprise/ventas |
| **Jasper** | Copy de marca (Brand Voice) | $69-250+/seat | Brand Voice, drafts rápidos | Text-only, output genérico, billing turbio |
| **Canva Magic Studio** | Suite multimodal de EJECUCIÓN | **$15/mes** | Mejor relación precio-capacidad; outputs editables | Es diseño/ejecución, **no cerebro de estrategia** |
| **AdCreative.ai** | Fábrica de creativos de performance | $39-999 | Volumen + scoring de conversión | Fábrica de creativos, no OS |
| **HubSpot Breeze** | IA dentro del CRM | $0-4.700+ | IA de marca en CRM | "Only works in HubSpot"; encierro |
| **Creatify / Flair / Predis** | Monofunción (UGC / foto-producto / social) | $10-49 | Baratas, nicho | Jaulas de crédito; sin estrategia ni coherencia |

### El dolor transversal de 2026: "AI slop"
El insulto definitorio del año. **54% de estadounidenses reportan fatiga de IA.** Causa raíz: la IA se entrena en "el promedio de internet", así que su default suena como todos ([averi.ai](https://www.averi.ai/blog/the-ai-content-crisis-why-your-brand-voice-sounds-like-everyone-else-s), [mojo.biz](https://mojo.biz/anti-ai-backlash-real-heres-how-smart-brands-are-using-ai-without-looking-they-are)). Los que ganan ponen la IA en las **DECISIONES** (audience intelligence, optimización), no visible en el output — con voz de marca definida, guardrails y revisión humana.

### El HUECO que Papandi puede tomar

```
        EJECUCIÓN barata          ⟵── ocupado (Canva $15, AdCreative, Creatify)
        y multimodal

        CRM / enterprise          ⟵── ocupado (HubSpot, Copy.ai $249+)

  ┌─────────────────────────────┐
  │  CEREBRO (estrategia + voz   │  ⟵── VACÍO / mal servido
  │  de marca profunda) +        │     Icon lo intenta pero es ejecución de ads y cojea
  │  COHERENCIA multicanal +     │     Copy.ai se fue. Nadie da estrategia + coherencia
  │  glass-box, para el SMB      │     + glass-box para el operador chico.
  └─────────────────────────────┘
```

> **⚠️ Nota de honestidad (de la crítica):** El hecho de que Copy.ai *abandonara* el SMB puede significar que **no era rentable**, no que esté libre. Icon vende ejecución a $39, no estrategia — es evidencia **débil o contraria** a la tesis "se paga por estrategia". **Esto no es un veredicto; es una hipótesis que debes probar (§9) antes de invertir la capa de cerebro cara.**

**Ancla de precio del mercado:** $15-49/mes está normalizado para "suite" (Canva $15, Creatify $49, Icon $39). Papandi entra en esa banda o justifica prima con estrategia+coherencia que nadie da. Pero **ese ancla se deriva de competidores, no de willingness-to-pay medida de tu ICP** (§9).

---

## 3. Routers de arte/video: cuál para qué + "nosotros el cerebro, ellos las manos"

### El mercado ya se dividió en capas
**Routers/agregadores** (fal.ai, Replicate) exponen decenas/cientos de modelos bajo UNA clave. **Modelos** (Kling, Veo, Seedance, FLUX, Sora) son las manos. **Papandi se integra en la capa de router — nunca cablea un modelo.** Esto no es opinión: el propio CLAUDE.md lo prohíbe (no client lock-in), y "un despliegue de producción mediano usa 14 modelos distintos" ([teamday.ai](https://www.teamday.ai/blog/ai-image-video-api-providers-comparison-2026)).

> **⚠️ Cifra load-bearing marcada:** ese "14 modelos" viene de UN blog de vendor y coincide sospechosamente con el pitch "14-en-1" de Icon. **Trátalo como direccional, no como dato duro.** La tesis del router se sostiene igual por el patrón cualitativo (fal, Higgsfield, OpenArt todos multi-modelo), no por ese número.

### fal.ai vs Replicate (la capa de acceso)

| | **fal.ai** | **Replicate** |
|---|---|---|
| Endpoints | ~985 (una sola API/clave) | ~200 |
| Precio/velocidad | ~30-50% más barato (hasta 80% en video), cold-start <1s | Mejores docs/comunidad |
| Exclusivas | Sora 2, Kling O1, Seedance 2.x | Excluye propietarios como Sora 2 |
| Patrón | `fal.subscribe()` + webhooks (async) | Similar |

**Recomendación:** **fal.ai como capa primaria** (más endpoints, mejor costo/velocidad, async/webhooks nativo), Replicate como fallback. Ambos pay-per-use, sin suscripción.

### La TABLA DE ENRUTAMIENTO (esto es tu propiedad intelectual defendible)

| Intención de marketing | Modelo | Costo (verificar en build) |
|---|---|---|
| Imagen de producto con **texto legible** | GPT Image / FLUX [max] | FLUX ~$0.05/img |
| **Personaje de marca consistente** en carrusel (edición por texto) | **FLUX.1 Kontext** (~92% identidad con 1 ref) | pro/max |
| Commodity barato en volumen | SDXL | $0.003/img |
| Anuncio hablado con **lipsync** | **Veo 3.1** (diálogo+SFX+ambiente) o Seedance | Veo Std $0.40/s, Fast $0.15/s |
| **Mini-película multi-toma, misma mascota, multiidioma** | **Kling 3.0** (reference locking + Voice Binding, 5 idiomas) | Kling ~$0.09/s |
| Video cinematográfico + física + audio nativo | **Seedance 2.x** (hasta 50 refs) | Fast $0.04/s |
| Movimiento de cámara específico (dolly/orbit) | **Higgsfield** (Motion DNA) | por suscripción |
| Talking-head / avatar puro | **Hedra Character-3** | — |
| Imagen 4K de alta consistencia | Seedream 4.x | ~$0.04/img |

### La estrategia "nosotros el cerebro, ellos las manos"
- **Papandi decide:** qué generar, con qué modelo, con qué referencias, y produce **el prompt exacto**. El usuario lo pega en su generador **O** Papandi lo ejecuta vía fal.
- **Diseña por REFERENCIAS desde el día 1:** captura imagen de referencia de marca/personaje + start/end frame, porque TODOS los modelos top ya los consumen (Veo hasta 3, Seedance hasta 50, Kling N). **Sin esto Papandi no puede prometer coherencia de marca** — que es tu moat.
- **Abstrae al proveedor por volatilidad:** trata cada modelo como intercambiable detrás del router y degrada con gracia (si "audio nativo" → Veo/Seedance; si cae uno, el otro). Replica el patrón de degradación que ya usa el Router de pretel-os.
- **Costeo por tarea listo para el ledger:** precios públicos por unidad → pre-estima y atribuye por `project_id` **antes** de generar (encaja con tu cost ledger y el tope `MEDIA_BUDGET_USD=20`).

### Riesgo cuantificado de proveedor
Sora 2 pasó de exclusiva a reportarse **discontinuado (24-sep-2026)**; Midjourney y Luma **no tienen REST estable** (Discord/web-app) → probablemente fuera del MVP. **Regla:** ningún modelo individual debe ser >X% del valor de Papandi. La tabla de enrutamiento es un activo vivo que hay que mantener; presúpuestalo como costo recurrente, no one-time.

---

## 4. VEREDICTO: ¿Producción = playground tipo Kling/OpenArt, o algo distinto?

### 🎯 VEREDICTO: NO un playground. Un MOTOR DE COHERENCIA con glass-box.

**Razonamiento con la evidencia:**

1. **El playground ya es commodity.** fal.ai regala ~985 endpoints por debajo; OpenArt/Higgsfield ya son el playground bonito. Si Papandi compite en "acceso a modelos + UI de generación", pelea contra suites con años de ventaja (Canva $15) y pierde. **La amplitud de generación no es defendible.**

2. **Lo que el mercado NO tiene y SÍ duele:** coherencia de marca de punta a punta (queja #1 = "AI slop", output genérico) + verificabilidad (hallazgo maestro). Ningún playground resuelve "mismo personaje + misma voz + misma marca a través de 20 ganchos distintos, con el trail de por qué". **Ese es el trabajo.**

3. **El estado del arte confirma la dirección:** Coca-Cola + Adobe **Project Fizzion** (mayo 2025) codifica la intención creativa en un **"StyleID" legible por máquina** que aplica reglas de marca automáticamente across formatos/plataformas/mercados. Modelo explícito: **"Designers Lead. AI Follows"** ([Coca-Cola](https://www.coca-colacompany.com/media-center/the-coca-cola-company-introduces-fizzion)). **Esa es literalmente la tesis de un OS de marketing con IA — y hoy solo la tienen las Fortune 500.** Papandi puede democratizarla para el SMB.

4. **Lo que sí debes copiar del playground (table-stakes de UX):** controles de referencia + slider de influencia 0-100 (como `--cref`/`--sref` de Midjourney), outputs **editables** (no PNG plano), iteración sin ansiedad de costo. Pero eso es el **cómo se ve**, no el **qué es**.

> **En una frase:** Producción en Papandi = *"dame la marca y el gancho, te devuelvo la campaña coherente, con el prompt exacto y las fuentes, lista para que TÚ la apruebes y la poseas"* — no *"aquí tienes 100 modelos, suerte"*.

---

## 5. Coherencia de marca en campañas

Este es el corazón del moat. El research de marca es el más accionable de todos.

### 5.1 Cómo mantener identidad a través de distintos ganchos: el modelo de DOS CAPAS

> **Principio operativo de las marcas de clase mundial:** *"modifica cómo apareces sin cambiar quién eres"* (Coca-Cola, 138 años — [Resound](https://resoundcreative.com/what-138-years-of-coca-cola-teaches-about-brand-consistency/)).

**Papandi debe modelar la marca en dos capas explícitas:**

| **CAPA 1 — CORE INMUTABLE** (guardrail en CADA pieza) | **CAPA 2 — EXPRESIÓN DE CAMPAÑA** (varía por gancho) |
|---|---|
| Logo, paleta, tipografía | Gancho / ángulo creativo |
| **Voz cuantificada** (no adjetivos prosaicos) | Imagen/video específico |
| Promesa de marca | Copy de la ejecución |
| Personaje/mascota + refs | Canal y formato |
| Disclaimers legales | Datos del listing/evento |

**Cuantifica la voz** (crítico para reproducibilidad por IA): escala tipo NN/g de 4 dimensiones (Funny-Serious, Formal-Casual, Respectful-Irreverent, Enthusiastic-Matter-of-fact) → perfil "80% casual, 7/10 entusiasmo" + ejemplos do/don't ([Column Five](https://www.columnfivemedia.com/brand-voice-vs-tone/)). **La IA sigue reglas cuantificadas de forma fiable; falla en ironía/humor sutil → por eso el humano queda en el loop para esas capas.** No prometas voz perfecta 100% automática.

**El equivalente al StyleID de Fizzion es tu ventaja directa:** un objeto de marca legible por máquina (design tokens + voz cuantificada + assets aprobados) que se **inyecta como contexto/guardrail en TODA generación**. Ya tienes la infraestructura conceptual (`design_spec`, brand guidelines por proyecto). **Formalizarlo como "brand StyleID inyectado en cada prompt" es la implementación de referencia del líder del mercado.**

### 5.2 La "Big Idea" como entidad de primera clase
Una campaña **no es una lista de piezas sueltas** — es UNA idea rectora + N ejecuciones derivadas. Anti-patrón real: Johnnie Walker tenía 7 campañas desconectadas que no se apoyaban → se unificó bajo **"Keep Walking"** ([Smart Insights](https://www.smartinsights.com/traffic-building-strategy/campaign-planning/four-steps-developing-big-idea-campaign/)). **Papandi debe forzar estructuralmente que cada pieza declare a qué Big Idea pertenece.**

Debajo de la Big Idea: **3-7 content pillars** fijos de los que sale TODO el contenido → garantizan coherencia temática entre campañas distintas sin coordinar pieza por pieza ([Kontent.ai](https://kontent.ai/blog/content-pillars/)).

### 5.3 Reutilizar multimedia entre campañas: atomización hub-and-spoke
Un activo core (Big Idea / whitepaper / video) → decenas de spokes (blog, carrusel, clips, email) **reshaped por canal, NO republicados idénticos** ([Bluetext](https://bluetext.com/blog/the-content-atomization-playbook-one-idea-dozens-of-deliverables/)). Cada spoke se mapea al buyer journey (awareness/consideration/decision) y a un pillar. **Esto es un flujo NATIVO de Papandi, no un extra.**

### 5.4 Integrar la identidad visual de una empresa
El onboarding debe **extraer** el StyleID de la marca del cliente (subir logo/guía → derivar tokens + refs de personaje) y luego inyectarlo. `guidelines != design system`: uno dice las reglas, el otro las **aplica consistente cada vez** ([whatifdesign](https://whatifdesign.co/feeds/blog/brand-guidelines-vs-design-system)). **Papandi necesita AMBOS:** reglas legibles + sistema que las aplica automáticamente.

---

## 6. Recomendación de UI/UX + biblioteca/DAM + flujo de aprobación

### 6.1 UI/UX de la biblioteca: board visual, NO árbol de carpetas
Copia el modelo **Air** (la referencia de UX): thumbnails en Boards/sub-boards, vistas conmutables **Gallery / Table / Kanban**, vistas guardadas, version stacking con compare lado a lado, anotación sobre el asset, auto-tag por IA, **cero training** ([Air](https://air.inc/resources/best-dam-solutions), [Picflow](https://picflow.com/compare/dam/air-inc)). Default: **Kanban-para-aprobaciones** como vista de campaña.

### 6.2 Los 3 mandatos de UX no-negociables (los más citados en TODO el research)

1. **🚫 NUNCA cobrar créditos por regeneración dentro del loop creativo.** Es el patrón MÁS odiado (Canva, Figma Make, Lovable): usuarios queman "3000+ créditos en una hora" y **dejan de iterar por ansiedad de costo** — lo opuesto a lo que un OS de IA quiere. "El artboard es un cementerio de ideas descartadas" ([Medium](https://medium.com/design-bootcamp/credit-limits-and-the-death-of-design-exploration-1798256671aa), [Figma forum](https://forum.figma.com/share-your-feedback-26/figma-make-ai-credit-limits-not-feasible-51713/)). → Empaqueta iteración generosa en la suscripción; mide al nivel de campaña/asset final, no por tweak.

2. **📝 Todo output aterriza en un objeto EDITABLE y estructurado** (capas, texto, brand tokens), nunca un PNG plano. Es la ventaja #1 citada de Canva; los generadores de PNG plano "obligan a recrear manualmente" ([aitoolanalysis](https://aitoolanalysis.com/canva-magic-studio-review/)).

3. **🎨 Brand kit EMPUJADO al flujo como guardrail activo**, no un PDF de referencia. Colores/fuentes/logos a un click; auto-flag de output off-brand; validación de marca en tiempo de generación → ser el *"active governance engine"* que el mercado dice que falta ([Frontify guide](https://www.frontify.com/en/guide/ai-tools-for-brand-management)).

**Además:** expón controles de **referencia + influencia 0-100** (no solo un prompt box). Y diseña la **búsqueda como feature de primera clase desde el día 1** — es donde hasta Frontify falla a escala (búsqueda débil, sin auto-tag). Tu stack LLM/embeddings es ventaja natural aquí. Los usuarios pierden hasta **20 min y 35% de su día** buscando assets ([monday.com](https://monday.com/blog/project-management/marketing-asset-management/)) — haz de *"nunca pierdas un asset"* una promesa headline.

> **⚠️ Cifras 35%/20min marcadas como direccionales** — vienen de blogs de vendor de DAM (sesgo de venta). El dolor es real y convergente, pero no las trates como dato duro.

### 6.3 DAM: el reto real es ADOPCIÓN, no tecnología
El cuello de botella recurrente: equipos suben archivos sin metadata, duplican, saltan aprobaciones → bypassean el sistema cuando la aprobación es lenta ([Marq](https://www.marq.com/blog/brand-governance/), [Stockpress](https://stockpress.co/resources/5-best-practices-for-smart-digital-asset-management/)). **Regla de oro:** *"hacer lo correcto más fácil que lo incorrecto"* — reutilizar debe ser más fácil que recrear, o el DAM muere.

### 6.4 Flujo de aprobación: gates por riesgo, NO cadenas de email

**Tres carriles por riesgo** ([Typeface](https://www.typeface.ai/blog/content-quality-control-in-ai-marketing-enterprise-governance-and-best-practices), [Marq](https://www.marq.com/blog/brand-governance/)):

| Riesgo | Ejemplo | Gate | SLA |
|---|---|---|---|
| **Bajo** | Post social | Checks automáticos + 1 aprobador (o auto-clear) | 2-4h |
| **Medio** | Blog / email | Validación completa + revisión marketing | 1-2 días |
| **Alto** | Comms ejecutivas / posicionamiento | Multi-nivel incl. legal | 3-7 días |

Con **regiones locked vs flexible**: locked (logo, layout, disclaimers) hacen CONFIABLE la generación automática; flexible (gancho, imagen, copy) es donde la IA opera. Anotación sobre el asset + routing automático + status visible (mata el *"¿dónde está mi aprobación?"*).

> **💰 Diferenciador de pricing concreto:** **NO cobres por asiento a revisores/externos.** La queja #1 de Ziflow es que cada cliente/freelancer necesita un seat pagado ([Ziflow vs Filestage](https://www.ziflow.com/blog/ziflow-vs-filestage)). Deja que externos comenten/aprueben por **link sin login ni seat**. Edge real para el SMB/solo-marketer.

---

## 7. Qué hacen las mejores agencias — y qué necesita Papandi para estar a su nivel

### El diferenciador #1 no es la ejecución: es el RIGOR que da permiso para arriesgar
- **Mischief:** *"nuestro rigor nos da permiso para estar locos"* — ganan Effie/WARC de efectividad Y son las más atrevidas.
- **Wieden+Kennedy:** *"Fail Harder"*, reaccionan a la cultura no a la logística, juegan el juego largo.
- El patrón: **base analítica dura debajo, audacia arriba.** El promedio invierte el orden ([Ad Age](https://adage.com/events-awards/a-list-creativity/aa-mischief-2026/)).

### El brief es el punto de falla MÁS CARO de la industria
> **33% del presupuesto de marketing se desperdicia por briefs pobres.** 80% de marketers creen que escriben buenos briefs; solo **10% de agencias coinciden** ([IPA/BetterBriefs, 1.700+ profesionales, 70+ países](https://ipa.co.uk/news/betterbriefs)).

**Esto es tu punto de mayor apalancamiento.** Un módulo de Papandi que produzca un **brief de calidad-agencia** (UN insight diferenciador, dirección estratégica clara, "pensamiento reductivo": todo lo que necesitas y nada más) es un wedge diferenciable y **medible**. Es el eslabón entre tu Inteligencia Temporal (radar) y tu Estudio de Producción.

### El playbook AI-native (cómo medir PMF real)
- **PMF real = "la IA hace una parte MATERIAL del trabajo a alto margen bruto (50%+)"**, medido por **RPE** (revenue per employee) y **HURT** (minutos de revisión humana por deliverable). Si HURT tiende a cero, el margen tiende a software ([Emergence Capital](https://www.emcap.com/thoughts/the-ai-native-services-playbook)).
- **Señal de fracaso ("mirage PMF"):** márgenes planos, entrega humana-pesada, trabajo bespoke que crece con cada cliente.
- **Productizar del PATRÓN, no del día uno:** custom primero (revela problemas comunes), estandarizar cuando emergen reglas (~80 clientes). **Enfócate en 1-2 jobs-to-be-done; la amplitud es "el camino más rápido al mirage PMF".**
- **Data flywheel = el foso:** cada engagement mejora la IA y hace la entrega más predecible. Ya tienes la infraestructura (buckets/projects/lessons/embeddings) — el diseño debe hacer que cada corrida **componga ventaja**, no solo entregue output una vez.

> **Para estar al nivel de las mejores, Papandi necesita 3 cosas que YA puede construir:**
> 1. **Un gate de brief** que obligue a UN insight antes de generar (replica a Mischief/W+K).
> 2. **Instrumentar HURT** (cuánto corrige el operador por pieza) como métrica de PMF, no volumen de output.
> 3. **El data flywheel explícito** (cada keyword research / pieza / calendario mejora el contexto del proyecto para la siguiente).

---

## 8. EL SCOPE RECOMENDADO

### 8.1 ¿Quién es el USUARIO? (fundamentado — y con la salvedad de la crítica)

> **⚠️ HONESTIDAD BRUTAL:** el research **NO investigó quién es el usuario de Papandi.** Mezcló cuatro compradores incompatibles (consumidor final anti-IA, marketer B2B enterprise, agencia, solopreneur) y extrapoló como si fueran uno. **Todo el scoping cuelga de definir esto — y hoy está inferido, no medido.**

**Hipótesis de ICP (a validar en §9), triangulada desde la evidencia + tu memoria:**

> **El solopreneur / dueño de PYME (o freelancer de marketing con 5-15 clientes) que vende a mercado US-inglés, no es técnico, y hoy hace malabares con Jasper + Canva + Buffer + AdCreative por separado — datos que no fluyen entre silos.**

Por qué esta hipótesis y no otra:
- **Copy.ai dejó este segmento** (se fue a $249+ enterprise) e **Icon lo valida** (aunque cojea).
- Es la **población Trustpilot** (castiga complejidad/billing opaco) → tu UX "Desarrollar idea"/grid+detalle apunta ahí.
- El caso del operador solo (12 retainers a $750-1k, <$500/mes en tools, [Unkoa](https://www.unkoa.com/one-person-agency-10x-output-how-solo-marketers-use-ai-to-scale-in-2025/)) muestra que **existe un ICP que paga por leverage** — pero es ilustrativo, no benchmark.
- Coherente con tu estrategia de idioma (back en inglés, salida por locale) y tus memorias (oferta por funcionalidad, fase 2 por avatar).

**Lo que NO sabes de este ICP (huecos que bloquean el caso de negocio):** su willingness-to-pay concreta, cuántos hay, su CAC, y **si pagaría por ESTRATEGIA vs ejecución barata**.

### 8.2 NECESARIO (el MOAT) vs POSIBLE (table-stakes)

| **NECESARIO — el MOAT (constrúyelo tú, es defendible)** | **POSIBLE — table-stakes (úsalo por debajo / copia el patrón)** |
|---|---|
| 🧠 **Cerebro de estrategia**: gate de brief (1 insight), Big Idea + content pillars como entidades | 🔌 Generación multimodal → **fal.ai por debajo** (no reconstruir) |
| 🎨 **StyleID inyectado** (voz cuantificada + tokens + refs) en cada generación | 🖼️ UI de biblioteca board-based → copiar patrón Air |
| 🔍 **Glass-box / verificabilidad**: cada deliverable con trail de fuentes + prompt exacto | ✅ Flujo de aprobación con anotación + carriles por riesgo |
| 🔗 **Coherencia multicanal**: atomización hub-and-spoke reshaped por canal | 📅 Calendario / scheduling |
| ♻️ **Data flywheel**: cada corrida mejora el contexto del proyecto | 🏷️ Auto-tag / búsqueda semántica (tu stack embeddings ya lo habilita) |
| 📊 **Métricas de relación** (fatiga/engagement de calidad), no vanity clicks | 💳 Cost ledger por `project_id` (ya lo tienes) |

**La regla:** no compitas en amplitud de diseño (Canva) ni volumen de ads (AdCreative). Diferénciate en la **CAPA DE CEREBRO + COHERENCIA + GLASS-BOX** que ninguna herramienta de ejecución tiene.

### 8.3 ROADMAP por fases (qué construir primero)

**El principio rector: productizar del patrón, 1-2 JTBD, no amplitud.**

```
┌── FASE 0 (ANTES de construir más) — DESCONFIRMAR ───────────────┐
│  • Smoke test / fake-door: "OS de estrategia+marca" vs           │
│    "fábrica barata de output" → ¿por cuál paga el ICP?           │
│  • 10-20 entrevistas + modelado de costo unitario                │
│  → Sin esto, todo lo de abajo es apuesta a ciegas.               │
└──────────────────────────────────────────────────────────────────┘

FASE 1 — EL MOAT MÍNIMO (el wedge medible)
  1. Gate de BRIEF (1 insight diferenciador) ← mayor apalancamiento
  2. StyleID por proyecto (voz cuantificada + tokens + refs) inyectado en generación
  3. Glass-box en cada deliverable (fuentes + prompt exacto)
  → JTBD #1: "dame un brief y una pieza coherente que YO pueda verificar y poseer"

FASE 2 — COHERENCIA MULTICANAL (lo que nadie da)
  4. Big Idea + content pillars como entidades de primera clase
  5. Atomización hub-and-spoke (1 core → N spokes reshaped por canal)
  6. Producción como MOTOR DE COHERENCIA sobre fal.ai (tabla de enrutamiento
     + diseño por referencias + outputs editables + iteración sin ansiedad de costo)

FASE 3 — BIBLIOTECA + GOVERNANCE (adopción = reutilizar > recrear)
  7. DAM board-based (patrón Air) con auto-tag + búsqueda semántica
  8. Aprobación por carriles de riesgo + regiones locked/flexible + link sin seat
  9. Data flywheel explícito + métricas de relación

FASE 4 — GLOBAL (solo cuando el núcleo US retiene)
  10. Modo transcreación con checkpoint humano (NO traducción)
  11. Disclosures de IA automáticos (C2PA/metadata) por plataforma/jurisdicción
```

**Por qué este orden:** Fase 1 es el moat mínimo *medible* (brief + StyleID + glass-box) — ataca la queja #1 (AI slop) y el hallazgo maestro (verificabilidad) a la vez. Producción entra en Fase 2 **como motor de coherencia, no como playground** (que es lo que el veredicto §4 dictó). La biblioteca/aprobación es Fase 3 porque solo crea valor cuando ya hay volumen de assets que reutilizar. Global es Fase 4, nunca antes de retener el núcleo.

---

## 9. Riesgos + preguntas abiertas (de la crítica)

### 🔴 Riesgos que pueden hundir el barco

| Riesgo | Por qué importa | Mitigación |
|---|---|---|
| **La tesis "se paga por estrategia" no está validada** | Icon vende ejecución a $39, no estrategia. Copy.ai *huyó* del SMB (¿no rentable?). Evidencia débil/contraria | **Fase 0 obligatoria**: smoke test de mensajería antes de invertir la capa de cerebro cara |
| **Economía unitaria sin calcular** | Video a $0.40/s + tope $20 + "no cobrar por regeneración" pueden ser **incompatibles**. Margen IA = 50-60%, no 80-90% | Modelar costo real por deliverable vs precio-ancla ANTES de fijar el modelo |
| **Churn, no adquisición, define la viabilidad** | IA <$50/mes retiene solo **23% del ingreso a 12 meses** ([Userpilot](https://userpilot.com/blog/customer-churn/)); "maldición del AI wrapper" | Activación a UN resultado publicable en la 1ª sesión; evitar el segmento <$50 como oferta central; empujar anual |
| **Paradoja del etiquetado** | 80-91% EXIGE etiquetar IA, pero etiquetar "AI-made" **baja** la calidad percibida de contenido idéntico ([NIM](https://www.nim.org/en/publications/detail/transparency-without-trust)) | El escape es **calidad que sobrevive el escrutinio** (glass-box), no ocultar la IA. Pero **verifica si el etiquetado es OBLIGATORIO** (EU AI Act etiqueta desde ago-2026; FTC; Meta/TikTok) → convierte feature en requisito no-negociable del MVP |
| **Volatilidad de proveedor** | Sora 2 exclusiva → discontinuada en meses | Ningún modelo >X% del valor; degradación con gracia; tabla de enrutamiento como activo vivo con costo de mantenimiento |
| **Adopción del DAM** | El sistema muere si crear on-brand no es más fácil que la alternativa | "Hacer lo correcto más fácil que lo incorrecto" como principio de diseño no-negociable |

### ❓ Preguntas abiertas (contradicciones sin resolver en el research)
- **¿Reemplazar o amplificar la voz?** Un stream castiga la automatización sin humano; otro celebra a Icon por "68 ads en 30 min". **No reconciliado.** → Tu postura: amplificar (human-in-the-loop), pero medir si el ICP realmente lo valora o solo quiere volumen.
- **¿Pay-as-you-go o anti-créditos?** Ambos son "por uso" pero uno recomienda pay-as-you-go y otro dice que créditos-por-tweak es lo más odiado. → Resolución: métrica al nivel de campaña/asset final, iteración libre. Pero choca con tu `MEDIA_BUDGET_USD=20` → **modelar §9**.
- **¿Gen Z anti-IA o pro-IA?** Declaran desconfianza pero son los mayores usuarios de IA. Puede ser desconfianza **declarada, no comportamiento**. No cruzar sin datos de adopción por edad.
- **¿Distribución/publicación?** El "OS multicanal" es hoy una **promesa sin validar en su capa de ejecución** — nadie investigó APIs, rate limits, ni políticas de contenido-IA de Meta/TikTok/LinkedIn/X. **Sin canal de publicación, el "multicanal" no existe.**

---

## 🎯 LAS 3 DECISIONES QUE DEBES TOMAR AHORA

> Estás saturado. Reduce a esto. Todo lo demás espera.

### **DECISIÓN 1 — ¿Producción es playground o motor de coherencia?**
**Recomendación: MOTOR DE COHERENCIA, sobre fal.ai por debajo.** No construyas otro playground de generación (commodity que fal/Canva/OpenArt ya regalan). Construye lo que nadie tiene: mismo personaje + voz + marca a través de N ganchos, con prompt exacto + fuentes. **Diseña por referencias + StyleID desde el día 1, o no puedes prometer coherencia — que es tu único moat defendible.**
*→ Si dices SÍ: el scope de producción se simplifica dramáticamente (eres el cerebro, no el modelo).*

### **DECISIÓN 2 — ¿Validas la tesis "se paga por estrategia" ANTES de construir la capa cara?**
**Recomendación: SÍ, Fase 0 no-negociable.** Un smoke test / fake-door de mensajería ("OS de estrategia+marca" vs "fábrica barata de output") + 10-20 entrevistas al ICP + modelado de costo unitario. **Es la semana más barata que gastarás** — porque Icon (ejecución a $39) y la huida de Copy.ai del SMB son evidencia *débil o contraria* a que la estrategia se venda sola. **No inviertas el cerebro caro a ciegas.**
*→ Si dices NO a validar: aceptas construir sobre una hipótesis no confirmada. Legítimo si lo haces con los ojos abiertos.*

### **DECISIÓN 3 — ¿El moat de Fase 1 es Brief + StyleID + Glass-box?**
**Recomendación: SÍ.** Estos tres son (a) lo más apalancado (brief = 33% del presupuesto que la industria desperdicia), (b) lo que ataca la queja #1 (AI slop) y el hallazgo maestro (verificabilidad) simultáneamente, y (c) construibles sobre tu infraestructura actual (design_spec, cost ledger, embeddings). **1-2 JTBD, no amplitud** — la amplitud es "el camino más rápido al mirage PMF". Producción, biblioteca y global vienen DESPUÉS.
*→ Si dices SÍ: tienes un roadmap ejecutable y un moat medible (instrumenta HURT = minutos de corrección humana por pieza).*

---

**Archivos del proyecto relevantes para ejecutar este scope** (todos en `C:\Users\prett\Documents\sandia-marketing`):
- `lib/estudio/` + `app/api/estudio/` — el Estudio de Producción (aquí vive la Decisión 1: convertirlo en motor de coherencia)
- `lib/gateway/` — el AI Gateway (aquí vive la tabla de enrutamiento sobre fal.ai, §3)
- `lib/wizard/phase1/` + `phase2/` — donde vive el StyleID / voz cuantificada por avatar (§5, Fase 1)
- `lib/radar/` + `app/api/radar/` — Inteligencia Temporal, insumo del gate de brief (§7)
- `docs/model-selection.md` + `docs/design-system.md` — base para la tabla de enrutamiento y el StyleID