# Module 1 Runbook: Infrastructure Setup

## Date: 2026-04-23

## Environment
- Machine: ASUS Vivobook S 15 S5506MA
- OS: Ubuntu 24.04 Desktop (dual-boot with Windows)
- Partition: 240GB (nvme0n1p6)
- RAM: 16GB
- CPU: Intel (check /proc/cpuinfo)

## Deviation from original plan
Original tasks.md assumed WSL→Ubuntu migration. Actual: fresh Ubuntu install as dual-boot.
No WSL data migrated in this pass — services rebuilt clean.

## Services installed

| Service | Version | Status | Port | Auto-start |
|---------|---------|--------|------|------------|
| Ubuntu | 24.04.4 LTS | Running | — | Yes |
| Tailscale | 1.96.4 | Connected (100.94.235.92) | — | Yes |
| Docker | 29.4.1 | Running | — | Yes (systemd) |
| Postgres 16 | 16.13 | Running | 5432 | Yes (systemd) |
| pgvector | 0.6.0 | Installed | — | — |
| LiteLLM | 1.83.13 | Configured (keys pending) | 4000 | Yes (user systemd) |
| n8n | latest | Running | 5678 | Yes (docker restart) |
| cloudflared | (pending install) | .deb at /tmp/cloudflared.deb | — | Pending |
| Node.js | 22.x | Installed | — | — |
| Python | 3.12.3 | Installed | — | — |
| Claude Code | 2.1.119 | Installed | — | — |

## Tailscale
- IP: 100.94.235.92 (changed from WSL 100.80.39.23)
- Account: prettelv1@gmail.com

## Pending items (operator action required)
1. Install cloudflared: `sudo dpkg -i /tmp/cloudflared.deb`
2. Enable user-services on boot: `sudo loginctl enable-linger pretel`
3. Replace LiteLLM API keys in ~/.env.litellm, then start service: `systemctl --user start litellm`
4. Configure Cloudflare Tunnel:
   - `cloudflared tunnel login`
   - `cloudflared tunnel create pretel-os`
   - configure `/etc/cloudflared/config.yml` with ingress rules
   - `sudo cloudflared service install`
5. Replace n8n credentials in ~/n8n/.env (currently `admin` / `changeme_replace_this`)
6. Import n8n workflows from WSL export (via n8n UI at http://127.0.0.1:5678)
7. Generate GPG key for backup encryption: `gpg --gen-key` (use `backup@pretel` as email)
8. Smoke-test Forge pipeline after n8n workflows imported
9. Update SESSION_RESTORE.md with new Tailscale IP

## Sleep/suspend
Masked: sleep.target, suspend.target, hibernate.target, hybrid-sleep.target

## Backup
- Script: ~/dev/pretel-os/infra/backup/pg_backup.sh
- Timer: daily at 02:00 via systemd user timer (pretel-os-backup.timer)
- Encryption: GPG (key pending creation — backups currently unencrypted)
- Test run (2026-04-23): SUCCESS against `postgres` db, file at ~/backups/pretel-os-db/pretel_os_20260423_230333.dump (unencrypted, GPG key pending)
