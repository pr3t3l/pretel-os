# Campañas — plan de prueba desde la UI (aceptación, CM1-CM5)

> Para el operador. Sigue los bloques EN ORDEN (el estado se va construyendo). Cada paso trae su
> **✅ Esperado** — si no pasa, es un bug (dime el bloque.paso). Prueba en **papandi.com**. Base:
> `spec_Campanas.md` + `build_plan_campanas.md`. Módulo en prod 2026-07-09.

## Antes de empezar (requisitos)
- [ ] Un proyecto con **Fase 2 firmada** (voz 2.0 · pilares 2.3 · ganchos 2.5) de al menos un avatar — sin
      eso, /angulos no tiene ángulos y no hay nada que atar.
- [ ] Idealmente un pilar que **«pide»** (modo reforzar) y otro que **«da valor»** — los verás como badge en
      la tarjeta del ángulo. Los necesitas para el Bloque 5 (CM4).
- *(El «hoy» y las fechas usan tu zona horaria local.)*

---

## Bloque 0 — Evergreen es el default (la base, SIN tocar campañas)
Primero confirma que lo de siempre sigue intacto.
- [ ] **0.1** En **/angulos**, desarrolla un ángulo cualquiera (sin elegir campaña). **✅ Esperado:** se
      desarrolla normal, **sin** chip de campaña en la tarjeta.
- [ ] **0.2** Ve a **/media**. **✅ Esperado:** la pieza aparece **sin** chip de campaña; con el filtro
      **Evergreen** (si existe) sale; el módulo Campañas no afecta nada de lo evergreen.

---

## Bloque 1 — Crear la campaña (CM1 + CM2)
- [ ] **1.1** En el nav lateral aparece **«Campañas»** (icono megáfono). Clic → **/campanas**.
      **✅ Esperado:** carga la página «Tus campañas» + la nota de Evergreen.
- [ ] **1.2** Clic **«＋ Nueva campaña»**. **✅ Esperado:** se abre el formulario.
- [ ] **1.3** Llena: **Nombre** (ej. «Prueba Julio»), **Tipo = Evento**, **Día del evento** (una fecha ~2-3
      semanas adelante), **Concepto** (1 frase), **Oferta** (ej. «20% con código TEST»). Clic **«Crear y
      proponer el arco →»**. **✅ Esperado:** la campaña aparece en la lista y se abre su **tablero** con un
      **arco** (Teaser · Pico · Cierre) lleno de huecos «por desarrollar».
- [ ] **1.4** Mira el arco. **✅ Esperado:** 3 columnas; **Teaser** con badge **«da valor»**, **Pico** y
      **Cierre** con **«pide»**; cada hueco con una fecha DENTRO de la ventana; el pico cae el día del evento.
- [ ] **1.5** *(Tipo Custom)* Crea otra con **Tipo = Custom**. **✅ Esperado:** aparecen campos **Inicio** y
      **Fin**; la ventana usa TUS fechas. *(Nota conocida: una custom se guarda como «evento» internamente —
      el label del tablero dirá «tipo: evento». Es cosmético.)*

---

## Bloque 2 — El tablero es interactivo (CM2)
En el tablero de tu campaña:
- [ ] **2.1** En un hueco, cambia el **canal** (el select de arriba). **✅ Esperado:** cambia y queda
      guardado (recarga la página → sigue el cambio).
- [ ] **2.2** En un hueco, cambia el **ángulo** (el select con los ganchos 2.5). **✅ Esperado:** cambia el
      texto del ángulo y persiste.
- [ ] **2.3** Clic la **✕** de un hueco. **✅ Esperado:** el hueco desaparece.
- [ ] **2.4** Clic **«＋ añadir pieza»** en una fase. **✅ Esperado:** aparece un hueco nuevo en esa fase.
- [ ] **2.5** Clic **«Activar»**. **✅ Esperado:** el estado pasa a **«activa»** (verde). Clic **«Desactivar»**
      → vuelve a **«borrador»**. (Déjala **activa** para el siguiente bloque.)
- [ ] **2.6** Mira el **medidor de ratio** abajo. **✅ Esperado:** muestra dar:pedir del arco + una barra.

---

## Bloque 3 — Atar/desarrollar desde Ángulos (CM3a — el corazón)
Con la campaña **activa**:
- [ ] **3.1** Ve a **/angulos**. **✅ Esperado:** arriba aparece un selector **«Desarrollar para: Evergreen
      (default) | Campaña ▾»** con tu campaña en la lista.
- [ ] **3.2** Elige tu **campaña** en el selector. **✅ Esperado:** aparece en rojo «lo que desarrolles se ata
      aquí».
- [ ] **3.3** Desarrolla un ángulo (cualquiera, ~1 min). **✅ Esperado:** toast «…atada a la campaña»; la
      **tarjeta del ángulo** gana un **chip con el color y nombre** de la campaña.
- [ ] **3.4** Vuelve a **/campanas** → tu campaña. **✅ Esperado:** esa pieza ya aparece en el tablero bajo su
      fase (como pieza **real**, no hueco punteado).

---

## Bloque 4 — El reflejo en Media y Agenda (CM3b + CM3c)
- [ ] **4.1** En **/media**, usa el filtro **«Campaña»** → elige tu campaña. **✅ Esperado:** la pieza atada
      sale, con su **chip de color**. Cambia a filtro **«Evergreen»** → la pieza de campaña **NO** sale (solo
      las evergreen, como la del Bloque 0).
- [ ] **4.2** En **/agenda**, abre un día **dentro de la ventana** de la campaña. En «Agendar aquí» elige tu
      pieza de campaña (debe estar **producida/aprobada** — apruébala en su drawer si hace falta).
      **✅ Esperado:** al agendar, ese día muestra una **banda de color** arriba (a lo largo de los días de la
      ventana), la píldora agendada lleva un **cuadrito del color** de la campaña, y el rail derecho lista
      **«Campañas del mes»**.

---

## Bloque 5 — El develop se escribe DISTINTO en campaña (CM4 — lo sutil)
La fase se infiere del ángulo: **«pide» → pico** · **«da valor» → teaser**.
- [ ] **5.1** *(el pedir)* En **/angulos**, con la **campaña elegida**, desarrolla un ángulo cuyo badge diga
      **«pide»**. Abre la pieza y **lee el cierre**. **✅ Esperado:** el CTA/cierre **usa tu oferta** («20% con
      código TEST») **+ el deadline real** (fin de la ventana), con urgencia honesta (last-call). Y la pieza
      **respira el concepto** de la campaña.
- [ ] **5.2** *(el dar)* Desarrolla un ángulo cuyo badge diga **«da valor»** (teaser). Lee la pieza.
      **✅ Esperado:** construye **expectativa** hacia la campaña / el concepto; **NO** vende la oferta ni mete
      deadline.
- [ ] **5.3** *(el default)* Cambia el selector a **Evergreen** y desarrolla el mismo tipo de ángulo. Compara.
      **✅ Esperado:** la versión evergreen **no** mete concepto de campaña ni oferta/deadline — se escribe como
      siempre. (Esa diferencia = CM4 funcionando.)

---

## Bloque 6 — El ciclo (CM5)
- [ ] **6.1** *(auto-cierre)* Crea una campaña **Custom** con **Fin = ayer** (fecha pasada). **✅ Esperado:** en
      la lista/tablero se muestra **«cerrada»** automáticamente, y **no** ofrece Activar/Desactivar.
- [ ] **6.2** *(ganchos expiran)* Ve a **/angulos**. **✅ Esperado:** esa campaña cerrada **NO** aparece en el
      selector «Desarrollar para» (no puedes atar piezas nuevas a una campaña terminada).

---

## Bloque 7 — Limpieza (y la vuelta a evergreen)
- [ ] **7.1** En el tablero de una campaña de prueba, clic **«Eliminar»** → confirma. **✅ Esperado:** la
      campaña desaparece; sus piezas **vuelven a evergreen** (verifícalo en /media: ya sin chip, y salen en el
      filtro Evergreen).

---

## Resumen de qué prueba cada bloque
| Bloque | Milestone | Qué valida |
|---|---|---|
| 0 | — | Evergreen es el default (nada se rompió) |
| 1 | CM1 + CM2 | crear campaña + arco propuesto + tipos (evento/lanzamiento/custom) |
| 2 | CM2 | tablero editable + activar/desactivar + ratio |
| 3 | CM3a | **atar desde Ángulos** (el hilo `campaign_id`) |
| 4 | CM3b + CM3c | reflejo en Media (filtro/chip) + Agenda (banda/chips) |
| 5 | CM4 | el develop inyecta concepto + oferta + deadline real (vs evergreen) |
| 6 | CM5 | auto-cierre por ventana + ganchos expiran |
| 7 | — | eliminar → piezas vuelven a evergreen |
