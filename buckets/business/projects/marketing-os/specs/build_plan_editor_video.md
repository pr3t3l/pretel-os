# build_plan_editor_video — Plan de construcción del Editor (Etapa 5 unificada)

> Spec madre: `spec_Editor_Video.md` (firmar antes de construir). Patrón de entrega igual al resto:
> cada tajada `npm run verify` EXIT 0 + build de producción EXIT 0, commit+push (Vercel deploya),
> prueba real, y solo entonces la siguiente. Repo: `sandia-marketing`. Render SIEMPRE en nuestro
> ffmpeg (`-nostdin`, veryfast, inputs finitos, `scale` a px absoluto — nunca scale2ref; kill-timeout).

## Orden y principio

Value-first + reuse-first. La **Fase E1 arregla el dolor del operador** (el módulo numérico de
imágenes) y de paso levanta el FRAMEWORK del timeline; las fases siguientes cuelgan pistas de ese
framework. Las transiciones (la vieja 5B) son la E3. Todo converge en UN editor.

```
E1 timeline+medios (dolor) → E2 captions+música al timeline → E3 clips+transiciones → E4 playhead/pulido → E5 prueba real
```

## Fase E1 — El timeline + la pista de MEDIOS (arregla lo mal pensado)

- [x] E1.1 `components/estudio/timeline/timeline.tsx`: componente `Timeline` puro-presentacional —
      regla de segundos, zoom (±), playhead, bloques con **arrastre para mover** y **extremos para
      recortar** (pointer events; snapping a junturas de clip / inicios de beat / playhead). Sin
      lógica de negocio. **En prod 2026-07-13** (`1aa5050`).
- [x] E1.2 Modelo `design_spec.timeline.media[]` + coerción tolerante + ops puras
      (`lib/video/timeline.ts`, 10 tests) + persistencia debounced en la pieza. **En prod** (`9d9aa05`).
- [x] E1.3 (v1) El EDITOR (`components/estudio/editor/video-editor.tsx`): lienzo 9:16 con capas DOM
      (mover + handle de resize en el canvas) + 4 pistas (Clips/Subtítulos/Medios/Música — Medios
      interactiva, el resto referencia) + «＋ Imagen» abre la Biblioteca (B3). El módulo numérico
      quedó COLAPSADO como «modo anterior» (retirarlo del todo cuando el operador valide). **En
      prod** (`1aa5050`+`d2e58fc`). **+ ③④⑤ como PANTALLAS navegables del Director** (indicador
      clicable, ⑤ a lo ancho 1280px, layout lienzo-izquierda/panel-derecha) — pedido explícito del
      operador 2026-07-13 (`7e48143`).
- [x] E1.4 El quemado consume `timeline.media` (imágenes de storage propio → overlays por ventana).
      Snap-a-palabra opcional PENDIENTE (los inicios de beat ya son puntos de imán del timeline).
- [ ] E1.5 **criterio de cierre (falta la prueba del operador):** agregar una imagen, ARRASTRAR su
      bloque en el tiempo, redimensionarla en el canvas, quemar → aparece exactamente ahí.

## Fase E2 — Subtítulos y Música como PISTAS del timeline

- [ ] E2.1 Pista de SUBTÍTULOS: los beats del karaoke como bloques del timeline; clic abre el panel
      de estilo por-bloque (galería + finos, YA construido — solo re-ubicar el disparador en el
      timeline). El `.ass` sigue saliendo del estilo por-bloque.
- [ ] E2.2 Pista de MÚSICA: la pista elegida como bloque (recortar dónde entra); reusa el selector
      y la mezcla bajo la voz. Persistir `timeline.music`.
- [ ] E2.3 `verify` + push · criterio: captions y música se ven y editan desde el timeline; el reel
      final es idéntico al de hoy en esos aspectos.

## Fase E3 — Clips + TRANSICIONES (absorbe la vieja 5B)

- [ ] E3.1 Armado con NUESTRO ffmpeg (hoy es concat vía fal, que no hace xfade): grafo
      `xfade`+`acrossfade` encadenado por juntura, duraciones por transición; `-nostdin`, veryfast,
      inputs finitos. (Reusa `lib/api/server/ffmpeg.ts`.) Fallback a concat simple sin transiciones.
- [ ] E3.2 Pista de CLIPS en el timeline con JUNTURAS: «+» entre clips → grid de transiciones
      (corte, fade/dissolve, slide↑↓←→, wipe, circleopen, zoom) + duración. Persistir
      `timeline.clips[].transitionIn`.
- [ ] E3.3 Preview: la juntura muestra el ICONO de la transición; el efecto real en el «Reel final»
      (contrato de fidelidad §3). Audio con `acrossfade`.
- [ ] E3.4 `verify` + push · criterio: transición «slide» de 0.5s entre clip 1 y 2 se ve en el reel
      final con crossfade de audio.

## Fase E4 — Playhead unificado + pulido

- [ ] E4.1 Playhead compartido lienzo↔timeline (scrubbing): el preview salta al arrastrar el
      playhead; las capas DOM (captions/overlays) se sincronizan al `currentTime`.
- [ ] E4.2 Animaciones de entrada/salida de overlays (fade/pop vía `\t`/alpha del quemador) +
      opacidad; y el «pop» del keyword resaltado (nice-to-have de CapCut).
- [ ] E4.3 Biblioteca de medios limpia (subir imagen/video corto, elegir de keyframes/brand-assets),
      z-order si hay >1 overlay, y estados de guardado del timeline robustos.
- [ ] E4.4 `verify` + push.

## Fase E5 — Prueba real + cierre

- [ ] E5.1 El operador arma un reel completo en el editor (clips+transición + captions por-bloque +
      1-2 medios arrastrados + música) y queda contento. Checklist doctrina-video-2026.
- [ ] E5.2 Retro-doc: cerrar `spec_Director_de_Video.md` ⑤, actualizar memoria, decisión de cierre.

## Notas de reúso / riesgo

- Reúso alto: captions por-bloque, música, motor de overlay (scale a px absoluto), quemador,
  alineación. El grueso NUEVO es la UI del timeline (E1.1) y las transiciones (E3).
- Riesgo principal: el armado con xfade en nuestro ffmpeg (encadenar transiciones correctamente).
  Se valida LOCAL con frames antes de push (como todo lo de video).
- Sin costo nuevo de runtime (cómputo propio), sin proveedor, solo-desktop.
- Regla de oro ffmpeg serverless ya aprendida: `-nostdin`, inputs finitos, `scale` no `scale2ref`,
  encode veryfast, kill-timeout de red de seguridad.
