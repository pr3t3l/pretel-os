# Spec — Superficies de Producción y Distribución (Ángulos · Media · Agenda)

**Estado:** AUTORIDAD del mundo C17 (documenta lo CONSTRUIDO y desplegado; 2026-07-08). Reemplaza a
`spec_Estudio_Produccion_Publicacion.md` (SUPERSEDED) como la autoridad de superficie. Trinity:
spec = este doc · plan = `build_plan_estudio_angulos.md` + `build_plan_media_calendario.md` ·
tasks = registradas.
**Decide:** dónde se PRODUCE (Ángulos), dónde vive lo producido (Media), y dónde se AGENDA (Agenda),
bajo el modelo C17 (`spec_Modelo_Contenido.md`, firmado 2026-07-06).

---

## 0. El modelo (C17)

El **ÁNGULO** (el gancho 2.5, rico y sagrado) es la **unidad de producción**. **PIEZA = ángulo × canal**
(el canal decide formato y gate; el ángulo, la sustancia). El plan es **generativo/infinito** (mismos
pilares → años de contenido; las «28» eran solo un sorteo inicial, ya retirado). El **PILAR** es la raíz
diagnóstica del loop (si TODOS los ángulos de un pilar fallan → re-planear el pilar).

**El pipeline, tres superficies:**
```
PRODUCIR (Ángulos /angulos) → BIBLIOTECA (Media /media) → AGENDAR (Agenda /agenda) → PUBLICAR → MEDIR
```

**El estado de una pieza (une las tres):** `desarrollada` (borrador) → `producida` (con media) →
`aprobada` → `programada` (≥1 entrada en `scheduled_posts`) → `publicada` → *[métricas — luego]*.
Color unificado (tokens de fase): ◐ borrador (papaya) · ● lista (verde, = producida|aprobada) · ✓ publicada (azul).

---

## 1. ÁNGULOS (`/angulos`) — el TALLER

Por avatar (C15). Carga: pilares 2.3 (con `anchor` + `ratio_policy_plain`), ganchos 2.5 (= los ángulos),
matriz 2.2, identidad visual 2.0.5, set de rodaje, y las piezas del proyecto.

**La tarjeta de ángulo** (`est-acard`, con división interna):
- **EL DOLOR** (arriba, sagrado): el texto del gancho + su arquetipo + el badge dar/pedir.
- **DESARROLLAR PARA** (abajo): los **chips de canal** (uno por canal firmado 2.2, con icono de
  plataforma + estado-color de esa pieza `ángulo×canal`) + las **capas**:
  - **FORMA** (el molde retórico, del Cerebro de Ganchos): «Papandi sugiere 5 estilos» — filtra los 4.550
    moldes (embudo E0-E1 por categoría/goal, intercalado para diversidad) y el LLM elige 5. **Doctrina del
    molde (C17.1): el molde ENMARCA el ángulo, NO lo comprime** — las palabras del ángulo son el contenido,
    el molde solo aporta el tejido conectivo; si deja una promesa abierta, la cierra la esencia 0.1. La
    apertura elegida (`hookFilled`) se puede **editar a mano** y viaja **verbatim** al develop («APERTURA
    APROBADA … ÚSALA TAL CUAL»). Guardias `keepsAngle`/`addsFabricatedUrgency` avisan si el LLM reescribe.
  - **ESCENA** (apertura visual, solo video): 16 `visual-hooks.ts`.
- **LA MEDIA DENTRO DEL ÁNGULO**: tira de miniaturas de las piezas hechas (cualquier canal) — clic abre el drawer.
- **CTA**: «Desarrollar para «X»» (nuevo) o «Ver la pieza de «X»» (ya hecho — no re-paga).

**El develop** (`/api/estudio/produce`): `buildBrief(ángulo + pilar + canal)` → `buildDevelopSystem`
(doctrina por canal C3, journey 2.2, contexto temporal del radar, personaje/voz del kit, identidad visual)
→ UNA llamada → la pieza (texto/guion + `design_spec` + tips + QA). Un molde de canal por formato
(video = clips + personaje/set repetidos + cámara + narración; imagen = composición; email = texto plano).

**El ratio dar:pedir**: `pieceIntent` (modo del pilar + goal de la forma; `get_sales`=pedir). Avisa, no bloquea.

## 2. MEDIA (`/media`) — la BIBLIOTECA

Por PROYECTO (filtro por avatar). Todo lo producido, en un sitio. Filtros: avatar · canal · estado
(agrupado por color) · buscador. Cada card: preview + estado-color + **franja de métricas APAGADA**
(`👁 — 🔖 — ➚ — · pronto`; se enciende con la fuente de medición, spec Fase 4). Clic → lleva a la pieza en
`/angulos` (`?piece=<id>`) — un solo lugar de detalle (el drawer), cero duplicación. «Reusar lo viejo» =
abrir su ángulo y desarrollar otro canal (Etapa D).

## 3. AGENDA (`/agenda`) — el CALENDARIO

De cero (reemplaza el `/calendar` viejo, que mostraba un plan CALCULADO por `buildPublicationPlan`,
muerto). **Lee AGENDAS reales** (`scheduled_posts`): lo que el operador asigna.
- **Rejilla del mes** (reusa el CSS `cal-*`): por día, píldoras compactas (icono de canal + título +
  punto dar/pedir + color de estado); marcadores del **radar** (`/api/radar/upcoming` — infra compartida).
- **Panel del día**: slots de **hora** (con mejor-hora sugerida por canal, cadencia R3) + los posts
  agendados (con media) + **«Agendar aquí»** → picker con toggle **`[Sin asignar | Reusar]`** → piezas
  **verdes** (producida/aprobada = listas) → clic crea la entrada.
- **Medidor dar:pedir** del mes (política per-proyecto de 2.3, default 3:1) — avisa al agendar un «pedir» fuera de ratio.

**`scheduled_posts`** (migración `20260708120000`): `{ id, project_id, piece_id, avatar_key, channel,
scheduled_at (día+hora), status: programada|publicada|cancelada, is_reshare, note }`. Una pieza → N
publicaciones (por eso tabla, no campo). Accesor `lib/api/schedule.ts`.

**Doctrina de reposteo (C17.1, firmada):** el ÁNGULO se reusa infinito (repurpose). Cross-canal = piezas
DISTINTAS (export nativo, sin watermark ajeno). Repost idéntico al MISMO canal = solo re-share evergreen
con gap + aviso (varios canales castigan el duplicado exacto). El toggle «Reusar» honra esto.

## 4. El pipeline de calidad de producción (cosechado de `spec_Estudio §3`)

Sobrevive de la spec superseded, ahora anclado al develop de `/angulos`:
- **La promesa / anti-promesa por tipo de pieza** (contrato de honestidad §0 del viejo): qué SÍ y qué
  NO promete cada formato — el filtro anti-genérico.
- **Doctrina por canal (R3, C3)**: reglas invisibles en el prompt (email texto plano · Reddit self-post ·
  Blog SEO E-E-A-T primera persona · Reel movimiento/cortes · carrusel save…). `channelToContentType` +
  `developTypeInstruction`.
- **Imagen** (`produce-media`): 1 prompt por generador + `brandSuffix` + `reference_image_url` (FLUX Kontext).
- **Video** (`video-generate`): clips + personaje/set como referencias (Kling `elements`) + voz nativa;
  `video-routing.ts` (Kling/Seedance/Veo). Post-producción = Etapa G (fuera de alcance).
- **Wrapper / AI Gateway** (`spec_AI_Gateway_Wrapper`): `generate()` único, failover, `design_spec` schema, cost metering.
- **Pricing por modo** (`spec_Production_Support_and_Pricing`): el `production_mode` cuelga de la pieza
  (ángulo × canal), no de un derivado 2.4.

## 5. Los gates (habilitados por la fase Identidad — ver `spec_Phase_Identidad §3`)

| Tipo de pieza | Gate |
|---|---|
| Video (Reel/TikTok/Short) | Duro: identidad firmada + personaje aprobado |
| Imagen/carrusel/pin/Stories | Duro: identidad visual firmada |
| LinkedIn/Blog | No bloquea: sin identidad → solo-texto + aviso |
| Email/Reddit/Grupos FB/X | Sin gate (texto-nativo) |

## 6. Verificación (lo construido, verificado en producción)

- Desarrollar los 4 tipos (texto/imagen/video/email) end-to-end; editar la apertura y que viaje verbatim
  (verificado en DB: `form_filled` → `hookFilled` → «APERTURA APROBADA»).
- Agendar: 3 posts en `scheduled_posts`, día correcto (UTC guardado, local leído).
- Media: filtro por estado agrupado (producida cae en «aprobada»/verde).
- `npm run verify` verde por etapa; deploy continuo. `/estudio` y `/calendar` jubiladas (swap 2026-07-08).

## 7. Fuera de alcance

- **Campañas** → `spec_Campanas.md` (solo el enganche: `scheduled_posts.campaign_id` + override de
  personaje/set por campaña).
- **Post-producción de video** (captions, unión de clips, frame chaining) → `build_plan_etapa_G_video.md`.
- **Métricas / el loop de medición** → `spec_Phase_4_Medir.md` (la franja de Media se enciende ahí).
- **La fase Identidad** (dónde se DEFINE la marca) → `spec_Phase_Identidad.md`.
