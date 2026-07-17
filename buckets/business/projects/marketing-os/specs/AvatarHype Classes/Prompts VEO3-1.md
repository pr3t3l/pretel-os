# Prompts VEO3.1

## 1) Formato y tipo de vídeo

- formato: `9:16`
- dispositivo: `iPhone front-camera selfie`
- tipo de captura: `handheld`
- objetivo visual: `hyper-realistic`, `casual UGC`, `not cinematic`

Ejemplo

```jsx
A hyper-realistic 9:16 handheld iPhone front-camera selfie video.
```

Empezamos con instrucciones visuales claras de cámara y estilo, y 9:16 es especialmente adecuado para TikTok, Reels y Shorts.

---

## 2) Identidad del personaje

- edad aproximada
- nacionalidad / tipo de español
- aspecto general
- si hay referencia: que **la identidad coincida exactamente**

**Ejemplo:**

```
The exact same woman from the provided reference images. Identity, face, skin texture, hair, and outfit must match perfectly at all times.
```

Google también recomienda usar referencias visuales y flujos guiados por imágenes para mejorar consistencia.

---

## 3) Entorno

- lugar
- hora del día
- tipo de luz
- ambiente general
- si debe coincidir con un frame de referencia

**Ejemplo:**

```
Outdoor modern residential area with palm trees and light-colored buildings. Natural daylight only. Slightly imperfect lighting. No cinematic look.
```

Definiciones muy concretas.

---

## 4) Acción principal

- 1 acción principal + 1 micro-acción secundaria

**Ejemplo:**

```
She is lightly jogging while recording herself in selfie mode and speaking naturally to camera.
```

Un clip de 8 segundos no es para meter 5 acciones.

---

## 5) Física humana

Este bloque es clave en UGC porque el mayor fallo suele ser el movimiento falso.

- ritmo natural
- pequeños errores
- microshake
- respiración
- rebote vertical
- movimientos no repetitivos

**Ejemplo:**

```
She moves in a completely natural human way: slight vertical bounce, subtle side-to-side sway, natural shoulder movement, inconsistent micro-movements, and breathing that subtly affects motion and speech.
```

No vale con decir natural, el prompt tiene que definir que significa “natural”

---

## 6) Idioma y forma de hablar

Importante especificar idioma, en español de España sobretodo para que no lo haga con acento latino.

**Ejemplo:**

```jsx
Use informal conversational Spanish as spoken in Spain.  
The phrasing, rhythm, and wording must feel like a real casual conversation between people in Spain.

Include natural filler words and imperfections typical in Spain, such as:
- “a ver…”
- “es que…”
- small pauses and hesitations

Avoid neutral or generic Spanish phrasing.
```

```jsx
She speaks in authentic Castilian Spanish from Spain, with natural rhythm, slight hesitations, and informal cadence typical of real speech. Not Latin American Spanish.
```

---

## 7) Tono emocional

Esto controla si parece anuncio, actriz, o persona real.

**Qué poner:**

- calm
- confident
- reflective
- casual
- not selling
- not performing

**Ejemplo:**

```
Tone: calm, reflective, slightly confident, like talking to someone while exercising, not performing and not selling anything.
```

---

## 8) Script

- corto
- fácil de pronunciar
- con pausas reales
- pensado para 8 segundos

---

## 9) Comportamiento

Este bloque define **cómo habla mientras hace la acción**.

- empieza a hablar ya en marcha
- mira fuera de cámara un momento
- parpadea
- respira
- se recoloca
- no parece ensayado

**Ejemplo:**

```
She keeps jogging during the entire clip, starts speaking slightly mid-thought, blinks naturally, briefly glances away, and has subtle pauses between phrases.
```

---

## 10) Cámara

En UGC este bloque cambia todo.

- handheld
- off-center framing
- no stabilization
- autofocus shifts
- rolling shutter
- phone handling artifacts

**Ejemplo:**

```
Handheld iPhone selfie, slightly off-center framing, natural micro-shake from movement, minor autofocus adjustments, rolling shutter effect, no stabilization.
```

---

## 11) Luz

La luz demasiado perfecta mata el UGC.

**Ejemplo:**

```
Natural daylight only, slight exposure changes while moving, soft uneven shadows.
```

---

## 12) Audio

Google recomienda describir diálogo, ambiente y efectos de sonido.

- raw iPhone microphone
- light wind
- distant traffic
- breathing
- no music

**Ejemplo:**

```jsx
Audio: raw iPhone microphone, light wind, distant ambient outdoor noise, audible breathing, no music.
```

---

## 13) Negative prompt

Sirve para decirle al modelo lo que **NO** quieres.

**Ejemplo:**

```jsx
Negative prompt: studio lighting, beauty filter, perfect skin, ad-like polish, exaggerated gestures, robotic delivery, over-sharpening, artificial background, unnatural motion, flicker.
```

---

## 14) Start frame / End frame

Si hay referencias, este bloque es de los más potentes.

Google soporta **first frame** y **last frame** para guiar la transición entre ambos estados.

**Ejemplo:**

```jsx
START FRAME
Matches the first reference image: she is already jogging in selfie mode wearing sunglasses.

END FRAME
Matches the second reference image: she has removed the sunglasses and is slightly closer to camera while still jogging.
```

## Plantilla

```jsx
**A hyper-realistic 9:16 handheld iPhone front-camera selfie video.

[CHARACTER]
The exact same [man/woman] from the provided reference images. Identity, face, skin texture, hair, and outfit must match perfectly at all times.

[GOAL]
The goal is maximum realism. The video must feel like a real casual UGC selfie, not AI-generated.

[ENVIRONMENT]
[Describe exact location, lighting, time of day, and background.]

[ACTION]
The subject is [main action] while speaking naturally to camera.

[HUMAN MOTION]
Movement must feel completely natural and human:
- [bounce]
- [sway]
- [micro-movements]
- [breathing]
- [non-repetitive motion]

[LANGUAGE]
The subject speaks in authentic Castilian Spanish from Spain, with natural rhythm, slight hesitations, and informal cadence. Not Latin American Spanish.

[TONE]
[calm / confident / reflective / casual / not selling / not performing]

[SCRIPT]
“[insert script]”

[BEHAVIOUR]
- [keeps moving]
- [starts speaking naturally]
- [blinks]
- [brief glance away]
- [small pauses]
- [subtle facial motion]

[CAMERA]
- handheld iPhone selfie
- slightly off-center framing
- natural micro-shake
- minor autofocus shifts
- no stabilization

[LIGHTING]
- natural daylight only
- slight exposure changes
- soft uneven shadows

[AUDIO]
- raw phone microphone
- light ambient noise
- natural breathing
- no music

[NEGATIVE PROMPT]
studio lighting, beauty filter, perfect skin, ad-like polish, exaggerated gestures, robotic** 
```


