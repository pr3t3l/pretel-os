# pretel-os — Tasks

**Status:** Phase 0 closing (foundation complete, pre-commit). Phase 1 next.
**Owner:** Alfredo Pretel Vargas
**Last updated:** 2026-04-19
**Location in repo:** `/tasks.md` (root level)

This document is the atomic task list. It is the source of truth for "what to do next" at any moment. If you open a new chat, search this file for the first unchecked `[ ]` — that's where you are. Each task has a "Done when" line that is objectively checkable.

Rules for this document:

- **Check boxes only when Done-When passes.** No "mostly done." No partial credit.
- **Never delete a task.** If a task becomes obsolete, strike through and note why. Git history preserves it anyway.
- **Never estimate time.** If you want to jot a note about complexity, use "confidence" (low/medium/high) instead.
- **Every task points to its authority.** If a task derives from a CONSTITUTION rule, a DATA_MODEL section, or an ADR, reference it in square brackets.
- **New tasks get appended at the end of their module.** Do not insert mid-list — breaks the ordering.

---

## Index

- [Phase 0: Foundation commit](#phase-0-foundation-commit)
- [Pre-Module 1: Repo setup](#pre-module-1-repo-setup)
- [Module 1: infra_migration](#module-1-infra_migration)
- [Module 2: data_layer](#module-2-data_layer)
- [Module 3: mcp_server_v0](#module-3-mcp_server_v0)
- [Module 4: router](#module-4-router)
- [Module 5: telegram_bot](#module-5-telegram_bot)
- [Module 6: reflection_worker](#module-6-reflection_worker)
- [Module 7: skills_migration](#module-7-skills_migration)
- [Module 8: lessons_migration](#module-8-lessons_migration)
- [Continuous operations](#continuous-operations)

---

## Phase 0: Foundation commit

Goal: All foundation artifacts live in the `pr3t3l/pretel-os` repo, tagged `foundation-v1.0`.

### P0.T1 — Create the repo

- [x] **P0.T1.1** Create private GitHub repo `pr3t3l/pretel-os` via GitHub web UI.
  - Done when: `https://github.com/pr3t3l/pretel-os` returns a 200 and shows an empty repo.
- [x] **P0.T1.2** Clone the empty repo locally to the working directory of choice (suggest `~/dev/pretel-os` on Asus Rock).
  - Done when: `git status` inside the clone returns "nothing to commit."
- [x] **P0.T1.3** Initialize basic repo hygiene files.
  - Create `.gitignore` with at minimum: `.env`, `.env.*`, `!.env.*.example`, `__pycache__/`, `*.pyc`, `.venv/`, `node_modules/`, `*.log`, `/fallback-journal/`, `/transcripts/`.
  - Create `README.md` with a 5-line description pointing to `CONSTITUTION.md`, `plan.md`, `tasks.md`, `docs/`, `SESSION_RESTORE.md`.
  - Create `LICENSE` file — operator's choice (suggest "All rights reserved" for personal repo, or MIT if you ever plan to share skills publicly).
  - Done when: `.gitignore`, `README.md`, `LICENSE` exist at repo root.

### P0.T2 — Populate foundation docs

- [x] **P0.T2.1** Copy `CONSTITUTION.md` to repo root.
  - Done when: `git status` shows `CONSTITUTION.md` as new file.
- [x] **P0.T2.2** Copy `plan.md` to repo root.
  - Done when: `git status` shows `plan.md` as new file.
- [x] **P0.T2.3** Copy `tasks.md` (this file) to repo root.
  - Done when: `git status` shows `tasks.md` as new file.
- [x] **P0.T2.4** Copy `SESSION_RESTORE.md` to repo root.
  - Done when: `git status` shows `SESSION_RESTORE.md` as new file.
- [x] **P0.T2.5** Create `docs/` directory and move the 4 content foundation docs there.
  - `docs/PROJECT_FOUNDATION.md`
  - `docs/DATA_MODEL.md`
  - `docs/INTEGRATIONS.md`
  - `docs/LESSONS_LEARNED.md`
  - Done when: `ls docs/` shows all 4 files.
- [x] **P0.T2.6** Copy `CHANGELOG_AUDIT_PASS_3.md` to `docs/audits/CHANGELOG_AUDIT_PASS_3.md` and create `docs/audits/README.md` pointing to it.
  - Done when: `docs/audits/` has both files.
- [x] **P0.T2.7** Copy `AUDIT_PROMPT_GPT.md` and `AUDIT_PROMPT_GEMINI.md` to `docs/audits/prompts/`.
  - Done when: `docs/audits/prompts/` has both files.

### P0.T3 — Verify cross-references survive the move

- [x] **P0.T3.1** Grep for `DATA_MODEL §` in all files under the repo. Verify every reference still resolves to a real section.
  - Done when: `grep -r "DATA_MODEL §" .` output is fully reviewed; any broken references fixed.
- [x] **P0.T3.2** Grep for `CONSTITUTION §` similarly.
  - Done when: `grep -r "CONSTITUTION §" .` output is fully reviewed; any broken references fixed.
- [x] **P0.T3.3** Grep for `INTEGRATIONS §`, `PROJECT_FOUNDATION §`, `LESSONS_LEARNED §` similarly.
  - Done when: all references fully reviewed.

### P0.T4 — First commit + tag

- [x] **P0.T4.1** Stage all foundation files: `git add -A`.
  - Done when: `git status` shows all expected files staged.
- [x] **P0.T4.2** Commit with message from the CHANGELOG.
  - Suggested message body (copy from CHANGELOG section "Commit foundation al repo"):
    ```
    feat: foundation v1.0 — SDD documents for pretel-os personal cognitive OS

    Five foundation documents after 3-round adversarial audit:
    - CONSTITUTION v4: 44 immutable rules, 5 layers, 4 workers, source priority
    - PROJECT_FOUNDATION v3: 8-module roadmap, 19 ADRs, 8 productized services
    - DATA_MODEL v3: 21 tables, partitioned logs, pgvector + lifecycle funcs
    - INTEGRATIONS v2: 10 services, MCP auth Phase 1 required, UptimeRobot
    - LESSONS_LEARNED v1: Process doc + 10 seed lessons + migration plan for 89

    Audit Pass 3 applied 19 fixes across 4 priority buckets.
    See docs/audits/CHANGELOG_AUDIT_PASS_3.md for full change log.

    Co-audited with: GPT-5.4, Gemini 3.1 Pro, Claude Opus 4.7
    ```
  - Done when: `git log -1` shows the commit with this message.
- [x] **P0.T4.3** Tag the commit as `foundation-v1.0`.
  - Command: `git tag -a foundation-v1.0 -m "Foundation v1.0 — audit-hardened SDD foundation"`
  - Done when: `git tag -l foundation-v1.0` returns the tag.
- [x] **P0.T4.4** Push branch and tags to origin.
  - Commands: `git push origin main && git push origin foundation-v1.0`
  - Done when: tag visible on GitHub under "Releases" or "Tags."

**Exit Phase 0** — all of P0.T1 through P0.T4 checked.

---

## Pre-Module 1: Repo setup

Goal: Repo has a working skeleton before any module work begins.

### PM1.T1 — Add pre-commit hooks

- [x] **PM1.T1.1** Decide hook framework: native git `.git/hooks/pre-commit` shell script or the `pre-commit` Python framework.
  - Recommendation: use the `pre-commit` framework — it handles multi-hook composition, easier to add hooks later, shareable if you ever open-source.
  - Done when: decision noted here (strikethrough the unused option).
- [x] **PM1.T1.2** Create `.pre-commit-config.yaml` at repo root with three hooks:
  - `pre-commit-token-budget` — scans `identity.md`, `buckets/*/README.md`, `buckets/*/projects/*/README.md`, `skills/*.md` against budgets per CONSTITUTION §2.3.
  - `pre-commit-scout-safety` — scans any file under `buckets/scout/` against `scout_denylist` patterns loaded from a local YAML mirror of the DB table.
  - `pre-commit-env-scan` — blocks commits of files matching `*.env*` (except `*.env.*.example`) or containing `sk-ant-` / `sk-proj-` / `sk-litellm-` patterns outside example files.
  - Done when: `.pre-commit-config.yaml` committed.
- [x] **PM1.T1.3** Write each hook script under `infra/hooks/`:
  - `infra/hooks/token_budget.py` — uses `tiktoken` with `cl100k_base` encoding.
  - `infra/hooks/scout_safety.py` — reads patterns from `infra/hooks/scout_denylist.yaml` (this file is mirror of DB, operator-maintained, not committed if it contains sensitive patterns — use example file for repo).
  - `infra/hooks/env_scan.py` — regex-based scanner.
  - Done when: all three scripts exist, executable, and run successfully on a dummy commit.
- [x] **PM1.T1.4** Install hooks locally via `pre-commit install`.
  - Done when: `.git/hooks/pre-commit` exists as a link/copy from pre-commit framework.
- [x] **PM1.T1.5** Test each hook with a deliberately bad file.
  - Create `test-file.md` with a synthetic secret → env_scan blocks commit → remove file → commit succeeds.
  - Create `buckets/scout/test.md` with a denylist pattern → scout_safety blocks → remove → commit succeeds.
  - Create `identity.md` that exceeds 500 tokens → token_budget blocks → trim → commit succeeds.
  - Done when: all 3 block/pass cycles verified.

### PM1.T2 — Add CI for the same hooks

- [x] **PM1.T2.1** Create `.github/workflows/pre-commit.yml` that runs pre-commit on every PR.
  - Done when: file committed and a test PR triggers the workflow.
- [x] **PM1.T2.2** Add `.github/workflows/markdown-lint.yml` (optional but useful) — catches broken links and inconsistent heading levels.
  - Done when: workflow passes on current repo state.

### PM1.T3 — Create the skeleton directory structure

- [x] **PM1.T3.1** Create placeholder directories with `.gitkeep` files (git does not track empty directories):
  - `specs/.gitkeep`
  - `identity.md` (placeholder — will be populated in Module 3)
  - `AGENTS.md` (placeholder — will be populated in Module 3)
  - `buckets/personal/README.md` (placeholder with "TBD in Module 3")
  - `buckets/business/README.md` (placeholder)
  - `buckets/scout/README.md` (placeholder)
  - `skills/.gitkeep`
  - `templates/.gitkeep`
  - `src/.gitkeep`
  - `migrations/.gitkeep`
  - `infra/systemd/.gitkeep`
  - `infra/backup/.gitkeep`
  - `infra/monitoring/.gitkeep`
  - `runbooks/.gitkeep`
  - `exports/.gitkeep`
  - `.env.pretel_os.example` (copy from INTEGRATIONS §13 template)
  - Done when: `tree -L 2` matches the target structure in `plan.md §3`.
- [x] **PM1.T3.2** Create `infra/timeouts.yaml` with all values from INTEGRATIONS §1.4 table.
  - Done when: file committed, every timeout named in INTEGRATIONS is present as a key.
- [x] **PM1.T3.3** Commit skeleton with message "chore: repo skeleton per plan.md §3".
  - Done when: commit on main.

### PM1.T4 — Copy SDD templates

- [x] **PM1.T4.1** Copy the 10 SDD templates from `pr3t3l/sdd-system` into `templates/`.
  - Command: `git clone --depth 1 https://github.com/pr3t3l/sdd-system /tmp/sdd && cp /tmp/sdd/templates/* templates/ && rm -rf /tmp/sdd`.
  - Done when: `templates/` has the 10 template files (spec.md, plan.md, tasks.md templates + any others).
- [x] **PM1.T4.2** Commit templates with message "chore: import SDD templates from pr3t3l/sdd-system".
  - Done when: commit on main.

**Exit pre-Module 1** — all of PM1.T1 through PM1.T4 checked. Repo is now ready for module work.

---

## Module 1: infra_migration

Goal: Vivobook runs Ubuntu 24.04 Desktop as an always-on server. All prior services (n8n, Postgres 16, LiteLLM, Tailscale, cloudflared, Forge pipeline) operational on the new OS. WSL retired.

Authority: `docs/PROJECT_FOUNDATION.md §4 Module 1`, `docs/INTEGRATIONS.md`.

### M1.T1 — Write the module spec

- [x] **M1.T1.1** Create `specs/infra_migration/spec.md` from `templates/spec.md`.
  - Fill: What (new OS + service migration), Why (stability + systemd-ready), Inputs (existing WSL state + service configs), Outputs (new Ubuntu install + verified services), Constraints (no data loss, no Forge regression), Failure modes (hardware failure, config drift, credential loss).
  - Done when: spec.md complete, reviewed by a self-check "would another LLM understand this in a new chat?".
- [x] **M1.T1.2** Create `specs/infra_migration/plan.md` with phases: Phase A (backup + inventory), Phase B (OS install), Phase C (core services reinstall), Phase D (application migration), Phase E (verification + cutover).
  - Done when: plan.md has all 5 phases with gates.
- [x] **M1.T1.3** Create `specs/infra_migration/tasks.md` from `templates/tasks.md` — the per-module atomic task list. This file (the top-level `tasks.md`) only mirrors high-level M1 tasks; deep atomic detail lives in `specs/infra_migration/tasks.md`.
  - Done when: module tasks.md exists with all tasks from M1.T2 through M1.T10 expanded.

### M1.T2 — Pre-migration backup (no cuts yet)

- [ ] **M1.T2.1** Inventory all services currently on the Vivobook.
  - Command: `docker ps -a > /tmp/docker_inventory.txt` on the Vivobook.
  - Command: `systemctl --user list-units --type=service > /tmp/systemd_user_inventory.txt`.
  - Command: `sudo systemctl list-units --type=service > /tmp/systemd_system_inventory.txt`.
  - Command: `crontab -l > /tmp/cron_inventory.txt` (and `sudo crontab -l` for root if any).
  - Done when: all 4 inventory files exist on Vivobook.
- [ ] **M1.T2.2** Export n8n workflows to JSON.
  - Per INTEGRATIONS §9.10 procedure: `curl -H "X-N8N-API-KEY: $N8N_API_KEY" "http://127.0.0.1:5678/api/v1/workflows?active=true" > ~/n8n_export_$(date +%Y%m%d).json`.
  - Done when: export JSON file exists and is non-empty.
- [ ] **M1.T2.3** Dump all Postgres databases.
  - Command: `pg_dumpall -U postgres -f ~/postgres_full_dump_$(date +%Y%m%d).sql` or per-database `pg_dump -Fc` for each.
  - Done when: dump files exist, size sanity-checked against `psql -c '\l+'` expected sizes.
- [ ] **M1.T2.4** Back up `~/.litellm/config.yaml`, `~/.env*`, `/etc/cloudflared/`, `/etc/n8n/` or wherever live configs reside.
  - Command: `tar -czf ~/config_backup_$(date +%Y%m%d).tar.gz ~/.litellm/ ~/.env* /etc/cloudflared/ 2>/dev/null`.
  - Done when: tarball exists, contents verified via `tar -tzf`.
- [ ] **M1.T2.5** Copy ALL backup artifacts to THREE locations.
  - Location 1: external USB drive plugged into Vivobook.
  - Location 2: Asus Rock via Tailscale `rsync` or `scp`.
  - Location 3: Supabase Storage via rclone (encrypted): `gpg --encrypt --recipient backup@pretel --output full_backup.tar.gz.gpg && rclone copy full_backup.tar.gz.gpg supabase-storage:backups/pre-m1/`.
  - Done when: all 3 locations have the same backup set, verified by checksum comparison.
- [ ] **M1.T2.6** Test restore of one component from each backup location.
  - Pick the smallest database, restore to a scratch DB on the Vivobook (before reinstall), verify row counts match.
  - Done when: restore drill successful, noted timestamp in `runbooks/module_1_infra_migration.md` (which you create for this purpose — the runbook grows as you go).

### M1.T3 — Hardware preparation

- [x] **M1.T3.1** Verify Vivobook has Ubuntu 24.04 Desktop ISO on bootable USB.
  - Download ISO from ubuntu.com, verify SHA256 against official, flash to USB via Rufus (Windows) or `dd` (Linux).
  - Done when: boot into USB successfully (BIOS → F2/Del, boot order USB).
- [x] **M1.T3.2** Decide disk layout.
  - Recommendation: single LUKS-encrypted root + /home partition. Encrypt at rest — required for INTEGRATIONS §1.3 credential storage policy.
  - Decision noted in `runbooks/module_1_infra_migration.md`.
- [x] **M1.T3.3** Note down ALL BIOS settings and current network config before wiping.
  - Screenshot BIOS screens (phone camera), document IP/DNS settings, any Wi-Fi network credentials.
  - Done when: documentation exists and is stored with backups (not on Vivobook).

### M1.T4 — OS install

- [x] **M1.T4.1** Boot Vivobook from Ubuntu USB, run installer with full disk encryption.
  - Create operator user `operator` (or chosen name), set strong password (stored in password manager).
  - Done when: Ubuntu desktop boots to login screen.
- [x] **M1.T4.2** First-boot basics: `sudo apt update && sudo apt upgrade -y && sudo apt install -y curl wget git vim build-essential tmux htop net-tools`.
  - Done when: all packages installed without error.
- [x] **M1.T4.3** Disable automatic sleep/suspend (this is a server now).
  - Command: `sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target`.
  - Also: Settings → Power → Screen Blank: Never, Automatic Suspend: Off.
  - Done when: `systemctl status sleep.target` shows "masked."
- [x] **M1.T4.4** Configure `operator` user for auto-login (so unattended reboot works).
  - Edit `/etc/gdm3/custom.conf` → `AutomaticLoginEnable = true`, `AutomaticLogin = operator`.
  - Done when: reboot test — server comes back up to a logged-in session.
- [x] **M1.T4.5** Set timezone and NTP.
  - Command: `sudo timedatectl set-timezone America/New_York && sudo timedatectl set-ntp true`.
  - Done when: `timedatectl status` shows correct timezone and NTP synchronized.

### M1.T5 — Reinstall Tailscale

- [x] **M1.T5.1** Install Tailscale.
  - Command: `curl -fsSL https://tailscale.com/install.sh | sh`.
  - Done when: `tailscale --version` returns a version.
- [x] **M1.T5.2** Authenticate Tailscale.
  - Command: `sudo tailscale up`.
  - Follow browser prompt, authenticate with operator's Google account.
  - Done when: `tailscale status` shows the Vivobook online and reachable from the Asus Rock.
- [x] **M1.T5.3** Confirm the tailnet IP is stable (should be `100.80.39.23` or the node's prior IP; may change — that's OK, update references in INTEGRATIONS if so).
  - Command: `tailscale ip -4`.
  - Done when: IP noted, INTEGRATIONS updated if needed (commit amendment).

### M1.T6 — Install Docker

- [x] **M1.T6.1** Install Docker Engine per official Ubuntu instructions.
  - Follow `https://docs.docker.com/engine/install/ubuntu/` exactly. Don't use the apt-version — it's outdated.
  - Done when: `docker --version` and `docker compose version` return versions.
- [x] **M1.T6.2** Add `operator` user to `docker` group so you don't need `sudo` for docker commands.
  - Command: `sudo usermod -aG docker operator && newgrp docker`.
  - Done when: `docker ps` works without sudo.
- [x] **M1.T6.3** Enable Docker to start at boot.
  - Command: `sudo systemctl enable docker`.
  - Done when: `systemctl status docker` shows "enabled."

### M1.T7 — Reinstall Postgres 16 + pgvector

- [x] **M1.T7.1** Install Postgres 16.
  - Command: `sudo apt install -y postgresql-16 postgresql-contrib-16`.
  - Done when: `sudo systemctl status postgresql` shows active.
- [x] **M1.T7.2** Install pgvector extension.
  - Command: `sudo apt install -y postgresql-16-pgvector`.
  - Done when: `sudo -u postgres psql -c "CREATE EXTENSION IF NOT EXISTS vector;" test_db` succeeds (create `test_db` first).
- [x] **M1.T7.3** Configure Postgres for local access.
  - Edit `/etc/postgresql/16/main/postgresql.conf`: `listen_addresses = 'localhost'` (no remote access — MCP server connects via localhost).
  - Edit `/etc/postgresql/16/main/pg_hba.conf`: set `local all operator md5` for operator user connections.
  - Restart: `sudo systemctl restart postgresql`.
  - Done when: `psql -h localhost -U operator -d postgres -c '\l'` prompts for password and succeeds.
- [ ] **M1.T7.4** Restore the n8n Postgres dump to a new n8n database (do not touch pretel_os DB yet — that comes in Module 2).
  - Command: `sudo -u postgres createdb n8n && pg_restore -U operator -d n8n ~/postgres_full_dump_*.sql` (or specific n8n dump).
  - Done when: `psql -d n8n -c '\dt'` shows n8n's tables.

### M1.T8 — Reinstall LiteLLM proxy

- [x] **M1.T8.1** Install LiteLLM in a Python venv.
  - Command: `python3 -m venv ~/.venvs/litellm && ~/.venvs/litellm/bin/pip install litellm[proxy]`.
  - Done when: `~/.venvs/litellm/bin/litellm --version` returns a version.
- [ ] **M1.T8.2** Restore `~/.litellm/config.yaml` from backup.
  - Done when: file in place, keys visible (but still encrypted in backup tarball is OK — keys go in `~/.env` per INTEGRATIONS).
- [x] **M1.T8.3** Create systemd user unit for LiteLLM.
  - Path: `~/.config/systemd/user/litellm.service`.
  - Content: ExecStart that activates venv and runs `litellm --config ~/.litellm/config.yaml --port 4000`.
  - EnvironmentFile pointing to `~/.env.litellm`.
  - Done when: `systemctl --user daemon-reload && systemctl --user start litellm` succeeds, `curl -f http://127.0.0.1:4000/health` returns success.
- [x] **M1.T8.4** Enable LiteLLM to start at boot.
  - Command: `systemctl --user enable litellm && sudo loginctl enable-linger operator`.
  - `enable-linger` allows user services to run without login.
  - Done when: reboot test — LiteLLM auto-starts.

### M1.T9 — Reinstall n8n in Docker

- [x] **M1.T9.1** Create `/home/operator/n8n/docker-compose.yml` with the same image version currently running.
  - Check version before reinstall: `docker inspect <n8n-image>` on WSL for exact tag.
  - Volume mount for persistent data: `./n8n_data:/home/node/.n8n`.
  - EnvironmentFile or inline: `N8N_BASIC_AUTH_USER`, `N8N_BASIC_AUTH_PASSWORD`, connection to Postgres `n8n` database.
  - Done when: `docker compose up -d` brings up n8n and `curl -f http://127.0.0.1:5678/healthz` succeeds.
- [ ] **M1.T9.2** Import all n8n workflows from the JSON export.
  - Via n8n UI → Workflows → Import from File.
  - Done when: all workflows visible in the UI, activated state matches pre-migration.
- [ ] **M1.T9.3** Smoke-test the Forge pipeline end-to-end on a known input.
  - Run one Forge job on a test product URL. Verify all 8 phases complete, output matches baseline from pre-migration.
  - Done when: test output captured, no errors, diff against baseline output is acceptable (cost + quality within ±10% is fine).

### M1.T10 — Reinstall Cloudflare Tunnel

- [x] **M1.T10.1** Install `cloudflared` via apt package.
  - Follow official Cloudflare Ubuntu instructions.
  - Done when: `cloudflared --version` works.
- [ ] **M1.T10.2** Restore `/etc/cloudflared/` from backup, including the credentials JSON.
  - Set `/etc/cloudflared/<UUID>.json` permissions to 0600.
  - Done when: `/etc/cloudflared/config.yml` and credentials JSON in place.
- [x] **M1.T10.3** Install cloudflared as systemd service.
  - Command: `sudo cloudflared service install`.
  - Note: MCP server isn't running yet, so the tunnel currently has nothing to tunnel to. That's fine — the ingress rules stay configured.
  - Done when: `sudo systemctl status cloudflared` shows active.
- [x] **M1.T10.4** Verify tunnel comes online (the Cloudflare side).
  - Check Cloudflare dashboard → Zero Trust → Networks → Tunnels → your tunnel shows "HEALTHY" status.
  - Done when: dashboard shows green.

### M1.T11 — Backup discipline test

- [x] **M1.T11.1** Create `infra/backup/pg_backup.sh` from DATA_MODEL §10.1 script.
  - Edit to use correct paths and `pretel_os` DB name placeholder (actual DB created in Module 2; for now the script can target `n8n` DB as a test).
  - Done when: script exists, is executable.
- [x] **M1.T11.2** Create systemd timer for daily backup at 02:00.
  - `infra/systemd/pretel-os-backup.timer` and `infra/systemd/pretel-os-backup.service`.
  - Done when: `systemctl --user list-timers` shows the timer scheduled.
- [x] **M1.T11.3** Run backup manually once. Verify encrypted output file in local backup dir.
  - Command: `~/pretel-os/infra/backup/pg_backup.sh`.
  - Done when: `.dump.gpg` file exists, non-zero size, plaintext dump was deleted per script.
- [ ] **M1.T11.4** Do a restore drill to a scratch database.
  - Create scratch DB, decrypt backup, `pg_restore`, verify row count matches source.
  - Log the drill in `control_registry.restore_drill` (manually into YAML mirror since DB not populated yet — record in runbook).
  - Done when: drill successful, runbook updated.

### M1.T12 — Exit gate verification

- [x] **M1.T12.1** Create `runbooks/module_1_infra_migration.md` if not already.
  - Contents: full step-by-step of what was done, credential rotation notes (if any rotated during migration), any deviations from plan.
  - Done when: runbook exists, covers every task in M1.
- [x] **M1.T12.2** Verify exit gate per `plan.md §6 Module 1`:
  - [ ] Vivobook boots directly into Ubuntu 24.04 Desktop (WSL retired).
  - [ ] All prior services operational on the new OS (checked via per-service health checks).
  - [ ] Forge pipeline runs end-to-end on new setup.
  - [ ] Backup script tested with verified restore drill.
  - [ ] `runbooks/module_1_infra_migration.md` exists.
- [x] **M1.T12.3** Commit Module 1 artifacts with message "feat(M1): infra migration complete — Ubuntu 24.04, WSL retired".
  - Done when: commit on main.
- [x] **M1.T12.4** Tag as `module-1-complete` (optional but helpful for resumption).
  - Done when: tag exists.

**Exit Module 1** — all of M1.T1 through M1.T12 checked.

---

## Module 2: data_layer

Goal: The `pretel_os` database exists with all 16 Phase-1 tables, indexes, functions, triggers, partitions, seeded controls.

Authority: `docs/DATA_MODEL.md` (the authoritative schema), `docs/PROJECT_FOUNDATION.md §4 Module 2`.

### M2.T1 — Write the module spec

- [x] **M2.T1.1** Create `specs/data_layer/spec.md` from template.
  - Done when: spec.md complete.
- [x] **M2.T1.2** Create `specs/data_layer/plan.md` with phases: Phase A (DB creation), Phase B (table migrations 1-16), Phase C (Phase-2 tables 17-21), Phase D (functions + triggers + views), Phase E (partitions + seeds), Phase F (verification).
  - Done when: plan.md complete.
- [x] **M2.T1.3** Create `specs/data_layer/tasks.md` with atomic tasks (mirrors M2.T2 through M2.T10).
  - Done when: tasks.md complete.

### M2.T2 — Create the pretel_os database and user

- [x] **M2.T2.1** Create dedicated DB user for pretel-os.
  - Command: `sudo -u postgres createuser --pwprompt pretel_os` (strong password stored in `.env.pretel_os`).
  - Done when: user exists.
- [x] **M2.T2.2** Create the `pretel_os` database owned by this user.
  - Command: `sudo -u postgres createdb -O pretel_os pretel_os`.
  - Done when: `psql -U pretel_os -d pretel_os -c 'SELECT 1;'` works.
- [x] **M2.T2.3** Update `.env.pretel_os` with the connection string.
  - `DATABASE_URL=postgresql://pretel_os:<password>@127.0.0.1:5432/pretel_os`.
  - Done when: `.env.pretel_os` has correct string, file mode 0600.

### M2.T3 — Write migration 0001: extensions

- [x] **M2.T3.1** Create `migrations/0001_extensions.sql` with `CREATE EXTENSION IF NOT EXISTS vector;`, `CREATE EXTENSION IF NOT EXISTS pg_trgm;`, `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";` (for `gen_random_uuid()` if not included by default — usually is in PG16).
  - Done when: file exists, runs cleanly against the empty DB.

### M2.T4 — Write migrations 0002-0017 (Phase-1 tables)

Map each migration file to the DATA_MODEL section. Each migration runs independently; each is idempotent via `CREATE TABLE IF NOT EXISTS`. Each creates the table AND its indexes.

- [x] **M2.T4.1** Migration `0002_lessons.sql` — per DATA_MODEL §2.1 including `lesson_status` enum, `lessons` table, all indexes (bucket+status partial, applicable_buckets GIN, project, tags GIN, related_tools GIN, category, utility_score, title trgm), HNSW vector index (partial status='active').
- [x] **M2.T4.2** Migration `0003_tools_catalog.sql` — per DATA_MODEL §2.2 including `catalog_kind` enum, `tools_catalog` table, indexes (kind, buckets GIN, utility partial, client_id partial), HNSW (partial non-deprecated non-archived).
- [x] **M2.T4.3** Migration `0004_projects_indexed.sql` — per DATA_MODEL §2.3.
- [x] **M2.T4.4** Migration `0005_project_state.sql` — per DATA_MODEL §2.4 including `related_lessons UUID[]` column and related indexes.
- [x] **M2.T4.5** Migration `0006_project_versions.sql` — per DATA_MODEL §2.5.
- [x] **M2.T4.6** Migration `0007_skill_versions.sql` — per DATA_MODEL §2.6.
- [x] **M2.T4.7** Migration `0008_conversations_indexed.sql` — per DATA_MODEL §3.1.
- [x] **M2.T4.8** Migration `0009_conversation_sessions.sql` — per DATA_MODEL §4.6.
- [x] **M2.T4.9** Migration `0010_cross_pollination_queue.sql` — per DATA_MODEL §3.2 (includes `confidence_score`, `impact_score` columns).
- [x] **M2.T4.10** Migration `0011_routing_logs_partitioned.sql` — per DATA_MODEL §4.1, with `PARTITION BY RANGE (created_at)` and explicit monthly partition for current month + next month.
- [x] **M2.T4.11** Migration `0012_usage_logs_partitioned.sql` — per DATA_MODEL §4.2, partitioned.
- [x] **M2.T4.12** Migration `0013_llm_calls_partitioned.sql` — per DATA_MODEL §4.3, partitioned.
- [x] **M2.T4.13** Migration `0014_pending_embeddings.sql` — per DATA_MODEL §4.4.
- [x] **M2.T4.14** Migration `0015_reflection_pending.sql` — per DATA_MODEL §4.5.
- [x] **M2.T4.15** Migration `0016_scout_denylist.sql` — per DATA_MODEL §6.7.
- [x] **M2.T4.16** Migration `0017_control_registry.sql` — per DATA_MODEL §5.6.

Each task above is done when:
- SQL file exists, reviewed against DATA_MODEL section.
- Running it against the DB succeeds.
- Querying the resulting table with `\d+ {table}` matches the schema in DATA_MODEL.

### M2.T5 — Write migration 0018: Phase-2 tables

- [x] **M2.T5.1** `0018_phase2_tables.sql` — creates `patterns`, `decisions`, `gotchas`, `contacts`, `ideas` per DATA_MODEL §5.1-5.5. Bundle into one migration because they're deferred-deployment Phase-2 tables.
  - Done when: migration runs, all 5 tables exist.

### M2.T6 — Write migration 0019: functions and triggers

- [x] **M2.T6.1** `0019_functions_triggers.sql` contains:
  - `set_updated_at()` trigger function per DATA_MODEL §6.1.
  - `auto_index_on_insert()` trigger per DATA_MODEL §6.2 (writes to `pending_embeddings`).
  - `find_duplicate_lesson()` function per DATA_MODEL §6.3.
  - `recompute_utility_scores()` function per DATA_MODEL §6.4.
  - `archive_low_utility_lessons()` function per DATA_MODEL §6.5 (with the structured-reference fix).
  - `summarize_old_conversation()` function per DATA_MODEL §6.6.
  - `archive_dormant_tools()` function per DATA_MODEL §6.8.
  - `CREATE TRIGGER trg_set_updated_at_*` for every table with an `updated_at` column.
  - `CREATE TRIGGER trg_auto_index_*` on tables with embeddings.
  - Done when: migration runs, `\df` shows all functions, `\dg+` shows all triggers.

### M2.T7 — Write migration 0020: Scout safety trigger

- [x] **M2.T7.1** `0020_scout_safety_trigger.sql` — creates `scout_safety_check()` function and `trg_scout_safety_lessons` trigger per DATA_MODEL §6.7.
  - Done when: trigger fires correctly on test insert (insert a fake Scout-tagged lesson with a known denylist term → trigger raises exception → remove term → insert succeeds).

### M2.T8 — Write migration 0021: views

- [x] **M2.T8.1** `0021_views.sql` — all views from DATA_MODEL §7:
  - `v_tool_utility_leaderboard`
  - `v_lessons_pending_review_count`
  - `v_crosspoll_inbox`
  - `v_tool_lessons`
  - `v_daily_cost_by_purpose`
  - Done when: all views query successfully even against empty tables.

### M2.T9 — Write migrations 0022-0023: seeds

- [x] **M2.T9.1** `0022_seed_tools_catalog.sql` — empty for now. The 10 skills get registered in Module 7, not here. This migration exists as a placeholder so Module 7 can append to it or add a new migration.
  - Done when: file exists with only a comment explaining its role.
- [x] **M2.T9.2** `0023_seed_control_registry.sql` — inserts the 6 seed controls per DATA_MODEL §5.6 example comments.
  - Values: scout_audit (90d), restore_drill (90d), key_rotation_anthropic (180d), key_rotation_openai (180d), pricing_verification (90d), uptime_review (30d).
  - Done when: migration runs, `SELECT control_name, cadence_days FROM control_registry` returns 6 rows.

### M2.T10 — Migration runner + schema_migrations table

- [x] **M2.T10.1** Create `migrations/0000_schema_migrations.sql` for the tracking table per DATA_MODEL §9.2.
  - Done when: table created.
- [x] **M2.T10.2** Create `infra/db/migrate.py` — a simple Python runner that reads migrations in order, applies only unapplied ones (checks `schema_migrations`), records checksums.
  - Done when: script works, runs all 23 migrations, `SELECT * FROM schema_migrations` shows 23 rows.
- [x] **M2.T10.3** Document migration procedure in `runbooks/migrations.md`:
  - How to add a new migration (numbering convention, forward-only rule).
  - How to rollback (inverse migration, never editing applied ones).
  - Done when: runbook exists.

### M2.T11 — Populate scout_denylist

- [x] **M2.T11.1** Operator authors denylist patterns locally — patterns specific to Scout Motors vocabulary that must never appear in the Scout bucket.
  - Example patterns: specific supplier names, product codenames, internal cost codes, proprietary specs.
  - Store as YAML file in `infra/provisioning/scout_denylist_seed.yaml` (operator-private; NOT committed to repo — add to `.gitignore`).
  - Done when: YAML file has ≥ 10 patterns.
- [x] **M2.T11.2** Script at `infra/db/load_scout_denylist.py` reads YAML, inserts to DB.
  - Done when: `SELECT count(*) FROM scout_denylist` returns correct count.

### M2.T12 — Health check script

- [x] **M2.T12.1** Create `infra/db/health_check.py` that verifies:
  - All 21 tables exist.
  - All expected functions and triggers exist.
  - All expected indexes exist.
  - `scout_denylist` has ≥ 1 pattern.
  - `control_registry` has 6 rows.
  - Extensions `vector`, `pg_trgm`, `uuid-ossp` are installed.
  - Monthly partitions for current + next month exist on the 3 log tables.
  - Done when: script runs green.

### M2.T13 — Exit gate verification

- [x] **M2.T13.1** Run `infra/db/health_check.py` — all checks pass.
- [x] **M2.T13.2** Update `runbooks/module_2_data_layer.md` with DB admin procedures (connect, backup, restore, add column, reindex).
- [x] **M2.T13.3** Commit with message "feat(M2): data layer complete — 21 tables, partitions, scout_denylist seeded".
- [x] **M2.T13.4** Tag `module-2-complete`.

**Exit Module 2.**

---

## Module 3: mcp_server_v0

Goal: FastMCP server exposing the minimum useful tool set, auth-enforced, reachable via Cloudflare Tunnel from Claude.ai and Claude Code.

Authority: `docs/PROJECT_FOUNDATION.md §4 Module 3`, `docs/INTEGRATIONS.md §11.1`, `docs/CONSTITUTION.md §2, §8, §9`.

### M3.T1 — Write the module spec

- [x] **M3.T1.1** `specs/mcp_server_v0/spec.md` — per template.
- [x] **M3.T1.2** `specs/mcp_server_v0/plan.md` — phases: A scaffolding, B tool impl, C auth, D deploy, E client connect, F verification.
- [x] **M3.T1.3** `specs/mcp_server_v0/tasks.md` — detailed atomic list.

### M3.T2 — Scaffold the MCP server codebase

- [x] **M3.T2.1** Create `src/mcp_server/` directory with Python package structure:
  - `__init__.py`
  - `main.py` — FastMCP app entry point.
  - `auth.py` — X-Pretel-Auth middleware.
  - `tools/` subdirectory for tool implementations.
  - `db.py` — Postgres connection pool, lazy init.
  - `config.py` — reads env vars.
  - Done when: directory structure exists.
- [x] **M3.T2.2** Create `src/mcp_server/requirements.txt` with pinned versions:
  - `fastmcp==<current-pinned-version>`
  - `psycopg[pool,binary]==3.2.*`
  - `anthropic==<current>`
  - `openai==<current>`
  - `python-dotenv`
  - Done when: file exists with pins.
- [x] **M3.T2.3** Create venv and install deps.
  - Command: `python3 -m venv /home/operator/.venvs/pretel-os && /home/operator/.venvs/pretel-os/bin/pip install -r requirements.txt`.
  - Done when: `pip list` shows all deps installed.

### M3.T3 — Implement auth middleware

- [x] **M3.T3.1** `auth.py` implements FastMCP middleware that reads `X-Pretel-Auth` header and compares to `MCP_SHARED_SECRET` using `hmac.compare_digest`.
  - 401 on mismatch. Logs auth_failed to `routing_logs` (only request_id + reason).
  - Done when: unit test passes for valid + invalid secrets + missing header.
- [x] **M3.T3.2** Integrate middleware into FastMCP app in `main.py`.
  - Done when: starting server without header → any request returns 401.

### M3.T4 — Implement lazy DB initialization

- [x] **M3.T4.1** `db.py` exposes `get_pool()` and `is_healthy()`.
  - `get_pool()` returns psycopg connection pool, initialized on first call.
  - Background task refreshes `_db_healthy` global every 30s via SELECT 1.
  - On startup, DB is NOT required — `main.py` starts regardless.
  - Done when: starting server with Postgres stopped → server starts, `is_healthy()` returns False, tools degrade gracefully.

### M3.T5 — Implement tools (minimum set)

For each tool: code, unit tests, register with FastMCP, document in docstring (used by `tool_search`).

- [x] **M3.T5.1** `get_context(message: str, session_id: str | None = None)` — stub version for M3. Returns just L0 (reads `identity.md` from disk). Full Router lives in M4. Logs to `routing_logs`.
- [x] **M3.T5.2** `search_lessons(query: str, bucket: str | None = None, tags: list | None = None, limit: int = 5, include_archived: bool = False)` — embeds query, filter-first + HNSW search.
- [x] **M3.T5.3** `save_lesson(title, content, bucket, tags, category, severity: str | None = None, applicable_buckets: list | None = None, related_tools: list | None = None)` — inserts with `status='pending_review'`. Pre-save dedup via `find_duplicate_lesson()`. Auto-approval per CONSTITUTION §5.2 rule 13.
- [x] **M3.T5.4** `register_skill(name, description_short, description_full, applicable_buckets, skill_file_path)` — inserts to `tools_catalog`, appends line to L0 `identity.md`.
- [x] **M3.T5.5** `register_tool(name, description_short, description_full, applicable_buckets)` — similar to register_skill but for `kind='tool'`.
- [x] **M3.T5.6** `load_skill(name)` — reads the markdown at `skill_file_path` from tools_catalog row, returns content.
- [x] **M3.T5.7** `tool_search(query)` — returns tool definitions (signature, docs) matching query. Per CONSTITUTION §9 rule 38.

Each tool done when:
- Code passes unit test against a test DB.
- Registered in FastMCP.
- Docstring complete (used by tool_search).
- Degraded-mode path: if `is_healthy()` False, returns appropriate degraded response per CONSTITUTION §8.43(c).

### M3.T6 — Health endpoint

- [x] **M3.T6.1** Add `GET /health` route returning `{"status": "ok", "db_healthy": <bool>}`.
  - Per CONSTITUTION §8.43(a), always returns 200 when MCP server is up, even if DB is down.
  - Done when: `curl http://localhost:8787/health` returns JSON.

### M3.T7 — systemd unit

- [x] **M3.T7.1** Create `infra/systemd/pretel-os-mcp.service`:
  - User service on operator user.
  - EnvironmentFile=/home/operator/.env.pretel_os.
  - ExecStart=/home/operator/.venvs/pretel-os/bin/python -m mcp_server.main.
  - Restart=on-failure, RestartSec=5s.
  - Done when: unit file exists.
- [x] **M3.T7.2** Install and start.
  - `systemctl --user daemon-reload && systemctl --user enable --now pretel-os-mcp`.
  - Done when: `systemctl --user status pretel-os-mcp` shows active (running).
- [x] **M3.T7.3** Verify auto-start at boot — `sudo loginctl enable-linger operator` ensures user services run without login.
  - Done when: reboot, service comes back up.

### M3.T8 — Cloudflare Tunnel ingress

- [x] **M3.T8.1** Update `/etc/cloudflared/config.yml` ingress to route `mcp.alfredopretelvargas.com` → `http://localhost:8787`.
  - Done when: `sudo systemctl restart cloudflared` and `dig mcp.alfredopretelvargas.com` resolves.
- [x] **M3.T8.2** Verify DNS CNAME in IONOS points `mcp` subdomain to `<tunnel-UUID>.cfargotunnel.com`.
  - Done when: `curl -f https://mcp.alfredopretelvargas.com/health` returns 200 from ANY machine (not just operator's).

### M3.T9 — UptimeRobot monitoring

- [ ] **M3.T9.1** Log into UptimeRobot, create HTTP(S) monitor:
  - URL: `https://mcp.alfredopretelvargas.com/health`.
  - Interval: 5 minutes.
  - Alert: email to operator.
  - Done when: monitor created, first ping successful.
- [ ] **M3.T9.2** Update `control_registry` with last_completed_at on uptime_review control (initial setup counts).
  - Done when: `SELECT last_completed_at FROM control_registry WHERE control_name='uptime_review'` returns current timestamp.

### M3.T10 — Write identity.md (L0 content)

- [x] **M3.T10.1** Author `identity.md` at repo root per `plan.md §7.6`:
  - Operator identity (name, location, timezone, languages).
  - Bucket names + 1-line descriptions.
  - Tool catalog entries (1-line each for the 6 tools registered above — the `register_skill`/`register_tool` tools will append to this file automatically as more are added).
  - Summary of immutable invariants (reference CONSTITUTION §2.7 and §3).
  - Done when: file exists, under 500 tokens (pre-commit hook enforces).

### M3.T11 — Write AGENTS.md

- [x] **M3.T11.1** Author `AGENTS.md` per `plan.md §7.6`:
  - Reading order for LLMs coming into the repo.
  - Inline the 9 agent rules from CONSTITUTION §9.
  - Directory map (copy from `plan.md §3`).
  - Done when: file exists, committed.

### M3.T12 — Client connection tests

- [x] **M3.T12.1** Configure Claude.ai connector:
  - Settings → Connectors → Add custom MCP.
  - URL: `https://mcp.alfredopretelvargas.com`.
  - Custom headers: `X-Pretel-Auth: <value from .env>`.
  - Done when: Claude.ai shows "Connected" for this connector.
- [x] **M3.T12.2** Test `get_context` from Claude.ai.
  - Ask: "what's my current state per pretel-os?"
  - Expected: response grounded in identity.md content.
  - Done when: response is sensible.
- [x] **M3.T12.3** Configure Claude Code `~/.config/claude/mcp.json` with same URL + header.
  - Done when: `claude` CLI shows pretel-os tools available.
- [x] **M3.T12.4** Test a tool via Claude Code.
  - Command: `claude "save a test lesson: 'pretel-os MCP is alive' with tag test"`.
  - Verify via psql: `SELECT title FROM lessons WHERE 'test' = ANY(tags)`.
  - Done when: lesson saved with `status='pending_review'`.

### M3.T13 — Exit gate verification

- [x] **M3.T13.1** Run all smoke tests: save_lesson, search_lessons, get_context all succeed.
- [x] **M3.T13.2** Write `runbooks/module_3_mcp_server.md` — deploy procedure, restart, rollback.
- [x] **M3.T13.3** Commit + tag `module-3-complete`.

**Exit Module 3.**

---

## Module 4: router

Goal: Intelligent classifier + layer assembler replacing the stub `get_context`.

Authority: `docs/CONSTITUTION.md §2.2, §2.3, §2.7, §5`.

### M4.T1 — Spec

- [ ] **M4.T1.1** `specs/router/spec.md`.
- [ ] **M4.T1.2** `specs/router/plan.md` — phases: A classifier, B layer loader, C source priority, D telemetry, E fallback, F tuning.
- [ ] **M4.T1.3** `specs/router/tasks.md`.

### M4.T2 — Classification prompt engineering

- [ ] **M4.T2.1** Author Haiku classification prompt in `src/mcp_server/router/prompts/classify.txt`.
  - Input: user message + current L0 + current session context.
  - Output: JSON with `bucket`, `project`, `skill`, `complexity` (LOW/MEDIUM/HIGH), `needs_lessons` (bool), `confidence` (0.0-1.0).
  - Done when: prompt exists, 10 test examples in `tests/router/classification_examples.md` all classified correctly.
- [ ] **M4.T2.2** Implement `classifier.py` — calls Haiku via Anthropic SDK, parses JSON response, handles parse errors with fallback rules.
  - Done when: unit tests pass.
- [ ] **M4.T2.3** Prompt caching — system prompt is static, cache it per INTEGRATIONS §2.6.
  - Done when: second classification call shows `cache_read_tokens > 0` in llm_calls.

### M4.T3 — Layer loader

- [ ] **M4.T3.1** `layer_loader.py`:
  - `load_L0()` → reads identity.md.
  - `load_L1(bucket)` → reads `buckets/{bucket}/README.md` or sub-bucket.
  - `load_L2(bucket, project)` → reads project README + state rows + relevant module file.
  - `load_L3(skill)` → calls `load_skill(skill)` tool.
  - `load_L4(query, bucket, tags)` → filter-first search_lessons with HNSW.
  - Each respects budget from CONSTITUTION §2.3.
  - Done when: each loader unit-tested.

### M4.T4 — Source priority resolution

- [ ] **M4.T4.1** `conflict_resolver.py`:
  - Detects conflicts via semantic similarity + keyword overlap.
  - Applies priority regime per CONSTITUTION §2.7: immutable invariants first, then ordered L2 > L3 > L4 > L1 > L0 for contextual.
  - Records conflicts to `routing_logs.source_conflicts`.
  - Done when: synthetic conflict test returns higher-priority source + log entry.

### M4.T5 — Telemetry

- [ ] **M4.T5.1** Every `get_context` call writes a complete `routing_logs` row including:
  - classification, classification_mode, layers_loaded, tokens_assembled_total, tokens_per_layer, over_budget_layers, rag_expected, rag_executed, lessons_returned, tools_returned, source_conflicts, degraded_mode, latency_ms.
  - Done when: `SELECT count(*), avg(latency_ms) FROM routing_logs WHERE created_at > now() - interval '1 day'` returns reasonable numbers after a day of use.

### M4.T6 — Fallback classifier

- [ ] **M4.T6.1** `fallback_classifier.py` — pure Python, no LLM.
  - Keyword + regex matching against bucket names, project names from L0.
  - Returns conservative classification (e.g., `complexity=LOW` when uncertain).
  - Triggered when Haiku unreachable or over rate limit.
  - Done when: tests pass with Haiku mocked as failing.

### M4.T7 — Client-reported user satisfaction

- [ ] **M4.T7.1** Add optional `session_feedback` parameter to a new tool `report_satisfaction(request_id, score)` — 1-5 integer.
  - Writes to `routing_logs.user_satisfaction`.
  - Documented for client-side Claude prompts: "if the response was helpful, call `report_satisfaction(4)` or similar."
  - Done when: calling it updates the right row.

### M4.T8 — Integration tests

- [ ] **M4.T8.1** End-to-end test: `get_context("help me debug my n8n batching")` returns:
  - bucket=business (or the bucket holding n8n projects).
  - complexity=HIGH or MEDIUM.
  - L4 lessons filtered with tags containing "n8n".
  - Total tokens within budget.
  - Done when: returned bundle matches expectations, verified manually first, then automated in `tests/router/e2e.py`.

### M4.T9 — Exit gate

- [ ] **M4.T9.1** Verify gate from `plan.md §6 Module 4`.
- [ ] **M4.T9.2** `runbooks/module_4_router.md` — debugging classifications, Haiku outage handling.
- [ ] **M4.T9.3** Commit + tag `module-4-complete`.

**Exit Module 4.**

---

## Module 5: telegram_bot

Goal: python-telegram-bot v21 app exposing all pretel-os commands + voice transcription + passive notification channel.

Authority: `docs/INTEGRATIONS.md §8`.

### M5.T1 — Spec

- [ ] **M5.T1.1** `specs/telegram_bot/spec.md`.
- [ ] **M5.T1.2** `specs/telegram_bot/plan.md`.
- [ ] **M5.T1.3** `specs/telegram_bot/tasks.md`.

### M5.T2 — Bot registration

- [ ] **M5.T2.1** Register bot with BotFather via Telegram app.
  - Name, username, description, commands list.
  - Capture token.
  - Done when: token in `.env.pretel_os` as `TELEGRAM_BOT_TOKEN`.
- [ ] **M5.T2.2** Capture operator's chat_id.
  - Message the bot from operator's Telegram account, capture chat_id from webhook or `getUpdates`.
  - Store as `TELEGRAM_OPERATOR_CHAT_ID`.
  - Done when: env var set.

### M5.T3 — Bot scaffolding

- [ ] **M5.T3.1** `src/telegram_bot/` package structure.
- [ ] **M5.T3.2** `requirements.txt` — `python-telegram-bot==21.*`, plus MCP client lib or direct HTTP to the MCP server.
- [ ] **M5.T3.3** `main.py` with Application builder, command handlers, voice message handler.
- [ ] **M5.T3.4** Long-polling mode enabled (Phase 1 per INTEGRATIONS).
- [ ] **M5.T3.5** Rate limiting (python-telegram-bot handles automatically).

### M5.T4 — Command handlers

Each command done when: handler implemented, auth check (operator_chat_id only), end-to-end test via Telegram.

- [ ] **M5.T4.1** `/start` — registers chat_id, confirms to operator.
- [ ] **M5.T4.2** `/save <text>` — calls `save_lesson` via MCP.
- [ ] **M5.T4.3** `/review_pending` — presents pending lessons one at a time with inline keyboard (Approve / Edit / Reject / Merge).
- [ ] **M5.T4.4** `/cross_poll_review` — similar for `cross_pollination_queue`.
- [ ] **M5.T4.5** `/morning_brief` — triggers Morning Intelligence on-demand (this hooks to a workflow in n8n).
- [ ] **M5.T4.6** `/reflect` — forces Reflection worker on current session (requires Module 6 for full implementation; stub it here).
- [ ] **M5.T4.7** `/idea <text>` — inserts into `ideas` table.
- [ ] **M5.T4.8** `/status` — runs parallel health checks, returns 🟢🟡🔴 summary per INTEGRATIONS §8.4.
- [ ] **M5.T4.9** `/project <name>` — summarizes project state.
- [ ] **M5.T4.10** `/search_lessons <query>` — wraps MCP tool.
- [ ] **M5.T4.11** `/help` — lists commands.

### M5.T5 — Voice transcription

- [ ] **M5.T5.1** Decide transcription provider.
  - Option A: OpenAI Whisper API (~$0.006/min, reliable, simpler).
  - Option B: Local `whisper.cpp` on Vivobook (free, requires GPU, more setup).
  - Recommendation: A for M5 simplicity. Revisit after a month of usage data.
  - Done when: decision logged, option A implemented.
- [ ] **M5.T5.2** Voice message handler — downloads OGG, transcribes via Whisper API, routes result through classification pipeline:
  - If text looks like a lesson → proposes `save_lesson` (shown in chat for approval).
  - If text looks like an idea → `ideas` insert.
  - If text looks like a question → `get_context` + LLM response.
  - Done when: voice message → correctly routed outcome.

### M5.T6 — systemd unit

- [ ] **M5.T6.1** `infra/systemd/pretel-os-bot.service`, enable + start, lingering user.
  - Done when: service active, survives reboot.

### M5.T7 — Exit gate

- [ ] **M5.T7.1** Verify each command works end-to-end via real Telegram.
- [ ] **M5.T7.2** `runbooks/module_5_telegram_bot.md` — token rotation, webhook migration, debugging.
- [ ] **M5.T7.3** Commit + tag `module-5-complete`.

**Exit Module 5.**

---

## Module 6: reflection_worker

Goal: Event-triggered LLM call that reads transcripts and proposes lessons.

Authority: `docs/CONSTITUTION.md §2.6, §5.2`.

### M6.T1 — Spec

- [ ] **M6.T1.1** `specs/reflection_worker/spec.md`.
- [ ] **M6.T1.2** `specs/reflection_worker/plan.md`.
- [ ] **M6.T1.3** `specs/reflection_worker/tasks.md`.

### M6.T2 — Session tracking

- [ ] **M6.T2.1** MCP `get_context` creates/updates `conversation_sessions` row on every call — tracks session_id, client_origin, bucket, project, turn_count, last_seen_at.
  - Done when: after a Claude.ai session, the row exists with correct values.
- [ ] **M6.T2.2** Append transcript to `transcript_path` (JSONL file) on every turn.
  - Done when: `cat /home/operator/pretel-os-data/transcripts/<session_id>.jsonl` shows the turns.

### M6.T3 — Trigger detection

- [ ] **M6.T3.1** `src/workers/reflection_triggers.py` — runs every 5 min via systemd timer.
  - Detects sessions with close criteria met:
    - `close_session` — `last_seen_at < now() - 10 min` AND `closed_at IS NULL`.
    - `time_fallback_60min` — open session with `started_at < now() - 60 min` AND `reflection_fired = false`.
    - `turn_fallback_20` — `turn_count >= 20` AND `reflection_fired = false`.
  - `task_complete` — set directly by MCP when a tool signals task completion.
  - Done when: trigger tests pass.

### M6.T4 — Reflection prompt + implementation

- [ ] **M6.T4.1** Author Sonnet reflection prompt in `src/workers/prompts/reflect.txt`.
  - Input: transcript + session metadata + bucket L1 for context.
  - Output: JSON with `lessons: [...]`, `cross_pollination: [...]`, `state_updates: [...]`.
  - Done when: prompt on 5 test transcripts produces sensible output.
- [ ] **M6.T4.2** `reflection_worker.py` — calls Sonnet, parses JSON, writes to DB.
  - Proposals go to `lessons` with `status='pending_review'`, `cross_pollination_queue`, `project_state`.
  - Auto-approval per CONSTITUTION §5.2 rule 13.
  - Done when: end-to-end: trigger → Sonnet call → DB writes.

### M6.T5 — Degraded mode

- [ ] **M6.T5.1** If Sonnet unreachable, insert payload to `reflection_pending` per DATA_MODEL §4.5.
  - Done when: simulated Sonnet outage → row in `reflection_pending` with `status='pending'`.
- [ ] **M6.T5.2** Retry loop reads `reflection_pending` every hour, attempts replay. After 5 attempts → `status='abandoned'` + `gotcha` entry.
  - Done when: tested with flaky API.

### M6.T6 — Morning Intelligence (minimum)

- [ ] **M6.T6.1** Separate n8n workflow `morning_intelligence_daily`:
  - Runs at 06:00 America/New_York.
  - Reads routing_logs, control_registry overdue, cross_pollination pending, yesterday's high-severity lessons.
  - Generates text brief via Sonnet.
  - Sends to operator via Telegram (using bot token).
  - Optionally: synthesizes voice via OpenAI TTS per INTEGRATIONS §9.1.
  - Done when: workflow exists in n8n, first morning triggers and message arrives.

### M6.T7 — Dream Engine (core)

- [ ] **M6.T7.1** `src/workers/dream_engine.py` — runs at 02:00 America/New_York via systemd timer.
  - Tasks:
    - Call `recompute_utility_scores()`.
    - Call `archive_low_utility_lessons()`.
    - Call `archive_dormant_tools()`.
    - Call `summarize_old_conversation()` for candidates >90 days.
    - Dedup pass (similarity ≥ 0.95) → merge proposals to `cross_pollination_queue`.
    - Create next month's log partitions if current-month is near end.
    - Process `reflection_pending` queue.
    - Check `control_registry` overdue, send Telegram alerts.
    - Write weekly YAML export on Sundays.
  - Done when: script runs clean, all tasks execute without error.

### M6.T8 — Exit gate

- [ ] **M6.T8.1** Verify Reflection + Morning Brief + Dream Engine all operational.
- [ ] **M6.T8.2** `runbooks/module_6_reflection.md`.
- [ ] **M6.T8.3** Commit + tag `module-6-complete`.

**Exit Module 6.**

---

## Module 7: skills_migration

Goal: Ten skills in `skills/`, registered in `tools_catalog`, embedded, retrievable.

Authority: `docs/PROJECT_FOUNDATION.md §4 Module 7`.

### M7.T1 — Spec

- [ ] **M7.T1.1** `specs/skills_migration/spec.md`.
- [ ] **M7.T1.2** `specs/skills_migration/plan.md`.
- [ ] **M7.T1.3** `specs/skills_migration/tasks.md`.

### M7.T2 — Migrate existing skills (7)

Each skill done when: file exists in `skills/`, under 4,000 tokens (pre-commit hook enforces), registered via `register_skill` MCP call, embedding populated in tools_catalog.

- [ ] **M7.T2.1** `skills/vett.md` — VETT framework methodology.
- [ ] **M7.T2.2** `skills/sdd.md` — Spec-Driven Development process.
- [ ] **M7.T2.3** `skills/scout_slides.md` — abstract patterns only, no employer data.
- [ ] **M7.T2.4** `skills/declassified_pipeline.md` — 4-agent pipeline methodology, product-agnostic.
- [ ] **M7.T2.5** `skills/forge.md` — Product Intelligence 8-phase pipeline.
- [ ] **M7.T2.6** `skills/marketing_system.md` — product-agnostic marketing playbook.
- [ ] **M7.T2.7** `skills/finance_system.md` — personal + rental + small-business financial analysis.

### M7.T3 — Author new skills (3)

- [ ] **M7.T3.1** `skills/client_discovery.md`.
  - Purpose: 5-question structured intake for a new freelance client.
  - Inputs: raw meeting transcripts or voice notes.
  - Outputs: structured JSON updating `project_state` + drafted L2 project README.
  - Done when: file committed, test invocation produces correct output.
- [ ] **M7.T3.2** `skills/sow_generator.md`.
  - Purpose: drafts SOWs for a given client + service tier.
  - Inputs: client_id + service name (Forge/VETT/SDD/...).
  - Outputs: Markdown SOW with deliverables, timeline, cost.
  - Done when: test invocation produces a viable SOW.
- [ ] **M7.T3.3** `skills/mtm_efficiency_audit.md`.
  - Purpose: industrial-engineering audit of a client's digital workflow stack.
  - Inputs: workflow descriptions, tool stack, time-to-completion metrics.
  - Outputs: structured audit report with bottlenecks + n8n/AI automation proposals.
  - Productizable: $2.5-5k per audit.
  - Done when: file + test invocation complete.

### M7.T4 — Retrieval tests

- [ ] **M7.T4.1** For each bucket, query a relevant topic and verify the right skill appears in top-3 via `recommend_tools`.
  - Business + "market research" → vett in top-3.
  - Business + "new project scaffolding" → sdd in top-3.
  - Business + "client workflow audit" → mtm_efficiency_audit in top-3.
  - Personal + "monthly finance check" → finance_system in top-3.
  - Done when: all 10 skills are retrievable.

### M7.T5 — Exit gate

- [ ] **M7.T5.1** Verify all 10 in `tools_catalog`, each has embedding.
- [ ] **M7.T5.2** `runbooks/module_7_skills.md` — how to add a new skill.
- [ ] **M7.T5.3** Commit + tag `module-7-complete`.

**Exit Module 7.**

---

## Module 8: lessons_migration

Goal: 89 existing YAML lessons migrated to DB + 12 Gemini Strategic ideas seeded to `ideas`.

Authority: `docs/LESSONS_LEARNED.md §8`, `docs/PROJECT_FOUNDATION.md §5.2`.

### M8.T1 — Spec

- [ ] **M8.T1.1** `specs/lessons_migration/spec.md`.
- [ ] **M8.T1.2** `specs/lessons_migration/plan.md`.
- [ ] **M8.T1.3** `specs/lessons_migration/tasks.md`.

### M8.T2 — Stage YAMLs in repo

- [ ] **M8.T2.1** Copy `LL-MASTER.yaml` and `LL-FORGE.yaml` from `pr3t3l/openclaw-config` to `migrations/data/` (staging — deleted after migration).
  - Done when: both files in repo under that path.

### M8.T3 — Transformation script

- [ ] **M8.T3.1** `src/workers/migration_yaml_to_db.py`:
  - Parses YAML via `yaml.safe_load`.
  - For each entry: maps OpenClaw schema → pretel-os schema per LESSONS_LEARNED §2.
  - Inserts with `source='migration_LL-MASTER'` or `source='migration_LL-FORGE'`, `status='pending_review'`.
  - Skips entries with unknown required fields; logs to stderr.
  - Done when: dry-run shows all 89 entries parsed, schema mismatches handled.

### M8.T4 — Embedding via Batch API

- [ ] **M8.T4.1** After insert, collect lesson IDs and their `title + content` text.
- [ ] **M8.T4.2** Use OpenAI Batch API (50% discount per INTEGRATIONS §3.6):
  - Submit batch.
  - Wait up to 24h for results.
  - Parse results → update `lessons.embedding` for each row.
  - Done when: `SELECT count(*) FROM lessons WHERE embedding IS NOT NULL AND source LIKE 'migration_%'` returns ≥ 75.

### M8.T5 — Dedup pass

- [ ] **M8.T5.1** Run `find_duplicate_lesson()` against the whole migrated set.
  - For each pair with similarity ≥ 0.92, flag as `merge_candidate` in `cross_pollination_queue`.
  - Expected batch: ~10 pairs.
  - Done when: queue populated.

### M8.T6 — Operator review batch

- [ ] **M8.T6.1** Via Telegram `/review_pending`, operator walks through entries.
  - Approve → `status='active'`.
  - Reject → `status='rejected'`.
  - Merge → operator resolves which wins; losing entry → `merged_into`.
  - Done when: `SELECT count(*) FROM lessons WHERE status='active' AND source LIKE 'migration_%'` returns 75-89.

### M8.T7 — Seed ideas table

- [ ] **M8.T7.1** Script to insert the 12 ideas from PROJECT_FOUNDATION §5.2 Backlog into `ideas` table.
  - Each with `status='new'`, category per the table.
  - Done when: `SELECT count(*) FROM ideas WHERE status='new'` returns 12.

### M8.T8 — Retrieval verification

- [ ] **M8.T8.1** Run test queries:
  - "n8n batching" → returns n8n-related lessons in top-3.
  - "Scout VBA inputbox" → returns Scout patterns in top-3.
  - "OpenClaw architecture" → returns decision-related lessons in top-3.
  - Done when: each query validated.

### M8.T9 — Cleanup

- [ ] **M8.T9.1** Delete `migrations/data/LL-*.yaml` from the repo (they live in git history and in `pr3t3l/openclaw-config`).
  - Done when: files removed, commit "chore: remove migration staging files".
- [ ] **M8.T9.2** Document `MIGRATION_TODO.md` — lessons still `pending_review` after batch review, with operator notes for future cleanup.
  - Done when: file exists at repo root.

### M8.T10 — Exit gate

- [ ] **M8.T10.1** Verify gate from `plan.md §6 Module 8`.
- [ ] **M8.T10.2** `runbooks/module_8_lessons.md`.
- [ ] **M8.T10.3** Commit + tag `module-8-complete`.

**Exit Module 8 — Phase 3 closes. Foundation plan complete.**

---

## Continuous operations

These are not module tasks. They happen in the background once the relevant module is live.

### CO.T1 — Weekly review ritual (Sundays)

- [ ] (Recurring) `/review_pending` in Telegram — walk through new lessons.
- [ ] (Recurring) `/cross_poll_review` — apply or dismiss cross-pollination proposals.
- [ ] (Recurring) Check `control_registry` for overdue controls.
- [ ] (Recurring) Review Dream Engine's weekly YAML export (in `exports/`) — scan for patterns.

### CO.T2 — Monthly review ritual

- [ ] (Recurring) UptimeRobot monthly report review; update `control_registry.uptime_review.last_completed_at`.
- [ ] (Recurring) Review `v_daily_cost_by_purpose` for the month — look for cost anomalies.
- [ ] (Recurring) Scan `ideas` table for items to promote.

### CO.T3 — Quarterly review ritual

- [ ] (Recurring) Scout audit per `control_registry.scout_audit` — review `buckets/scout/` for leaks.
- [ ] (Recurring) Restore drill per `control_registry.restore_drill`.
- [ ] (Recurring) Pricing verification per `control_registry.pricing_verification`.
- [ ] (Recurring) Review CONSTITUTION for amendment candidates — any rules that reality disproved?

### CO.T4 — Biannual (every 180 days)

- [ ] (Recurring) Key rotation per `control_registry.key_rotation_*`.

---

## Notes for future chats

If you're reading this file in a new chat:

1. Find the first unchecked `[ ]`. That's your next task.
2. Read the 3-5 tasks surrounding it for context.
3. Open `plan.md §6` for that module's full "Done when" list.
4. Open `specs/{module}/spec.md` for the full implementation spec (if module has started).
5. Begin.

Never assume a task is "probably done" without checking its Done When. Always verify.

---

**End of tasks.md.**
