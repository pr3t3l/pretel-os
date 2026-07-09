# Síntesis del Corpus: SEO con IA

**Curso fuente:** "SEO con IA" — BigSEO (agencia de marketing digital)
**Archivos leídos:** 21 archivos .txt extraídos de 11 clases (C1–C11) + resumen docx
**Fecha de síntesis:** 2026-06-09

---

## 1. Visión general del curso

El curso construye un sistema de posicionamiento orgánico aumentado por IA. Su argumento central: la IA no reemplaza el criterio SEO, lo amplía. El profesional que combina dominio de los fundamentos del SEO con uso estratégico de modelos de lenguaje produce resultados más escalables, precisos y sostenibles que el que usa solo una de las dos piezas.

El material está estructurado como un workflow de 10 fases secuenciales que van desde la comprensión del entorno hasta la construcción de autoridad de largo plazo. En cada fase aparecen herramientas concretas, prompts reproducibles y criterios de decisión.

---

## 2. Frameworks clave

### 2.1 E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness)
Marco de evaluación de calidad de Google. Aparece en múltiples capítulos como el criterio rector de qué contenido merece posicionarse. Se aplica especialmente en temáticas YMYL (Your Money or Your Life: salud, finanzas, seguridad).

- **Experiencia:** el autor ha vivido o experimentado el tema.
- **Expertise:** conocimiento técnico demostrable.
- **Autoridad:** reconocimiento por parte de otros actores del sector.
- **Confianza:** veracidad, fuentes, transparencia.

**Implicación práctica:** antes de crear contenido con IA, definir qué señales E-E-A-T va a proyectar esa pieza y ese dominio.

### 2.2 Intención de búsqueda (tres tipos)
El formato del contenido debe seguir a la intención, no al revés.

| Tipo | Descripción | Formato adecuado |
|---|---|---|
| Transaccional | El usuario quiere comprar o contratar | Página de producto/servicio |
| Informativa | El usuario quiere aprender o entender | Artículo, guía, tutorial |
| Mixta | La intención no es del todo clara | Requiere interpretación; combina formatos |

Error frecuente señalado por el curso: crear contenido cuyo formato no coincide con la intención → baja relevancia → penalización de posicionamiento.

### 2.3 Arquitectura de clusters (pillar page + páginas secundarias)
Estructura para evitar canibalizaciones y consolidar autoridad temática:

- **Pillar page:** página principal que cubre el tema de forma amplia.
- **Cluster pages:** páginas secundarias con subtemas específicos enlazadas a la pillar.
- **Regla clave:** cada URL debe tener su propia intención de búsqueda y conjunto de palabras clave **único**.

La IA acelera la construcción de esta arquitectura mediante análisis semántico y sugerencia de agrupaciones temáticas.

### 2.4 Authority Topic (autoridad temática)
Un dominio especializado en un solo nicho puede superar en posicionamiento a medios generalistas con mayor autoridad de dominio global. Ejemplo del curso: **Don Camper** (doncamper.es), portal especializado en autocaravanas que posiciona por encima de medios generalistas para búsquedas como "qué es una camper".

**Implicación:** la especialización es el camino más accesible para sitios nuevos. Exige profundidad, consistencia editorial, actualización y coherencia temática.

### 2.5 JSON-Prompting
El framework metodológico más singular del curso. Transforma la creación de contenido SEO de tarea artesanal a proceso técnico, estructurado y escalable.

**Principio:** usar formato JSON para estructurar los prompts dirigidos a LLMs. El beneficio no es que la IA "entienda mejor el JSON" (los LLMs siguen procesando texto), sino que el formato obliga al humano a organizar su input con lógica, eliminando ambigüedades y omisiones.

**Ventajas:**
- Persistencia intra-modelo e inter-modelo: el mismo prompt produce resultados más consistentes.
- Modularidad: modificar un campo (por ejemplo, `"tone": "formal"`) sin reescribir todo el prompt.
- Portabilidad: funciona en ChatGPT, Claude, Gemini con mínimas adaptaciones.
- Integración con automatizaciones: compatible con Make, Zapier, n8n y hojas de cálculo.

---

## 3. Workflow completo de 10 fases (según el curso)

### Fase 1: Comprensión del entorno AI Overview
Antes de producir contenido, auditar cómo se comporta Google en el nicho objetivo.

**Pasos:**
1. Listar las palabras clave más importantes del sector.
2. Buscar cada una en Google y registrar: ¿aparece AI Overview? ¿Qué tipo de intención domina? ¿Qué tipo de dominio posiciona (generalista, especializado, ecommerce)?
3. Documentar en hoja de cálculo: keyword | tipo de intención | AI Overview (sí/no) | tipo de dominio dominante | viabilidad.
4. Concluir qué tipo de contenido premia Google en ese nicho.

**Por qué importa:** AI Overview reduce el tráfico de búsquedas informacionales (responde sin clic). Entender su frecuencia en el nicho cambia la estrategia de contenidos.

### Fase 2: Keyword Research con IA (generación)
Usar modelos de lenguaje para ampliar semántica y acelerar la ideación.

**Workflow práctico:**
1. Partir de una palabra clave semilla.
2. Pedir a la IA: sinónimos, variaciones semánticas, preguntas frecuentes, modificadores de intención (por ubicación, precio, características, tipo de usuario).
3. Separar términos informativos vs. transaccionales.
4. Detectar clusters temáticos y decidir cuáles merecen página propia.

**Resultado:** lista amplia de candidatas a palabras clave, no validadas aún.

### Fase 3: Validación del Keyword Research con datos reales
La lista de la IA es punto de partida, no resultado final.

**Herramientas:**
- **Google Keyword Planner (Google Ads):** volumen de búsqueda, competencia, CPC.
- **Keyword Combiner (Atrox Creative):** generación masiva de combinaciones long tail.

**Estrategia iterativa:** dividir la lista en bloques, procesar cada bloque en el planificador, consolidar resultados. Regla: una keyword sin volumen o sin valor estratégico no merece esfuerzo.

### Fase 4: Arquitectura SEO (evitar canibalizaciones)
Con el keyword research validado, diseñar la estructura del sitio.

**Pasos:**
1. Separar temas grandes (candidatos a pillar pages).
2. Decidir qué tema merece página principal.
3. Crear subtemas relacionados (cluster pages).
4. Asignar una intención única a cada URL.
5. Usar la IA para sugerir jerarquías de navegación y organización de clusters.

**Prompt de ejemplo (del corpus):**
> "Te voy a facilitar un Keyword Research del sector del alquiler de caravanas. Asume el rol de un especialista en SEO y en base a este Keyword Research deberás crearme una arquitectura SEO transaccional para estructurar los contenidos de mi sitio web..."

### Fase 5: Producción de contenido
Crear piezas útiles, exhaustivas y alineadas con la intención.

**Criterios de calidad:**
- Responde a la intención de búsqueda de forma inmediata (respuesta principal en el primer párrafo).
- Ofrece visión completa del tema con datos verificados.
- Resuelve los "puntos de dolor" del usuario (dudas, problemas, necesidades adyacentes).
- Se adapta al formato que mejor encaja con la consulta.

**Gap de profundidad:** analizar a la competencia y ofrecer información más completa y valiosa.
**Gap de formato:** presentar los datos de manera más clara, visual y accesible.

### Fase 6: Optimización On-Page
Lista de verificación para cada página producida:

- [ ] Title con palabra clave principal y atractivo para el clic
- [ ] Meta descripción orientada a CTR (no al ranking directamente)
- [ ] Encabezados H1 > H2 > H3 con jerarquía lógica
- [ ] Enlazado interno con sentido
- [ ] Usabilidad y experiencia de usuario
- [ ] Velocidad de carga (Mobile-First Indexing)
- [ ] Freshness: contenido actualizado (2010 vs. 2025 no es lo mismo)
- [ ] Schemas / datos estructurados
- [ ] Control de errores de respuesta (404, 500)
- [ ] Imágenes optimizadas: **peso recomendado 100–120 KB** sin pérdida de calidad

### Fase 7: SEO técnico asistido por IA (datos estructurados y redirecciones)

#### Datos estructurados (Schema.org + JSON-LD)
**Workflow de 3 pasos:**
1. **Generación:** describir a la IA el negocio o página → obtener JSON-LD.
2. **Validación:** comprobar en Schema Markup Validator y Prueba de Resultados Enriquecidos de Google.
3. **Implementación:** insertar el código validado en `<head>` del sitio.

**Prompt de ejemplo:**
> "Actúa como especialista en SEO técnico. Necesito datos estructurados para la página de inicio de un negocio de alquiler de autocaravanas y campers en Madrid. Incluye descripción de la empresa, tipos de vehículos y sección de preguntas frecuentes. Genera el código JSON-LD correspondiente."

**Jerarquía Schema.org:** `Thing > CreativeWork/Organization/Event/...` → cuanto más específico, más preciso el contexto asignado por Google.

#### Redirecciones con IA (seguridad ante todo)
**301 vs. 302:**
- 301 (permanente): transfiere ~toda la autoridad → usar en migraciones, cambios de dominio.
- 302 (temporal): no transfiere autoridad → usar para pruebas o mantenimiento.

**Flujo seguro:**
1. Generar reglas con prompt claro en ChatGPT (especificar: tipo 301, mapeo 1:1, sin bucles, sin barras dobles).
2. Validar sintaxis con .htaccess Tester (TechnicalSEO.com).
3. Revisar opcionalmente con segunda IA (Gemini) para detectar errores.
4. Comprobar que cabeceras devuelven 301 correctamente.

**Advertencia explícita del curso:** nunca confiar ciegamente en el código generado por IA. Siempre validar antes de producción.

### Fase 8: Escalado con JSON-Prompting

**Workflow de 4 pasos:**
1. Generar el JSON-Prompt inicial (objetivos del contenido).
2. Analizar la competencia en SERP.
3. Enriquecer el JSON-Prompt con los hallazgos del análisis competitivo.
4. Generar el contenido final con el modelo adecuado.

**Tres GPTs personalizados del curso:**
1. **SERP Analytic GPT:** analiza resultados de búsqueda y los devuelve en JSON estructurado con `mainTopics`, `subTopics`, `relevance` (0–1).
2. **Generador de JSON-Prompt GPT:** convierte instrucciones en lenguaje natural a JSON completo con todos los campos SEO.
3. **Generador de Contenido JSON GPT:** toma el JSON final y redacta el contenido respetando todos los parámetros.

### Fase 9: Medición y mejora continua
**Herramienta principal:** Google Search Console.

**Dónde mirar:**
- Informe de Rendimiento: clics + impresiones + posición media.
- Filtrar por período estable (último mes).
- **Zona de oportunidad inmediata:** keywords en posiciones 10–13 → con pequeños ajustes pueden entrar en primera página.
- Para aparecer en AI Overview: necesitas al menos Top 20; la mayor probabilidad está en Top 10.

**Ciclo de trabajo:**
```
investigar → validar → estructurar → producir → optimizar → medir → actualizar
```

La freshness (actualidad del contenido) es señal de relevancia valorada por los algoritmos.

### Fase 10: Construcción de autoridad
**Tres factores de autoridad en la era AI Overview:**

1. **PageRank:** calidad sobre cantidad. Un enlace de fuente prestigiosa vale más que decenas de irrelevantes.
2. **Link Building estratégico:** colaboraciones, menciones naturales, contenido que otros quieran citar.
3. **Fuerza de marca:** menciones sin enlace, presencia en redes, coherencia de identidad digital.

**Autoridad temática (Authority Topic):** construir un ecosistema coherente con páginas pilar, subtemas bien cubiertos, lenguaje especializado, actualización constante y consistencia editorial. No es publicar artículos aislados; es ser referente en un territorio temático.

---

## 4. Prompts y herramientas concretas del corpus

### 4.1 Prompts reproducibles

**Keyword Research — variedad semántica y long tail:**
```
Tengo una web de servicios en la que alquilo autocaravanas a particulares de toda España y voy a realizar un Keyword Research. Asume el rol de un especialista en SEO y partiendo de la palabra clave principal 'Alquiler caravanas' devuélveme toda la variedad semántica relacionada con cada término. Por ejemplo, empezarías con el término 'Alquiler' y me devolverías sinónimos o términos relacionados. Luego seguirías con el siguiente término. Por último, dame términos que pueda concatenar con esta palabra clave y que den lugar a nuevas palabras clave long tail.
```

**Keyword Research — transaccional:**
```
Tengo una web de servicios en la que alquilo autocaravanas a particulares de toda España y tengo que realizar un Keyword Research transaccional para el sector de alquiler de caravanas. Asume el rol de un especialista en SEO y devuélveme un listado extenso de palabras clave que podría utilizar un usuario interesado en contratar este servicio. [...] Estas keywords serán utilizadas para construir la arquitectura SEO, por lo que deben permitir la creación de páginas de productos, categorías y secciones comparativas.
```

**Keyword Research — informacional + calendario editorial:**
```
Tengo una web de servicios en la que alquilo autocaravanas a particulares de toda España y voy a realizar un Keyword Research. Asume el rol de un especialista SEO y devuélveme un listado extenso de palabras clave que podría utilizar un usuario interesado en informarse sobre este servicio. [...] Ahora quiero que me crees un calendario editorial para que pueda ir publicando un contenido a la semana atacando cada una de las palabras clave que me has facilitado. [...] Devuélveme este calendario en forma de tabla.
```

**Arquitectura SEO desde keyword research:**
```
Te voy a facilitar un Keyword Research del sector del alquiler de caravanas. Asume el rol de un especialista en SEO y en base a este Keyword Research deberás crearme una arquitectura SEO transaccional para estructurar los contenidos de mi sitio web. [...] Organiza el esquema de la arquitectura en formato árbol, con enlaces internos sugeridos para mejorar la distribución de autoridad y la experiencia de usuario.
```

**Datos estructurados JSON-LD:**
```
Actúa como especialista en SEO técnico. Necesito datos estructurados para la página de inicio de un negocio de alquiler de autocaravanas y campers en Madrid. Incluye descripción de la empresa, tipos de vehículos y sección de preguntas frecuentes. Genera el código JSON-LD correspondiente.
```

**Redirecciones .htaccess:**
```
Genera reglas .htaccess de redirección 301 para Apache, sin bucles ni barras dobles, con correspondencia 1:1 entre las siguientes URLs…
```

### 4.2 Esquema JSON para contenido SEO (campos del curso)

```json
{
  "name": "Título del contenido (H1, no modificar)",
  "wordCount": 1200,
  "language": "es",
  "topicOverview": "Descripción general de la temática",
  "mainTopics": ["Tema central"],
  "subTopics": ["Temas complementarios"],
  "avoidTopics": ["Temas excluidos"],
  "primaryKeyword": "keyword principal",
  "secondaryKeywords": ["kw secundaria 1", "kw secundaria 2"],
  "searchintent": "informational | transactional",
  "paragraphs": 8,
  "previousContent": {
    "content": "texto original",
    "mandatory": 3,
    "significativeAdding": true
  },
  "serpResume": "Resumen de temas del Top 10 para la keyword principal",
  "paragraphLength": {
    "minChars": 150,
    "maxChars": 400,
    "charVariability": 0.5
  },
  "writingStyle": ["Professional"],
  "sections": ["Introducción", "Sección 2", "Sección 3", "Conclusión"],
  "hasH3": true,
  "hasSources": false,
  "entities": [
    {
      "entity": "Nombre de la entidad",
      "name": "nombre",
      "wikipediaUrl": "https://...",
      "wikidataUrl": "https://...",
      "relevance": 0.8
    }
  ],
  "internalLinks": [
    { "url": "https://...", "anchor": "texto ancla" }
  ],
  "readingLevel": "high",
  "useHumor": false
}
```

**Campo `mandatory` (0–5):** a mayor valor, mayor libertad de la IA para modificar el contenido original.
**Campo `charVariability` (0–1):** 0 = párrafos de longitud similar; 1 = gran variación entre párrafos.

### 4.3 Sistema de tres GPTs encadenados

| GPT | Función | Input | Output |
|---|---|---|---|
| **SERP Analytic** | Analiza los Top 10 resultados | URLs o textos de la SERP | JSON con `mainTopics`, `subTopics`, `relevance` |
| **Generador de JSON-Prompt** | Convierte instrucciones NL a JSON SEO | Instrucciones en lenguaje natural | JSON-Prompt completo |
| **Generador de Contenido JSON** | Redacta el contenido final | JSON-Prompt completo | Artículo/página optimizada |

### 4.4 Herramientas mencionadas en el corpus

| Herramienta | Uso en el curso | URL |
|---|---|---|
| Google Search Console | Análisis de rendimiento, posición media, detección de keywords en posición 10–13 | search.google.com/search-console |
| Google Keyword Planner | Validación de volumen, competencia y CPC | ads.google.com/home/tools/keyword-planner |
| ChatGPT | Keyword research, redirecciones, JSON-Prompting | chatgpt.com |
| Claude AI | Redacción de contenido de alta calidad y lenguaje natural a partir de JSON | claude.ai |
| JSON Editor Online | Validación visual de JSON antes de usar | jsoneditoronline.org |
| Schema.org | Referencia oficial de tipos de datos estructurados | schema.org |
| Schema Markup Validator | Validación de sintaxis de datos estructurados | validator.schema.org |
| Prueba de Resultados Enriquecidos (Google) | Validar si el código JSON-LD genera rich results | search.google.com/test/rich-results |
| TechnicalSEO.com (.htaccess Tester) | Validar reglas de redirección antes de producción | technicalseo.com/tools/htaccess |
| Keyword Combiner (Atrox Creative) | Generación masiva de combinaciones long tail | atroxcreative.com/keyword-combiner |
| Ahrefs / Sistrix | Análisis masivo de búsqueda y visibilidad (mencionadas como profesionales) | ahrefs.com / sistrix.com |
| Google Centro de la Búsqueda | Directrices oficiales de calidad de contenido | developers.google.com/search/docs |

---

## 5. Mapeo al sistema Sandi (fases del workflow)

| Contenido del curso | Fase Sandi |
|---|---|
| Comprensión del entorno AI Overview, análisis de intención de búsqueda, comportamiento del sector en SERP | **Phase 0 – Research** |
| Keyword research (generación + validación), identificación de demanda informacional vs. transaccional | **Phase 0 – Research** |
| Arquitectura SEO, clusterización, definición de pillar pages y páginas de servicio | **Phase 1 – Oferta** (estructura de la oferta digital) |
| Producción de contenido, JSON-Prompting, sistema de 3 GPTs, calendario editorial | **Phase 2 – Contenido** |
| SEO Off-Page, link building, fuerza de marca, distribución orgánica | **Phase 3 – Distribución** |
| Google Search Console, análisis de posición media, freshness, detección de oportunidades | **Phase 4 – Medir** |
| Actualización y optimización continua de contenidos, mejora de páginas en posición 10–13 | **Phase 5 – Ajustar** |
| Autoridad temática, PageRank, construcción de marca, señales E-E-A-T | **Phase 5 – Ajustar** + **Módulo A – Business Case** (credibilidad del operador) |
| Datos estructurados + Rich Results | **Phase 2 – Contenido** (producción técnica) |
| Redirecciones 301/302 con IA | **Phase 5 – Ajustar** (mantenimiento técnico) |

---

## 6. Qué aporta este material que un spec de marketing genérico no tendría

### 6.1 Operacionalización técnica del contenido (JSON-Prompting como sistema ingenieril)
Un spec genérico dice "crear contenido de calidad". Este curso entrega un sistema de especificación de contenido reproducible mediante JSON, con campos granulares: longitud de párrafos por caracteres, variabilidad, nivel de lectura, entidades semánticas con URLs de Wikipedia/Wikidata, intención de búsqueda explícita, escalas de modificación del contenido original (mandatory 0–5). Es un sistema de producción, no una guía.

### 6.2 Tratamiento de AI Overview como variable estratégica
La mayoría de specs de marketing no distinguen entre búsquedas que activarán AI Overview (informacionales) y las que no (transaccionales). Este curso construye toda la estrategia de contenidos en torno a esa distinción, porque afecta directamente al tráfico esperado y a la medición del rendimiento.

### 6.3 Sistema de validación cruzada con múltiples IAs
El curso enseña explícitamente a usar una segunda IA (Gemini) para validar el código generado por la primera (ChatGPT). Esta práctica de supervisión cruzada es rara en materiales de marketing genérico y es muy relevante en contextos técnicos (redirecciones, datos estructurados).

### 6.4 Arquitectura de authority topic como estrategia de competencia asimétrica
El concepto de que un sitio especializado puede superar a medios generalistas con más autoridad de dominio (caso Don Camper vs. medios generalistas) invierte la lógica de "necesito mucha autoridad para competir". Da un camino concreto para proyectos nuevos o de nicho.

### 6.5 Pipeline de tres GPTs encadenados con roles diferenciados
El flujo SERP Analytic → Generador de JSON-Prompt → Generador de Contenido es una arquitectura de agentes especializada que va más allá de "usa ChatGPT para escribir". Cada GPT tiene un system prompt documentado con sus campos de output definidos.

### 6.6 Criterio cuantitativo para priorización de keywords (posición 10–13)
El "fruto más cercano" es un concepto accionable: keywords ya indexadas entre posición 10 y 13 que con optimización mínima pueden entrar en primera página. Es un criterio de priorización que un spec genérico no especificaría.

### 6.7 Operacionabilidad de la frescura del contenido (freshness)
El curso no solo menciona la freshness como factor SEO, sino que la incluye como elemento de checklist On-Page obligatorio, con la nota de que un contenido de 2010 no es equivalente a uno de 2025 en términos de señales de relevancia.

### 6.8 Gestión segura de deuda técnica SEO con IA
El módulo de redirecciones no dice solo "usa IA". Establece un protocolo de seguridad: generar → validar sintaxis → revisar con segunda IA → comprobar cabeceras → implantar en producción. Es un proceso de gestión de riesgo técnico, no solo de automatización.

---

## 7. Observaciones sobre limitaciones del material

- El curso usa ejemplos de un único sector (alquiler de autocaravanas en España). Los prompts son directamente aplicables pero requieren adaptación del dominio.
- No cubre SEO programático (generación masiva de páginas mediante plantillas de datos).
- El tratamiento de AI Mode (búsqueda conversacional de Google) es superficial; se menciona pero no se dan estrategias específicas.
- La sección de link building es conceptual, sin tácticas de prospección o outreach.
- No aborda SEO internacional ni hreflang (aunque el prompt de redirecciones incluye URLs multilingüe como ejemplo).

---

*Este archivo es parte del corpus de conocimiento del sistema Sandi. Síntesis generada desde los archivos fuente en `_corpus_extracted/Marketing Documentacion Teorica/3. SEO con IA/`.*
