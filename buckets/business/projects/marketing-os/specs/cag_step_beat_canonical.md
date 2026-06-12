# CAG — El beat de paso canónico ("el mensaje 1000 de 10")

**Status:** ejemplo de referencia LOCKED (operador, 2026-06-12: "esto es lo que quiero replicar exactamente — que en cada una de las partes pase esto: analice lo que ha pasado y entregue esto").
**Uso:** ejemplo CAG para el prompt de TODO renderer de paso del wizard (patrón B1 guion+LLM). Cuando un paso presenta una propuesta sobre datos del proyecto, su salida debe seguir esta anatomía. Origen: paso 2.1 (content mix) de la sim fundacional — el mensaje que el operador calificó "1000 de 10".

---

## La anatomía (8 movimientos, en orden)

1. **El instrumento primero, en llano.** Antes de cualquier número: qué mide este paso, con los estados/niveles traducidos a lenguaje de humano (emoji + frase vivida: "😣 sabe que duele, no que hay salida" — nunca "Problem Aware" a secas en el cuerpo; el término técnico puede ir entre paréntesis o en el panel).
2. **El dato PROPIO del usuario, citado.** "Tu Fase 0 **midió**: 25 · 50 · 20 · 5" — su proyecto, su medición, no un benchmark genérico. El usuario reconoce SU trabajo previo alimentando este paso (inversión visible).
3. **La regla del paso + su porqué.** La no-obviedad que evita el error clásico: "el reparto NO copia esa foto — depende de tu estrategia". Una frase de por qué.
4. **La propuesta con desviación glass-box.** Si la propuesta se aparta de la receta base, decir EXACTAMENTE por qué, anclado a algo que el usuario YA firmó: "tu demanda es mixta — **como ya firmaste** — y ese intent se captura, no se despierta".
5. **Tabla foto-vs-propuesta con porqué por fila.** Columnas: estado en llano · su dato medido · la propuesta · el porqué de UNA línea. Sin filas huérfanas de razón.
6. **Los candados a la vista.** Cada chequeo del gate, en línea y con su margen: "suma 100 ✓ · bandas ✓ · desviación máx 10 (el límite que exigiría justificación es 30) ✓ — la alarma no dispara". El usuario ve cuánto espacio le queda ANTES de tocar nada.
7. **La traducción "en cristiano".** UNA línea memorable que convierte los porcentajes en algo físico: "de cada 10 piezas, 4 educan al que sufre fees, 3 le hablan al que compara, 1.5 capturan al que busca YA, 1.5 siembran en los dormidos."
8. **El ask con autonomía + guardarraíl visible.** Firma fácil ("puede ser '2.1 ok'") + libertad de ajustar + qué pasará si se sale del riel ("si te alejas >30 puntos, el sistema te pedirá la justificación — por diseño"). Y el puente: qué desbloquea el siguiente paso.

## Reglas de capa (USER-CORRECTED)

- **NUNCA códigos de decisión (D-xxx) en capa usuario.** Se dice "como ya firmaste" / "tu decisión de [paso]"; la referencia exacta y trazable vive en el panel ("Tus decisiones") y en el registro — no en el beat. (Corrección literal del operador: "solo recuerda no incluir D-032".)
- Nombres de señal/alarma (CONTENT-004): en el beat se describen en llano ("el sistema te pedirá justificación"); el código puede vivir en el panel para el curioso. *(Inferencia de la doctrina de capas — el operador no lo corrigió explícitamente.)*
- Los términos técnicos del oficio (awareness, etc.) pueden aparecer UNA vez entre paréntesis como educación; jamás como vocabulario portador.

## Variante B — El beat de corrección con research (LOCKED 2026-06-12, mismo mandato)

Cuando el usuario objeta un dato/propuesta y pide investigación, el beat cambia de anatomía (origen: la ronda de cadencias de 2.2, también calificada "Perfecto" + "guarda el formato"):

1. **Reconocer la cazada, decompuesta.** Si hubo error propio, separar SUS capas glass-box ("mi notación era ambigua Y el número era bajo igual") — nunca defensiva, nunca auto-flagelación.
2. **El corpus/lo propio PRIMERO.** Buscar en las fuentes del proyecto antes que en internet, y reportar honesto qué hay y qué falta ("tu corpus no trae números, pero trae la regla que te da la razón: 7-11-4").
3. **Los estudios con cifras y escala.** Investigación externa con magnitudes que dan autoridad ("Buffer analizó 11M+ posts; Sprout ~2 mil millones de interacciones") — nunca "los expertos dicen".
4. **Tabla operativa con matices.** Piso → meta → techo/alerta → ventanas. Los datos contradictorios se muestran, no se esconden ("sábado mejor día en TikTok, pero findes débiles en IG").
5. **La jugada de eficiencia.** Cómo el sistema hace viable el número para ESTE usuario ("el mismo carrusel sirve 2 redes; te llega hecho").
6. **El mandato del usuario capturado como requisito.** Si pidió una capacidad ("que sea trigger de notificaciones"), confirmarla convertida en tarea/spec con su esencia citada.
7. **En cristiano + ask** (igual que la variante A).
8. **Fuentes al pie, linkeadas.** Toda cifra externa con su link — el research sin fuentes es opinión.

## El ejemplo íntegro (limpio de capa usuario)

> **El instrumento primero:** cuando alguien se cruza con tu contenido, está en uno de 4 momentos mentales: 😴 no sabe que le duele · 😣 sabe que duele, no que hay salida · 🔍 compara salidas · 🎯 busca esto exacto, hoy.
> Tu investigación **midió** dónde está tu mercado: 25% dormido · 50% sabe que duele · 20% comparando · 5% buscando exacto. Y la regla clave: **el reparto del contenido NO copia esa foto** — depende de tu estrategia. Tu cuña firmada es EDUCAR: el grueso va a despertar al que sabe que duele. Pero cada momento pide contenido distinto — no le vendes al dormido, ni le explicas qué es una fee al que ya compara.
>
> **Mi propuesta** — con un ajuste glass-box: tu demanda es mixta (como ya firmaste): cuando Amazon sube fees, tu clienta no necesita educación — **busca con palabras exactas**. Ese intent se captura, no se despierta. Por eso subo la captura sobre la receta base:
>
> | Momento mental | Mercado (foto) | Tu contenido | Por qué |
> |---|---|---|---|
> | 🎯 Busca esto exacto | 5% | **15%** | Las ventanas de rabia tienen búsqueda exacta — se capturan |
> | 🔍 Compara salidas | 20% | **30%** | Tu clienta es más consciente que el mercado promedio (lo firmaste al elegirla) |
> | 😣 Sabe que duele | 50% | **40%** | El grueso: el playbook ES la educación — tu cuña |
> | 😴 Dormido | 25% | **15%** | La pista de prospectos nuevos (la regla prohíbe dejarla en 0) |
>
> **Chequeos del candado, a la vista:** suman 100 ✓ · dentro de las bandas de tu estrategia ✓ · desviación máxima 10 puntos (el límite que exigiría justificación firmada es 30) ✓.
>
> **En cristiano: de cada 10 piezas, 4 educan al que sufre fees, 3 le hablan al que compara, 1.5 capturan al que busca YA, y 1.5 siembran en los dormidos.**
>
> **¿Firmas el reparto 15/30/40/15?** (puede ser "ok" — o ajusta cualquier número; si te alejas >30 puntos de la foto, el sistema te pedirá la justificación, por diseño). Con tu firma pasamos a decidir DÓNDE vive cada pieza.
