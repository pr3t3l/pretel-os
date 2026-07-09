# Corpus Knowledge: SEM con IA — Síntesis Estructurada

**Fuente:** Módulo 5 – "SEM con IA" (11 clases + recursos + prompts listos para usar)
**Fecha de síntesis:** 2026-06-09
**Archivos leídos:** 19 (C1–C11, incluyendo archivos de recursos y prompts)

---

## 1. Marco Conceptual Base

### 1.1 Definición de Paid Media y SEM
El módulo parte de la distinción entre **recoger demanda** (Google Ads / Microsoft Advertising — el usuario ya busca) y **generar demanda** (Meta, TikTok, LinkedIn — se impacta a usuarios sin intención activa previa). Esta dicotomía es el eje estratégico de todo el sistema: primero decide qué tipo de demanda estás atacando, luego elige la plataforma y la mecánica creativa.

SEM = búsqueda pagada + SEO (visibilidad en motores de búsqueda). No equivale solo a Google Ads.

### 1.2 Los cuatro procesos esenciales del Paid Media
1. **Investigación y planificación** — mercado, keywords, audiencias, benchmarks
2. **Creación y configuración** — copys, creatividades, ajustes técnicos
3. **Optimización** — pujas, presupuesto, experimentos
4. **Análisis y reporte** — KPIs, decisiones basadas en datos

La IA interviene en todos los procesos, pero la toma de decisiones estratégica permanece en el profesional.

### 1.3 Taxonomía de IA aplicada al Paid Media
| Tipo de IA | Función en campañas |
|---|---|
| Predictiva | Estima clics, conversiones, CPA futuros desde datos históricos |
| Generativa | Produce textos, imágenes, ideas creativas, guiones de vídeo |
| Analítica | Detecta patrones, segmentos rentables, oportunidades de optimización |
| Automatizadora | Clasifica keywords, estructura campañas, genera informes operativos |

---

## 2. Frameworks y Metodologías Clave

### 2.1 Framework "Prompt Maestro + Herramienta Autónoma" (C3)
El patrón central del módulo para cualquier tarea repetitiva:

```
1. Pide a ChatGPT que actúe como "ingeniero de prompts"
2. ChatGPT genera un PROMPT MAESTRO para la tarea
3. Tomas ese prompt maestro y lo ejecutas con los datos reales
4. Opcionalmente: llevas el prompt maestro a Google AI Studio para
   convertirlo en una aplicación web autónoma con interfaz
```

Este patrón se repite para: análisis de clientes, estructuración de campañas, generación de copys, análisis de términos de búsqueda, análisis de informes de rendimiento.

**Ejemplo literal del curso:**
> "Eres ingeniero de prompts, quiero que me des un prompt para que se haga un estudio de un cliente, buyer persona, sector en el que trabaja, y todo lo que consideres que un profesional de marketing tiene que conocer, solo dándote la https:xxxxxxxxxx"

### 2.2 Framework de Análisis de Clientes con Triple Herramienta (C3)
1. **ChatGPT** con prompt maestro → diagnóstico inicial desde URL del cliente
2. **Gemini** con mismo prompt → segunda perspectiva, detecta matices distintos
3. **Consolidar** ambas salidas → informe unificado sin sesgo de una sola fuente
4. **Google AI Studio** → convertir el flujo en app web "AI Marketing Analyst" para escalar

Componentes del diagnóstico que produce:
- Descripción del negocio y modelo operativo
- Mercado y competidores
- Buyer personas (perfiles detallados)
- Customer journey / recorrido de compra
- Posicionamiento estratégico
- Propuestas SEO y SEM
- KPIs relevantes para el tipo de negocio
- Oportunidades de mejora

### 2.3 Clasificación de Keywords en Dos Fases (C4)
**Fase 1 — Clasificación por intención de búsqueda:**
- **Informativa:** "qué es", "cómo funciona", "ventajas de"
- **Comercial:** comparativas, reseñas, "mejores X"
- **Transaccional:** "comprar", "precio", "cotizar", "rentar", "oferta"

Output: Excel con tres hojas separadas por intención.

**Fase 2 — Agrupación semántica:**
- Dentro de las keywords transaccionales (mayor impacto en conversiones)
- Detecta patrones temáticos (ej: Autocaravanas / Campers / Furgonetas / Genéricas)
- Cada grupo → un grupo de anuncios en Google Ads
- Output: Excel con hojas por tema

**Por qué importa:** relevancia entre keyword ↔ anuncio ↔ landing = mejor Quality Score.

### 2.4 Estructura de Copy Publicitario para Google Ads (C5)
Componentes obligatorios de un prompt de generación de copys:
1. **Rol profesional** — "especialista senior en Google Ads y redacción PPC, +10 años"
2. **Objetivo** — maximizar CTR, respetar límites de caracteres de Google
3. **Instrucciones técnicas:**
   - 20 títulos cortos (máx. 30 caracteres)
   - 20 títulos largos (máx. 90 caracteres)
   - 20 descripciones (máx. 90 caracteres)
   - Lenguaje orientado a beneficios, tono persuasivo-profesional
   - Sin mayúsculas completas ni signos repetidos
   - CTAs: "Descúbrelo", "Compra online", "Reserva ahora"
4. **Formato de salida** — limpio, copiable directamente en Google Ads
5. **Contexto del negocio** — URL del sitio o texto completo pegado

Workflow iterativo: primer resultado → ajuste incremental ("Repite los títulos largos pero añade CTA al final") → no reescribir prompt completo.

Escala: AI Studio como generador de copys autónomo con exportación CSV para cargas masivas en Google Ads Editor.

### 2.5 Estructura de Landing Page para PPC (C6)
Principio fundamental: **entorno binario** — el usuario convierte o abandona; sin distracciones, sin menús, sin links externos.

Secciones obligatorias (extraídas del prompt del curso):
1. Encabezado principal con propuesta de valor
2. Subtítulo que refuerza el beneficio o resuelve una objeción
3. Beneficios clave (máx. 5 puntos)
4. Bloque visual del producto/servicio
5. Formulario simple (nombre, email, teléfono, botón enviar)
6. Sección de confianza (testimonios, logos, garantías)
7. CTA final potente

Tecnología: HTML + TailwindCSS, diseño responsive (mobile-first), canvas para prototipado.

Proceso con IA: ChatGPT genera el esqueleto/wireframe → iteración rápida sobre texto → compartir enlace con equipo de diseño → evitar retrabajo sobre diseño terminado.

### 2.6 Análisis de Términos de Búsqueda con IA (C8)
Los términos de búsqueda son datos reales de lo que los usuarios escriben. Clasificación en cuatro categorías de decisión:

| Categoría | Definición | Acción |
|---|---|---|
| Rentables | Generan conversiones, CPA bajo | Reforzar — nuevas campañas, más presupuesto |
| Informacionales | "qué es", "cómo", "tutorial", "pdf" | Añadir a lista de negativas |
| Fuera del modelo | "gratis", "empleo", "trabajo", "segunda mano" | Negativizar — tráfico irrelevante |
| No convierten | Gasto > 0, conversiones = 0 | Revisar landing, oferta, pujas; pausar |

Output esperado: Excel con 4 hojas separadas + columna "Clasificación" en cada hoja.

**Prompt listo para usar (C8_PROMPT):**
> "Actúa como un analista senior de Google Ads con más de 10 años de experiencia en detección de desperdicio publicitario..."

### 2.7 Estrategia Meta Ads con Estructura de Embudo (C9)
La herramienta para Meta genera propuestas estratégicas con esta estructura:
- **Análisis del Negocio:** público objetivo, diferenciadores, tono de comunicación
- **Estrategia de Campañas:** basada en etapas TOFU / MOFU / BOFU
- **Audiencias:** intereses relevantes + Lookalike + Remarketing
- **Copy:** estilos adaptados a formatos Meta (feed, stories, reels)
- **Visual:** imágenes, carruseles, vídeos cortos
- **KPIs:** tabla de métricas por objetivo
- **Recomendaciones:** Píxel de Meta, tests A/B, campañas estacionales

Datos de entrada al formulario: web del cliente, tipo de negocio, presupuesto mensual (€), ubicación, objetivos (Tráfico / Conversiones / Leads / Alcance / Interacción).

### 2.8 Análisis de Informes de Rendimiento (C10)
Flujo de meta-prompting para análisis de datos:

```
1. Pide a ChatGPT: "Eres ingeniero de prompts, necesito un prompt muy
   desarrollado que me ayude a analizar este excel de rendimiento de
   campañas de Google Ads"
2. ChatGPT genera el PROMPT ÓPTIMO con rol experto + estructura del informe
3. Abres un chat limpio, pegas ese prompt, adjuntas el Excel
4. El modelo produce informe estructurado
5. Para Meta Ads: adjuntas nuevo archivo EN LA MISMA CONVERSACIÓN
   (el contexto del rol se conserva)
```

Métricas clave que el modelo analiza:
- Google Ads: inversión total, conversiones, clics, CPA promedio, CTR por campaña, distribución de presupuesto
- Meta Ads: resultados, clics, gasto total, CTR, rendimiento por creatividad, segmentación demográfica (edad/sexo)

### 2.9 Integración Automatizada de Datos (C11)
Stack de data pipeline para reporting unificado:

```
Windsor.ai → URL conector (JSON/CSV) → Google AI Studio → Panel interactivo
```

**Windsor.ai:** conecta Facebook Ads, GA4, Google Ads, LinkedIn Ads, TikTok Ads en un repositorio centralizado. Plan gratuito: 1 usuario, hasta 10 fuentes.

**Campos del conector configurables:** Account Name, Campaign, Clicks, Date, Source, Spend, Sessions.

**Google AI Studio como BI tool:** con prompt en lenguaje natural crea dashboard con métricas centrales, gráficos de evolución temporal, gasto por plataforma, tablas de rendimiento por campaña, filtros interactivos. Sin código.

---

## 3. Prompts Listos para Usar (del Corpus)

### Prompt 1: Generador de Análisis de Cliente (C3)
```
Eres ingeniero de prompts, quiero que me des un prompt para que se haga
un estudio de un cliente, buyer persona, sector en el que trabaja, y todo
lo que consideres que un profesional de marketing tiene que conocer,
solo dándote la https:xxxxxxxxxx
```
→ Luego: "ahora actúa como ingeniero de promts y hazme un promt optimizado
para crear una aplicación en ai studio con las instrucciones del promt anterior"

### Prompt 2: Clasificador de Keywords por Intención (C4)
```
Actúa como ingeniero de prompts. Quiero que redactes un prompt detallado
donde, a partir del archivo de Excel que te adjunto con palabras claves,
se logre el objetivo que analice y agrupe automáticamente las palabras clave
en diferentes hojas del Excel, clasificándolas según su intención de búsqueda
(informativa, comercial o transaccional), para facilitar la estructuración
de campañas de Google Ads bien segmentadas.
```

### Prompt 3: Agrupador Semántico de Keywords (C4)
```
Actúa como ingeniero de prompts experto en Google Ads y análisis semántico
de palabras clave. Quiero que redactes un prompt avanzado que permita, una
vez subido un archivo Excel con palabras clave, que el modelo actúe como un
especialista en estructuración de campañas de Google Ads. El objetivo es que
el modelo analice y agrupe automáticamente las palabras clave en diferentes
hojas dentro del mismo Excel, clasificándolas según su significado o intención
de búsqueda, y separando claramente los términos relacionados con cada tipo
de vehículo [...] Descarga el excel con los resultados
```

### Prompt 4: Generador de Copys para Google Ads — Performance Max (C5)
```
Actúa como un especialista senior en Google Ads y redacción PPC, con más
de 10 años de experiencia creando anuncios de alto rendimiento para
campañas Performance Max.

Objetivo: Generar títulos y descripciones totalmente optimizados para
maximizar el CTR, cumpliendo de forma estricta los límites de caracteres
establecidos por Google.

Instrucciones:
- Crea 20 títulos cortos (máximo 30 caracteres)
- Crea 20 títulos largos (máximo 90 caracteres)
- Crea 20 descripciones (máximo 90 caracteres)
- Usa un lenguaje claro, natural y orientado a beneficios, tono persuasivo
  pero profesional
- Capitaliza correctamente (sin mayúsculas completas ni signos repetidos)
- Incluye CTAs: "Descúbrelo", "Compra online", "Reserva ahora"

Formato de salida: limpio, organizado, fácilmente copiable en Google Ads.

Lo quiero para esta web: [PEGAR TEXTO DE LA WEB]
```

### Prompt 5: Landing Page HTML con TailwindCSS (C6)
```
Actúa como experto en diseño web y optimización de conversiones para
campañas de Google Ads. Quiero que diseñes una landing page transaccional
enfocada en captar leads, con estructura profesional y orientada a maximizar
el CTR y el ratio de conversión. Lo realizarás con la función canvas.
Te proporcionaré el texto completo del producto o servicio (nombre,
beneficios, características y CTA principal). Con esa información, genera
una landing page en HTML con TailwindCSS, visualmente atractiva, clara
y adaptada a móviles. [estructura completa: encabezado + subtítulo +
beneficios + bloque visual + formulario + confianza + CTA final]
Lo quiero para esta web: (PEGAR AQUÍ EL CONTENIDO DE LA WEB)
```

### Prompt 6: Diseñador de Anuncios IA — App en AI Studio (C7)
App web completa con panel de control (izquierda) + galería de resultados (derecha):
- Input: foto del producto (drag&drop/portapapeles), nombre, CTA, precio original/oferta/descuento
- Output: 3 formatos automáticos — 1200x1200 (1:1), 1200x675 (16:9), 960x1280 (3:4)
- Edición por lenguaje natural por cada imagen individual
- "Reglas de Oro": producto intocable, dimensiones exactas, solo texto del usuario, ediciones conservan formato

### Prompt 7: Video Ads 100% Transaccionales (C7)
```
Actúa como un director creativo y publicista experto en vídeos de alto
rendimiento [...] Tu objetivo es crear el guion y la descripción visual
exacta para generar un vídeo publicitario de 10 segundos, en formato
1080x1920, 100% transaccional.

Estructura persuasiva:
- 0–2 s: impacto visual, producto en primer plano, música dinámica
- 2–5 s: producto en uso/diferentes ángulos, resaltando atractivo visual
- 5–8 s: precio original tachado vs precio oferta con efecto zoom
- 8–10 s: logo + CTA potente ("¡Cómpralo ahora!") con sonido de clic
```

### Prompt 8: Analista Senior de Google Ads — Términos de Búsqueda (C8)
```
Actúa como un analista senior de Google Ads con más de 10 años de
experiencia en detección de desperdicio publicitario y optimización
de campañas. Tu tarea es analizar un archivo Excel con los términos de
búsqueda que activan las campañas y clasificar automáticamente cada
término según su intención y rentabilidad.

Clasifícalos en:
- Rentables (conversiones > 0)
- Informacionales (consultas tipo "qué es", "cómo", "definición", "pdf",
  "imagen", "youtube", "curso", "tutorial")
- Fuera del modelo de negocio (palabras como "gratis", "empleo",
  "trabajo", "oficina")
- No convierten (tienen gasto pero 0 conversiones)

Genera un nuevo Excel con cuatro hojas separadas [...] añadiendo una
nueva columna llamada "Clasificación".
```

### Prompt 9: Generador de Propuestas Meta Ads (C9)
App web con formulario → propuesta estratégica completa con:
- Análisis del negocio + buyer persona
- Estrategia por etapas TOFU/MOFU/BOFU
- Audiencias (intereses + lookalike + remarketing)
- Copy con emojis + imagen generada por IA por cada anuncio
- KPIs en tabla
- Exportación PDF/Word/Excel

### Prompt 10: Análisis de Informe de Rendimiento (C10)
```
Eres ingeniero de promts necesito un promt muy desarrollado que me ayude
a analizar este excel de rendimiento de campañas de google ads
```
→ Genera prompt experto → nueva sesión → adjuntar Excel → informe estructurado.

---

## 4. Herramientas Concretas Mencionadas

| Herramienta | Uso principal |
|---|---|
| **ChatGPT** | Prompt maestro, análisis de cliente, copys, clasificación keywords, análisis de informes, análisis de términos de búsqueda |
| **Google AI Studio** | Convertir prompts en apps web autónomas; dashboards desde Windsor.ai; diseñador de anuncios; generador de copys |
| **Gemini (+ modelo Veo)** | Segunda perspectiva en análisis de clientes; generación de vídeos publicitarios |
| **Windsor.ai** | Data pipeline — centraliza Facebook Ads, GA4, Google Ads, LinkedIn Ads, TikTok Ads en URL conector (JSON/CSV) |
| **Google Ads** | Plataforma de campañas de búsqueda; fuente de exportación de términos de búsqueda e informes de rendimiento |
| **Meta Ads (Facebook/Instagram)** | Campañas de generación de demanda; fuente de informes; objetivo de la herramienta de propuestas |
| **Microsoft Advertising (Bing Ads)** | Alternativa a Google Ads para captura de demanda |
| **TikTok Ads / LinkedIn Ads** | Generación de demanda en nichos específicos |
| **Looker Studio** | Visualización de datos; mencionado como fuente análizable por ChatGPT |
| **Google Ads Editor** | Carga masiva de copys vía CSV |

---

## 5. Mapeo a Fases del Sistema Sandia

| Fase | Contenido del módulo que mapea aquí |
|---|---|
| **Phase 0: Research / ICP** | C3 — Análisis de cliente con ChatGPT + Gemini: buyer persona, mercado, competidores, KPIs relevantes. C4 — Investigación y clasificación de keywords por intención |
| **Módulo A: Business Case** | C3 — Diagnóstico estratégico desde URL: ventajas competitivas, oportunidades de mercado, modelo de negocio. C2 — ROI publicitario, CPA, métricas de inversión |
| **Phase 1: Oferta** | C6 — Landing page como extensión de la oferta: propuesta de valor, beneficios, formulario de conversión. C9 — Análisis del negocio en propuesta Meta: qué vende, qué lo hace especial |
| **Phase 2: Contenido** | C5 — Generación de copys con prompts estructurados. C7 — Creación de imágenes y vídeos publicitarios con IA. C9 — Copy para Meta con emojis + imágenes generadas |
| **Phase 3: Distribución** | C1/C2 — Estrategia Paid Media: Google Ads (recogida de demanda) vs Meta/TikTok/LinkedIn (generación de demanda). C4 — Estructura de campañas en Google Ads. C9 — Propuesta de campañas Meta con TOFU/MOFU/BOFU. C11 — Integración multi-plataforma con Windsor.ai |
| **Phase 4: Medir** | C8 — Análisis de términos de búsqueda (desperdicio vs rentabilidad). C10 — Análisis de informes Google Ads + Meta Ads con LLM. C11 — Dashboard unificado Windsor.ai → AI Studio con filtros interactivos |
| **Phase 5: Ajustar** | C8 — Acciones de optimización por categoría de términos (negativizar, pausar, reforzar). C10 — Informe incluye recomendaciones de ajuste por campaña. C9 — Tests A/B, campañas estacionales como recomendaciones adicionales |

---

## 6. Qué Aporta Este Material Sobre un Spec de Marketing Genérico

### 6.1 Operacionalidad inmediata
Un spec genérico describe QUÉ hacer. Este curso describe CÓMO hacerlo exactamente, con:
- Prompts listos para copiar y pegar (9 prompts completos en archivos _PROMPT.txt separados)
- Formatos de salida especificados (número exacto de copys, dimensiones de imágenes, estructura de hojas Excel)
- Límites técnicos precisos (30 car. títulos cortos, 90 car. títulos largos/descripciones en Google Ads)

### 6.2 El patrón "Prompt Maestro como Producto"
No es solo "usa IA para hacer X". El patrón es: **convierte el prompt en una aplicación autónoma reutilizable** (Google AI Studio). Esto permite escalar el trabajo de agencia — un solo especialista puede gestionar múltiples clientes con herramientas internas estandarizadas.

### 6.3 Ingeniería de prompts como método, no como táctica
El módulo enseña a pedir a la IA que **genere sus propios prompts óptimos** (meta-prompting). Esto es más avanzado que los enfoques genéricos de "escribe un buen prompt": el profesional actúa como director del proceso, no como redactor de instrucciones.

### 6.4 Clasificación de términos de búsqueda como bucle de optimización
La categoría "No convierten" es especialmente valiosa: no son negativos obvios sino términos que pasan el filtro de intención pero fallan en conversión. El módulo propone un análisis sistemático y diferenciado de las cuatro categorías, con acciones distintas para cada una. Un spec genérico diría "revisa las keywords negativas"; esto dice cómo clasificar 10.000 términos en minutos.

### 6.5 Stack de data pipeline explícito para Paid Media
La integración Windsor.ai → Google AI Studio es un flujo técnico concreto que no aparece en specs de marketing genéricos. Resuelve el problema de consolidación de datos multi-plataforma sin código, para agencias o freelancers sin equipo de datos.

### 6.6 Estructura de video ad con segundos asignados
El prompt de video para C7 especifica estructura narrativa por intervalos de 2 segundos (impacto / producto en uso / precio / CTA). No es "crea un vídeo persuasivo" sino un guion técnico de producción reproducible.

### 6.7 Meta Ads con TOFU/MOFU/BOFU como output de IA
La herramienta de propuestas Meta genera automáticamente la estructura de embudo completa a partir de datos básicos del cliente. Esto acelera la fase de estrategia de distribución de días a minutos.

### 6.8 Análisis demográfico en Meta Ads como input de segmentación
El módulo indica que el análisis de rendimiento de Meta incluye explícitamente el rendimiento por edad y sexo, con el propósito de guiar experimentos A/B. Conecta el análisis (Phase 4) directamente con ajustes de segmentación (Phase 5).

---

## 7. Reglas y Limitaciones Explícitas del Módulo

- La IA no reemplaza el juicio estratégico — toda propuesta requiere validación profesional
- No introducir datos sensibles de clientes en herramientas externas (RGPD / privacidad)
- La IA puede generar correlaciones que no explican causas reales — el criterio profesional es el filtro
- En video ads (Gemini/Veo): los resultados pueden presentar variaciones; la iteración es parte del proceso
- En el diseñador de anuncios IA: el producto es "sagrado" — la foto original no se altera
- Los prompts tienen que ser limpios para ser reutilizados; el contexto del chat anterior puede contaminar resultados (por eso para el análisis de informes se recomienda abrir un chat nuevo con el prompt optimizado)

---

## 8. Stack de Herramientas Recomendado del Curso

```
INVESTIGACIÓN Y PLANIFICACIÓN
├── ChatGPT           → Análisis de cliente, buyer persona, keywords
└── Gemini            → Segunda perspectiva del análisis

CREACIÓN DE CAMPAÑAS
├── ChatGPT           → Estructura de campañas, copys, clasificación keywords
├── AI Studio         → Apps autónomas: copy generator, ad designer, meta proposals
└── Gemini + Veo      → Vídeos publicitarios

OPTIMIZACIÓN
└── ChatGPT           → Análisis de términos de búsqueda (Excel → 4 hojas)

ANÁLISIS Y REPORTING
├── ChatGPT           → Análisis de informes (Google Ads + Meta Ads)
├── Windsor.ai        → Data pipeline multi-plataforma
└── AI Studio         → Dashboard interactivo desde Windsor.ai

PLATAFORMAS PUBLICITARIAS
├── Google Ads        → Búsqueda, PMax, Display (recogida de demanda)
├── Meta Ads          → Facebook/Instagram (generación de demanda)
├── TikTok Ads        → Audiencias jóvenes, contenido vídeo
├── LinkedIn Ads      → B2B
└── Microsoft Ads     → Alternativa a Google en búsqueda
```

---

*Síntesis generada automáticamente desde los 19 archivos .txt del corpus. Citable con referencia a archivo fuente: `C[N]_[NOMBRE].pdf.txt` en la carpeta original del corpus.*
