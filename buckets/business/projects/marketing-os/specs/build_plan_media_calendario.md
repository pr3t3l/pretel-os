# Build plan — Distribución C17: Ángulos (media dentro) · Media · Calendario

> **Estado: BORRADOR para firma del operador (2026-07-08).** Nace de la conversación de rediseño
> de la distribución tras C17. NO construir hasta firma. Igual que `/angulos` se hizo de cero
> (el Estudio se basaba en el *derivado*, muerto), el **Calendario se hace de cero**: se basaba en
> `buildPublicationPlan` (las ~28 finitas auto-agendadas), muerto con C17.

## Contexto

C17 invirtió el modelo: el **ángulo** (gancho 2.5) es la unidad; la **pieza = ángulo × canal**. La
distribución se reparte en **tres superficies** encadenadas en un pipeline:

```
PRODUCIR      →   BIBLIOTECA   →   AGENDAR       →  PUBLICAR  →  MEDIR
(Ángulos)         (Media)          (Calendario)                  (luego)
la pieza vive     ve TODO lo       pone fecha/hora   el post      cierra el loop
en su ángulo      producido        a lo aprobado     sale         de automejora
```

**Estado de una pieza (unifica las tres superficies):**
`borrador` (tiene texto) → `aprobada` (lista) → `programada` (≥1 entrada en `scheduled_posts`) →
`publicada` → *[métricas]*.
- Sin programar → vive en **Media**, «producida sin asignar» (lo que el Calendario ofrece).
- Programada → tiene fecha/hora/canal en el **Calendario**. La pieza vive en Media siempre; el
  Calendario solo le pone cita.

---

## Decisiones transversales (firmar)

1. **Media = por PROYECTO**, con filtro por avatar (no por-avatar). Para reusar «lo de hace un año»
   quieres verlo todo junto. (operador 2026-07-08)

2. **Ratio dar:pedir = política POR PROYECTO** ✅ *FIRMADO 2026-07-08 — ya operativo*. Se lee de
   `ratio_policy_plain` (2.3, fallback 2.4); **no** una constante global. `3:1` es solo el *default*
   cuando no hay política. No hay verdad universal (la industria cita 3:1, 4:1, 80/20 — heurísticas).
   Editable. **Adaptativo desde métricas (v2):** si la audiencia tolera más «pedir» sin caer
   seguidores/engagement, se afloja sola; si castiga, se aprieta. Necesita la conexión de métricas.

3. **Doctrina de reposteo** ✅ *FIRMADO 2026-07-08* (respuesta al «¿algunos canales castigan
   repostear?» — sí):
   - **El ÁNGULO se reusa infinito** — es el corazón de C17. Reusar = pieza nueva para otro canal
     (*repurpose*). Siempre bien.
   - **Cross-canal** (mismo mensaje a IG + TikTok + YT) = **piezas distintas** (el blog no es el
     reel). Export nativo por canal, **cero watermark de otra plataforma** (TikTok suprime el
     contenido con marca de agua ajena).
   - **Repost idéntico al mismo canal** = rendimiento decreciente / supresión (TikTok deprioriza
     duplicados exactos; IG favorece lo fresco). Permitido **solo** como *re-share evergreen* con
     **(a) gap de tiempo mínimo + (b) aviso**. Nunca por defecto.
   - Producto: el toggle **«Reusar»** del Calendario ofrece media ya usada para re-share evergreen
     (con gap+aviso) o como semilla de repurpose. El camino por defecto sigue siendo pieza fresca.

4. **Scheduling = tabla `scheduled_posts`** (`piece_id`, `channel`, `scheduled_at`, `status`,
   `is_reshare`), **no** un campo de fecha en la pieza: una pieza **puede** agendarse >1 vez
   (re-share evergreen), y el Calendario lee **entradas**, no piezas. Cada entrada = una píldora.

5. **Slots de HORA:** el día tiene horas; se asigna a hora concreta, con **horas sugeridas por
   canal** (doctrina de cadencia R3 — mejor hora por plataforma), editables.

---

## Fase A — Ángulos: la media DENTRO del ángulo (opción A)

La fricción que resuelve: en el Estudio viejo una tarjeta *era* una pieza (1:1) y mostraba su media.
Con C17 el ángulo es 1-a-muchos, así que la media se fue a una sección aparte («Piezas») —
desconexión. La opción A la trae de vuelta a su ángulo.

- La tarjeta de ángulo (`est-acard`) crece una **tira de resultados**: por canal desarrollado, su
  miniatura (visual → media; texto → extracto) + estado-color. Desarrollas Blog → su miniatura
  aparece en la misma tarjeta.
- **Se quita la galería plana «Piezas» de `/angulos`** (se muda a Media, Fase B).
- Reusa: el drawer, el preview de media (visual/texto/placeholder), `famOf`, los estados-color,
  `ChannelIcon`. **Nuevo:** la tira de resultados dentro de `est-acard`.

## Fase B — Media (página NUEVA)

- Ruta nueva (p. ej. `/projects/[id]/media`). De cero, reusando componentes del drawer/preview.
- **Rejilla de TODAS las piezas del proyecto.** Filtros: canal · pilar · estado · dar/pedir ·
  avatar · con/sin media · **buscador**.
- **Card:** preview + título + canal + pilar + estado + **franja de MÉTRICAS** (diseñada, **apagada**
  — se enciende con la fuente; Media es su casa: es donde miras «qué funcionó»).
- **Acciones:** abrir (drawer) · **reusar → repurpose** a otro canal (Etapa D) · re-share evergreen.
- **Reusar lo viejo:** sin límite temporal para ver/reusar; el aviso de gap solo aplica al re-share
  al **mismo** canal.

## Fase C — Calendario (NUEVO, no reusar)

| Conservar | Matar | Nuevo |
|---|---|---|
| El **radar** (eventos/ventanas estacionales para anclar piezas) | `buildPublicationPlan` (28 finitas) | El modelo de **asignación** (`scheduled_posts`) |
| La **cadencia** por canal (frecuencia + mejor hora) | El auto-agendado de derivados | El **panel del día** con slots de hora + media |
| La **política de ratio** | La galería plana en `/angulos` | El **medidor dar:pedir** en la línea de tiempo |

- **Rejilla (el horario):** mes/semana. Por día, **píldoras compactas** — icono de canal + título
  corto + punto dar/pedir + color de estado. Varios por día = pila («+N»). **Nada de media en las
  celdas** (imposible con varios eventos/día — la media va al panel).
- **Radar:** eventos/ventanas como marcadores sutiles en sus días (anclar piezas a una ventana).
- **Panel del día (al seleccionar):**
  - **Slots de HORA** (sugeridos por canal, editables).
  - Los posts agendados de ese día **con su media**.
  - **«Agendar aquí»** → picker con toggle **`[Sin asignar | Reusar]`**:
    - *Sin asignar:* piezas aprobadas sin entrada en `scheduled_posts`.
    - *Reusar:* piezas ya usadas → re-share evergreen (gap+aviso) o semilla de repurpose.
  - Elegir → preview → enlazar a `(día, hora, canal)` → crea la entrada `scheduled_posts`.
- **Medidor dar:pedir** de la semana/mes: «Das 6 · Pides 2 · política 3:1 ✓/⚠». El intent se
  **DERIVA** (modo del pilar + goal de la forma), no se clasifica a mano. Aviso al agendar un
  «pedir» fuera de ratio — solo avisa, el operador manda.

## Métricas (luego — tenerlo en mente)

Solo el **hueco** en Media ahora (apagado). El cable, cuando exista fuente (la spec Fase 3 ya define
`utm_resolved` + tags: `hook_id`, `visual_hook`, `intent`, `campaign_id`…). El loop de automejora
cierra aquí: qué gancho/forma/apertura/pilar **convierte** → alimenta el ratio adaptativo (decisión 2)
y el diagnóstico por pilar (C17).

---

## Orden de construcción

**A → B → C.** Métricas = hueco en B, cable después.
- A es lo más contenido y ya aprobado (extiende `build_plan_estudio_angulos`).
- B es mediano (mover la galería + filtros + reusar + hueco).
- C es el grande (migración `scheduled_posts` + panel del día + asignación); de cero, con la regla
  dura: el Calendario viejo vive hasta la aprobación final del nuevo.

## Muere con este plan

`buildPublicationPlan` (las 28 finitas) · el auto-agendado de derivados · la galería plana en
`/angulos` · el campo `suggestedDate`-como-única-agenda (lo sustituye `scheduled_posts`).

## Estado de ejecución

- **Fase A ✅** desplegada (sandia `0fa422e`): la media dentro del ángulo; se quitó la galería plana.
- **Fase B ✅** desplegada (sandia `bbd5dd4`): la página **Media** (`/projects/[id]/media`) —
  biblioteca del proyecto + filtros + franja de métricas apagada; enlaza a la pieza en `/angulos`
  vía `?piece=<id>` (un solo drawer, cero duplicación). Nav «Media» entre Producir y Calendario.
- **Fase C** — pendiente (el Calendario, el grande).

## Decisiones firmadas (2026-07-08)

- Nombre: **«Media»**.
- **Re-share evergreen:** el campo `is_reshare` nace con `scheduled_posts`; la UI del re-share es v2.
- **Franja de métricas:** dibujada **apagada** en las cards de Media (reserva espacio, comunica que
  viene).
