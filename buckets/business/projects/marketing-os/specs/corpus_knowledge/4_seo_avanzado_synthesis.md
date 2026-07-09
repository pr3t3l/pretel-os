# Síntesis: SEO Avanzado con IA (Curso BigSEO)

**Fuente:** Carpeta `_corpus_extracted/Marketing Documentacion Teorica/4. SEO Avanzado con IA`
**Archivos procesados:** 12 .txt (introducción, 5 capítulos + recursos de cada uno)
**Fecha de síntesis:** 2026-06-09

---

## 1. Visión general del módulo

Este módulo representa la capa técnico-programática del SEO: pasa de la optimización manual a la automatización escalable mediante Python, APIs, herramientas de auditoría (Screaming Frog) y orquestadores de flujos (n8n). El hilo conductor es: **extraer datos de la web → estructurarlos → agruparlos semánticamente → enriquecerlos con entidades → generar briefs listos para redacción**, todo de forma reproducible y con IA integrada en cada paso.

El módulo asume conocimiento previo de SEO on-page/off-page básico y de uso de ChatGPT para prompts, y construye sobre eso con scripting, APIs y workflows.

---

## 2. Frameworks clave

### 2.1 Pipeline completo SEO con IA (marco transversal del módulo)

```
Investigación (keywords + SERP)
  → Scraping programático (HTML / SERP APIs)
    → Clustering por intención (SERP similarity)
      → Auditoría técnica (Screaming Frog + GPT)
        → Enriquecimiento semántico con entidades
          → Brief automatizado (n8n workflow)
            → Contenido listo para publicar
```

Cada etapa tiene su herramienta canónica y su script/workflow concreto.

### 2.2 Metodología BigSEO de Keyword Research

- **Identificación de temas:** prompts en ChatGPT para idear clusters de contenido.
- **Generación de ideas de KW:** consultas reales + tendencias emergentes (Google Keyword Planner).
- **Evaluación de competencia:** datos de Planner + análisis predictivos de IA.
- **Exploración horizontal:** IA generativa para expandir sinónimos, variaciones y temas adyacentes.

### 2.3 Framework de clustering por intención (SERP-based)

Principio central: **si dos keywords muestran el mismo Top 10 de URLs, comparten intención y deben apuntar a la misma página.**

Jerarquía de clusters → arquitectura del sitio:
- Nivel superior: categoría amplia (ej. "zapatillas").
- Nivel intermedio: subcategoría (ej. "zapatillas deportivas").
- Nivel inferior: nicho/variante (ej. "zapatillas running").

Métricas de similitud disponibles (en orden de sofisticación):
1. **Jaccard simple:** intersección / unión (sin tener en cuenta orden).
2. **Jaccard ponderado / Score posicional:** mayor peso a coincidencias en posiciones 1–3.
3. **NDCG adaptado:** considera posición y orden completo.

Algoritmos de clustering aplicables tras calcular la matriz: aglomerativo, DBSCAN, jerárquico.

### 2.4 Framework de entidades: de keywords al Knowledge Graph

- **Keyword** = lo que busca el usuario (cadena de texto).
- **Entidad** = objeto semántico que Google reconoce (persona, lugar, organización, evento, concepto).
- El **Knowledge Graph** conecta nodos (entidades) con aristas (relaciones) y produce paneles de conocimiento, rich snippets, carruseles.
- Optimizar para entidades = alinear el contenido con los grafos de conocimiento del motor.

### 2.5 Arquitectura del workflow n8n para briefs automatizados

```
Formulario (inputs del usuario)
  → DataForSEO (Top 10 orgánico)
    → Código JS (filtrar / priorizar URLs)
      → Loop: Wait → Firecrawl (URL → Markdown)
        → Information Extractor LLM (JSON por URL)
          → Aggregate (consolida todos los JSON)
            → Information Extractor LLM (meta-resumen JSON)
              → Message to Model (brief final con heading structure)
```

---

## 3. Métodos y pasos accionables

### 3.1 Web Scraping con Python (C2)

**Proceso básico (4 pasos):**
1. Solicitud HTTP con `requests` (incluir User-Agent para evitar bloqueos).
2. Obtención del HTML bruto.
3. Análisis / extracción con `BeautifulSoup` (usar `select_one()` con Copy Selector de DevTools para elementos complejos).
4. Almacenamiento en CSV / XLSX / JSON.

**Scraping con IA (ScrapeGraphAI):**
- Usa `SmartScraperGraph` de la librería `scrapegraphai`.
- En lugar de reglas HTML fijas, se pasa un **prompt en lenguaje natural** (ej.: "Dame el nombre y precio de las 3 primeras autocaravanas").
- El modelo (GPT-4o) interpreta el contexto semántico aunque la estructura HTML varíe.
- Escala a múltiples URLs iterando sobre listas y guardando resultados en dict/CSV/XLSX.

**Pipeline SERP → scraping:**
- Llamar ValueSERP/DataForSEO para obtener Top N URLs de una query.
- Iterar esas URLs con el scraper IA.
- Exportar resultados a Google Colab → CSV descargable.

**Librerías esenciales:** `requests`, `beautifulsoup4`, `selenium`, `helium`, `scrapegraphai`, `pandas`, `openpyxl`.

### 3.2 Clustering de Keywords (C3)

**Pasos del script:**
1. Cargar CSV con columnas `keyword` + `volumen` (exportado de Ahrefs / SEMrush / GKP).
2. Para cada keyword: llamar API SERP (ValueSERP o DataForSEO) → obtener lista Top 10 de URLs.
3. Construir matriz de similitud entre pares de keywords.
4. Aplicar algoritmo de clustering con umbral configurable.
5. Exportar `clusters_keywords.xlsx` con columnas: `keyword`, `volumen`, `cluster`, `top10` (opcional).
6. Mapear cluster → URL (o definir nueva URL si no existe).

**Buenas prácticas:**
- Limpiar duplicados y normalizar el CSV antes de procesar.
- Respetar rate limits de la API; usar batching y caché.
- Priorizar clusters por volumen agregado y valor transaccional, no sólo por volumen.
- Hacer QA humana sobre un porcentaje de los clusters.
- Guardar versiones con fecha para comparativa temporal (evolución de intenciones).
- Integrar mapping cluster → URL en CMS, n8n, Airtable o Sheets.

**Alternativa avanzada:** combinar SERP similarity + embeddings de texto para detectar intenciones difusas.

### 3.3 Auditoría técnica con Screaming Frog + GPT (C4)

**Configuración para integrar GPT:**
1. Activar renderizado JavaScript: `Configuración → Spider → Renderizado → JavaScript`.
2. Abrir `Configuración → Personalizado → JavaScript personalizado`.
3. Seleccionar plantilla de la biblioteca o crear la propia.
4. Editar tres constantes: `API_KEY` (OpenAI), `question` (el prompt), `userContentList` (body, H1, title, meta).
5. Ejecutar rastreo; los resultados GPT aparecen en pestaña "JavaScript personalizado".
6. Exportar a CSV/Excel para análisis posterior o integración en flujos.

**Casos de uso con prompts:**

| Caso | Prompt de ejemplo |
|---|---|
| Resumen de contenido | "Resume el contenido principal de esta página en 3 oraciones concisas." |
| Alt text para imágenes | Usar plantilla "Generate alt text for images" de la biblioteca. |
| Clasificación de intención | "Clasifica esta página como Informativa, Transaccional o Navegacional según su contenido principal." |
| Evaluación de calidad | "Evalúa si el contenido de esta página responde claramente a la intención de búsqueda del título." |

**Nota de coste:** Screaming Frog Pro = 239 €/año. Versión gratuita limitada a 500 URLs.

### 3.4 Enriquecimiento con entidades (C5)

**Proceso con TextRazor:**
1. Copiar texto del artículo top-rankeado para la keyword objetivo.
2. Pegar en la interfaz de TextRazor (o llamar a su API).
3. Obtener lista de entidades + relevancia.
4. Usar esa lista como **checklist** de conceptos que el propio artículo debe cubrir.

**Integración en prompts con IA (JSON estructurado):**
- Construir un JSON con: `keyword`, `temas principales`, `entidades detectadas`.
- Pasar ese JSON al LLM como contexto para guiar la generación.
- El GPT personalizado "Generador de JSON-Prompt" (recurso del curso) facilita la construcción de este JSON.
- Siempre revisar y enriquecer lo generado: verificar precisión factual, tono y aportes originales.

**Buenas prácticas:**
- Incluir datos verificables (fechas, nombres, referencias) que anclen la entidad.
- Usar schema markup (datos estructurados) cuando aplique para reforzar la identificación de entidades por Google.
- Priorizar comprensión del tema sobre repetición de keywords; las entidades aparecen de forma orgánica cuando el texto es de experto.

### 3.5 Workflow n8n de briefs automáticos (C6)

**Nodo a nodo — configuración clave:**

**Nodo 1 — Formulario:** recoge título provisional, keyword principal, keywords secundarias, idioma, localización.

**Nodo 2 — DataForSEO:** `Get Live Google Organic SERP Advanced`; mapear keyword + idioma + localización; limitar a top 10 o top 20.

**Nodo 3 — JavaScript (código):** filtrar dominios no relevantes (redes sociales, foros); priorizar por autoridad; limitar a top 3–5 URLs para controlar coste; convertir a array para `Loop Over Items`.

**Nodo 4 — Loop + Wait + Firecrawl:** iterar por URL; pausa de 1–2 s entre llamadas; Firecrawl scrapea y devuelve Markdown limpio + metadatos.

**Nodo 5 — Information Extractor (JSON por URL):** LLM extrae un JSON estructurado con `serpResume`, `mainTopics` (topic + relevance 0–1), `subTopics` (definition + bulletPoints + relevance). Ver schema completo en sección 4.

**Nodo 6 — Aggregate:** consolida los JSON individuales en un array.

**Nodo 7 — Information Extractor (meta-resumen):** LLM recibe el array de 10 JSON y produce un único JSON consolidado; agrupa topics semánticamente idénticos; mantiene el relevance más alto; crea nuevo `serpResume` como meta-resumen global.

**Nodo 8 — Message to Model (brief final):** recibe el meta-JSON; produce estructura de headings H1/H2/H3 con estilo conversacional, sin lenguaje corporativo, con tono de "conversación con un buen amigo". Output listo para entregar a redactor o CMS.

**Gestión de costes:**
- DataForSEO: bajo coste por consulta, depende de volumen.
- Firecrawl: créditos gratuitos limitados; planes para escala.
- LLMs: primer pase (extracción) → modelos económicos; generación final → modelo premium.
- Cachear resultados SERP para keywords con baja volatilidad.

---

## 4. Prompts y herramientas concretas

### Prompts listos para usar

**Screaming Frog — clasificación de intención:**
```
Clasifica esta página como Informativa, Transaccional o Navegacional según su contenido principal.
```

**Screaming Frog — evaluación de calidad:**
```
Evalúa si el contenido de esta página responde claramente a la intención de búsqueda del título.
```

**n8n — extracción JSON por URL (system prompt):**
```
Eres un modelo especializado en análisis de resultados de búsqueda de Google.
TAREA PRINCIPAL: Analiza el contenido en detalle. Extrae los temas clave, enfoques y ángulos tratados.
Sin copiar contenido literal, sintetiza la información en lenguaje original. No omitas información relevante.
FORMATO DE RESPUESTA: Devuelve EXCLUSIVAMENTE un objeto JSON con estructura: serpResume, mainTopics (topic + relevance), subTopics (definition + bulletPoints + relevance). Los valores de relevance deben estar entre 0 y 1.
```

**n8n — meta-resumen (prompt a LLM):**
```
Eres un LLM experto en análisis y síntesis de datos estructurados. Recibe un array de 10 objetos JSON (resúmenes de páginas top 10 de Google) y genera un único JSON consolidado. Agrupa topics semánticamente idénticos, mantén el relevance más alto, crea un serpResume como meta-resumen global. No pierdas ningún tema ni matiz técnico de los inputs.
```

**n8n — generación del brief final (extracto del prompt):**
```
I will provide you with a JSON summary of the top 10 Google results for the keyword: [keyword].
Convert this summary into a heading structure (h1, h2, h3...) covering all relevant content.
Writing style: professional but conversational — address the reader as "you." Avoid: corporate language, passive voice, encyclopedia tone. Don't repeat phrases. Your priority is benefits and emotions, not features.
```

**ScrapeGraphAI — scraping con IA:**
```python
SmartScraperGraph(
    prompt="Dame el nombre y precio de las 3 primeras autocaravanas que aparecen en el contenido. No me des información de otras URLs distintas a la que te facilito.",
    source=url,
    config={"llm": {"api_key": OPENAI_API_KEY, "model": "openai/gpt-4o"}}
)
```

**TextRazor → JSON para IA (flujo entidades):**
1. TextRazor extrae entidades del artículo top-rankeado.
2. Las entidades se pasan al GPT personalizado "Generador de JSON-Prompt" para construir el prompt estructurado.
3. Ese JSON se usa como contexto en la llamada al LLM generador de contenido.

### Herramientas del módulo

| Herramienta | Rol en el pipeline |
|---|---|
| **Google Colab** | Entorno de ejecución Python sin instalación local |
| **Python (requests, BeautifulSoup, Selenium, Helium)** | Scraping tradicional y automatización de navegación |
| **ScrapeGraphAI** | Scraping semántico con IA (sin reglas HTML fijas) |
| **ValueSERP** | API para obtener Top N URLs de una SERP |
| **DataForSEO** | API SERP robusta; también usada en n8n |
| **Screaming Frog SEO Spider** | Crawler SEO técnico; integra GPT via JS personalizado |
| **TextRazor** | Extracción de entidades y topics de textos |
| **GPT Personalizado "Generador de JSON-Prompt"** | Construye prompts estructurados JSON para guiar generación de contenido |
| **n8n** | Orquestador de workflows; conecta DataForSEO + Firecrawl + LLMs |
| **Firecrawl** | Scraping dentro de n8n → Markdown limpio por URL |
| **OpenAI GPT-4o / Claude** | LLMs para extracción JSON, meta-resumen y brief final |
| **Google Keyword Planner** | Datos de volumen, competencia, CPC |
| **Ahrefs / SEMrush** | Exportación de listas de keywords para clustering |

---

## 5. Mapeo al sistema Sandi (fases)

| Fase Sandi | Material de este módulo que aplica |
|---|---|
| **Phase 0 — Research / ICP** | Metodología BigSEO: identificación de temas con prompts + GKP; clustering para descubrir intenciones reales del mercado; scraping de competidores para inteligencia de precios y posicionamiento. |
| **Phase 1 — Oferta** | Clustering + entidades revelan qué temas cubre la competencia con autoridad → informa propuesta de valor diferenciada y gaps de contenido. |
| **Phase 2 — Contenido** | Bloque central del módulo: workflow n8n genera briefs accionables desde SERP; enriquecimiento con entidades garantiza relevancia semántica; Screaming Frog + GPT clasifica intención y evalúa calidad del contenido existente. |
| **Phase 3 — Distribución** | Arquitectura web derivada del clustering (siloing, enlazado interno, canonicalización) es prerequisito para distribución orgánica eficaz. Los alt texts generados automáticamente mejoran accesibilidad y SEO de imágenes. |
| **Phase 4 — Medir** | API de Google Search Console integrada en Python para extraer CTR, impresiones y ranking promedio de forma programática; exportación de auditorías Screaming Frog a CSV para dashboards. |
| **Phase 5 — Ajustar** | Versionado de clusters (comparativa temporal); re-ejecución periódica de scripts de clustering para detectar cambios de intención; cacheo + re-auditoría Screaming Frog para medir impacto de cambios técnicos. |
| **Módulo A — Business case** | Los costes explícitos del módulo (Screaming Frog 239€/año, DataForSEO por consulta, Firecrawl créditos, OpenAI/Anthropic por token) permiten calcular ROI vs. horas humanas ahorradas. |

---

## 6. Qué aporta este material que un spec de marketing genérico no tendría

1. **Scraping programático como fuente primaria de datos competitivos.** Un spec genérico asume investigación manual o herramientas SaaS. Este módulo proporciona el código Python real (con `requests`, `BeautifulSoup`, `ScrapeGraphAI`) para extraer precios, contenidos y estructuras de competidores a escala, incluyendo integración con APIs SERP para automatizar la obtención de URLs objetivo.

2. **Clustering basado en señales reales de SERP (no en semántica subjetiva).** La métrica de similitud sobre el Top 10 real de Google es más objetiva que la agrupación manual por sinónimos. El output directo (cluster → URL) mapea inmediatamente a decisiones de arquitectura: qué páginas consolidar, qué páginas crear, dónde hay canibalización.

3. **Integración GPT dentro de Screaming Frog para auditoría semántica a escala.** Un spec estándar describiría auditorías técnicas como proceso manual. Aquí el crawler ejecuta prompts GPT sobre cada URL rastreada (clasificación de intención, evaluación de calidad, generación de alt text), produciendo columnas adicionales exportables que alimentan dashboards o flujos downstream.

4. **Framework de entidades + Knowledge Graph como capa de señal semántica.** La distinción keyword/entidad y el uso de TextRazor para extraer entidades de los top-competidores es una técnica de optimización de segunda generación (post-keywords) que la mayoría de specs de marketing no contemplan. El flujo TextRazor → JSON-Prompt → LLM permite escalar esta práctica.

5. **Workflow n8n completo y reproducible para brief generation.** Con schemas JSON explícitos, prompts detallados por nodo, y arquitectura de 8 nodos documentada, este módulo ofrece un blueprint deployable, no solo una descripción conceptual. Incluye consideraciones de rate limiting, costes reales, caching y validación de schema entre nodos.

6. **Explicitación de costes por herramienta y estrategias de optimización.** La mayoría de specs no desglosan el coste operativo de cada herramienta. Este módulo especifica: Screaming Frog 239€/año, DataForSEO por consulta, Firecrawl por créditos, LLMs por token; y propone tácticas de reducción: top 3 en vez de top 10, modelos económicos en primer pase, caché de SERP.

7. **Python + Google Colab como capa de pegamento.** El módulo establece que Google Colab es el entorno estándar de ejecución, compartible y sin instalación local. Esto es relevante para un sistema de marketing que necesite colaboración o que opere sobre Windows sin entorno Python local configurado.

---

## 7. Observaciones sobre aplicabilidad al sistema Sandi específicamente

- El workflow n8n de briefs es directamente integrable en el pipeline de Phase 2 Contenido de Sandi: reemplaza o complementa la investigación manual de la SERP previa a la redacción.
- El clustering SERP-based es el insumo ideal para la **arquitectura de contenido** de un cliente nuevo (Phase 0 Research): en lugar de asumir qué páginas crear, se parte de evidencia empírica de cómo Google ya segmenta el mercado.
- La integración Screaming Frog + GPT para clasificación de intención puede ejecutarse sobre el sitio del cliente antes del onboarding para detectar oportunidades y problemas técnicos preexistentes (Phase 0, auditoría inicial).
- TextRazor + entidades es una técnica de mejora de contenido existente (Phase 5 Ajustar): auditar artículos propios ya publicados, extraer entidades faltantes vs. los top competidores, y reescribir selectivamente.
- n8n ya está en el stack de Sandi (mencionado en la arquitectura del sistema). Este módulo proporciona el workflow concreto más relevante: generación de briefs SEO automatizados.

---

*Síntesis generada el 2026-06-09. Fiel al material del curso BigSEO — SEO Avanzado con IA.*
