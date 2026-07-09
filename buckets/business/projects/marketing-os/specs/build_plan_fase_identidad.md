# Build plan — Fase «Identidad» (nueva fase del ciclo)

> **Estado: BORRADOR de build (2026-07-08).** El `spec_Phase_Identidad.md` está FIRMADO — esto es
> el «cómo». Se apoya en el inventario del código existente (agente, 2026-07-08). NO construir sin
> que el operador vea este plan.

## Contexto + caveat C17

La fase separa **DEFINIR** (Identidad: identidad visual firmada + bibliotecas de personajes/sets)
del **PRODUCIR** (Estudio/Ángulos). Hoy viven como strips dentro del Estudio.

**Caveat:** el §1.5 del spec describe el modelo viejo (las 28, `buildPublicationPlan`, `rotateHook`)
que **C17 ya jubiló**. El corazón de la fase (dónde se define + bibliotecas + gates) es independiente
de eso — se ignora ese trozo.

## La decisión de arquitectura (del inventario): CERO migración de BD

Los artefactos ya existen en `project_phase_artifacts`:
- Identidad visual: `phase_2 / 2.0.5 / brand_visual_identity / ""` (compartido).
- Set de rodaje: `distribution / rodaje / set_kit / ""` (compartido).

**No hay un `phase="identity"` en el enum** — crearlo exigiría migración de enum + regenerar
`database.types.ts`. **En su lugar:** la nueva biblioteca `cast` vive en `distribution / identity /
cast / ""` (fase `distribution` que ya existe, artefacto nuevo). Cero migración de BD; los puntos de
consumo (produce/produce-media/video-generate) solo cambian por LEER el cast en vez del set_kit.

## El modelo `cast` (reemplaza el set_kit singular)

```ts
type CastAsset     = { id, nombre, image_url, source: "generada"|"subida", aprobado, prompt|null };
type CastCharacter = CastAsset & { voz: string | null };   // el personaje LLEVA su voz
type Cast = { schema_version:"v1", personajes: CastCharacter[], sets: CastAsset[],
              default_personaje_id: string|null, default_set_id: string|null };
```

- **N personajes + N sets**, con defaults de marca. **No se firman** (biblioteca viva; `aprobado`
  por asset = «listo para Kling», reversible — no es firma de fase).
- **Migración sin pérdida:** `castFromKit(set_kit)` → 1 personaje (con `voz` = kit.voice.descriptor),
  1 set, defaults apuntando a ellos. On-the-fly al leer (no reescribe destructivo).
- **Cascada de resolución:** `resolveCast(cast, override?)` → pieza > campaña > default. v1 usa el
  DEFAULT (sin override UI); el parámetro `override` queda listo para campaña/pieza (v2).

## Fases del build

### B1 — El modelo + la cascada (fundación, sin UI)
- **B1a** ✅ objetivo de este commit: `lib/estudio/cast.ts` — `Cast` + `coerceCast` + `castFromKit`
  (migración) + `resolveCast`/`castCharacterImage`/`castSetImage`/`castVoice`/`castReady` (puros) +
  tests (incluye el test de migración sin pérdida del spec §6).
- **B1b** — cargador server `loadCast(supabase, projectId)`: lee `distribution/identity/cast`; si no
  existe, convierte el `set_kit` viejo al vuelo (`castFromKit`). Cablear produce/produce-media/
  video-generate para resolver por el default vía el cargador (additive → el comportamiento del
  default es idéntico al de hoy; el set_kit sigue siendo la fuente hasta que la página escriba cast).

### B2 — La página `/identity` + el Estudio pierde los strips
- Ruta `app/projects/[projectId]/identity/page.tsx`. Nav: añadir a `app-shell` (`BUILT_PHASES` +
  `PHASE_ROUTES`) y al Hub «Tu camino».
- **Identidad visual con FIRMA** (`GateSignature` `G-Phase-Identidad`): las 3 rutas (importar+feedback
  / co-crear con porqué / piezas sueltas). Reusa `VisualIdentityPanel` (se MUEVE del Estudio).
- **Bibliotecas** personajes/sets con foto-chips (reusa `AssetSlot`/`rodaje-generate`/`uploadBrandAsset`
  + `rehostToBrandAssets`), N de cada uno, defaults, `castFromKit` en la primera visita.
- **Estudio/Ángulos:** los editores (`VisualIdentityPanel`, `RodajePanel`) y sus mutaciones se van;
  queda un **resumen readonly** (swatches + thumbnail + badge) con link «editar en Identidad».
  `PieceDrawer.onOpenRodaje` deep-linkea a `/identity`.
- **FIRMADO ES VISIBLE** (spec §6b): el paso firmado muestra resumen legible aunque colapsado;
  «Enmendar» separado; nunca esconder lo firmado.

### B3 — Los gates por tipo de pieza (spec §3)
| Tipo | Gate |
|---|---|
| Video (Reel/TikTok/Short) | **Duro:** identidad firmada + personaje aprobado |
| Imagen/carrusel/pin/Stories | **Duro:** identidad firmada |
| LinkedIn/Blog | **No bloquea:** sin identidad → solo-texto + aviso |
| Email/Reddit/Grupos FB/X | **Sin gate** |
- Extiende el candado que ya existe (kit→video); botón Desarrollar de piezas visuales muestra el
  candado educativo con link a `/identity`.

## Qué se conserva / consume igual (del inventario)

`brand_visual_identity` (2.0.5) sigue en `phase_2/2.0.5`; `visualIdentityBriefLine` (texto) +
`brandSuffix` (imagen) intactos. `character` (BrandCharacter texto) e imagen de personaje/set +
voz siguen entrando a produce (system prompt) y video-generate (charImg/setImg refs). B1b solo
cambia la FUENTE (cast en vez de set_kit) preservando el default.

## Verificación (spec §6)
- Migración: proyecto con `set_kit` → cast con 1 personaje + 1 set + defaults, cero pérdida (test).
- Cascada: sin override usa default; con override de campaña usa el de campaña (tests puros).
- Gates: video sin personaje aprobado → candado con link; email nunca bloqueado.
- `npm run verify` verde por sub-fase; `/estudio` intacto hasta el swap (regla dura).

## Orden
B1a (modelo+tests) → B1b (cargador+cablear produce/video) → B2 (página+mover strips) → B3 (gates).
