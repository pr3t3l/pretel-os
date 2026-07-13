# spec_Editor_Video — El Editor (Etapa 5 del Director, unificada)

> **Estado: BORRADOR PARA FIRMA (2026-07-13).** Reemplaza el diseño ad-hoc actual del ⑤ (paneles
> sueltos de captions / música / imágenes con tiempo NUMÉRICO) por UN editor de línea de tiempo
> estándar de la industria. Une en UNA sola etapa: subtítulos + medios (imágenes/stickers) +
> **transiciones** entre clips + música. Nace del feedback del operador (2026-07-13): «ese módulo de
> las imágenes está muy mal pensado… ¿qué tal si la persona coloca desde el segundo 15 al 2.5? …
> miren cómo es el estándar de la industria». Dejamos de improvisar; esto se firma antes de construir.

---

## 1. El problema (por qué existe este spec)

El ⑤ actual creció por parches: los subtítulos por-bloque quedaron bien (galería de presets), pero
los **medios (imágenes/stickers)** se agregan con un modo NUMÉRICO — «modo tiempo / desde el
segundo X por N s» o «con una palabra». Eso NO es como se edita video en ningún lado: es confuso
(¿desde el 15 hasta el 2.5?), no se ve dónde cae la imagen en el reel, y mezcla dos conceptos
(tiempo absoluto vs palabra hablada). Además las **transiciones** entre clips (pedidas como 5B) no
tienen dónde vivir. La respuesta correcta —y la que piden CapCut, Clipchamp, Kapwing, Veed— es UN
**editor de línea de tiempo**: pistas, bloques que se ARRASTRAN en el tiempo, resize/posición en el
canvas, transiciones en las junturas. Este spec define ese editor y absorbe las 5A/5B en uno solo.

## 2. Investigación — el estándar de la industria (verificado)

Modelo universal (idéntico en CapCut, Clipchamp, Kapwing, Veed):

- **Timeline multipista abajo, no lineal.** Los medios se colocan en PISTAS; una pista más ALTA se
  dibuja ENCIMA (el z-order = el orden de apilado). El preview muestra la cima de la pila.
- **Overlays / Picture-in-Picture:** el usuario suelta la imagen/video en una pista superior, la
  **redimensiona y posiciona ARRASTRÁNDOLA en el CANVAS** (handles), y **define CUÁNDO aparece
  arrastrando los EXTREMOS del bloque en la línea de tiempo** — nunca escribiendo un número.
  (CapCut PC: «drag the ends of the overlay track to set when it appears and disappears».)
- **Transiciones:** se agregan en la JUNTURA entre dos clips — clic en «Transición» / arrastrar la
  transición a la unión / botón «+» entre clips → aparece un panel de propiedades para elegir tipo y
  ajustar la DURACIÓN en segundos. Tipos estándar: fade/dissolve, slide, wipe, zoom, whip/whoosh; y
  fade-in/out para entradas/salidas de overlays.
- **Subtítulos/Texto:** viven como una pista propia (auto-captions alineados) con estilo por bloque.
- **Preview:** un lienzo 9:16 con PLAYHEAD que se arrastra (scrubbing) y reproduce en vivo.
- **Render:** los editores del navegador previsualizan en el navegador y RENDERIZAN aparte (nube).
  El preview es una APROXIMACIÓN; el archivo final se compone al exportar.

Fuentes: [CapCut — overlay/PiP en pistas + arrastrar extremos](https://www.capcut.com/resource/how-to-add-capcut-overlays) ·
[CapCut — timeline multipista](https://filmora.wondershare.com/advanced-video-editing/capcut-timeline.html) ·
[Clipchamp — timeline y capas](https://support.microsoft.com/en-us/topic/how-to-work-with-the-timeline-in-clipchamp-80ad81aa-d81e-45e9-bf9b-538c0f7202a4) ·
[Clipchamp — transiciones (arrastrar a la juntura + panel de duración)](https://support.microsoft.com/en-us/clipchamp/how-to-add-transitions-and-fades-to-videos) ·
[Clipchamp — PiP overlay (resize/posición en el preview)](https://clipchamp.com/en/blog/how-to-navigate-video-editing-tools/).

## 3. Principio arquitectónico (no negociable)

**El navegador PREVISUALIZA; NUESTRO ffmpeg RENDERIZA.** Cero WASM (ffmpeg.wasm/WebCodecs) — lento,
frágil, memoria; y el operador confirmó solo-desktop, no hay razón para renderizar en el cliente.
Esto ya es nuestra arquitectura y coincide con lo que hacen los editores online (previsualizan
aprox., exportan en la nube). Implica el **contrato de fidelidad**: el preview es fiel en lo que se
puede baratamente (captions con la misma .ttf, overlays como capas DOM sobre el frame real), y lo que
no se puede previsualizar barato (las TRANSICIONES entre clips) se muestra como MARCADOR en la
juntura y se ve exacto solo en el «Reel final» quemado. Costo de render: ~$0 (cómputo propio),
sin proveedor nuevo, sin costo por uso.

## 4. El modelo del Editor (nuestro)

Pantalla completa (dentro del Director, paso ⑤ «Edición»). Tres zonas:

### 4.1 Lienzo (preview 9:16, arriba)
- Reproduce el arreglo con un **playhead**; barra de transporte (play/pausa, tiempo, scrubbing).
- La base es el **reel armado** (los clips ya unidos, un mp4). Encima, capas DOM sincronizadas al
  `currentTime`: subtítulos (karaoke), overlays (imágenes/stickers).
- El elemento SELECCIONADO se manipula EN el lienzo: **arrastrar para mover** + **handles para
  redimensionar** (reemplaza el arrastre-solo-vertical actual y el `wPct` por selector).
- Guías de safe zones (14%/35%) como hoy.

### 4.2 Línea de tiempo (abajo) — PISTAS
De arriba a abajo (z-order de dibujo = de abajo hacia arriba en el video):
1. **Pista de CLIPS** (base): los clips elegidos en orden, con **junturas** entre ellos. Clic en una
   juntura → panel de **transición** (tipo + duración). (Absorbe la 5B.)
2. **Pista de SUBTÍTULOS**: los beats del karaoke como bloques (de la alineación whisper). Clic en un
   bloque → panel de estilo por-bloque (la galería de presets + ajustes finos, YA construido).
3. **Pista de MEDIOS (overlays)**: imágenes / stickers / palabras gigantes como **bloques
   arrastrables**. Arrastrar el bloque = mover en el tiempo; arrastrar los extremos = recortar
   inicio/fin. (Reemplaza el «desde el segundo X».) El botón «＋ Medio» abre: subir imagen/video,
   o elegir de la BIBLIOTECA del proyecto (keyframes del reel, brand-assets) — sin la palabra
   «keyframe» a secas ni el modo «con una palabra» como default (ver §5).
4. **Pista de MÚSICA**: la pista elegida (selector + preview ya construido), como un bloque; se
   puede recortar dónde entra.
- La línea de tiempo tiene **regla de segundos**, **zoom** (±) y **snapping** (a inicios de clip, al
  playhead, a inicios de palabra). Un playhead compartido con el lienzo.

### 4.3 Panel de propiedades (derecha, contextual al elemento seleccionado)
- Transición: tipo (grid de miniaturas) + duración.
- Bloque de subtítulo: la galería de presets + ajustes finos (YA existe).
- Overlay: tamaño (o handles en canvas), opacidad, animación de entrada/salida (fade/pop), y su
  rango de tiempo (reflejado del bloque, editable).
- Música: volumen bajo la voz, fade.

## 5. La redesign del módulo de MEDIOS (el dolor puntual del operador)

Muere el modelo numérico. Nace el bloque en la pista de MEDIOS:
- **Agregar** un medio lo pone en el playhead con una duración por defecto (p.ej. 3s); un thumbnail
  del medio se ve en el bloque.
- **Ubicar en el tiempo** = arrastrar el bloque por la pista. **Recortar** = arrastrar sus extremos.
  Se VE exactamente dónde cae respecto al reel y a las palabras.
- **Posición/tamaño** = arrastrar y handles EN el canvas (WYSIWYG).
- **Fuente del medio**: el «＋ Medio» NO inventa su propio picker — abre **La Biblioteca de Media**
  (`spec_Biblioteca_Media.md`): media subida, creada por IA (keyframes/clips), avatars+sets del cast
  (read-only), etc., por bloques y sin jerga. El editor CONSUME; la biblioteca PROVEE. La capa de
  lectura de la biblioteca (`lib/media/library.ts`) es prerequisito de este selector.
- El modo «con una palabra» NO desaparece pero deja de ser el default: se ofrece como **snap
  opcional** — al arrastrar un bloque cerca del inicio de una palabra, hace snap y muestra «entra con
  ‹palabra›». Lo mejor de ambos: control visual + la magia de sincronizar a la voz cuando conviene.
- El motor de quemado NO cambia (ya soporta overlay por ventana de tiempo con `scale` a px absoluto
  — el fix de scale2ref); el editor solo produce mejores `{startSec, durSec, x, y, wPx}`.

## 6. Transiciones (absorbe la 5B)

- Se configuran en la **juntura entre clips** (pista de clips): «+» → grid de transiciones + duración.
- Tipos v1 (ffmpeg `xfade`): corte (ninguna), fade/dissolve, slide (izq/der/arriba/abajo), wipe,
  circleopen/close, zoom. Audio: `acrossfade` en la juntura.
- **El armado se MUEVE a NUESTRO ffmpeg** (hoy es concat vía fal, que no hace xfade): un solo grafo
  `xfade`+`acrossfade` encadenado por juntura, con las duraciones de transición. (Reusa el patrón
  ffmpeg del quemador y de video-edit; `-nostdin`, encode veryfast, sin scale2ref.)
- Preview: la juntura muestra un ICONO de la transición; el efecto real se ve en el «Reel final».
  (Contrato de fidelidad del §3 — aceptable y estándar.)

## 7. Qué se REUTILIZA vs qué es NUEVO

**Reutiliza (ya en prod):** subtítulos por-bloque + galería + ajustes finos; música (selector +
mezcla bajo la voz); motor de overlay del quemador (scale a px absoluto, inputs finitos, veryfast,
kill-timeout); alineación whisper (beats); el quemador propio (libass + overlays); el patrón
ffmpeg compartido (`lib/api/server/ffmpeg.ts`).

**Nuevo:** (a) la UI de LÍNEA DE TIEMPO (pistas, bloques arrastrables, regla, zoom, snapping,
playhead compartido con el lienzo); (b) manipulación en el CANVAS (mover + handles de resize) para
overlays; (c) TRANSICIONES (armado con nuestro ffmpeg + xfade + panel de juntura); (d) el modelo de
datos del timeline en `design_spec.timeline` (pistas + bloques + transiciones) — fuente de verdad
del editor, de la que se derivan el .ass y los overlays del quemado.

## 8. Modelo de datos (borrador)

`design_spec.timeline = { clips:[{variantId, transitionIn?:{type,dur}}], captions:{beatStyles[]},
media:[{id, src, startSec, durSec, xPct, yPct, wPx, anim?}], music:{trackId, gain} }`. El quemado
consume esto (el .ass de las captions ya sale de aquí; los overlays de `media`; el armado de `clips`
+ transiciones). Persistir en la pieza (no efímero como hoy) para no perder el trabajo al recargar.

## 9. Criterios de aceptación

1. El usuario agrega una imagen y la ubica ARRASTRANDO un bloque en la línea de tiempo (no escribe
   segundos), la redimensiona/posiciona en el canvas, y en el «Reel final» aparece exactamente ahí.
2. El usuario pone una transición «slide» entre el clip 1 y 2 con 0.5s, y el reel final muestra la
   transición (con crossfade de audio).
3. Los subtítulos por-bloque siguen funcionando como hoy, ahora como pista del timeline.
4. El playhead reproduce el arreglo; el preview es fiel para captions/overlays (las transiciones se
   ven en el final).
5. Nada se pierde al recargar (timeline persistido en la pieza).
6. Un reel de 30s con captions + 1 imagen + 1 transición + música quema en <60s, sin cuelgues.

## 10. Fuera de alcance (v1)

Multi-pista arbitraria (>1 pista de overlays a la vez está OK, pero no capas ilimitadas), keyframing
de animación por-propiedad, curvas de velocidad, chroma key, máscaras. Se anotan para v2.

---

El plan de construcción por fases vive en `build_plan_editor_video.md` (Trinity). NO construir hasta
firma de este spec.
