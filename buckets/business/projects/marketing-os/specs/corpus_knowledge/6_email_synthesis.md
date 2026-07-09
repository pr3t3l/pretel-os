# Sintesis: Email Marketing — Lead Magnets, Flujos, Webinars, Secuencias

**Fuente:** Corpus extraido de PDFs del curso (15 archivos .txt, carpeta `6. Email Marketing`)
**Fecha de sintesis:** 2026-06-09

---

## 1. Vision general del modulo

El modulo cubre email marketing de extremo a extremo: desde la captacion de leads (lead magnets, formularios) hasta la conversion final (secuencias de venta, FOMO), pasando por flujos automatizados, webinars como lead magnets de consideracion y estrategias avanzadas de re-impacto. Todo el material incluye casos practicos trabajados con ChatGPT y prompts listos para reutilizar.

---

## 2. Frameworks clave

### 2.1 Customer Journey como eje organizador de todo el email marketing

El corpus organiza CADA decision (formato del lead magnet, tipo de contenido, tono del email, longitud de la secuencia) en funcion de la etapa del Customer Journey del lead:

| Etapa | Problema del lead | Formato de lead magnet recomendado | Tipo de secuencia de email |
|---|---|---|---|
| **Conciencia** | No sabe que tiene un problema o apenas lo detecta | Ebook, guia general, infografia | Bienvenida + Nurturing educativo |
| **Consideracion** | Evalua opciones, compara soluciones | Webinar en directo, checklist, comparativa | Nurturing de profundidad + pre-webinar |
| **Decision** | Listo para comprar, necesita el empujon final | Descuento, prueba gratuita, demo | Secuencia de ventas (PAS/AIDA + urgencia) |

**Regla critica documentada en el corpus:** Un ebook de la fase de conciencia NO debe incluir precios, modelos tecnicos ni llamadas a la compra — eso pertenece a fases posteriores. El indice debe depurarse activamente con ChatGPT si la IA los incluye por defecto.

### 2.2 Arquitectura de flujos: Funnel + Broadcast

El modelo recomendado es hibrido:

```
Lead entra -> [Funnel automatizado con objetivo especifico]
                  |
                  v
             Secuencia de bienvenida (3 emails)
                  |
                  v
             Secuencia de nurturing (variable)
                  |
                  v
             Secuencia de ventas (3-7 emails segun ticket)
                  |
                  v
             [Pasa a lista general] -> Broadcasts periodicos + nuevos funnels evergreen
```

**Dos modalidades complementarias:**
- **Funnel automatizado:** Se activa por una accion concreta (descarga, registro a webinar). Persigue un objetivo medible. Cierra cuando el usuario completa el recorrido.
- **Broadcast periodico:** Envio puntual a toda la base o un segmento. Mantiene la relacion viva. No tiene objetivo de conversion inmediata.

### 2.3 Estructura de las tres secuencias principales

**Secuencia 1 — Onboarding/Bienvenida (3 emails)**

| Email | Objetivo | Contenido clave |
|---|---|---|
| Email 1 | Entrega del recurso + primera impresion | Agradecimiento, link al lead magnet, instruccion para agregar a whitelist, fijacion de expectativas |
| Email 2 | Cualificacion del lead | Encuesta breve (1 pregunta), segmentacion progresiva |
| Email 3 | Autoridad de marca | Mision, valores, prueba social, invitacion a RRSS |

**Estructura exacta del email de bienvenida (8 puntos del corpus):**
1. Bienvenida y agradecimiento
2. Fijacion de expectativas
3. Instruccion para agregar a whitelist
4. Introduccion breve de la marca
5. Reafirmacion del valor del recurso entregado
6. Presentacion de autoridad o trayectoria
7. Invitacion a otros canales
8. Pregunta o encuesta de cualificacion

**Secuencia 2 — Nurturing**

- Objetivo: educar, generar confianza, no vender
- Estructura por email: saludo + objetivo explicito del correo + beneficios concretos + CTA a recurso (articulo/video) + despedida con continuidad
- Estilo: frases cortas, parrafos breves, tono amigable, lenguaje neutro en genero
- Duracion: variable segun nivel de conciencia del lead y valor del producto

**Secuencia 3 — Ventas**

Tematicas que debe cubrir la secuencia (en orden sugerido):
1. Presentacion de la oferta
2. Respuestas a preguntas frecuentes
3. Testimonios (con documento adjunto de testimonios reales)
4. Refuerzo de propuesta de valor
5. Casos de exito
6. Visualizacion del futuro del usuario
7. Ultimo aviso (urgencia/escasez — FOMO)

**Ventanas de urgencia recomendadas segun ticket:**
- Ticket bajo: 15 min — 1 hora
- Ticket medio: ~48 horas
- Ticket alto: 3-7 dias

### 2.4 Lead Magnet adaptado al Customer Journey

**Proceso sistematico de diseno (4 pasos):**

1. **Elegir formato** segun etapa del CJ y objetivo estrategico
2. **Definir tematica** basada en Keyword Research (lo que la gente realmente busca)
3. **Desarrollar contenido** con ChatGPT como apoyo
4. **Captacion minimalista:** pedir solo el email en el formulario inicial; ampliar datos via progressive profiling posterior

**Principios del lead magnet efectivo:**
- Resuelve un problema claro, concreto y relevante
- El valor percibido justifica el intercambio de datos
- Cuantos mas campos en el formulario, menor tasa de conversion
- Comenzar con solo el email; datos adicionales se recaban en Email 2 (encuesta)

### 2.5 Webinar como lead magnet de consideracion

**Estructura de 1 hora recomendada:**
1. Bienvenida concisa (5 min)
2. Revision de dudas comunes
3. Bloque central de demostraciones comparativas (el nucleo)
4. Recomendacion de productos segun perfil de usuario
5. Espacio de venta con oferta concreta + urgencia/escasez
6. Ronda de preguntas (resolver objeciones)

**Post-webinar:** secuencia de seguimiento por email para:
- Recordar la oferta a asistentes
- Entregar valor adicional
- Reactivar a quienes no asistieron

**Palabras clave para webinars de consideracion:** deben ser comparativas ("comparativa robot aspiradores"), no informativas. Filtran leads con alta intencion de compra.

### 2.6 Estrategias avanzadas

**Funnel por Buyer Persona diferenciado:**
- Un solo funnel para toda la lista rara vez funciona
- Segmentar por perfil psicografico/motivacional (no solo demografico)
- Ejemplo: lista de alquiler de autocaravanas tiene al menos 3 personas distintas (familias, aventureros, parejas) con mensajes completamente diferentes

**Ofertas flash:**
- Aprovechan la base existente sin nueva inversion en adquisicion
- Se activan sobre leads que mostraron interes pero no convirtieron
- La urgencia temporal es el detonador de decision

**Estrategia Evergreen de re-impacto:**
- Para leads que no compraron en la primera secuencia
- Se vuelve a impactar con un angulo completamente diferente del mismo producto
- Ejemplo: primera secuencia = ahorro de tiempo; segunda secuencia = eficacia con mascotas
- Un "no" desde un beneficio puede ser un "si" desde otro beneficio

**Optimizacion de asuntos + pre-headers:**
- El asunto captura atencion; el pre-header sostiene la curiosidad
- Deben diseñarse en par, como duo complementario
- Malas practicas a evitar: palabras spam, exceso de mayusculas, exceso de signos de exclamacion
- Longitud ideal: menos de 40 caracteres (limite movil)
- Test A/B: enviar 2 versiones a segmentos pequeños, elegir la ganadora para el envio masivo

---

## 3. Metodos y pasos accionables

### Proceso completo para crear un lead magnet + flujo desde cero

**Paso 1: Keyword Research**
- Identificar que busca el Buyer Persona en Google en su etapa del CJ
- Elegir keywords con la intencion correcta (informativa para conciencia, comparativa para consideracion)

**Paso 2: Crear el lead magnet con ChatGPT**
- Crear proyecto en ChatGPT con nombre claro + contexto de nicho + buyer persona + objetivos
- Prompt de ideas de titulo (con keyword + rol de copywriter + objetivo de fase CJ)
- Prompt de indice
- Prompt de correccion del indice (eliminar contenido de fases posteriores)
- Prompt de desarrollo del contenido completo
- Prompt de imagen de portada (Freepik AI)

**Paso 3: Configurar formulario de captacion**
- Solo pedir email en primera instancia
- Guardar datos adicionales para Email 2 (encuesta de cualificacion)

**Paso 4: Crear secuencia de bienvenida (3 emails)**
- Email 1: entrega del recurso + estructura de 8 puntos
- Email 2: encuesta de cualificacion (1 CTA unico)
- Email 3: presentacion de autoridad de marca

**Paso 5: Crear secuencia de nurturing**
- 2-5 emails segun nivel de conciencia del lead
- Cada email: saludo + objetivo + beneficios + CTA a recurso + despedida

**Paso 6: Crear secuencia de ventas**
- 3-7 emails segun ticket del producto
- Cubrir las 7 tematicas estrategicas en orden
- Para cada email de venta: usar estructura PAS o AIDA (alternar)
- Incluir postdata con frase resumen que provoque accion

**Paso 7: Optimizar asuntos**
- Usar GPT personalizado "BIG Asuntos" (prompt incluido en corpus)
- Generar 5 alternativas diferentes para cada email
- Una de las 5 debe incluir emoji
- Todas < 40 caracteres
- Realizar Test A/B con las 2 mejores

**Paso 8: Conectar al broadcast**
- Al terminar el funnel, el lead pasa a lista general de broadcasts periodicos
- Mantener la relacion activa con contenido de valor periodico
- Activar nuevos funnels evergreen desde esa lista cuando sea pertinente

---

## 4. Prompts concretos del corpus

### 4.1 Prompt para ideas de lead magnet (ebook o webinar)

```
Actua como un experto copywriter y genera tres ideas para hacer un [ebook/webinar en directo] 
para [descripcion de audiencia].

El objetivo es captar leads en la fase de [conciencia/consideracion] e incluirlos en su base de 
datos para guiarlos hacia la compra con emails a traves de su customer journey.

Las ideas que me ofrezcas tienen que contener titulos con esta keyword: [KEYWORD PRINCIPAL]

Justifica tus ideas. Si lo haces bien y consigues mejorar las tasas de conversion del lead magnet 
actual, te llevaras una recompensa de $1.000. Tomaté tu tiempo y preguntame lo que quieras 
para hacer bien tu trabajo.
```

### 4.2 Prompt para corregir indice a la fase de conciencia

```
Hay un error en tu indice, este [ebook/contenido] es para la fase de conciencia en el customer 
journey del usuario, no le hables todavia de temas propios de la fase de consideracion o de 
venta. El objetivo de la fase de conciencia es inspirar y resolver un problema del usuario. 
En este caso, quieren [necesidad del usuario]. Revisa el indice para resolver este problema del 
usuario y plantea [la solucion] como la mejor opcion, sin empujar a la venta.
```

### 4.3 Prompt para email de bienvenida (narrativo, no bullet points)

```
Como especialista en copy que eres, escribe el email de bienvenida para los usuarios que se 
descargan el [nombre del lead magnet]. Escribe un email conversacional, no desarrolles 
unicamente bullet points, sino que quiero que sea un email narrativo y cercano, incluyendo 
cada uno de los elementos de esta estructura:

Bienvenida y agradecimiento: [accion especifica]
Fijacion de expectativas: [lo que recibiran]
Suscripcion a la whitelist: [instrucciones paso a paso para Gmail]
Reafirmacion de beneficios: [lista de beneficios]
Otras formas de conexion: [canales concretos]

Escribe con un tono amigable y familiar.
Haz un email conversacional breve y directo incluyendo todas las tematicas de la estructura.
Evita tecnicas de copywriting persuasivo para generar una conexion con el usuario.
Usa palabras de genero neutro sin usar el @ ni la x.
```

### 4.4 Prompt para email de ventas (estructura completa)

```
#OBJETIVOS
Eres un copywriter con anos de experiencia creando textos persuasivos para proyectos 
digitales. Tu especialidad es hacer Emails de venta que conviertan. Si tus emails consiguen 
tasas de conversion de mas de 40%, consigues una recompensa de 2.000$ por cada uno.

#COMO ACTUAR
Vas a crear emails que conviertan a usuarios en clientes.

#INSTRUCCIONES CONCRETAS
Vas a crear un email para [objetivo especifico de venta].
El buyer persona es [descripcion del buyer persona].
Contexto: el usuario ha tenido ya puntos de interaccion con la marca.

Estructura del email: Alterna entre el uso de la tecnica de copywriting PAS (problema, 
agitacion, solucion) o la tecnica AIDA (Atencion, Interes, Deseo, Accion).
No hace falta que indiques cuando inicias cada parte, simplemente escribe el email con el 
formato final.
Nunca hables de caracteristicas, habla de beneficios para el usuario.
Incluye siempre un CTA a la venta: [oferta concreta con urgencia temporal].
Incluye una postdata con una frase resumen relevante que provoque accion en el usuario.
El tono debe ser informal, profesional, respetuoso y cercano.

#REFUERZO DE INSTRUCCIONES
Usa copy persuasivo, teniendo en cuenta los disparadores mentales que hacen que el usuario 
compre. Usalos y justifica su uso. Tomaté el tiempo que necesites.
```

### 4.5 GPT personalizado "BIG Asuntos" (prompt completo del corpus)

```
#OBJETIVOS
Eres un copywriter experto en email marketing. Tu especialidad es hacer Asuntos que impacten. 
Si tus asuntos consiguen tasas de apertura de mas de 40%, consigues una recompensa de 
2.000$ por cada uno.

#COMO ACTUAR
Crearas asuntos que capten la esencia del email e impacten en la base de datos.

#INSTRUCCIONES CONCRETAS
Cuando el usuario te de el texto del email, responderas con 5 alternativas de asuntos de menos 
de 40 caracteres. Cada uno tendra un subtitulo de menos de 40 caracteres que complemente 
la informacion del asunto.

Revisaras documentacion adjunta para saber que practicas evitar para no caer en filtros de spam.

IMPORTANTE: Nunca ofrezcas asuntos si el usuario no ha compartido el texto del email.

Los 5 asuntos deben ser completamente diferentes para que el usuario pueda elegir dos y hacer 
un Test A/B. Una de las 5 alternativas tiene que tener un emoji (siempre).

Puedes usar emojis, corchetes, parentesis. Evita vocabulario que provoque filtros de spam.
El tono debe ser informal, profesional, respetuoso y cercano.

#REFUERZO DE INSTRUCCIONES
Revisa la documentacion adjunta sobre malas practicas. Ofrece 5 alternativas completamente 
diferentes que destaquen puntos distintos del email. Incluye subtitulos complementarios de 
menos de 40 caracteres.
```

### 4.6 Prompt para indice de webinar (estructura de 3 pilares)

```
Vamos a hacer esta tematica: "[TITULO DEL WEBINAR]"

Ahora, haz un indice de lo que debemos tratar en este webinar para que sea de interes para 
mi buyer persona principal, [descripcion del buyer persona].

Incluye:
Introduccion: Ideas para potenciar la autoridad de mi marca
Contenido de valor: [comparativa/demostracion de productos concretos]
Fase de ventas: Ideas para potenciar la venta inmediata.
```

---

## 5. Herramientas mencionadas

| Herramienta | Uso especifico en el corpus |
|---|---|
| **ChatGPT** | Ideas de lead magnets, indices, contenido completo de ebooks, redaccion de emails de todos los tipos, iteraciones sobre parrafos concretos via "Lienzo" |
| **ChatGPT Proyectos** | Almacenar contexto persistente (nicho, buyer persona, objetivos) para mantener coherencia en proyectos largos |
| **ChatGPT Lienzo (Canvas)** | Edicion parrafo a parrafo de emails y contenido; ajuste de tono y estructura de lectura en F |
| **Freepik AI Image Generator** | Generar portadas de ebooks con prompts de imagen fotorrealista |
| **GPT Personalizado "BIG Asuntos"** | Generador especializado de asuntos + pre-headers con reglas anti-spam incorporadas |
| **ActiveCampaign** (referenciado en URL de ejemplo) | Plataforma de email marketing con automatizacion (usada en el caso real mostrado) |
| **Factorial** | Ejemplo de SaaS con lead magnet de prueba gratuita + captacion en 2 pasos |
| **HubSpot** | Ejemplo de plantilla gratuita como lead magnet |

---

## 6. Mapeo a fases del sistema Sandi

| Fase Sandi | Contenido del corpus que mapea |
|---|---|
| **Phase 0 — Research/ICP** | Keyword Research para definir tematica del lead magnet; analisis del Buyer Persona para segmentar funnels; identificacion de la etapa del CJ del lead objetivo |
| **Phase 1 — Oferta** | Diseno del lead magnet (formato + tematica + valor percibido); estructura del webinar con elementos de venta; ventanas de urgencia por ticket; oferta flash sobre base existente |
| **Phase 2 — Contenido** | Creacion de ebooks con ChatGPT (prompts completos); creacion de emails de nurturing; estructura narrativa de emails (no bullet points); tono por etapa del CJ |
| **Phase 3 — Distribucion** | Configuracion de flujos automatizados (onboarding + nurturing + ventas); modelo hibrido funnel + broadcast; pre-webinar email sequence; post-webinar follow-up |
| **Phase 4 — Medir** | Tasa de apertura como KPI principal de asuntos; tasa de conversion como KPI de emails de venta; Test A/B de asuntos; tasa de finalizacion de formularios (progressive profiling) |
| **Phase 5 — Ajustar** | Estrategia evergreen de re-impacto (cambio de angulo); iteracion de parrafos concretos via Lienzo; optimizacion de asuntos con GPT + Test A/B; ajuste de longitud de secuencias segun ticket |
| **Modulo A — Business Case** | Email como activo propio (independiente de algoritmos); ROI superior al de otros canales tras construir base; re-impacto evergreen como multiplicador de inversion existente |

---

## 7. Que aporta este material que un spec de marketing generico no tendria

### 7.1 Prompts listos para produccion, no solo descripciones

El corpus entrega prompts completos y probados con estructura `#OBJETIVOS / #COMO ACTUAR / #INSTRUCCIONES CONCRETAS / #REFUERZO`, incluyendo el mecanismo de "recompensa de $1.000-$2.000" como tecnica de elicitacion de calidad en LLMs. No describe como deberia ser un email — muestra el prompt exacto que lo genera.

### 7.2 GPT personalizado pre-configurado para asuntos

El "BIG Asuntos" es un sistema de prompt con reglas de negocio incorporadas: 5 alternativas obligatorias, < 40 caracteres, 1 emoji siempre, diferenciacion entre asuntos para Test A/B, consulta activa de lista de palabras spam. Esto es un activo reutilizable, no una recomendacion abstracta.

### 7.3 Regla de pureza por etapa del CJ (aplicada al indice)

La instruccion de "corregir el indice para eliminiar contenido de fases posteriores" es operacional: define exactamente que eliminar (precios, modelos, contratacion) y por que. Un spec generico diria "adaptar el contenido a la etapa del usuario"; este material muestra el prompt de correccion con razonamiento explicito.

### 7.4 Progressive profiling como estrategia de captacion en 2 pasos

El corpus documenta el patron: solo pedir email en el formulario (minimizar friccion) y usar Email 2 de la secuencia de bienvenida para la encuesta de cualificacion. Esto es una decision de diseno especifica con impacto medible en tasas de finalizacion.

### 7.5 Estructura de ventas por ticket con ventanas de urgencia

Ticket bajo = 15 min a 1 hora. Ticket medio = 48 horas. Ticket alto = 3-7 dias. Esta calibracion especifica no suele aparecer en materiales genericos de email marketing.

### 7.6 Evergreen re-impacto por cambio de angulo (no de producto)

El framework de re-impacto evergreen propone re-abordar al mismo lead con un beneficio completamente diferente del mismo producto, no con un producto diferente. La logica de "cada motivacion es una segunda oportunidad" es una distincion tacita que la mayoria de specs no hace explicita.

### 7.7 Casos practicos duales (autocaravanas + robot aspirador)

El corpus trabaja dos nichos completos en paralelo, demostrando que los frameworks se aplican a productos muy diferentes. Esto proporciona ejemplos concretos citables y un modelo de transferencia: "aplica el mismo patron del webinar de robot aspirador a tu industria".

### 7.8 Ejemplos de buena vs. mala respuesta del GPT de asuntos

El corpus incluye un par "buena respuesta / mala respuesta" del GPT personalizado de asuntos, documentando el fallo especifico (dar asuntos sin haber recibido el texto del email). Esto es aprendizaje por contraste, util para calibrar el GPT personalizado.

---

## 8. Notas de integracion con el sistema Sandi

- **Lead magnet** es el entry point de toda la maquinaria de email: conecta directamente con Phase 3 (distribucion organica/pagada que lleva trafico al formulario) y es el prerequisito de toda la automatizacion.
- **La segmentacion por Buyer Persona** requiere que Phase 0 (Research/ICP) haya entregado al menos 2-3 perfiles diferenciados; sin eso, el funnel adaptado por persona no puede construirse.
- **El webinar** es el lead magnet de consideracion que conecta Phase 2 (produccion de contenido en vivo) con Phase 3 (distribucion del registro) y Phase 1 (la oferta que se presenta al final del webinar).
- **Los KPIs** (tasa de apertura, CTR, tasa de conversion) deben estar en el dashboard de Phase 4 para alimentar los ciclos de Test A/B documentados en Phase 5.
- **El broadcast periodico** es el mecanismo que mantiene viva la base entre funnels, y es el canal desde el que se lanzan las ofertas flash y los funnels evergreen de re-impacto.

---

*Sintesis generada a partir de lectura completa de 15 archivos del corpus. Todos los prompts y frameworks son fiel transcripcion/adaptacion del material original del curso.*
