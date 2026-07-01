# Healthy Families

Bucket: business  
Status: Active  
Created: 2026-06-18  
Objective: Construir el producto completo de forma autónoma vía MCPs (Supabase + Vercel), módulo a módulo, verificando TODO E2E antes de darlo por hecho (build → server local 4000 → navegador → push → smoke en prod) y limpiando siempre los datos de prueba. Modelo de negocio: suscripción por HOGAR dentro de la familia extendida (titular adulto cubre 4 plazas = cuentas registradas; plaza extra $10/año; plan Dúo para abuelos; admin ≠ titular — gobernanza separada de facturación). Stripe + Resend se dejan para el cierre final (bloqueos externos juntos).

## Description

App familiar con IA para que las familias se conozcan y se quieran mejor. Núcleo emocional (no logístico como Cozi): pregunta del día en espejo + racha familiar, juegos intergeneracionales "Conoce a tu familia" (la abuela juega sin cuenta), diario privado que escucha y va perfilando a cada quien, reto semanal generado desde los perfiles, tareas y puntos para niños con premios pactados, calendario relacional (cumpleaños derivados del árbol + recordatorios proactivos con los gustos del cumpleañero), legado y cápsulas de memoria, grupos privados dentro de la familia extendida (función 85) y red personal privada (amigos/ex separados de la familia, función 22). Privacidad ESTRUCTURAL por RLS: el contenido de cada persona (diario, respuestas, perfil IA) jamás sale al compartir. Toda la IA pasa por un único gateway cognitivo. Incluye consola de operación /admin para el operador (coste IA, almacenamiento/disco, negocio, soporte sin contenido, inspector de prompts) y un harness de QA agéntico (actores LLM autónomos + auditores deterministas + inyección de escenario multi-día). En español primero (mercado hispano vacío; canal WhatsApp), luego EE.UU. Repo: https://github.com/pr3t3l/Healthy-Families-2026 · Producción: https://healthy-families-2026.vercel.app · Supabase: pcbkmptcmkxcghajtlln · Vercel: prj_Ov9NnVkdc2KJX2EWchT758L6Od8X.

## Stack

- Next.js 16 (Turbopack, App Router)
- Tailwind 4
- next-intl (en default / es)
- Supabase: Postgres + RLS + Edge Functions (Deno) + Vault + pg_cron
- ai-gateway único (OpenRouter, google/gemini-2.5-flash), schemas zod blandos
- Vercel (deploy automático desde main)
- web-push (PWA, sin app stores en MVP)
- Stripe + Resend (pendientes, M07)

## Skills

- None registered

## Current State

- Status: Active
- Phase: Initial

## Key Decisions

(none yet)

## Notes

(add as project evolves)
