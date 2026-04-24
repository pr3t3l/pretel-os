# Module 1: Infrastructure Setup

## What
Fresh Ubuntu 24.04 (dual-boot) setup as always-on development server. All services operational: Postgres 16 + pgvector, Docker, n8n, LiteLLM proxy, Tailscale, Cloudflare Tunnel.

## Deviation from original plan
Original plan assumed WSL-to-Ubuntu migration with data backup/restore. Actual execution: fresh Ubuntu install on new partition (dual-boot). No WSL data to migrate — services rebuilt from scratch. n8n workflows and Postgres data will be imported from WSL backup when available.

## Inputs
- Ubuntu 24.04 Desktop installed on 240GB partition
- Tailscale account (prettelv1@gmail.com)
- Cloudflare account with existing tunnel config
- API keys for Anthropic, OpenAI, Gemini (in password manager)
- n8n workflow exports (from WSL, if available)

## Outputs
- All services running via systemd (auto-start on boot)
- Backup script tested with verified restore drill
- Runbook documenting full setup

## Constraints
- No secrets in git (CONSTITUTION §3.4)
- All timeouts declared in infra/timeouts.yaml (INTEGRATIONS §1.4)
- Backup encrypted at rest (CONSTITUTION §3.5)
