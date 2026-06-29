# AI Gateway / Wrapper — PROPUESTA (stub)

**Project**: business/marketing-os
**Status**: **PENDIENTE — a desarrollar** (stub capturado para no perderlo; NO codear hasta firmar). Origen: sesión Estudio 2026-06-28.
**Decisión de alcance:** spec **APARTE** de `spec_Admin_Cost_Intelligence.md` (Módulo C). El Gateway es **integración** (la mecánica de llamar a los proveedores); el **costo/billing/catálogo-al-día** vive en Módulo C. Se cruzan, no se duplican.
**Consumidor:** `spec_Estudio_Produccion_Publicacion.md` §4 (el Estudio pide "genera esto" y el Gateway resuelve).

---

## Por qué existe
El Estudio genera imágenes/videos/texto vía varios proveedores (FLUX, Seedream, Nano Banana, Runway, Veo, Kling…). Cada uno tiene su forma de llamarlo, sus límites, su formato. El Gateway es **la capa única** que el Estudio usa, para no casarnos con un proveedor y poder enrutar por precio/calidad/disponibilidad.

## Qué debe contener (índice a desarrollar)
0. **Propósito** + relación con Módulo C (costos) y el Estudio (consumidor).
1. **Interfaz única** del wrapper: `generate(asset_type, brief, mode, endpoint?) → asset` — contrato que el Estudio consume sin saber del proveedor.
2. **Catálogo de endpoints** (los servicios disponibles) y **cómo se mantiene al día** (servicios nuevos salen seguido).
3. **Adapter por proveedor** — cómo se construye cada request y sus **peculiaridades**: auth, formato de entrada/salida, params, límites, watermark, latencia, políticas.
4. **Onboarding de un nuevo modelo/proveedor** — el checklist para añadir un adapter (probar precio/calidad → adapter → registrar en catálogo → promover desde Módulo C).
5. **Routing:** default por caso de uso + "elige tu engine" (C5-avanzada) + BYO/BYOK.
6. **Failover / reintentos / timeouts** entre proveedores.
7. **Normalización de salida** (formatos, tamaños) + entrega a la **biblioteca** (Estudio §5).
8. **Medición de costo por llamada** → ledger de **Módulo C** (alimenta el COGS por usuario y el pricing del Estudio §9).
9. **Políticas por proveedor** (contenido, caras de personas, uso comercial) — el Gateway las conoce y enruta/avisa.
10. **Pendientes / decisiones abiertas.**

## Tareas
- Registrada en pretel-os como tarea pendiente (ver `task_list`).
