# El pipeline de ideas — de dónde sale todo lo que ves en el Estudio

*Respuestas del sistema a las preguntas del operador (2026-07-06). Cada afirmación es verificable en el código citado.*

## ¿De dónde salen las ~28 ideas por avatar?

Son los **derivados de 2.4** (hoy "Multiplicación" — renombre pendiente). Cuando generaste 2.4, el LLM recibió como entrada TU trabajo firmado:

| Entrada | De dónde | Qué aporta |
|---|---|---|
| Pilares | 2.3 (construidos desde las fuerzas del avatar 0.3) | El dolor/tema de cada grupo de piezas |
| Canales firmados | 2.2 (`channels_declared`) | Los ÚNICOS canales donde caen ideas |
| Keywords medidas | 0.2 (DataForSEO) | Demanda real, no inventada |
| Oferta | 1.x (statement/estrategia) | Hacia dónde apunta el cierre |

Con eso produjo, POR PILAR: **1 pieza ancla** (long-form) + **5-6 derivados**, cada uno con `kind` (canal × formato, elegido de TUS canales de 2.2 — por eso cada idea ya trae canal asignado) y `note` (la idea concreta planificada). 4 pilares × ~7 ≈ **28 ideas, POR AVATAR**.

Código: `app/api/phase2/step-proposal/route.ts` (la generación de 2.4 recibe pilares + canales + keywords) · `lib/schemas/content-plan.ts` (`AtomizationMap`).

## ¿Por qué 28 ideas si hay ~40 ganchos de marca por avatar?

Porque hoy **la unidad de producción es el derivado** (la idea planificada con canal), y los ganchos de la biblioteca 2.5 **rotan como aperturas** sobre esas ideas: al desarrollar el derivado N de un pilar, abre con el gancho `N mod (ganchos del pilar)` — vencidos jamás, estacionales en ventana primero (`rotateHook` en `lib/estudio/brief.ts`).

La evolución acordada (Etapa D del plan): el **gancho como centro** — cada gancho de marca será desarrollable directamente a cualquier canal habilitado, sin esperar a que la rotación lo alcance. Los ganchos **no se consumen**: se re-expresan; dos piezas del mismo gancho varían la manera de decirlo.

## «Qué se DICE al abrir» — ¿viene de mi biblioteca (2.5/2.6)?

**Sí.** La sustancia de cada pieza ES tu gancho firmado: viaja al prompt como `GANCHO de apertura: "…"`. El catálogo de 4,550 plantillas solo aporta la **forma retórica** opcional de vestirlo (`FORMA RETÓRICA ELEGIDA … RELLÉNALA con EL DOLOR del proyecto — la plantilla aporta solo la FORMA`). Lo que estaba roto era la **UI**: nunca te mostraba tu gancho, así que parecía ignorado. (Fix en Etapa C: la card lo mostrará siempre.)

Código: `app/api/estudio/produce/route.ts` + `lib/estudio/prompts.ts` (`buildDevelopSystem`, bloques GANCHO y FORMA RETÓRICA).

## ¿Y cuando se acaban los 28 de un avatar?

1. Los **ganchos no se gastan** — rotan y se re-formulan (con historial anti-repetición, Etapa D).
2. El calendario ya avisa cuando la cola se agota; se añadirá el botón **«Multiplicar más piezas»** que re-corre la propuesta 2.4 (una llamada, disparada por ti).

## La memoria del Estudio (Etapa A, ya construida)

Las 5 formas sugeridas y tus elecciones (forma retórica + apertura visual + objetivo) se **persisten** en `distribution/estudio/hook_suggestions` (artefacto por avatar):

- Abrir el modal muestra lo guardado — **$0**.
- Solo se llama al LLM si esa combinación (pilar × derivado × objetivo) **nunca se pidió**.
- **«Dame otras 5»** es la única acción que fuerza una llamada nueva (reemplaza esa entrada).
- Tu elección sobrevive recargas y viaja con la pieza al desarrollar.
- Cada llamada queda registrada con costo real en `project_llm_calls` (visible en el futuro panel admin).

Código: `lib/estudio/estudio-choices.ts` (+ tests) · `app/projects/[projectId]/estudio/page.tsx`.
