# spec_Biblioteca_Media — La Biblioteca de Media unificada

> **Estado: BORRADOR PARA FIRMA (2026-07-13).** Nace del feedback del operador al escribir
> `spec_Editor_Video`: el editor necesita un «agregar media», pero HOY la media está regada
> (Identidad, /media, keyframes, subidas…) y el usuario no sabe dónde está nada. Este spec define
> UNA biblioteca unificada — que sirve de **sección** Y de **selector del editor** — construida como
> una **VISTA/ÍNDICE de solo-lectura ADITIVA** sobre el storage y la BD que ya existen. **Ni un byte
> se mueve, ninguna URL se reescribe, ninguna migración de archivos.** Basado en una auditoría
> multi-agente verificada contra el código (2026-07-13).

---

## 1. El problema

La media vive en un solo bucket físico (`brand-assets`) pero se REGISTRA regada como campos JSON
dentro de otras entidades (piezas, artefactos, el índice de música). No hay tabla «assets», no hay
GC, y no hay una superficie única para verla/elegirla. `/media` HOY **no muestra media: muestra
PIEZAS** (`listPieces`, incluye texto sin media y borradores) y salta a `/angulos?piece=` — es una
segunda galería de piezas, no un DAM. Identidad guarda avatars/sets, pero el usuario no los ve como
«media» disponible. El editor no tiene de dónde elegir de forma coherente. Falta la biblioteca.

## 2. El terreno de la media (auditoría verificada)

Un bucket físico: **`brand-assets`** (Supabase Storage, **público a propósito** — las URLs se mandan
a fal/Kling/Replicate como referencia). Todo se guarda por **URL pública absoluta congelada dentro de
JSON**, nunca por path resoluble. **Tres orígenes reales** que mapean 1:1 al estándar DAM: SUBIDA,
CREADA-IA, PRODUCIDA. Dos hogares de registro: `project_pieces` (media atada a pieza) y
`project_phase_artifacts` (media de Identidad, atada a marca). **No hay GC.**

| Tipo | Origen | Storage (prefijo en brand-assets) | Registro | Amarre |
|---|---|---|---|---|
| Keyframes | Creada IA | `${projectId}/rodaje-keyframe-*` | `design_spec.keyframes.images[]` | pieza (invariante N+1) |
| Clips | Creada IA (Kling…) | *(efímero fal, no rehost)* | `asset.variants[]` `group=1..N` | pieza + escena; caducan |
| Reel armado | Producida | `${projectId}/rodaje-reel-*` | `asset.variants[]` `group=90` | pieza |
| Reel final | Producida | `${projectId}/rodaje-reel-final-*` | `asset.variants[]` `group=91`; `kept`→`asset.url` | pieza (producto terminado) |
| Own-footage | Subida (TUS) | `own-footage/${projectId}/*` | `design_spec.own_footage.url` | pieza (prefijo validado) |
| Elementos (logo/overlay) | Subida | `${projectId}/rodaje-element-*` | `video-burn overlays[].url` | overlay (prefijo validado) |
| Carrusel/imagen | Creada IA | *(proveedor, no rehost hoy)* | `asset.images[]` | pieza |
| Cast — personajes/sets | Creada IA / Subida | `${projectId}/rodaje-character-*`,`-set-*`,`ref-*` | artefacto `distribution/identity/cast` | **Identidad** (elegible por campaña `cast_override` / pieza `ugc_cast_id`) |
| Ref. visual (marca) | Subida | `${projectId}/ref-*` | artefacto `phase_2/2.0.5/brand_visual_identity` | Identidad |
| Música | Subida offline | `_music/<slug>` + `_music/index.json` | el propio `index.json` (**sin BD**) | global |

## 3. La corrección CRÍTICA al modelo mental (reduce el riesgo)

**Producir NO es el embudo de la media.** `produce/route.ts` lee Identidad y Campañas **solo como
TEXTO** (extrae la voz del personaje y `name/concept/offer`; emite el guion `design_spec.scenes`). La
**MEDIA fluye por un segundo par de aristas DIRECTAS** — `keyframes/route.ts` y `video-generate/route.ts`
— que leen el artefacto del cast por su cuenta. Confirma tu instinto y lo afina: **las fases (0/1/2)
y Producir entregan COPY, no media** (correcto). Pero la media del cast la consumen las rutas de
generación, no Producir. Consecuencia para nosotros: la biblioteca es de solo-lectura y no toca
ninguna de esas aristas.

### Aristas de MEDIA (las de riesgo) — todas se dejan INTACTAS
- cast→keyframes (`castCharacterImage` como ancla Nano Banana).
- cast→video-generate (`charImg`/`setImg` a Kling — URL muerta = video sin cara, **silencioso**).
- cast_override (campaña) / ugc_cast_id (pieza) → resuelven POR ID a un `image_url`.
- keyframes→video (start/end encadenado, invariante N+1).
- foto-chips de campaña (`<img src=image_url>`), «guardar persona» de la galería.

## 4. El riesgo real: NO tocar el storage ni las URLs

El peligro **no** es la reorganización lógica (secciones/vistas/selectores) — es **tocar el storage
físico o las URLs**. `coerceAsset` NO valida que la URL resuelva → un asset con imagen 404 sigue
«válido y aprobado». Por eso la biblioteca es estrictamente una capa de índice/vista.

**PROHIBIDO (rompe algo en silencio):**
- ❌ Renombrar/mover el bucket `brand-assets` o el patrón `${projectId}/` → rompe TODAS las URLs. Catastrófico.
- ❌ Reescribir cualquier `image_url` de cast/keyframes/reels → rompe las aristas de §3.
- ❌ Cambiar prefijos validados: `own-footage/`, `_music/`, `rodaje-element-*` → falla subida/quemado.
- ❌ Mover la edición del cast fuera de `/identidad`.
- ❌ Hacer de la biblioteca una fuente de verdad — es índice/vista; la verdad sigue en `project_pieces` + artefactos.
- ❌ Listar el bucket CRUDO — mostraría huérfanos (no hay GC). Indexar SOLO por referencias registradas en JSON/artefactos.
- ⚠️ **GC (huérfanos) es un problema separado y pre-existente.** La biblioteca lo hace VISIBLE pero **NO borra en v1** (borrar un archivo aún referenciado por una URL en JSON es exactamente el fallo silencioso).

## 5. Estándar de la industria (DAM, investigado)

1. Un panel «Tu Media», **orígenes por PESTAÑA** (Subido / Generado IA / Stock) — no por ubicación física.
2. **Marca/Identidad = módulo SEPARADO que se INYECTA en el editor** («almacenado aparte, presentado integrado» — Canva/Adobe brand kit al tope).
3. Separar **assets** (materia prima) de **productos terminados** (exports) — Canva: Uploads vs Projects.
4. **Rail izquierdo conmutable + arrastrar-al-timeline**; flujo sube/genera → Library → timeline.
5. Carpetas/filtro por tipo/orden/búsqueda con chips/favoritos.
6. Etiquetado por origen y por proyecto/campaña.

## 6. El modelo propuesto — Biblioteca Unificada de Papandi

### 6.1 Principio: una VISTA/ÍNDICE, no una migración
Capa de **lectura** que agrega en tiempo de lectura desde las referencias YA registradas.

- **Opción A (v1, recomendada):** módulo front (`lib/media/library.ts` + página `/biblioteca`) que
  agrega desde `listPieces()`, `getArtifactContent(distribution/identity/cast)`, `phase_2/2.0.5` y
  `_music/index.json`. **Cero cambios de BD.** Es un *proyector* (mismo patrón que la awareness de
  pretel-os). Empezar aquí.
- **Opción B (solo si se exige búsqueda server-side cross-proyecto):** tabla-índice ADITIVA
  `media_index` (facetas `project_id, campaign_id, avatar_key, origin, kind, piece_id, url`) poblada
  por trigger/worker. Es **índice, no fuente de verdad** — se reconstruye si se cae.

### 6.2 Los bloques (mapeados sobre lo existente, sin mover nada)

| Bloque | Estándar | Se alimenta de | Rol |
|---|---|---|---|
| ① **Producida** | Projects/Exports | `asset.variants[]` reel-armado/reel-final (`kept`=oficial) + carruseles finales | Productos terminados |
| ② **Subida** | Uploads | `own-footage/*` + `rodaje-element-*` | Materia prima del operador |
| ③ **Creada IA** | AI Assets | keyframes + clips + carruseles IA | Materia prima generada |
| ④ **Avatars+Sets** | Brand Kit | artefacto `distribution/identity/cast` + `2.0.5` | **Read-only** (se edita SOLO en `/identidad`) |
| ⑤ **Música** | Audio library | `_music/index.json` | Global, read-only |

### 6.3 Doble función
- **Como sección** (`/biblioteca`, o re-propósito de `/media`): rail izquierdo con bloques ①–⑤;
  filtro por tipo, orden por fecha, búsqueda con **chips de campaña/avatar/canal** (aprovechando el
  `campaign_id` ya cosido), favoritos. El bloque ④ Identidad al TOPE, read-only, con insignia
  «editar en Identidad →».
- **Como selector**: el MISMO módulo se abre como drawer desde el editor / `/angulos` para elegir un
  asset e insertarlo (imagen de overlay, keyframe, etc.). El cast aparece arriba, consistente en todo.

### 6.4 Reconciliación de superficies
- **`/identidad` — NO SE TOCA.** Sigue siendo la casa del cast; la biblioteca solo lo **proyecta**
  read-only en ④. Generar/editar/aprobar sigue exclusivo de `/identidad`.
- **`/media` — se re-propósita** de «galería de piezas» a la biblioteca de assets (①–⑤); cada tarjeta
  = un **asset** (thumbnail que abre/descarga), no una pieza. «Saltar al ángulo» queda como acción
  secundaria del asset producido.

### 6.5 El moat (glass-box) que SÍ construir
Papandi ya cose `campaign_id` y atribuye costo por `project_id` (`logMediaCall` →
`project_llm_calls`/`project_api_calls`). La biblioteca puede ofrecer **facetas por
campaña/avatar/canal/origen** y **procedencia de costo** («generado en campaña X, avatar Y, costó
$Z»). DAM con procedencia — aditivo (solo lee el ledger) y es diferencial.

## 7. Criterios de aceptación

1. El usuario ve TODA su media en un solo lugar, por bloques (producida/subida/creada/avatars+sets/música),
   sin preguntarse «¿está en Identidad o en Media?».
2. Desde el editor, «agregar media» abre la biblioteca y elige un asset (no se navega a otra sección).
3. `/identidad` sigue funcionando idéntico; su cast se ve read-only en la biblioteca.
4. **Cero regresiones**: keyframes, cast_override, ugc_cast_id, quemado, subidas — todo intacto
   (la biblioteca no reescribe URLs ni mueve archivos).
5. La biblioteca indexa solo referencias registradas (nada de huérfanos del bucket crudo).

## 8. Cómo se junta con el Editor (spec_Editor_Video)
El «＋ Medio» del editor (E1.3) NO inventa su propio picker: abre ESTA biblioteca (bloques ②③④ como
fuentes de inserción; ① y ⑤ para otros contextos). El editor consume; la biblioteca provee. Se
construyen coordinados: la biblioteca (o al menos su capa de lectura `lib/media/library.ts`) es
prerequisito del selector de medios del editor.

## 9. Plan de construcción (fases)
- **B1** `lib/media/library.ts` — el proyector de solo-lectura (Opción A): agrega los 5 bloques desde
  las fuentes existentes, con tipos `{id, kind, origin, url, thumbUrl, pieceId?, campaignId?, avatarKey?, createdAt}`. Puro + tests. Cero BD.
- **B2** `/biblioteca` (o re-propósito de `/media`): la sección con rail de bloques + filtro + búsqueda
  con chips + favoritos. El bloque ④ read-only con «editar en Identidad →».
- **B3** El drawer selector: el mismo módulo como picker, integrado al editor / `/angulos`.
- **B4** Facetas glass-box (campaña/avatar/costo) — el moat.
- **B5** (opcional/futuro) Opción B `media_index` si se exige búsqueda server-side; visibilidad de
  huérfanos (SIN borrar).
- Cada fase: `verify` EXIT 0, push, prueba. **No construir hasta firma de este spec.**
