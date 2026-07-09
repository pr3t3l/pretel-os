# Spec — Fase «Identidad» (nueva fase del ciclo de vida)

**Estado:** v1 borrador — para firma del operador antes de construir (Etapa B del plan de control 2026-07).
**Decide:** dónde se DEFINE la identidad de marca (visual + personajes + sets + voz del personaje), cómo se educa al definirla, y qué gates habilita en Producción.
**Fuentes:** decisiones del operador (rondas 1-3, 2026-07-06) · `docs/research/doctrina-por-canal.md` (gates) · `docs/research/campanas-marketing-real.md` (overrides por campaña) · `spec_UX_Experience.md` (P1-P7) · `spec_Superficies_Produccion.md` (Ángulos = taller · Media = biblioteca · Agenda = distribución).

---

## 0. La tesis

**Identidad = donde DEFINES (una vez, con firma) · Producción (Ángulos) = el TALLER · Media = la BIBLIOTECA.**

Es el patrón de la industria (Canva Brand Kit, HubSpot brand settings, Adobe Express: la definición de marca vive aparte del editor). Hoy la identidad visual y el Set de Rodaje viven como strips DENTRO de la producción (Ángulos) — definición mezclada con producción. Esta fase los separa. Autoridad de las superficies: `spec_Superficies_Produccion.md`.

## 1. El ciclo de vida queda

```
Fundación (F0) → Oferta (F1) → Contenido (F2, cierra en 2.6)
   → IDENTIDAD (nueva)
   → PRODUCCIÓN (Ángulos: taller · Media: galería)
   → DISTRIBUCIÓN (Agenda) → MEDICIÓN → AJUSTE
```

- Las **campañas se OFRECEN** después (radar/lanzamiento) — jamás son requisito.

### 1.5 Qué pasa después de firmar 2.6 (el flujo — REESCRITO a C17, 2026-07-08)

> El §1.5 original describía el modelo muerto (`buildPublicationPlan`, las ~28, `rotateHook`, «pieza de
> 2.4»). C17 lo invirtió y el swap 2026-07-08 lo ejecutó. Autoridad de las superficies: `spec_Superficies_Produccion.md`.

**NADA se genera automáticamente al firmar.** Firmar la Fase 2 no produce contenido: deja LISTOS los
INSUMOS (voz, reparto, matriz, pilares con su ancla, y la biblioteca de **ÁNGULOS** 2.5). El flujo real:

1. **Los ÁNGULOS aparecen en Ángulos** (`/angulos`), agrupados por pilar. Cada gancho de 2.5 es un ángulo
   desarrollable. **NO hay una cola finita de 28** — el pozo es **generativo** (los mismos pilares dan años
   de contenido).
2. **El operador PRODUCE bajo demanda**: elige un ángulo, elige un canal, desarrolla — **pieza = ángulo ×
   canal**. Una a una; nada se produce solo. El mismo ángulo se lleva a varios canales (Etapa D integrada).
3. **Agendar es un paso APARTE** (Agenda `/agenda`): las piezas producidas/aprobadas se asignan a un
   día/hora/canal (`scheduled_posts`). El calendario NO nace lleno de un plan calculado — se llena con lo
   que el operador agenda.

**Configuración por pieza** (C17): gancho = el ángulo ELEGIDO (2.5, sin rotación) · canal = el ELEGIDO
(decide formato + doctrina por canal C3) · apertura (FORMA molde + ESCENA visual) = el operador la afina
(Cerebro de Ganchos; el molde ENMARCA, C17.1) · voz/personaje/identidad = del kit + identidad firmada.

**Decisiones del operador que sobreviven a C17:**
- **Producir en lote** («desarrolla mi semana»): un botón que dispara el develop de las piezas AGENDADAS de
  los próximos 7 días (~5-7 llamadas). La aprobación sigue pieza a pieza. (Pendiente de build.)
- **Cada pieza nace canal-específica** (el canal decide formato + doctrina). Un ángulo a varios canales ES
  el modelo base, no un extra.
- **La Agenda muestra el ESTADO** de cada pieza agendada (◐ borrador → ● lista → ✓ publicada). El estado
  vive en la pieza; la agenda le pone fecha.

## 2. Qué vive en Identidad

### 2.1 Identidad visual (el artefacto 2.0.5 se mantiene; cambia el hogar y gana firma)

- Paleta · estilo · mood · composición · motivos · tipografía · do/dont — igual que hoy.
- **Gana firma formal SOLO la identidad visual** (`GateSignature`, patrón G-Phase-X): es la FUNDACIÓN que TODA pieza hereda y cambiarla obliga a reprocesar → sign-once-governs-all. Sin firma, los gates de Producción no abren. **Los personajes y sets NO se firman** (§2.2 — son biblioteca viva, no fundación).
- **UX educacional con 3 rutas** al entrar (decisión del operador):
  1. **«Ya tengo marca»** → importar (URL / CSS / PDF / logo / colores) → Papandi la lee y **da feedback educado** (contraste, coherencia con el avatar, legibilidad) — nunca la acepta muda.
  2. **«No tengo nada»** → co-crear: Papandi propone desde los OBJETIVOS del proyecto + el avatar (psicología del color por audiencia/sector) — **cada color y tipografía CON su porqué** (glass-box; el porqué es citable).
  3. **«Tengo piezas sueltas»** (un logo, un color) → subir lo que hay + completar co-creando.
- Educación = micro-lección en el momento de la decisión (patrón beat del wizard, P1/P5) — jamás pantallas de teoría.

### 2.2 Bibliotecas unificadas: PERSONAJES y SETS (decisión del operador: unificar y linkear)

Reemplazan el `set_kit` singular actual:

```
identity/cast (artefacto compartido del proyecto)
├── personajes[]  { id, nombre, image_url (durable), source: generada|subida,
│                   voz (descriptor), aprobado, prompt (si generada — glass-box) }
├── sets[]        { id, nombre, image_url (durable), source, aprobado, prompt }
├── default_personaje_id · default_set_id   ← los defaults de MARCA
```

- **Generar con IA o subir** (ambas — reusa `rodaje-generate` + re-host durable al bucket).
- **Selección con foto-chips** en campaña/pieza: "elige tu personaje" (las caras) · "elige tu set" (los lugares).
- **Cascada de resolución: pieza > campaña > default de marca.** La campaña puede traer variante temática (ej. personaje con bandera del 4 de Julio) con aprobación previa — ver spec de campañas (R1 §3).
- **Varios sets/personajes: soportado nativo** (era la pregunta del operador — sí vale la pena; el modelo es N de cada uno con defaults).
- **NO se firman ni se bloquean (aclaración del operador 2026-07-06):** la biblioteca es VIVA — agregar/quitar/cambiar personajes y sets es libre en todo momento, sin re-firmar nada. El flag `aprobado` de un asset NO es una firma de fase: es solo "esta imagen está lista para mandar a Kling" (calidad), reversible cuando quieras. Se firma la FUNDACIÓN (colores/tipografía §2.1); la biblioteca se curó, no se congela.
- **Migración**: el `set_kit` actual (personaje+set+voz singulares) se convierte en el primer elemento de cada biblioteca + defaults. Sin pérdida.

## 3. Los gates que Identidad habilita (tabla R3, aprobada)

| Tipo de pieza | Gate |
|---|---|
| Video (Reel/TikTok/Short) | **Duro**: identidad firmada + personaje aprobado (kit) |
| Imagen / carrusel / pin / Stories | **Duro**: identidad visual firmada |
| LinkedIn / Blog | **No bloquea**: media default ON; sin identidad → sale solo-texto con aviso glass-box |
| Email / Reddit / Grupos FB / X | **Sin gate** (texto-nativo; la media RESTA — confirmado con data) |

Patrón: `GateSignature` + "Se abre al firmar el paso anterior". El botón Desarrollar de piezas visuales muestra el candado educativo con link a Identidad (ya existe el precedente del kit→video).

## 4. La producción (Ángulos) después de esta fase

- Pierde: los strips de definición (identidad y rodaje) → quedan como **resumen readonly** con link "editar en Identidad".
- Gana foco: **Ángulos** = el taller (ángulos por pilar → desarrollar → aprobar → generar); **Media** = la
  galería de todo lo creado (la biblioteca que pidió el operador).

## 5. Implementación (fases del build, tras la firma de esta spec)

1. **B1** — Modelo `identity/cast` + migración del `set_kit` + cascada de resolución en produce/video-generate (leer default; override por pieza llega con selección UI).
2. **B2** — Página `identity/` (ciclo renumerado en "Tu camino"): identidad visual con firma + 3 rutas + bibliotecas con foto-chips. Estudio → resúmenes readonly.
3. **B3** — Gates por tipo según §3 (extiende el candado existente kit→video).
4. UX bajo `spec_UX_Experience` (P1 una cosa a la vez · P2 progreso · P5 glass-box · P6 co-creación con autoría).

## 6. Verificación

- Migración: proyecto con `set_kit` existente → cast con 1 personaje + 1 set + defaults, cero pérdida (test).
- Cascada: pieza sin override usa default de marca; con override de campaña usa el de campaña (tests puros).
- Gates: pieza de video sin personaje aprobado → candado con link; email nunca bloqueado (tests + verificación visual del operador en prod).
- `npm run verify` verde por sub-fase; deploy continuo.

## 6b. Doctrina transversal — FIRMADO ES VISIBLE (corrección del operador 2026-07-06)

**Aplica a TODAS las fases (0/1/2/Identidad), no solo a esta** — pendiente reflejar también en `spec_UX_Experience`:

> Firmar = candado de **EDICIÓN** (editar re-abre la conversación y re-procesa los datos). NUNCA candado de **LECTURA**. Todo lo firmado se ve como **vista humana read-only, SIEMPRE legible sin re-firmar**.

Estado actual (bug de UX detectado): en Fase 2 el paso firmado ES un `<details>` colapsado por defecto — la vista read-only existe pero está escondida, y el operador cree que la única forma de verla es "Enmendar" (que sí edita). Olvida lo que firmó. Fix: el paso firmado muestra un **resumen legible aunque esté colapsado** (los titulares de lo firmado), expandir da la vista completa read-only, y **"Enmendar" queda como acción SEPARADA y explícita** (nunca el único camino para leer). El operador debe poder releer todo lo firmado sin riesgo de re-procesar. Esta fase Identidad nace ya con este patrón; las fases 0-2 se corrigen en un sweep aparte.

## 7. Fuera de alcance de esta spec

- Campañas (spec propia, de R1) — solo se honra aquí el punto de enganche (override de personaje/set por campaña).
- Personalización de video con botones (catálogo R2) — spec/etapa G.
- TTS/voz clonada (descartado: audio nativo de Kling, decisión firme).
