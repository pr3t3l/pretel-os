# CAG #4 — El transcript canónico (Fase 1 pasos 2-4 + Fase 2 completa, con las correcciones del operador)

**Status:** corpus CAG formal LOCKED (mandato del operador 2026-06-12, sesión 4: *"esta es el flujo que tuvimos durante el desarrollo de la fase 1 y la fase 2, quiero que cada paso refleje esta estructura que ya probamos... lo que hicimos en cada paso es lo que te he dicho todo el tiempo que debe seguir así"*).
**Qué es:** el transcript LITERAL de la simulación fundacional pegado por el operador como contraste contra el build. Es la espec viva de la experiencia — cierra el pendiente "CAG #4 formal" del blindaje (capa 3, `quality_armor_model_agnostic.md`).
**Cómo usarlo:** (1) fuente de los guiones-como-datos al reconstruir cada paso (`build_plan_experiencia_canonica.md` v2); (2) ejemplo de nivel en prompts de paso (extractos — el íntegro no cabe en cada prompt); (3) golden set para los evals de carácter y de paso (capa 8). Las intervenciones del operador (marcadas **[OPERADOR]**) son tan canon como los beats: muestran la dinámica corrección→regla.
**⚠️ Privacidad (D-037):** este doc contiene la historia familiar del nombre Papandi. Es material INTERNO — jamás en copy público ni en capa usuario.

---

## Fase 1 · Paso 2 de 5 — El offer stack (y los costos)

> Qué es este paso: el paso 1 diagnosticó (a Priya le falla la probabilidad — no nos cree, todavía). Este paso construye la respuesta: el entregable central + 3 a 7 refuerzos diseñados para atacar exactamente ese eje. Y tiene dos candados económicos que se firman juntos: el valor percibido del paquete debe ser ≥5× el precio, y el margen bruto ≥70%. Para el segundo candado necesitamos saber cuánto nos cuesta servir a un usuario — y eso es el modelo de costo de IA que parqueamos en 0.1.
>
> El instrumento primero: el modelo de costo responde una pregunta simple — ¿cuántos dólares de IA gasta un usuario al usar Sandi? — y separa lo medido (real, de producción) de lo estimado (etiquetado, se reemplaza al construir cada fase). De ahí salen el margen y el diseño de créditos.
>
> Los números reales (de project_llm_calls en prod — tu propio dogfood con Healthy Families, 13 llamadas, 0 errores, caching activo):
>
> Tu Phase 0 completa — los 5 gates, con research web real — costó $1.06 de IA.
>
> | Clase de acción | Ejemplo | Costo real por acción | Peso relativo |
> |---|---|---|---|
> | Beat ligero | preguntas del cowork | $0.005 | 1 |
> | Propuesta estratégica | personas, puerta, value equation | $0.025 | 5 |
> | Research con web | tu mercado, tu competencia | $0.31 | 60 |
>
> El hallazgo que cambia el diseño: el research es el 89.7% del costo ($0.95 de $1.06). Una acción de research cuesta ~60 beats. Implicación directa: un esquema "1 crédito = 1 acción" plana está roto de nacimiento — regala el margen a los usuarios research-intensivos. Los créditos deben pesar por clase (la semilla: beats incluidos · propuesta = 1 crédito · research = 10-12 créditos).
>
> El margen a $30/mes (tu hipótesis desde 0.2): uso típico (2-3 avatares) = COGS $3-6 → margen 80-90%, el candado pasa con holgura. Uso intensivo = 67-80%, borde. Sin límites de créditos = falla — que es exactamente lo que el sistema de créditos pesados previene. Estimaciones de Phases 1-5 etiquetadas como tales en ai_cost_model.json; se vuelven medición real cuando cada fase se construya.
>
> **Tres decisiones tuyas para armar el stack**
> 1. El entregable central de Priya — mi propuesta (tú dispones): "El plan de independencia del marketplace: estrategia por público (regalo corporativo / hogar / bodas), plan semanal concreto, borradores hechos, y cada dólar de canal propio medido." — Sandi configurada para SU situación. ¿Lo ajustas o va?
> 2. ¿Confirmas $30/mes como precio objetivo del stack? (hipótesis firmada en el brief; el candado de ratio exigirá entonces ≥$150 de valor percibido demostrable)
> 3. ¿Confirmas la dirección de créditos pesados por clase (beats incluidos / propuesta 1 / research 10-12)? El número fino se calibra en 1.4 con esta base.
>
> Con esas tres, te traigo el stack completo — bonuses con su fuerza atacada, valores con comparables de tus 17 competidores, y los dos candados calculados.

### 🍉 Sandi — sim · Paso 2: el stack de Priya, tarjeta por tarjeta

> Alfredo — con tu entregable central aprobado, armé el paquete completo. Recuerda los dos candados de este paso: el valor percibido debe ser ≥5× el precio ($30 → ≥$150), y el margen ≥70%. Cada valor cita un comparable real de tu scan de competencia — nada inventado.
>
> 🧱 El centro (aprobado por ti):
>
> El plan de independencia del marketplace — estrategia por público (regalo corporativo / hogar / bodas), plan semanal concreto, borradores de texto hechos, y cada dólar propio medido vs el alquilado.
> Valor: $99/mes · 📊 comparable: M1-Project cobra $99 por UN solo público y $199 por tres — sin loop de medición. Valuarnos al precio de SU tier de un público, dando varios con loop, es conservador a propósito.
>
> Las 4 tarjetas (✓ aceptas · ✏️ ajustas · ✕ descartas):
>
> | # | Tarjeta | Valor | Comparable real | Qué ataca |
> |---|---|---|---|---|
> | 1 | Ruta al primer dólar propio — hito de 30 días: emails capturados semana 1-2, primera venta propia trackeada día 30 | $97 | Plan one-shot de Fiverr: $144-165, sin ejecución | El eje débil (probabilidad) + "¿esto es otro humo?" + la cicatriz del Shopify fantasma — convierte "créeme" en "mide el hito" |
> | 2 | Medidor de independencia — revenue propio vs alquilado, semana a semana | $49 | Jungle Scout $49 / Helium 10 $129 — miden DENTRO de la jaula; este mide la salida | Su pull #2: independencia medible en dinero |
> | 3 | Borradores listos cada semana, por público — posts, emails, descripciones (texto + briefs para SUS fotos) | $49 | Copy.ai $49 / Jasper $69 — copy genérico sin estrategia | Rompe el hábito "toda mi operación está optimizada para el marketplace" — músculo propio sin soltar Amazon |
> | 4 | Escuela en el camino — micro-lecciones de marketing directo justo cuando las necesita | $39 | Cursos/gurús $500-2k (la quemada de Priya), en frío y con humo | Su miedo "el DTC es otro deporte — ¿podré sola?" |
>
> Los candados:
> - Valor del paquete: $99+97+49+49+39 = $333 → ratio 11.1× sobre $30 (candado pide 5×) ✅
> - Costo de servirlo: $7.20 escenario conservador → margen 76% (candado pide 70%; con tu COGS típico medido sube a 80-90%) ✅
>
> Lo que dejo honestamente descubierto (viaja a las siguientes fases, no se barre): la objeción "otra suscripción más" la cierra el copy de Phase 2 con ROI visible ("una venta propia de $40 paga el mes"); y el hábito más duro — "Amazon todavía paga las cuentas, la jaula es cómoda" — no se ataca con un bonus: se ataca en el paso 3 con la garantía honrable y el costo-de-seguir-igual.
>
> Y el re-score que prometimos en D-031: con este stack, propongo subir probabilidad de 4 → 6 (el hito medible + los números semanales). Composite re-proyectado: 8×6×5×6 = 1.440 — saldría del bloqueo blando. No lo firmo aún: espero la garantía del paso 3, que puede sumar, y tu visto.
>
> Tu turno: dispón de las 4 tarjetas (✓/✏️/✕). Con tu disposición pasamos al paso 3 — riesgo, urgencia y desplazamiento — que es 100% tuyo por regla del sistema.

### 🍉 Sandi — sim · Aclaremos el paso 2 (la culpa fue mía) — [ruptura-reparación tras confusión del operador con los "valores"]

> Primero: ¿cómo vas con el entendimiento? Muy bien — tu modelo de los Beats es correcto. Lo repito con tus palabras para confirmarlo: el usuario paga $30/mes → eso le da una bolsa de Beats → cada acción que hace dentro de las fases consume Beats (las acciones ligeras casi nada; las investigaciones con búsqueda web, mucho más — por eso pesan distinto) → y las sugerencias/notificaciones lo ayudan Y a la vez mueven consumo. ✅ Solo le pongo un guardarraíl a tu última idea, que ya dejé escrito: las sugerencias empujan consumo solo como consecuencia de ser útiles — una sugerencia diseñada para quemar Beats sin valor sería un dark pattern, y eso está prohibido por nuestras propias reglas. Tu instinto de producto es bueno; el guardarraíl lo hace honesto.
>
> Segundo — la llave que destraba todo lo demás: esos $99, $97, $49 de las tarjetas NO son precios. Nadie paga eso. Tu segunda lectura era la correcta: es el "esto es lo que recibes (y te ahorras) si nos eliges". Se llaman valores percibidos: lo que costaría comprar cada pieza por separado, con otro proveedor — y por eso cada uno cita un competidor real de tu scan. En la página de venta se ven como una lista que termina en una sola línea de precio. No son rangos, no son tiers, no son eslóganes por nivel — si algún día queremos niveles de precio (básico/premium), eso se decide en el paso 4.
>
> Tercero — el marco que se nos perdió: recuerda que estamos diseñando lo que Sandi le vende a Priya — nuestra clienta simulada, la diseñadora que vende en Amazon. "Regalo corporativo / hogar / bodas" son los públicos de ELLA (quién compra sus productos). Y de ahí salen los términos que no te entraban, en simple:
>
> - "Dólar propio vs alquilado": cuando Priya vende por Amazon, el cliente no es suyo — Amazon le cobra comisión y puede cerrarle la puerta mañana. Esa venta es "alquilada". Cuando vende por SU web a SU lista de correos, esa venta es "propia". (Me pasé de poético — en el producto diría: "ventas por tu web y tu lista vs ventas por Amazon".)
> - "Ruta al primer dólar propio": una meta diseñada con fecha — en 30 días, Priya logra su primera venta fuera de Amazon, medida. Las primeras semanas captura correos (su primer activo propio). Existe porque a Priya ya la estafaron gurús: no le pedimos fe, le damos un hito que puede verificar.
> - "Medidor de independencia": un número semanal simple — "¿qué % de mis ventas ya es mío?" — viendo cómo sube de 0% hacia su meta de 30%.
>
> Y ahora mira el paquete como PRIYA lo vería — esto es lo que el stack realmente es:
>
> *Para ti, que vendes en Amazon y el cliente nunca es tuyo: Te entrego tu plan para vender por TU web y TU lista — sin soltar Amazon.*
> - *Tu estrategia por cada público (corporativo · hogar · bodas) + plan semanal — valor $99/mes*
> - *Ruta al primer dólar propio: tu primera venta fuera de Amazon en 30 días, medida — valor $97*
> - *Medidor de independencia: cada semana, qué % de tus ventas ya es tuyo — valor $49/mes*
> - *Borradores de posts y emails listos cada semana — valor $49/mes*
> - *Mini-lecciones de marketing justo cuando las necesitas — valor $39/mes*
>
> *Todo esto vale $333. Tu inversión: $30/mes.*
>
> Esa última línea es la oferta entera. El cliente hace la resta solo — y decir que no se siente tonto. Los dos candados que pasamos (11× y 76%) solo verifican que esa línea sea verdad defendible y negocio sano.
>
> (Y esto ya quedó en el canon: el wizard SIEMPRE explicará "valor ≠ precio" antes de mostrar la primera tarjeta — misma medicina que con los scores.)
>
> ¿Aterriza ahora? Si sí, dispón de las 4 tarjetas (✓ aceptar / ✏️ ajustar / ✕ descartar) y pasamos al paso 3: la garantía — que es 100% tuya.

## Fase 1 · Paso 3 de 5 — La garantía, la urgencia y el reemplazo

> Alfredo — tu paquete quedó firmado. Este paso baja las tres últimas barreras, y aquí cambia el juego: es 100% tuyo. El sistema no decide ética por ti — yo propongo con su chequeo de honestidad, tú eliges. Primero, qué es cada pieza:
>
> 🛡️ La garantía — le quitas el riesgo al cliente y lo asumes tú. Solo se publica si la honrarías de verdad: una garantía que no cumplirías vale menos que ninguna.
> ⏰ La urgencia — una razón REAL para actuar hoy y no en 30 días. Si no existe, se deja en blanco: las cuentas regresivas inventadas son el sello de los gurús que quemaron a Priya.
> 🔄 El reemplazo — tu oferta debe REEMPLAZAR algo que ella ya hace, no sumarse encima. Contra la inercia, "una cosa más" siempre pierde.
>
> **Decisión 1 — La garantía. Dos opciones:**
> - A (mi recomendación): devolución incondicional, 30 días. "Si en tus primeros 30 días sientes que esto es otro humo, escríbenos y te devolvemos el mes. Sin formularios, sin letra pequeña." Por qué A: a Priya ya la estafaron — la letra pequeña le huele a escape de estafador; lo incondicional es la señal de confianza más fuerte para ELLA, y ataca directo el eje débil. Chequeo de honestidad: honrarla cuesta $30 + ~$2 de IA por quien la pida; a este precio el abuso esperable es bajo, y cada reembolso pre-lanzamiento es una conversación que nos enseña. La pregunta que solo tú puedes responder: ¿la honrarías sin dudar?
> - B: condicional — "sigue el plan 30 días; si completas tus sesiones y no terminas con tu plan + tus primeros suscriptores, mes devuelto." Más Hormozi, y el sistema PUEDE verificar la condición honestamente — pero introduce exactamente la letra pequeña que este avatar castiga.
>
> **Decisión 2 — La urgencia. Tres caminos:**
> - A (mi recomendación): plazo real de temporada, anclado al disparador #3 de Priya (quiere capturar las fiestas con canal propio). "Para llegar a Q4 vendiendo por tu propio canal, tu plan necesita 8-12 semanas de ventaja. Empezar hoy es llegar con audiencia; empezar en octubre es llegar tarde." Es matemática de calendario, no presión: el deadline lo pone diciembre, no nosotros. Con regla de retiro incluida: fuera de la ventana (jun-sep), esta urgencia se quita del copy — sostenerla cuando ya no es verdad sería fabricarla.
> - B: precio de fundadores ($30 sube al salir de beta) — solo si TÚ te comprometes de verdad a subirlo. Sin compromiso firme, es urgencia fabricada y queda prohibida. Es una decisión de pricing de largo plazo — puede esperar al paso 4.
> - C: ninguna — la oferta se sostiene sola con el 11× + la garantía. También es honesto.
>
> **Decisión 3 — La escasez:** mi recomendación es ninguna — no apilemos mecanismos de presión sobre alguien post-quemadura; nuestra honestidad ES el diferenciador. (Si algún día quieres "cohorte fundadora con soporte directo tuyo", sería escasez verdadera — limitada por tu tiempo real — pero hoy no la necesitamos.)
>
> **Decisión 4 — El reemplazo** (pieza obligatoria; el texto es propuesta). Aquí atacamos el hábito que el paquete dejó pendiente a propósito — "Amazon todavía paga las cuentas, la jaula es cómoda":
>
> "Esto no es una cosa MÁS encima de Amazon: reemplaza las horas que cada semana le regalas al algoritmo — peleando ads y viendo tu margen encogerse — por construir el canal que sí es tuyo."
>
> Y el costo de seguir igual: "cada mes igual = 30-70% del precio en fees y ads, cero clientes propios, y el negocio entero a una suspensión de distancia. Sigues construyendo el negocio de Amazon, no el tuyo."
>
> Esa última frase se volverá copy central en la fase de contenido.
>
> Tus cuatro elecciones (puedes responder corto: "1A, 2A, 3 ninguna, 4 va"): con ellas cierro el paso 3, firmo el re-score de probabilidad (4→6, composite 1.440 — saldría del bloqueo blando), y entramos al paso final: el precio, los Beats… y el nombre definitivo de Sandi.

## Fase 1 · Paso 4 de 5 — Precio, Beats… y el nombre

> Alfredo — paso 3 cerrado con tus cuatro firmas. Y mira lo que pasó con la ecuación: con el hito medible del paquete + tu garantía sin letra pequeña, la probabilidad subió de 4 a 6 → composite 1.440, estándar operativo. La oferta salió del bloqueo blando por diseño, no por maquillaje — el método funcionó exactamente como prometía.
>
> Qué es este paso: cerramos la oferta en tres piezas — el precio justificado (contra tu ecuación, tu paquete Y tu competencia), el nombre definitivo (la decisión que cargas desde el día 1), y la página única que alimentará todo el contenido. Tres decisiones, una por tarjeta:
>
> **Tarjeta 1 — El precio y los Beats** (ratificación — casi todo ya lo decidiste):
> - $30/mes, un solo plan — entrada por debajo del mercado ($99 de M1, $129 de Helium) con valor de tier premium (11×). No competimos por precio contra ChatGPT $20: competimos por sistema.
> - La bolsa mensual de Beats (tu nombre — aquí se ratifica como oficial): acciones ligeras incluidas · propuesta estratégica = 1 Beat · investigación con web = 10-12 Beats. La bolsa del plan alcanza ~1 Fundación completa o 2-3 ciclos de avatar/mes típicos. Pesos calibrables con datos reales (Módulo C).
> - La puerta gratis, con job declarado: el primer paso de la Fundación (el cowork de idea de "Tu negocio") gratis — el usuario vive la co-creación con SU idea, firma su primer gate, deja su email. El anzuelo es experimentar el método, no un PDF.
> - El ancla de venta: "Todo esto vale $333. Tu inversión: $30/mes."
> - (El precio de fundadores —subir post-beta— queda diferido: solo si TÚ te comprometes de verdad. No urge hoy.)
>
> **Tarjeta 2 — Cómo le hablamos a Priya** (el language pack — de aquí sale el tono de todo su copy):
> - Registro: profesional pragmático de seller — números, fees, márgenes; emocional solo en los momentos de rabia.
> - Frases que SÍ usa (de sus foros reales, 0.3): "the percentage they take" · "fees eating my margin" · "own my audience" · "my customer, not Amazon's" · "one suspension away".
> - Nunca decir: "AI marketing tool" (océano rojo, regla D-028) · "guru/secret/hack" (el vocabulario de los que la quemaron) · "quit Amazon" (no quiere irse — quiere dejar de depender).
>
> **Tarjeta 3 — EL NOMBRE.** Esta es tuya y es la grande. Lo que el método pide: que pase el test de la frase ("compré [nombre] y conseguí clientes constantes"), que encaje con el posicionamiento (guía multi-público que enseña haciendo), dominio disponible y trademark limpio. Ya investigué los dominios en vivo, ahora mismo:
>
> | Dominio | Estado |
> |---|---|
> | sandi.com / sandi.ai / sandi.app / heysandi.com | ❌ tomados (tu duda del día 1, confirmada) |
> | getsandi.com | ✅ disponible — $11.25/año |
> | trysandi.com | ✅ disponible — $11.25/año |
> | sandi.marketing | ✅ disponible — $9.99/año |
> | sandimarketing.com | ✅ disponible — $11.25/año |
>
> Mi recomendación, glass-box: quedarnos con Sandi como nombre definitivo. Razones: es nombre de persona — perfecto para un guía que acompaña (el patrón Alexa/Siri, y "Sandy" suena natural en inglés); la sandía 🍉 te da identidad visual propia e inolvidable en un mar de logos genéricos de IA; y todo tu producto ya respira ese carácter. El dominio raíz tomado no es bloqueo: getsandi.com es el patrón clásico de SaaS (getdrip, getharvest). Caveat honesto que no puedo resolver yo: el chequeo de trademark en US (USPTO) sobre "Sandi" para software/marketing — eso queda como verificación pre-lanzamiento tuya (idealmente con abogado), y lo dejo como gate, no como detalle.
>
> Si en cambio quieres explorar nombres nuevos, dame el "exploremos" y te traigo una ronda de candidatos con sus dominios chequeados en vivo.
>
> Tus tres decisiones: 1 (precio+Beats+puerta gratis) · 2 (language pack) · 3 (¿Sandi definitivo con getsandi.com / sandi.marketing, o exploramos?). Con las tres escribo la página única de Priya y cerramos Phase 1 completa.

**[OPERADOR — las correcciones del paso 4, literales]:**

> Sobre la tarjeta uno estoy de acuerdo en casi todo, ahora que lo pienso bien decir "Todo esto vale $333. Tu inversión: $30/mes." vamos a comparar con otras herramientas que las personas probablemente no van a conocer y va a ser como "no sé qué es esto, esto no es para mí" y se van — mejor usemos otra ancla.
> Sobre la tarjeta 2 todo me gusta, especialmente "frases que SÍ usa (de sus foros reales, 0.3)": me parece muy importante que usemos estas frases y esto como método estándar (buscar frases que se encontraron reales de los clientes durante el estudio de mercado para hablarles a ellos y atacar su punto de dolor).
> Otra cosa importante: necesitamos dejar marcado en la parte de los precios que tenemos que configurar toda la parte de los Beats y de los créditos — cargas, equivalencias, consumos, etc. — que realmente funcionen.
> Sobre el nombre, me gusta sandi.marketing / sandimarketing.com. La pregunta es: investiga competidores que correspondan al mismo nombre — yo identifiqué previamente 2. ¿No tendremos problemas legales por eso? Respóndeme después de investigar; dependiendo de eso exploramos.

### 🍉 Sandi — sim · Cierre de las tarjetas 1-2 y la respuesta del nombre

> Tarjeta 1, ancla nueva (tenías razón — propuesta v2, con el referente que Priya VIVE cada día):
>
> "Amazon se queda con $30-70 de cada $100 que vendes. Sandi cuesta $30 al mes — las comisiones de UNA sola venta — para construir el canal donde esa comisión te la quedas tú."
>
> Sin herramientas desconocidas: sus fees, su dolor literal ("the percentage they take"). Y de respaldo, el ROI simple: "una venta propia de $40 paga el mes." ¿Va?
>
> Tarjeta 2: firmada como método estándar — ya es regla del sistema, no estilo de esta oferta.
>
> Tarjeta 3 — La respuesta sobre el nombre, después de investigar. Encontré a tus dos… y más:
>
> | Quién | Qué es | Por qué importa |
> |---|---|---|
> | SANDI — Banco Santander | Registro US en clase 042: SaaS/PaaS de asistente personal + chatbot con lenguaje natural (campo: banca/finanzas), presentado 2020 + segunda solicitud 2024 | Un banco global posee "SANDI" registrado para un chatbot SaaS — nuestra forma exacta de producto, aunque su campo declarado sea finanzas |
> | SANDI — VORTO LLC | Registro US 2019, software descargable (logística) | Segunda marca viva "SANDI" en clase de software |
> | Sandy AI — Salesmate | Agente de ventas IA 24/7 | Homófono exacto, en software de ventas/CRM — nuestros propios compradores pueden conocerlo |
> | Sandi.app (NDIS) · Sandi health coach | Más asistentes IA llamados Sandi | El nombre está poblado justo en "asistente IA" |
>
> Mi lectura honesta (no soy abogada — esto es investigación, el veredicto legal es de un abogado pre-lanzamiento): el riesgo NO es trivial. Hay un registro vivo de clase software para un chatbot llamado SANDI en manos de un gigante, otro registro de software de 2019, y un gemelo fonético vendiéndole IA a dueños de negocio. Registrar "Sandi" para nuestro SaaS en US tiene probabilidad real de rechazo u oposición, y la confusión de mercado existe ya.
>
> Respuesta directa a tu pregunta: sí, podríamos tener problemas — y tu condición se cumple: exploramos.
>
> Arranqué la ronda 1 con datos (todo chequeado en vivo): el .ai de palabras simples está arrasado — pepita, mentora, sembra, cultiva, loopa, tendra, semora, audara, norra, steadi: tomados. Sobrevivieron: cultora.ai y seedra.ai ($160/2 años), más getsemora.com y getcultora.com ($11.25). De esos, te confieso: ninguno me enamora todavía — Cultora (la que cultiva audiencias) y Seedra (semilla → crecer, y las semillas son el alma de la sandía 🍉) son decentes, no definitivos.
>
> Para la ronda 2 necesito tu dirección — tres preguntas rápidas:
> 1. ¿Conservamos el guiño a la sandía (semilla/fruta/el 🍉 como identidad visual) o cortamos limpio?
> 2. ¿Nombre de persona-guía (el patrón Alexa/Siri que Sandi tenía) o palabra con significado (cultivar, sembrar, crecer)?
> 3. Dame 3-5 palabras o sensaciones que quieras que el nombre cargue (ej: "cercano, honesto, crece conmigo, no-corporativo").
>
> Con eso te traigo finalistas con dominio + screen de conflictos cada uno — y el que elijas pasa por abogado antes de comprometernos.

**[OPERADOR — la dirección del nombre, literal]:**

> Voy a arrojar ideas: la sandía me gusta porque tiene significado entre mi hija y yo, además me gusta lo de cultivar y crecer porque es lo que se hace en una empresa — se cultiva para que crezca. Mi hija me dice papaya, así que podemos hacer una combinación de esto. Pero como nuestro mercado principal es el mercado inglés debe ser fonéticamente fácil de recordar y entender — en mi caso personal, "Alfredo" nadie lo entiende, tengo que deletrearlo; pero "Alfred" todo el mundo lo entiende. Además preferiblemente que sea nombre de persona o que sea muy fácil y pegajoso. ¿Papandi? ¿Sapandi? O dejando de lado las frutas, ¿qué más se te ocurre?

### 🍉 Sandi — sim · Tu nombre estaba en tu casa

> Alfredo — repasemos lo que acabas de hacer sin darte cuenta: me diste el significado (tu hija y la sandía), el segundo significado (ella te dice papaya), el criterio técnico (la lección Alfredo→Alfred), dos logos ya dibujados… y el nombre. Yo solo lo verifiqué.
>
> Papandi — tu candidato — pasa TODO:
>
> | Criterio | Veredicto |
> |---|---|
> | El test Alfred (¿un americano lo dice a la primera?) | ✅ "pa-PAN-dee" — fonemas que cualquier angloparlante ya usa (panda, candy). Se escribe como suena. |
> | El test de la frase | ✅ "I use Papandi and my customers are steady now" — fluye. |
> | Pegajoso / nombre-apodo | ✅ Suena a apodo cariñoso — porque lo ES: papaya + sandía, los dos nombres de tu casa. Energía de personaje (el logo sonriente ya lo confirma). |
> | Significado | ✅ Las dos frutas de tu hija + se cultiva para que crezca — la historia real que ningún competidor puede copiar. |
> | Dominio | ✅ papandi.com ($11.25/año) Y papandi.ai ($160/2 años) — los dos libres. Primera vez en toda la exploración que el .com y el .ai del nombre raíz están disponibles. |
> | Conflictos | ✅ Cero resultados — ni empresa, ni marca, ni app llamada Papandi. Comparado con Sandi (un banco global con la marca registrada para un chatbot SaaS), es el escenario opuesto. |
>
> Tus otras dos, con honestidad: Sapandi la descartaría — "sap" en slang inglés significa tonto/ingenuo ("don't be a sap"); empezar así en mercado EN es regalarle el chiste al enemigo. Y Pandi (mi variante corta) es viable pero más débil: las raíces pandi.ai/getpandi.com están tomadas y "P&I" es jerga de seguros marítimos. La ruta sin frutas que pediste la exploré también (grova, ripely, pandia…) — todo tomado, y francamente ninguna carga la historia que Papandi trae gratis.
>
> Una pregunta delicada antes de cerrar, y es solo tuya: la historia del nombre — "así llama mi hija a las cosas que ama" — es oro puro para la marca (humana, imposible de copiar, exactamente lo no-corporativo que este mercado quemado necesita). Pero es TU familia. ¿La historia se hace pública como parte de la marca, o el nombre queda y la historia se queda en casa? Ambas funcionan — la marca con historia pública es más fuerte; tu privacidad manda.
>
> Si Papandi es el nombre, esto es lo que sigue (en orden):
> 1. Comprar papandi.com + papandi.ai HOY (~$172 total) — los dominios libres no esperan a nadie. La compra es tuya: te dejo los links listos o me autorizas y lo intento vía el MCP de Vercel.
> 2. Screen formal USPTO + abogado como gate pre-lanzamiento (queda como tarea — igual que habría sido con cualquier nombre).
> 3. name_status: working → final, D-037, rename de la marca en el producto (Sandi → Papandi: SOUL, wizard, todo — el personaje 🍉 sobrevive, ahora con papaya).
> 4. Escribo la página única de Priya con el nombre real → cierre del gate global G-Phase-1. Phase 1 completa.
>
> ¿Es Papandi?

**[OPERADOR]:** *"el nombre queda y la historia se queda en casa, y sí vamos por Papandi, y dale procede con la compra para papandi.com y la configuración"*

### 🍉 Sandi — PHASE 1 CERRADA 🎉

> Alfredo — mira lo que quedó en piedra hoy:
>
> La primera oferta completa del sistema existe. Papandi — The Marketplace Independence Plan: una ecuación que diagnosticó honesto (960, débil), un paquete que la arregló por diseño (1.440), dos candados económicos pasados con datos reales de TU producción, una garantía sin letra pequeña, una urgencia que se retira sola cuando deja de ser verdad, y una página de venta donde cada línea tiene firma tuya y fuente real.
>
> Y el producto tiene nombre. No uno cualquiera: el que acuñaste tú, de los nombres de tu casa, virgen en el mercado, con su dominio comprado, asignado y sirviendo producción — todo en una hora. "Sandi" cumplió su servicio como nombre de trabajo y se retira con honores (y con un banco global lejos de nuestros abogados).
>
> El marcador de la sesión 3: 9 decisiones (D-030 → D-038) · 8 artefactos firmados · 3 doctrinas tuyas ahora en el canon (la apertura de fase, nunca-un-número-sin-su-instrumento, el ancla con referentes vividos) · 1 módulo nuevo anclado (Admin & Cost Intelligence) · 1 spec validada contra corpus (el cabo suelto histórico, cerrado) · el modelo de costo con tu factura real ($1.06 la Fase 0) · los Beats bautizados por ti · y el pipeline sim-first validado por segunda vez.
>
> Lo que nos espera (el pipeline en su ritmo, un paso de desfase): Sim: Phase 2 — Contenido. El input ya está empacado: tu oferta firmada, las frases literales de Priya, el "replace don't add" como copy central, y las objeciones que el stack dejó declaradamente para el copy. Build (sandia): el step Oferta con los guiones que esta sim produjo + el rebrand Papandi + el hub del proyecto + el sistema de Beats — todo ya en tareas con dueño. Gates de lanzamiento (no bloquean nada): el screen legal de Papandi y, cuando quieras, la sesión del Módulo C.
>
> Phase 0 te dijo quién. Phase 1 te dijo qué y a cuánto. Phase 2 te dirá cómo se cuenta. Aquí te espero. 🍉

## Fase 2 · La apertura de fase

> 🍉 Sandi — sim · PHASE 2: Tu contenido 🎬
>
> La apertura, como manda nuestra regla:
>
> Phase 1 decidió QUÉ pones enfrente (tu oferta, su precio, su nombre: Papandi). Phase 2 responde cómo la cuentas: los temas que te hacen visible, los ganchos que detienen el scroll, y las piezas concretas por canal — en el idioma de cada público, no en el del producto. Por qué importa: el contenido no inventa la promesa, la traduce; aquí se fabrica todo el material que después se publica. Una oferta fuerte mal contada se queda invisible.
>
> El gate de entrada pasó — 13 de 13 checks aplicables ✅: tu oferta firmada con su paquete y garantía, el idioma de Priya listo, las fuerzas cubiertas vs las delegadas al copy, tu estrategia anclada. Una nota honesta: tu Fase 0 declaró el canal como "solo online" (ámbito, no lista) — los canales concretos los elegiremos en el paso 3 desde los hábitos reales de Priya (Reddit, foros de sellers, búsqueda). Y la distribución de conciencia de tu mercado quedó en: 50% sabe que tiene un problema, 20% busca solución, 5% te buscaría directo, 25% ni sabe — esto gobierna el paso 2.
>
> El mapa de esta fase — 6 paradas: declarar tu voz → repartir el esfuerzo por nivel de conciencia → matriz canal×momento → 4 pilares (uno por fuerza psicológica) → atomizar → biblioteca de ganchos.

## Fase 2 · Paso 1 de 6 — Tu voz de marca

> Qué es, primero: la voz de marca es cómo SUENA Papandi en todo lo que publica — la personalidad hecha palabras. Se declara antes de producir una sola pieza, porque si no, cada post sale con una personalidad distinta y el cliente percibe ruido (es el paralelo exacto de tu garantía: identidad no se automatiza). Un arquetipo es un molde de personalidad reconocible — hay 12 clásicos (el sabio, el héroe, el cuidador, el rebelde…) — y sirve para que cientos de piezas futuras suenen a UNA voz.
>
> Mi propuesta (anclada en los trabajos emocional y social de tu persona, como exige la regla — tú dispones):
>
> **Tarjeta 1 — El arquetipo:** Sabio + Cuidador — "el mentor que se queda". Por qué: el trabajo emocional firmado de tu persona es "dejar de sentir que el negocio depende de la suerte" — y la salida de la suerte es ENTENDER: glass-box, enseña-mientras-hace = sabio. Y el social es "ser visto como negocio serio, no hobby" — el sabio da seriedad sin corbata. El cuidador entra porque tu avatar llega quemado y con miedo: la voz acompaña, nunca lecturea. Compatible con el registro profesional de Priya, cero conflictos.
>
> **Tarjeta 2 — La promesa central** (una frase que ancla todo): "Ayudo a los expertos en lo suyo que ya venden a conseguir clientes constantes por canales propios, vía un plan guiado semana a semana que enseña haciendo, sin volverse marketeros de tiempo completo y sin humo."
>
> **Tarjeta 3 — El tono y el diccionario.** 5 descriptores: directo y llano · cálido sin azúcar · datos sobre promesas · honesto hasta la incomodidad · corto y escaneable. Siempre decimos: "tu canal propio", "tu cliente, no el de la plataforma", "te muestro de dónde sale", "medido en ventas, no en likes". Prohibido para siempre: revolucionario/increíble/único, guru/secret/hack/blueprint, ingresos pasivos, "herramienta de IA" (regla D-028), viral, 10x, "fácil y rápido". Ejemplo del espíritu: decimos "una venta propia de $40 paga el mes" — jamás "ROI increíble garantizado".
>
> **Tarjeta 4 — 5 reglas de consistencia testeables** (cada pieza futura se chequea contra ellas): cero prohibidos · ≥1 término preferido · máximo un "!" · todo número lleva fuente · titulares ≤12 palabras.
>
> Borrador completo en brand_voice.json. ¿Firmas la voz (puede ser "2.0 ok") o ajustas alguna tarjeta? Con tu firma pasamos al reparto del esfuerzo — donde tu 50% de "sabe que tiene un problema" se convierte en estrategia.

### 🍉 Sandi — sim · La promesa, reescrita con tu frase — [tras corrección del operador]

> Tu corrección era la pieza que faltaba — la quote del foro es ORO porque es el confidence-gap exacto de tu persona ("soy experto en lo que hago, no en buscar clientes", research 0.3). La Tarjeta 2 quedó así:
>
> La promesa pública (la frase de la voz): **"Eres experto en lo tuyo, no en buscar clientes. Para eso estoy yo: te guío, paso a paso, sin humo."**
>
> El ancla interna (formato completo): "Ayudo a los expertos en lo suyo a conseguir clientes constantes — yo guío el marketing paso a paso mientras ellos se enfocan en lo que saben hacer — sin volverse marketeros de tiempo completo y sin humo."
>
> Dos detalles del oficio que cuidé al reescribirla: dice "te guío" (no "yo me encargo") — porque tu alcance firmado es guía con borradores, no hacerlo-todo, y prometer de más sería el humo que prohibimos; y la tensión tú-en-lo-tuyo / yo-con-los-clientes entró también al diccionario como término preferido — va a reaparecer en ganchos y copy.
>
> Con tus tarjetas 1, 3 y 4 ya aprobadas ("de resto todo perfecto"), G-Phase-2.0 queda a una palabra: ¿firmas la voz con esta promesa?

## Fase 2 · Paso 2 de 6 — El reparto del esfuerzo

*(Este es el "mensaje 1000 de 10" — ya formalizado como variante A en `cag_step_beat_canonical.md`. Se preserva aquí en su contexto.)*

> El instrumento primero (nunca un número antes que su regla):
>
> Cuando alguien se cruza con tu contenido, está en uno de 4 momentos mentales: 😴 No sabe que le duele — vive las fees como "el costo de vender". 😣 Sabe que duele, no que hay salida — odia las comisiones, cree que "así es esto". 🔍 Compara salidas — ya busca "how to sell off Amazon". 🎯 Busca esto exacto — quiere el plan, hoy.
>
> Tu Fase 0 midió dónde está tu mercado: 25% dormido · 50% sabe que duele · 20% comparando · 5% buscando exacto. Y la regla clave: el reparto del contenido NO copia esa foto — depende de tu estrategia. Tu cuña firmada es EDUCAR (crear demanda): el grueso va a despertar al que sabe que duele. Pero cada momento pide contenido distinto — no le vendes al dormido, ni le explicas qué es una fee al que ya compara planes.
>
> Mi propuesta de reparto para la estrategia de Priya — con un ajuste glass-box: su demanda es mixta (lo firmaste): cuando Amazon sube fees, ella no necesita educación — busca con palabras exactas. Ese intent se captura, no se despierta. Por eso subo la captura sobre la receta base de educación:
>
> | Momento mental | Mercado (foto) | Tu contenido | Por qué |
> |---|---|---|---|
> | 🎯 Busca esto exacto | 5% | 15% | Las ventanas de rabia (fee hikes, suspensiones) tienen búsqueda exacta — se capturan |
> | 🔍 Compara salidas | 20% | 30% | Priya es más consciente que el mercado promedio (lo firmamos) |
> | 😣 Sabe que duele | 50% | 40% | Sigue siendo el grueso: el playbook de independencia ES la educación — tu cuña |
> | 😴 Dormido | 25% | 15% | La pista de prospectos nuevos (la regla prohíbe dejarla en 0 cuando tu estrategia es crear demanda) |
>
> Chequeos del candado, a la vista: los 4 números suman 100 ✓ · los 4 caen dentro de las bandas permitidas de tu estrategia ✓ · la desviación máxima vs la foto del mercado es 10 puntos (el límite que exigiría justificación firmada es 30) ✓ — la alarma no dispara.
>
> En cristiano: de cada 10 piezas que produzcamos, 4 educan al que sufre fees, 3 le hablan al que compara, 1.5 capturan al que busca YA, y 1.5 siembran en los dormidos.
>
> ¿Firmas el reparto 15/30/40/15? (puede ser "2.1 ok" o ajusta cualquier número — si te alejas >30 puntos de la foto, el sistema te pedirá la justificación por diseño). Con tu firma pasamos al paso 3: la matriz canal×momento — donde por fin decidimos DÓNDE vive cada pieza.

## Fase 2 · Paso 3 de 6 — Dónde vive cada pieza (la matriz, con DOS correcciones del operador)

> El instrumento primero: cada canal tiene UNA función — y el error clásico del marketing casero es ignorarla: publicar "en todos lados lo mismo" y terminar con el canal de despertar pidiendo la venta y el canal de venta educando. La matriz cruza tres cosas: el canal (dónde), el momento del viaje de tu clienta (recién despierta → compara → decide → se queda → recomienda) y el momento mental que ya repartimos. Cada cruce dice qué se publica, cada cuánto, y cómo se mide.
>
> El dato propio que manda aquí: tu investigación firmada dice, literal, dónde vive Priya: "tras una subida de fees o un susto de suspensión; buscando 'how to sell off Amazon build own audience'; foros de sellers." Los canales los eligen los hábitos de tu clienta, no la moda.
>
> [Propuesta v1: 4 canales (Blog/SEO, Foros, Email, Búsqueda pagada) + 3 descartes con nombre — YouTube (producción), Instagram/TikTok/Pinterest ("ahí viven los CLIENTES de Priya, no Priya"), LinkedIn (parqueado).]

**[OPERADOR — la corrección de las grandes superficies, literal]:**

> Nuevamente todo me encanta y quiero conservar el tipo de interacción, pero en este momento estoy en desacuerdo con las redes como Instagram y TikTok. El poder de estas redes —y aplica para todo— es que aquí vive todo: todos los mercados, todos los humanos. Fui a Guatemala y gente vendiendo en el piso en la calle llaveros estaba en TikTok, y grandes empresas están ahí, todo. Podemos potenciar en Blog/SEO, foros, email, pero no podemos dejar de lado las grandes superficies. 100% seguro: si lo focalizas adecuadamente encuentras tu público, y no puedo imaginar un mercado que no lo sea. Así que a menos que tengas un caso específico de cuándo no usar estas grandes redes, debe ser regla que estén (tratando de pensar en algo que no… incluso una casa para ancianos debe estar ahí — no por los ancianos sino por los hijos o nietos que la encontrarán).

> 🍉 Alfredo — tienes razón, y tu argumento me corrige algo importante. Déjame hacer el glass-box de mi error, porque tiene dos capas: mezclé "dónde está la atención de Priya" con "qué podemos producir". Tu punto de Guatemala y el asilo es exactamente el poder de estas redes: son grandes superficies de atención general — el algoritmo de intereses encuentra a tu público si el contenido habla su lengua. Y la prueba más irónica estaba en nuestro propio research: los gurús que quemaron a Priya construyeron sus imperios EN TikTok e Instagram — su atención ahí está más que validada; es donde nuestra voz sin-humo destaca por contraste. Mi objeción real era de producción (video para un operador solo), y eso se resuelve degradando el formato, no excluyendo el canal. Lo convierto en regla del sistema como pides.

### 🍉 Sandi — sim · La matriz, corregida por ti

> Tu regla ya es ley del sistema: las grandes superficies entran por defecto; excluirlas exige caso escrito. Y me corregiste algo más fino que un canal — me enseñaste a separar dos preguntas que yo mezclé: "¿está mi público ahí?" (casi siempre SÍ — tu asilo encontrado por los nietos) y "¿puedo producir para ahí?" (si no alcanza, se degrada el formato, no se excluye el canal). Esa válvula quedó escrita.
>
> La matriz enmendada — 5 canales:
>
> | Canal | Momento | Qué se publica | Ritmo | Cómo se mide |
> |---|---|---|---|---|
> | 📝 Blog/SEO | despierta → compara → decide | 1 guía semanal + landing evergreen por ventana de rabia | 1/sem | visitas, posición, signups |
> | 📱 Instagram/TikTok ← TU CORRECCIÓN | sembrar + despertar | carruseles educativos de texto + quote cards desde plantilla — Papandi genera el texto completo; producirlos toma minutos, no edición de video. Los guiones de reel quedan listos para activar video después | 2/sem | guardados y compartidos |
> | 💬 Foros de sellers | despertar | participación valor-primero, cero pitch | 2/sem | respuestas/menciones |
> | ✉️ Email | decide + se queda | bienvenida desde puerta gratis + nota semanal | 1/sem | apertura → clics |
> | 🎯 Búsqueda pagada | decide | solo en ventana de rabia → en pausa hasta post-beta | por ventana | costo por signup |
>
> Y nota la jugada que tu corrección habilitó: el 15% de contenido para "dormidos" que firmaste en el reparto no tenía motor real (solo foros — débil). Instagram/TikTok ES el motor nativo de despertar dormidos. Tu regla cerró un hueco que yo había dejado. Además: ese canal es el territorio de los gurús que quemaron a Priya — ahí nuestra voz sin-humo no es solo ética, es diferenciación visual inmediata.
>
> Los 3 que quedan fuera, ahora cada uno con su caso escrito (como exige tu regla): Pinterest — la superficie del comprador de Priya, no de Priya… aunque apunta esto: cuando PRIYA use Papandi para SU negocio de decoración, Pinterest será core en SU matriz — el caso es por producto, nunca doctrina · YouTube — degradado, no excluido: guiones listos para activar · LinkedIn — tu puerta de empresas, parqueada como decidiste.
>
> Candados re-chequeados: 5 momentos del viaje cubiertos ✓ · cada fila con métrica ✓ · carga ~6 acciones/semana, todas con borrador o plantilla hechos — y la válvula: si aprieta, social baja a 1/sem antes que salir de la matriz ✓.
>
> En cristiano: tu semana es 1 guía + 2 carruseles + 2 manos en foros + 1 email. Y cuando Amazon anuncie fees, la landing espera lista.

**[OPERADOR — la cazada de las cadencias, literal]:**

> Algo aquí no está bien: que me digas que cada dos semanas un post de Insta/TikTok no está bien — cada dos semanas para cualquier cosa es demasiado, especialmente para Insta o TikTok. Busca en el corpus si tenemos algo al respecto y busca a profundidad en internet información muy detallada sobre esto: cómo manejar las redes sociales, cada cuánto postear, cada cuánto hacer las cosas, a qué horas, en qué días, etc. Además esto debe ser un trigger de notificaciones: "recuerda postear, aquí está el contenido, el copy del contenido".

> 🍉 Cazaste dos cosas: mi notación ambigua ("2/sem" quise decir 2 por semana, no cada dos semanas — culpa mía, desde ya escribo "por semana") — y aun así tu instinto manda: para IG/TikTok incluso 2/semana puede ser poco. Voy a hacer lo que pides en orden: corpus primero, internet a profundidad después, y el trigger de notificaciones queda capturado como requisito del producto.

### 🍉 Sandi — sim · Cadencias corregidas: tu instinto + los datos — [la variante B canónica]

> Doble cazada tuya: mi notación era ambigua (era "2 por semana" — desde ya las cadencias se escriben completas, quedó como regla) — y aun así el número era bajo. Lo confirmaron el corpus Y los estudios:
>
> Lo que dice tu propio corpus (curso de RRSS): no trae números de cadencia, pero trae la regla que te da la razón — 7-11-4: para que alguien confíe y compre necesita ~7 horas de exposición, 11 interacciones y 4 impactos directos en su dolor. Eso no se logra con 2 posts por semana. La confianza exige presencia.
>
> Lo que dicen los estudios 2026 (Buffer analizó 11M+ posts de TikTok; Sprout ~2 mil millones de interacciones):
>
> | Canal | Piso de lanzamiento | Meta al rodar | Mejores ventanas (hora LOCAL de tu audiencia) |
> |---|---|---|---|
> | 📱 TikTok | 3-5 por semana | 1 al día (2-5/sem da +17% views por post; 11+/sem +34%; ojo: >5 al DÍA penaliza — riesgo de shadowban) | mar-vie 14-18h · sábado es el mejor día (hallazgo Buffer) |
> | 📱 Instagram | 3 feed por semana + stories ligeras diarias (repost del carrusel: ~30 seg) | 4-5 feed + Reels cuando activemos video | mar 13-19h · mié 12-21h (mejor hora única: mié 11am) · fines de semana NO (los más débiles) |
> | 💬 Foros | 2-3 por semana | escucha diaria ligera | la ventana es del hilo caliente, no del reloj |
> | ✉️ Email | 1 por semana — mismo día, misma hora (el hábito es del lector) | + secuencias automáticas | mar-jue mañana; tu apertura calibra |
> | 📝 Blog | 1 por semana | 1-2 | evergreen — resultados SEO reales en 3-6 meses de constancia |
>
> La jugada que hace esto viable para una persona: el MISMO carrusel se publica como slideshow de TikTok Y carrusel de Instagram — 3 piezas alimentan las dos redes. Carga total del piso: ~8-10 acciones/semana, y es honesta SOLO porque cada pieza te llega LISTA (carrusel desde plantilla = minutos). La escalera sube cuando el flujo ruede, y tus propios datos (fase de medición) calibran estos defaults — son promedios de estudios, tu público manda al final.
>
> Y tu mandato del trigger quedó capturado como requisito del producto: cada slot del calendario te notifica con el copy listo adentro — "toca postear: aquí está el contenido" — y al marcar "publicado", la medición sabe qué salió y cuándo. Nace con el build de la fase de publicación (tarea registrada, alta prioridad).
>
> En cristiano: tu semana es 3 carruseles que sirven a 2 redes + stories de 30 segundos + 1 guía + 2 manos en foros + 1 email — todo te llega hecho, y el sistema te avisa cuándo soltarlo y a qué hora.
>
> ¿Validas la matriz con estas cadencias? ("2.2 ok"). [Fuentes linkeadas al pie: Buffer TikTok 11M · Buffer mejores horas · Sprout Social 2026 · Sprout Instagram · JoinBrands · PostEverywhere · Reddit small-biz · Firstep]

**[OPERADOR]:** *"Perfecto, también guarda el formato de respuesta"* → la variante B quedó LOCKED en `cag_step_beat_canonical.md`.

## Fase 2 · Paso 4 de 6 — Los 4 pilares (la joya de esta fase)

> El instrumento primero: un pilar es un territorio de contenido — de qué habla todo tu volumen. El error clásico es organizarlos por tema o canal ("el blog", "los reels"): eso produce contenido, no estrategia. Nuestro método los organiza por fuerza psicológica: las 4 palancas que ya mapeaste para Priya en tu Fundación — sus dolores crónicos, sus momentos de rabia, sus miedos y sus hábitos. Así NINGUNA palanca queda sin contenido, y cada pieza sabe exactamente qué músculo empuja.
>
> Y hay una distinción fina que heredamos de tu oferta firmada — cada pilar trabaja en uno de dos modos:
> - REFORZAR: la fuerza YA la cubre tu paquete (la garantía ataca el miedo al humo) → el contenido amplifica las palabras exactas de tu oferta, no inventa narrativa paralela.
> - RESOLVER: tu oferta la delegó explícitamente al copy (la objeción "otra suscripción más") → el contenido es el ÚNICO que la ataca.
>
> Sin esta distinción pasan dos accidentes: piezas duplicadas que repiten lo que la oferta ya dice, o peor — un mensaje DISTINTO al de la oferta (disonancia que el cliente huele).
>
> Mis 4 pilares para Priya (cada uno con su fuerza, su modo y sus canales):
>
> | Pilar | Fuerza | Modo | De qué habla | Canales |
> |---|---|---|---|---|
> | 🧮 "La matemática de la jaula" | dolores crónicos (fees, dependencia) | resolver | el costo real de vender en Amazon, con números y fuentes — el contenido evergreen que captura su búsqueda crónica | blog/SEO + carruseles |
> | ⚡ "Ventanas de rabia" | disparadores (fee hike, suspensión, Q4) | reforzar (tu urgencia honesta) | respuesta RÁPIDA cuando Amazon anuncia algo: qué significa, qué hacer — la landing esperando + carrusel del momento | landing evergreen + social + foros calientes |
> | 🛡️ "Prueba, no promesas" | miedos | mixto: reforzar (humo→garantía e hito, con las palabras LITERALES de tu oferta) + resolver ("¿podré sola?" → behind-the-scenes del acompañamiento; "otra suscripción" → una venta de $40 paga el mes) | email + carruseles + foros |
> | 🔄 "Reemplaza, no agregues" | hábitos (la jaula cómoda) | reforzar — hereda LITERAL tu displacement: "las horas que le regalas al algoritmo" y el costo de seguir igual | comparativos SEO + carruseles + email |
>
> Candados a la vista: 4 fuerzas, 4 pilares — ninguna palanca huérfana ✓ · cada elemento ya-cubierto-por-tu-oferta usa las palabras de la oferta (cero disonancia) ✓ · cada delegado-al-copy tiene dueño ✓ · todos alimentan el multiplicador ✓.
>
> En cristiano: tu blog explica la mate, tu social aprovecha la rabia del momento, tu email demuestra con pruebas, y todo junto le susurra "reemplaza, no agregues".
>
> ¿Firmas los 4 pilares? ("2.3 ok" o ajusta nombres/énfasis).

**[OPERADOR]:** *"Firmo. Además me gusta mucho toda la explicación, debemos mantenerla [el instrumento + REFORZAR/RESOLVER, literal al canon]. Recuerda que debes blindar para que tengamos la misma calidad agnóstico al LLM que usemos — quiero entender cómo estás haciendo eso y cómo lo has estado haciendo en todas las fases anteriores y lo seguirás haciendo."* → nació `quality_armor_model_agnostic.md`.

## Fase 2 · Paso 5 de 6 — La multiplicación

> Los dos instrumentos de este paso, primero:
>
> La atomización: cada pilar produce 1 pieza larga (el ancla — donde vive la sustancia) y de ella salen mínimo 5 derivados (carruseles, email, respuestas de foro, quote cards). Por qué existe: sin esto, cada pieza se crea desde cero, el costo por pieza mata el plan en la semana 3, y abandonas. Con esto, un esfuerzo alimenta la semana entera. (El modelo original convierte 1 conferencia en 64 piezas; nuestro piso honesto es 1→6.)
>
> El ratio dar:pedir (la regla de oro del contenido): cuentas las piezas que DAN valor vs las que PIDEN algo. El default del oficio es 3:1 — tres regalos por cada pedido. Para TU caso lo subo a 5:1 en Instagram/TikTok: tu clienta viene quemada por gurús que solo piden — ser el que DA es diferenciación visual inmediata. En email (ya te dieron su correo: audiencia caliente) basta 2:1. Y esto no es dogma: la fatiga real medida en la fase 5 lo recalibra.
>
> El mapa (atomization_map.json) — una pieza ancla por pilar, cada una con sus 6 derivados:
>
> | Pilar | Pieza ancla (EN, el idioma de Priya) | Derivados |
> |---|---|---|
> | 🧮 Matemática | "The Real Math of Selling on Amazon: Where Your $100 Actually Goes" (~1.600 palabras, SEO) | carrusel IG + slideshow TikTok + email + respuesta de foro + quote card + stories |
> | ⚡ Ventanas | "Amazon Changed the Rules Again? Your 7-Day Response Plan" (landing que ESPERA el anuncio) | árbol se instancia POR EVENTO — el protocolo manda sobre el calendario |
> | 🛡️ Prueba | "We Tried It On Ourselves First: The Papandi Working Case" (tu run fundacional como prueba pública — con lo que salió mal incluido) | 6 derivados; hogar del re-impacto a no-convertidores |
> | 🔄 Reemplazo | "One More Year of Fees vs. One Year of Building Your Own Channel" (apunta a SU búsqueda literal) | 6 derivados; tu frase de displacement aparece TEXTUAL (regla del sistema) |
>
> Mira el detalle del primer árbol — hasta los asuntos del email vienen especificados (5 variantes ≤40 caracteres, par A/B elegido: "Where your $100 actually goes" vs "The math Amazon hopes you skip") — porque el asunto ES el gancho del canal email y decide la apertura.
>
> Candados a la vista: 1 ancla + 6 derivados por pilar (piso pide 5) ✓ · ratio del ciclo en redes: 5 valor : 1 pedido ✓ · email 4:1 sobre objetivo 2:1 ✓ · ningún derivado asume un momento mental superior al de su ancla ✓ · la sustitución de formatos (sin video V1: slideshow en vez de short) documentada con caso ✓.
>
> En cristiano: escribes — bueno, APRUEBAS, porque te llega hecha — una pieza larga por semana, y de ella salen tus 3 carruseles, tu email, tu respuesta de foro y tus stories. La semana entera, de un solo esfuerzo.
>
> ¿Firmas el mapa? ("2.4 ok"). Tras tu firma: produzco la prosa real de la pieza 1 completa — y cerramos la fase con el paso 6.

### 🍉 Sandi — sim · La pieza 1, producida

> El artículo completo (~1.310 palabras, EN) — pruébalo con el lead:
>
> *You sold $100 yesterday. How much of it is actually yours? Most sellers answer with their product margin. Almost nobody answers with the real number — because the real number hides across four different fees, two dashboards, and an ad bill that grows every quarter. Let's do the math together, slowly, with sources. No drama, no smoke.*
>
> La estructura entrega exactamente lo que el pilar promete: los 4 peajes con fuente → la tabla ($100 → te llegan $46-63 antes de fabricar nada) → el quinto costo que nadie factura ("the customer isn't yours... that feeling is not anxiety. It's an accurate read of the architecture") → y el giro honesto que nos diferencia de todos los gurús: "the answer is NOT quit Amazon" + la columna de los $97 + la verdad del costo propio ("8-12 weeks of runway... anyone who tells you otherwise is selling something") → cierre suave a la puerta gratis.
>
> El árbol de 6 derivados — destacados: Carrusel (IG + TikTok, misma pieza): 6 slides que cuentan la tabla — cierre sin CTA (es pieza de DAR). Email: par A/B listo con pre-header y cuerpo de 110 palabras. Respuesta de foro: la mate en 5 líneas, cero pitch, cero links. Quote card: "Of every $100 you sell on Amazon, $37–$54 is rent." — con fuente al pie. Stories: 3 frames con encuesta y pregunta — que además ESCUCHAN (alimentan hooks futuros).
>
> Candados pasados, a la vista: las 5 reglas de tu voz ✓ (cero prohibidos · preferidos presentes · un solo "!" en todo el paquete · cada número con fuente · título de 12 palabras) · anti-duplicación ✓ (el artículo NO usa tu frase de displacement — esa es del pilar 4, cada pilar su territorio) · ratio ✓ (5 de los 6 derivados son puro DAR).
>
> En cristiano: esto es lo que Papandi le entregará a Priya cada semana — una pieza con sustancia y fuentes, y su semana entera de redes, email y foros saliendo de ella. Lista para aprobar, no para redactar.

**[OPERADOR]:** *"Perfecto, solo recuerda que Instagram puede ser imágenes pero TikTok es video shorts, por eso debemos separarlos: un entregable es copy de imágenes con texto, otro de videos shorts."*

> 🍉 Cazada correcta — la naturaleza de cada red manda sobre la comodidad del multiplicador: Instagram = imágenes con texto (copy de slides), TikTok = video short (guion con estructura). La misma pieza ancla alimenta a ambos, pero son DOS entregables distintos. Y nota la elegancia: el guion de video ES texto — entra en nuestro alcance (Papandi entrega el guion listo con tomas y subtítulos; grabar son 5 minutos con green-screen o text-overlay).
>
> El guion real de la pieza 1 (~40 segundos, estructura del método: gancho 3-5s → cuerpo con micro-ganchos → cierre suave):
>
> *0-4s · HOOK — "You sold $100 on Amazon yesterday. Want to see how much is actually yours?" — en pantalla: "$100" gigante.*
> *4-12s — "Four fees nobody adds up for you. Referral: fifteen, right off the top." — los números van apilando.*
> *12-25s · micro-gancho — "Fulfillment? Five to nine more. And here's the one that surprises everyone — ads. Fifteen to twenty-five, just to stay visible."*
> *25-34s — "Storage and returns take the rest. You keep forty-six to sixty-three. Before making the product." — fuentes en pantalla.*
> *34-42s · cierre — "On your own channel, that same sale keeps about ninety-seven — and the customer stays yours. Keep Amazon. Build yours next to it." — $46 vs $97 lado a lado. Sin CTA dura: pieza de DAR.*

## Fase 2 · Paso 6 de 6 — La biblioteca de ganchos

> El instrumento: un gancho son las primeras 1-3 frases (o los primeros 3 segundos) de cualquier pieza — y decide TODO: ahí se gana o se pierde la mayoría de las impresiones. Sin biblioteca, cada pieza nueva reinventa su primer segundo; con ella, cada carrusel, email o guion agarra su gancho del estante — pre-filtrado, y con memoria de rendimiento. Los ganchos se construyen sobre plantillas probadas del oficio (problema-agita-resuelve, contrario, "la mayoría cree que…", brecha de curiosidad…) — el gate exige variedad para no sonar a disco rayado.
>
> Tu biblioteca: 40 ganchos — 10 por pilar, 8 plantillas, en el idioma de Priya. Prueba el sabor:
>
> | Pilar | Muestra |
> |---|---|
> | 🧮 | "There's a fifth Amazon fee. It never shows up on an invoice." · "Your ad budget isn't growing your business. It's paying your landlord." |
> | ⚡ | "The fee hike isn't your problem. Having only one landlord is." · "Suspended sellers don't get a warning. They get an email." |
> | 🛡️ | "Don't trust us. Track us — every number we publish cites its source." · "You're an expert at what you do — not at finding clients. That division of labor is the plan." ← tu frase del foro, ahora gancho |
> | 🔄 | "Staying on Amazon isn't the safe choice. Staying ONLY on Amazon is the risky one." · "Serious businesses own their customer list. Hobbies rent theirs." ← del social_job literal |
>
> Candados a la vista: 10 por pilar (pide ≥10) ✓ · 8 plantillas distintas (pide ≥4) ✓ · 40/40 pasan tu voz — cero términos prohibidos, números con fuente ✓ · 40/40 a salvo de anti-personas — cero promesas rápidas o garantizadas: justo el territorio donde los gurús pescan, filtrado doble ✓ · los 4 que ya viven en tu pieza 1 están marcados "en uso, sin testear" — la fase de medición les pondrá nota y los perdedores se retiran ✓.
>
> En cristiano: nunca más una pieza empezando de cero. Y la biblioteca aprende — los ganchos ganadores se quedan, los que no convierten se jubilan con datos, no con opiniones.
>
> ¿Firmas la biblioteca? ("2.5 ok"). Es la última firma de sub-paso — con ella consolido el plan de contenido completo y te presento el gate global de la Fase 2 para tu firma de cierre. 🏁

**[OPERADOR — el cierre]:** *"Perfecto, me encanta, amo lo que estamos construyendo. Insisto: recuerda que este mismo sentimiento es el que deben tener todos los usuarios gracias a la calidad. También me gusta ver los 40 ganchos pero al usuario no se los debemos presentar como JSON — genera una forma de presentarlo, puede ser como en otra ventana o algo así, ingéniate algo para eso."* → la estantería de ganchos (visor M6c) + la regla ningún-artefacto-como-JSON.
