# Spec — Fase «Identidad» (nueva fase del ciclo de vida)

**Estado:** v1 borrador — para firma del operador antes de construir (Etapa B del plan de control 2026-07).
**Decide:** dónde se DEFINE la identidad de marca (visual + personajes + sets + voz del personaje), cómo se educa al definirla, y qué gates habilita en Producción.
**Fuentes:** decisiones del operador (rondas 1-3, 2026-07-06) · `docs/research/doctrina-por-canal.md` (gates) · `docs/research/campanas-marketing-real.md` (overrides por campaña) · `spec_UX_Experience.md` (P1-P7) · `spec_Estudio_Produccion_Publicacion.md` §3.8 (Estudio = taller + biblioteca).

---

## 0. La tesis

**Identidad = donde DEFINES (una vez, con firma) · Estudio = el TALLER (produces) + la BIBLIOTECA (todo lo creado).**

Es el patrón de la industria (Canva Brand Kit, HubSpot brand settings, Adobe Express: la definición de marca vive aparte del editor) y es lo que la propia `spec_Estudio §3.8` ya firmó: "Pieza aprobada → biblioteca de assets → cola de publicación". Hoy la identidad visual y el Set de Rodaje viven como strips DENTRO del Estudio — definición mezclada con producción. Esta fase los separa.

## 1. El ciclo de vida queda

```
Fundación (F0) → Oferta (F1) → Contenido (F2, cierra en 2.6)
   → IDENTIDAD (nueva)
   → PRODUCCIÓN (Estudio: taller + galería)
   → DISTRIBUCIÓN (calendario/publicación) → MEDICIÓN → AJUSTE
```

- El **evergreen NO se inicia**: nace al firmar 2.4/2.6 (el plan finito ya agendado en el calendario ES el always-on). Identidad es el único paso entre firmar el plan y producirlo.
- Las **campañas se OFRECEN** después (radar/lanzamiento) — jamás son requisito.

## 2. Qué vive en Identidad

### 2.1 Identidad visual (el artefacto 2.0.5 se mantiene; cambia el hogar y gana firma)

- Paleta · estilo · mood · composición · motivos · tipografía · do/dont — igual que hoy.
- **Gana firma formal** (`GateSignature`, patrón G-Phase-X): sin firma, los gates de Producción no abren.
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
- **Migración**: el `set_kit` actual (personaje+set+voz singulares) se convierte en el primer elemento de cada biblioteca + defaults. Sin pérdida.

## 3. Los gates que Identidad habilita (tabla R3, aprobada)

| Tipo de pieza | Gate |
|---|---|
| Video (Reel/TikTok/Short) | **Duro**: identidad firmada + personaje aprobado (kit) |
| Imagen / carrusel / pin / Stories | **Duro**: identidad visual firmada |
| LinkedIn / Blog | **No bloquea**: media default ON; sin identidad → sale solo-texto con aviso glass-box |
| Email / Reddit / Grupos FB / X | **Sin gate** (texto-nativo; la media RESTA — confirmado con data) |

Patrón: `GateSignature` + "Se abre al firmar el paso anterior". El botón Desarrollar de piezas visuales muestra el candado educativo con link a Identidad (ya existe el precedente del kit→video).

## 4. El Estudio después de esta fase

- Pierde: los strips de definición (identidad y rodaje) → quedan como **resumen readonly** con link "editar en Identidad".
- Gana foco: **taller** (ideas por pilar → desarrollar → aprobar → generar) + **galería** de todo lo creado (la biblioteca que pidió el operador).

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

## 7. Fuera de alcance de esta spec

- Campañas (spec propia, de R1) — solo se honra aquí el punto de enganche (override de personaje/set por campaña).
- Personalización de video con botones (catálogo R2) — spec/etapa G.
- TTS/voz clonada (descartado: audio nativo de Kling, decisión firme).
