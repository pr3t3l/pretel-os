# docs/app — documentación de la implementación (Papandi / sandia-marketing)

Estos documentos describen **cómo está construida** la app desplegada (repo de código
`sandia-marketing`, en producción en papandi.com). Consolidados aquí desde
`sandia-marketing/docs/` el 2026-07-06 — pretel-os es el hogar único de toda la
documentación (doctrina, specs, investigación e implementación).

| Documento | Qué es |
|---|---|
| `ensamblador-de-prompts.md` | El compilador de dos etapas (fuente firmada → prompt → media): inventario campo-por-campo de las fases 0/1/2, gaps creado/usado/faltante, y los 10 fixes priorizados. |
| `pipeline-de-ideas.md` | De dónde salen las ~28 ideas del Estudio (derivados 2.4), por qué 28 y no 80, y cómo la biblioteca de ganchos 2.5 abre cada pieza. |
| `design-system.md` | El sistema de diseño de la app (tokens, paleta watermelon, tipografía). |
| `design-audit-2026-07.md` | Auditoría de diseño de las 11 rutas + chrome. |
| `model-selection.md` | Ruteo de modelos LLM por tarea (rationale + benchmark). |
| `archive/` | Notas de ejecución históricas. |

**Doctrina y specs del producto** (el "qué y por qué") viven en `../` (`specs/`, `docs/research/`,
`docs/BMC/`, `docs/Marketing Documentacion Teorica/`). Regla: *"qué y por qué" = specs/research ·
"cómo está construido" = docs/app*.
