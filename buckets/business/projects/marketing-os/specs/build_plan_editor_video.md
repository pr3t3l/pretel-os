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

- [ ] E1.1 `components/estudio/timeline/` (NUEVO): componente `Timeline` puro-presentacional —
      regla de segundos, zoom (±), playhead, y `Track`/`Block` genéricos con **arrastre para mover**
      y **arrastre de extremos para recortar** (pointer events; clamp a [0, reelSec]; snapping a
      inicios de clip / al playhead / a inicios de palabra). Sin lógica de negocio (props + eventos).
- [ ] E1.2 Modelo `design_spec.timeline.media[]` = `{id, src, kind, startSec, durSec, xPct, yPct,
      wPx, anim?}` + coerción tolerante (patrón `coerceScenes`) + persistencia en la pieza
      (`setPieceDesignSpec`) — el trabajo NO se pierde al recargar (hoy es efímero).
- [ ] E1.3 Reescribir el módulo de imágenes del ensamblador: fuera el «modo tiempo/palabra +
      desde el segundo X»; entra la **pista de MEDIOS** (bloques con thumbnail, drag-time + trim) +
      manipulación en el CANVAS (mover + **handles de resize**, reemplaza el selector `wPct`).
      «＋ Medio» = Subir / De este reel (keyframes) / De la marca — sin jerga ni «keyframe» a secas.
- [ ] E1.4 El quemado consume `timeline.media` (ya soporta overlay por ventana con `scale` a px
      absoluto; solo cambia la FUENTE de los `{startSec,durSec,x,y,wPx}`). Snap-a-palabra OPCIONAL
      (al soltar cerca del inicio de una palabra, engancha y marca «entra con ‹palabra›»).
- [ ] E1.5 `verify` + push · **criterio:** agregar una imagen, ARRASTRAR su bloque en el tiempo,
      redimensionarla en el canvas, quemar → aparece exactamente ahí. Cero campos numéricos.

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
