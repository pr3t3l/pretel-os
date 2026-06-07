# run/ — instancias trabajadas de la metodología

Esta carpeta guarda **runs**: instancias concretas de aplicar la metodología de marketing-os a un producto real (o de prueba). Distinto de `specs/` (la metodología abstracta).

Cada run es la "memoria" de un proyecto pasando por las fases 0→5, con sus artefactos (`business_context.json`, `buyer_persona.json`, `avatars.json`, `offer_spec.json`, …).

**Doble propósito:**
- Ejemplo trabajado (candidato a **ejemplo CAG** del Setup Agent — ver `specs/spec_Phase_0_Setup_Agent.md` §1).
- **Fixture de eval** para probar el sistema contra un caso real.

**Runs:**
- `sandi/` — el primer run: Sandi mismo (el sistema usándose a sí mismo). Estado en `sandi/run_log.md`.

> Nota: estos artefactos siguen **[Evolving Schema]** (Overall_WF §Pattern C) — son la semilla v1 de ESTE build; otros clientes/modelos traerán enfoque distinto. `schema_version` + `metadata` permiten que crezcan con el uso.
