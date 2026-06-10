# Sandi — Competitor Scan (Phase 0.4)

**schema_version:** v1 · **Fecha:** 2026-06-10 · **Estado:** scan completo, pendiente decisión del hueco (operador)
**Método (glass-box):** WebSearch + WebFetch sobre fuentes públicas (pricing pages, G2, comparativas 2026, encuestas). Cada precio cita su fuente. **Límite declarado:** Meta Ad Library y Google Ads Transparency son webapps JS que mi tooling no ejecuta — la sección Ads se construye de evidencia indirecta (peso histórico en la categoría + listas de mercado) y queda **flagueada para verificación manual (~10 min/marca)**. Lente del scan: el terreno del primer ciclo (Priya, D-026) + la categoría general.

---

## 1. Competidores SEO (rankean para "marketing plan/strategy generator" y afines)

| # | Competidor | URL | Precio | Posicionamiento (1 oración) |
|---|---|---|---|---|
| 1 | **M1-Project (Elsa AI)** | m1-project.com | **$99/mo** Startup (1 ICP, 1 estrategia, 50 cr) · $199 Pro (3 ICPs) · $399 Agency (9) | "AI marketing assistant" ICP-first que genera estrategia y assets para founders |
| 2 | **Piktochart** AI plan generator | piktochart.com | Freemium (60 cr/mes free; tiers 500–3,000 cr) | Generador visual de planes — wedge desde herramienta de diseño |
| 3 | **Venngage** AI plan generator | venngage.com | Freemium | Igual patrón: plan bonito como documento, wedge de diseño |
| 4 | **HubSpot** (Campaign Assistant / Marketing Hub) | hubspot.com | Free tier → ~$20/mo entrada | Suite inbound todo-en-uno con gravedad de CRM gratis |
| 5 | **Taskade** | taskade.com | Freemium → ~$8–20/mo | Productividad + plantillas AI; plan de marketing como template |

**M1-Project — el espejo más cercano.**
- Fortalezas: (1) metodología ICP-first seria (el único que arranca por el cliente, no por el copy), (2) 20+ generadores gratis que rankean y hacen funnel — **ya ejecutan la jugada create_demand**, (3) reviews fuertes (G2; casos con CTR +35%).
- Debilidades: (1) **one-shot**: genera estrategia y te suelta — sin loop ejecutar→medir→ajustar, (2) **multi-público como upsell**: 1 ICP a $99, 3 a $199 — castiga exactamente lo que nuestro beachhead necesita, (3) sin capa de educación: asume founder que lee marketing-speak.
- **Modelar (no copiar):** los generadores gratis como cuña SEO. **Evitar:** pricing por-ICP (anti-tesis D-009) y el plan-como-PDF estático.

**Piktochart/Venngage/Taskade.** Fortalezas: fricción cero, gratis, bonitos. Debilidades: output genérico, cero metodología, cero loop, cero educación. Modelar: el free-entry sin signup. Evitar: plan-como-entregable-estático (el usuario queda igual de perdido con un PDF lindo).

**HubSpot.** Fortalezas: marca/confianza, Academy gratis, CRM gravity. Debilidades para NUESTRO persona: abruma (suite de 100 features), asume conocimiento, su free es anzuelo a suite B2B-ish. Modelar: educación-como-imán (Academy). Evitar: suite-overwhelm día 1.

## 2. Competidores RRSS (ya tienen a nuestra audiencia)

| # | Quién | Canal/tamaño | "Precio" | Posicionamiento |
|---|---|---|---|---|
| 1 | **Alex Hormozi** | YouTube/IG, millones; audiencia = dueños pequeños exactos | Contenido free → books/equity | "Te doy los frameworks de $100M gratis" |
| 2 | **Neil Patel** | YT 1.11M + blog masivo | Free → funnel a NP Digital (agencia) | Tips accionables SEO/marketing |
| 3 | **HubSpot Marketing + Academy** | YT + cursos | Free | Educación inbound como imán de suite |
| 4 | **GaryVee** | Todas las redes, volumen brutal | Free → VaynerMedia | Atención/hustle, RRSS-first |
| 5 | *(terreno Priya)* **Jungle Scout / Helium 10 / My Amazon Guy** | YT con horas de tutoriales FBA | Free → sus tools | Educación de sellers como funnel |

Lectura: en RRSS el enemigo no vende software — **vende atención y educación gratis**. Nuestra cuña create_demand compite aquí por los mismos ojos. Modelar: lenguaje sin jerga de Hormozi (su audiencia ES nuestro ICP). Evitar: hustle-porn y promesas de cifras (choca con honestidad arquitectónica).

## 3. Competidores publicitarios (pautan en el espacio) — ⚠️ verificación manual pendiente

| # | Quién | Precio | Evidencia de pauta |
|---|---|---|---|
| 1 | **Mailchimp** | $13+/mo | Peso histórico top en SMB marketing terms [inferido — verificar en Ad Library] |
| 2 | **Constant Contact** | $12+/mo | Ídem [inferido] |
| 3 | **Jasper** | $59–69/mo (2026, subió de $39) | Paid search activo en "AI marketing" [inferido de SERPs comerciales] |
| 4 | **Semrush** | $139.95–199/mo | Agresivo en search ads de la categoría tools [inferido] |
| 5 | **HighLevel** | ~$97–297/mo | Pauta fuerte a agencias/consultores [inferido] |

Los 5 son pautas conocidas de la categoría; el chequeo puntual en Meta Ad Library / Google Ads Transparency (creatividades activas, ángulos) es trabajo manual de ~10 min/marca — **flag para el operador o para la próxima sesión con browser**. Lo que sí se infiere seguro: **todos pautan features/canal ("emails que convierten", "SEO data") — nadie pauta "estrategia guiada para el que no sabe"**.

## 4. Substitutos (mismo JTBD — "consíganme clientes para mi oferta" — por otro mecanismo)

| # | Categoría | Ejemplo / precio | Por qué los "contratan" | Mejor que Sandi en | Peor que Sandi en |
|---|---|---|---|---|---|
| 1 | **ChatGPT/Claude a mano** | $0–20/mo | Ya lo pagan; infinitamente flexible; "gratis" | Precio, flexibilidad | Sin metodología ni memoria: el no-marketer no sabe QUÉ pedirle (techo = su prompt); one-shot sin loop ni medición. **El substituto #1 a desplazar** |
| 2 | **Agencia / freelancer** | Retainer $1.5k–10k/mo (mediana SMB $5–8k); Fiverr plan $144–165 one-shot | Hace-por-ti, cero esfuerzo | Ejecución completa sin tocar nada | Precio 50–300×; caja negra; el dueño no aprende nada; Fiverr = plan genérico sin ejecución |
| 3 | **Cursos / educación** | HubSpot Academy free; certs $50–2k; gurús $500–2k | "Si aprendo, lo hago yo" | Profundidad teórica | Tiempo enorme; sin ejecución; el abrumado no los termina; gurús FBA = quemada probada (anxiety de Priya) |
| 4 | **Tools-para-marketers por canal** | Semrush $139.95+, Mailchimp $13+, Constant Contact $12+ | Resuelven UN canal bien | Profundidad por canal | Presuponen la estrategia y el marketero; nuestro persona no sabe qué canal tocar primero |
| 5 | *(Priya)* **Seller tools dentro del marketplace** | Helium 10 $129/mo (mató su starter); Jungle Scout $49–79/mo | Optimizan el juego actual | Datos del marketplace | Optimizan DENTRO de la jaula; ninguno la saca al canal propio |

## 5. Síntesis cross-canal + veredicto ERRC

### Huecos accionables (≥2 exigidos; encontré 4)

1. **H1 — Multi-público paralelo como core.** El más cercano (M1) lo cobra como upsell (1 ICP→$99, 3→$199) y sin loop por público. Nadie orquesta N estrategias en paralelo. Validación de demanda + hueco a la vez (D-009 confirmado contra mercado).
2. **H2 — El loop completo guiado para no-marketers.** Generadores = PDF one-shot; tools = canales sueltos que asumen estrategia; cursos = teoría sin ejecución; agencias = caja negra cara. **El acompañamiento estrategia→ejecutar→medir→ajustar con educación adaptativa y glass-box está vacío.** Es exactamente el espacio entre "$20 de ChatGPT" y "$5k de agencia".
3. **H3 — (Priya) Puente marketplace→canal propio.** Seller tools optimizan dentro; gurús queman; nadie guía la salida sistemática público-por-público.
4. **H4 — Entry pricing serio.** Helium $129 tras matar su starter; M1 $99; Semrush $139.95; agencias $1.5k+. A ~$30/mo con estrategia real: campo solo.

### Lente ERRC

- **Eliminar:** jerga sin traducir · prompts del usuario · el plan-PDF estático · dashboards de métricas vanity.
- **Reducir:** amplitud de suite (no todo-en-uno) · profundidad-por-canal pro (no competimos con Semrush en SEO técnico).
- **Incrementar:** acompañamiento del ciclo completo (0→5) · honestidad de claims (prohibición de sistema) · educación adaptativa (novato→competente) · atribución a dinero (KPI = revenue).
- **Crear:** orquestación multi-avatar paralela (N estrategias, N loops) · glass-box del razonamiento · memoria de agente por proyecto · (ciclo 1) playbook de independencia del marketplace.

### Veredicto de posicionamiento

**🔴 Océano rojo en la categoría "AI marketing tool"** — saturada (cientos de tools, ads caros, diferenciación marginal). Entrar ahí = competir en precio/features.
**🔵 Hueco azul en la intersección:** *"estratega multi-público guiado que te enseña mientras hace y cierra el loop hasta el dinero."* No es una feature de las tools existentes ni un upsell de M1 — es categoría propia. Manifestación para el ciclo 1 (Priya): **"tu salida del marketplace, público por público."**

**Recomendación de hueco a atacar (decisión del operador, ver pregunta en chat):** H1+H2 como posicionamiento de categoría, ejecutado primero como H3 en el terreno de Priya, con H4 (pricing) como cuña de entrada.

---

## Fuentes

- M1-Project pricing/features: m1-project.com + G2 + ai-cmo.net review (2026)
- Jasper $59–69: jasper.ai/pricing vía seoptimer/startupowl comparativas 2026 · Copy.ai $36–49: ídem
- Piktochart/Venngage/Taskade: sus generadores públicos + FitGap roundup 2026
- HubSpot: academy.hubspot.com (free) + pricing entrada ~$20
- Helium 10 $129 (starter eliminado) / Jungle Scout $49–79: helium10.com blog + demandsage/yaguara 2026
- Agencias $1.5k–10k+/mo (mediana $5–8k): clicksgeek/influenceflow/feedbird guías 2026 · Fiverr $144–165: fiverr hire pages
- Semrush $139.95–199 / Mailchimp $13+ / Constant Contact $12+: nerdwallet/moosend/semrush listas 2026
- RRSS: businessology/nogood/toplist rankings 2026 (Neil Patel 1.11M subs)
