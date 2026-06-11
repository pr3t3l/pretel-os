# Spec — UX Experience (la experiencia ES el producto)

**Project**: business/marketing-os · **Status**: v1.0 (research 2026-06-10) · **Aplica a**: `sandia-marketing` (toda pantalla, todo flujo)
**Norte del operador:** "como los iPhone — la experiencia de usuario es el principal goal. Que cada página tenga lo que necesita para seguir el flow entre fases, fácil de entender."
**Relación con la doctrina:** este spec NO inventa principios nuevos — nombra la ciencia detrás de lo que `SOUL_setup_agent.md` y `spec_Phase_0_Setup_Agent.md` ya mandan, y lo vuelve **buildable** (tokens, duraciones, patrones de pantalla). Si contradice al SOUL, el SOUL gana.

---

## 0. La tesis

El usuario de Sandi es **el experto en lo suyo que ya está abrumado** (persona D-025). Su fricción digital va de media (Marcus/Priya) a ALTA (Héctor: "yo trabajo con las manos, no con computadoras"). Para él, la UX no es estética: **es la diferencia entre terminar Phase 0 o abandonar en el paso 2.** Cada principio de abajo existe para proteger una sola cosa: **el flow entre fases** — que el usuario siempre sepa dónde está, qué sigue, y por qué.

## 1. Los 7 principios (ciencia → aplicación en Sandi)

### P1 — Una cosa a la vez (chunking)
*Ciencia:* dividir en pasos manejables reduce carga cognitiva; "one thing per screen" sube completion.
*En Sandi:* cada pantalla del wizard = **UN beat de conversación + UNA decisión**. Las 4 preguntas de 0.1 son 4 momentos, no un formulario de 4 campos. El centro de la pantalla nunca tiene dos preguntas activas. Revelación progresiva: lo avanzado (signal rules, specs) vive en el panel derecho, colapsado por defecto.

### P2 — Progreso visible y dotado (Zeigarnik + goal-gradient + endowed progress)
*Ciencia:* las tareas incompletas crean tensión que trae al usuario de vuelta (Zeigarnik); la motivación acelera cerca de la meta (goal-gradient); una barra que arranca pre-llenada motiva más que una en cero (endowed progress).
*En Sandi:* "Paso N de M" SIEMPRE visible (ya está en el guion del Setup Agent). El rail izquierdo muestra el lifecycle completo (0→5) con la fase actual encendida — el mapa del viaje entero. **Endowed:** al crear proyecto, la barra ya muestra "Fundación iniciada" (el primer tramo encendido). **Zeigarnik como retención:** al salir a mitad de fase, el email/badge de retorno nombra lo INCOMPLETO ("tu ICP quedó a 1 paso de cerrar"), nunca genérico.

### P3 — Feedback inmediato (la regla de los 100ms)
*Ciencia (HIG):* confirmación visual <100ms; lag >250ms correlaciona con abandono de sesión.
*En Sandi:* todo tap/click responde <100ms (estado visual optimista; el guardado real va detrás). Chip **"Borrador guardado"** (ya en el mockup) tras cada respuesta — el usuario NUNCA teme perder trabajo. Cuando Sandi "piensa" (research, LLM): **nunca spinner mudo** — narración de progreso en voz Sandi ("Buscando cuánta gente busca esto…"), porque la espera narrada se siente más corta y es glass-box.

### P4 — Movimiento con física (el sistema de motion)
*Ciencia (HIG/Material):* micro-feedback 100–200ms; navegación entre pantallas 200–250ms; cambios complejos ≤300ms. Entra con ease-out, sale con ease-in, transforma con ease-in-out. Continuidad por elemento compartido (el elemento viaja, no parpadea). Un solo sistema de motion para toda la app.
*En Sandi (tokens):*
| Token | Valor | Uso |
|---|---|---|
| `--motion-tap` | 120ms ease-out | botones, chips, selección de opción |
| `--motion-step` | 220ms ease-out (entra) / 180ms ease-in (sale) | transición entre sub-pasos del wizard (slide direccional: avanzar = →, volver = ←) |
| `--motion-panel` | 240ms ease-in-out | panel derecho, colapsos |
| `--motion-celebrate` | 400ms spring suave | cierre de gate (única excepción >300ms — es el pico) |
*Regla:* la dirección del movimiento SIEMPRE coincide con la dirección del flow (avanzar desliza hacia adelante). El stepper y el contenido comparten continuidad (el sub-paso activo "se expande" al centro — shared element).

### P5 — Glass-box visible, no invasiva
*Ciencia:* la confianza nace de entender el porqué; la transparencia reduce la ansiedad de caja negra (y es mandato D-018/SOUL).
*En Sandi:* toda conclusión de Sandi lleva su **chip de origen** ("📊 SBA 2025" / "💭 inferencia mía — corrígeme"). El panel derecho ("De dónde sale") muestra fuente→razonamiento→jerga-en-simple, colapsable, nunca obligatorio. Las inferencias se VEN distintas de los datos (estilo visual propio). Jerga: oculta por defecto; términos técnicos aparecen con traducción inline al hover/tap (educación adaptativa: si `user_knowledge_profile` sube, la traducción se atenúa).

### P6 — Co-creación con autoría (SDT: autonomía + competencia + relación)
*Ciencia:* la motivación durable viene de autonomía (yo decido), competencia (estoy aprendiendo) y relación (alguien me acompaña) — SDT; el "investment" del usuario en el producto crea valor almacenado que fideliza (Hooked).
*En Sandi:* toda propuesta de Sandi llega como **tarjeta de propuesta** con tres acciones de un toque: ✓ Aceptar · ✏️ Ajustar · ✕ Descartar (etiquetada "propuesta", con su porqué). Los gates se cierran con **ritual de firma** (acción deliberada, no un "next" más — es SU decisión, queda registrada con su nombre). El brief/avatares crecen A LA VISTA del usuario (panel "tu fundación" que se va llenando): su inversión acumulada es visible y suya — eso es fidelización estructural, no gamification pegada.

### P7 — Pico-final + recompensa variable
*Ciencia:* la memoria de una experiencia = su pico + su final (peak-end rule); las recompensas variables sostienen el regreso (Hooked) — y en Sandi la variabilidad es INTRÍNSECA y honesta: cada research trae hallazgos genuinamente distintos.
*En Sandi:* cada sub-paso cierra con una **victoria nombrada** ("Tu puerta quedó en piedra: 3 filtros, 2 anti-señales") + qué desbloqueó. Cada cierre de fase = momento celebrate (motion 400ms + resumen de lo construido). La recompensa variable legítima: **"mira lo que encontré"** — los hallazgos del research de Sandi (el espejo M1, el hueco de precio) se presentan como descubrimientos, porque LO SON. Prohibido fabricar variabilidad falsa (honestidad arquitectónica).

## 2. El patrón de pantalla canónico (cada página tiene lo que necesita para el flow)

Toda pantalla de fase responde 4 preguntas SIN scroll: **¿dónde estoy?** (rail lifecycle + "Paso N de M") · **¿qué me pide?** (un beat, una decisión) · **¿de dónde sale?** (panel glass-box) · **¿qué sigue?** (CTA primario único + lo que desbloquea).

```
┌─ rail lifecycle ─┬──────── centro ────────────┬─ panel derecho ─┐
│ 0 Research ●     │ Paso 2 de 5                │ De dónde sale   │
│   0.1 ✓          │ [beat de Sandi: 2-3 frases]│ (colapsable)    │
│   0.2 ← actual   │ [LA decisión: opciones     │ · fuente        │
│ 1 Oferta ○       │  sugeridas / tarjeta de    │ · razonamiento  │
│ ...              │  propuesta accept/edit]    │ · jerga simple  │
│                  │ [CTA →  + "borrador ✓"]    │ · decisiones    │
└──────────────────┴────────────────────────────┴─────────────────┘
```

- **Beat de Sandi** = los 6 movimientos en UI: captura/reflejo (texto corto), punto ciego (tarjeta flag SOLO si lo hay — calibrado), pregunta (controles), mostrar trabajo (chips fuente + panel), co-crear (tarjeta de propuesta).
- **Apertura de fase (USER-CORRECTED 2026-06-11):** al entrar a una fase por primera vez, el primer beat es su apertura canónica (Setup Agent spec §2b: de dónde venimos → qué responde esta fase → por qué importa → qué decides tú) — pantalla/beat propio, sin pregunta encima. La apertura queda **fija en el panel glass-box** como "¿Qué es esta fase?". Misma regla a nivel instrumento: si la pantalla muestra un score, el panel lleva su sección "¿Cómo se calcula?" y el beat lo introduce ANTES de mostrar números.
- **Capas de audiencia (USER-CORRECTED 2026-06-11):** tres capas, sin fugas entre ellas. (1) **Flujo principal** = lenguaje llano, una decisión — lo que TODO usuario entiende sin diccionario. (2) **Panel de apoyo** = profundidad opcional para el curioso ("¿Qué es esta fase?", "¿De dónde sale?", "¿Cómo se calcula?") — sigue siendo lenguaje de usuario, nunca obligatorio. (3) **Admin** (Módulo C) = la maquinaria técnica: modelos, costos por llamada, prompts, tablas. **Nombres de archivos, tablas, modelos e infraestructura NUNCA aparecen en las capas 1-2.** Regla de prueba: si Dana (la repostera) no lo entendería, no va en capa 1; si no le sirve para decidir mejor, tampoco en capa 2.
- El mockup de Claude Design (zip) aporta el chrome (rail/topbar/panel/tokens); este patrón aporta el ALMA conversacional. **Fusión, no reemplazo.** Anti-meta del Setup Agent spec: estructura sin los 6 movimientos = Typeform, no Sandi.

## 2c. El hub del proyecto (dashboard — mandato del operador 2026-06-11, D-034)

Hoy el proyecto aterriza directo en el wizard de fase — las cosas importantes quedan "enterradas" dentro de los pasos. **El proyecto necesita un hub**: una pantalla home donde el usuario ve su negocio completo de un vistazo y navega a todo. Contenido mandatado:

1. **Tus avatares, al frente** — tarjeta por avatar con su estado (🟢 activo y en qué fase va · ⚪ en banca con su trabajo de Fase 0 intacto) y la acción **"Encender este público"** visible AHÍ (no enterrada en el paso 0.3). El avatar activo enlaza a su loop (oferta→contenido→publicar→medir→ajustar).
2. **Puntos importantes siempre a la vista** — las decisiones clave firmadas, sin re-navegar los pasos: tu cliente ideal (beachhead), el precio sugerido (cuando 1.4 lo firme), el posicionamiento elegido, el nombre. Son el "resumen ejecutivo" vivo del proyecto.
3. **Métricas y resultados de las fases siguientes** — cuando Phase 3-5 corran: analíticas, resultados por avatar/estrategia, señales abiertas. El hub es donde el dueño VE su marketing funcionar (KPI primario = dinero, no likes).
4. La **Fundación (Fase 0)** queda accesible como sección cerrada/firmada (revisitable, enmendable — nunca trampa).

Regla de jerarquía: el hub responde "¿cómo va mi negocio y qué sigue?"; el wizard responde "¿qué decido ahora?". No se mezclan.

**Naming (doctrina del operador, mismo D-034):** nombres comunes del marketing > metáforas inventadas — "Tu cliente ideal" (no "Tu puerta"), "Tus avatares" (no "Tus personas"), "Tu competencia" (no "Tu cancha", ya renombrado). La jerga PROFUNDA sigue oculta (TAM/SAM, awareness levels); el término común del oficio sí se usa y se enseña.

## 3. Anti-patrones (never-dos de UX)

- ❌ Dos preguntas activas en una pantalla. ❌ Muro de texto (>4 frases por beat).
- ❌ Spinner mudo >400ms (siempre narración). ❌ Jerga sin traducción a un toque.
- ❌ Modal que interrumpe el flow para pedir algo que puede esperar. ❌ Perder trabajo del usuario (todo es draft persistente).
- ❌ Urgencia/escasez fabricada, badges falsos, confirmshaming — **prohibido por sistema** (honestidad arquitectónica, CONSTITUTION del producto).
- ❌ Animación >300ms fuera del momento celebrate. ❌ Movimiento que contradice la dirección del flow.
- ❌ Mostrar un score/puntuación antes de enseñar el instrumento que lo produce (qué mide, escala, cómo se combina, umbrales). Un número sin instrumento es jerga numérica.

## 4. Métricas de que la UX funciona (se miden desde V1)

- **Completion rate de Phase 0** (norte: >60% de quien crea proyecto cierra 0.1; benchmark interno a calibrar).
- Time-to-first-insight (<3 min desde signup hasta el primer "mira lo que encontré").
- Drop-off por sub-paso (el embudo del wizard — dónde se cae la gente).
- Retorno post-abandono (¿el Zeigarnik trigger funciona?).
- Feedback <100ms en interacciones (perf budget técnico).

## Fuentes

- [Apple HIG](https://developer.apple.com/design/human-interface-guidelines/) + [Designing Fluid Interfaces (WWDC18)](https://developer.apple.com/videos/play/wwdc2018/803/) — direct manipulation, feedback <100ms, momentum.
- [Material/duraciones y easing](https://courseux.com/ui-animations/) + [5 Rules for Motion in UI Transitions](https://www.equal.design/blog/5-rules-for-motion-in-ui-transitions) — 150/200-250/300ms, ease-out/in/in-out, shared elements.
- [Progress bar psychology (Userpilot)](https://userpilot.com/blog/progress-bar-psychology/) + [Zeigarnik effect (LogRocket)](https://blog.logrocket.com/ux-design/zeigarnik-effect/) — goal-gradient, endowed progress, open loops.
- [Hooked model (Amplitude)](https://amplitude.com/blog/the-hook-model) + [Variable rewards (Userpilot)](https://userpilot.com/blog/variable-rewards/) — trigger/action/variable reward/investment.
- Convergencia con doctrina propia: SOUL (pico-final = peak-end; nunca jerga; ruptura-reparación), Setup Agent spec (reconocer>recordar = recognition over recall; Paso N de M; calibración de flags), D-017 (SDT = lealtad), D-018 (co-creación = investment).
