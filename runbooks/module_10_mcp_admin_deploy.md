# Module 10 mcp_admin — deploy runbook (Phase D)

**Status:** Active (Phase D in progress 2026-05-07)
**Audience:** Operator following step-by-step to bring the admin console live.
**Prerequisite:** Phases A/B/C committed and pushed (`45730e2`).

This runbook takes you from "admin works on localhost:8088" to "admin lives at `https://mcp-admin.alfredopretelvargas.com` behind Cloudflare Access". Three external systems are configured: Cloudflare DNS, Cloudflare Tunnel, Cloudflare Zero Trust Access. The local systemd service is already enabled (Claude did M10.D.8-10 before handoff).

Every step has an "expected outcome" so you know whether to proceed or stop and triage.

---

## 0. Pre-flight (already done — for reference)

| Check | State | How verified |
|-------|-------|-------------|
| systemd unit installed + enabled | ✓ active (running) | `systemctl --user status pretel-os-admin.service` |
| Health check from localhost | ✓ `{"status":"ok"}` | `curl http://127.0.0.1:8088/health` |
| SC4: no SQL DML in admin code | ✓ zero hits | `grep -rEn "^\s*[^#]*\b(INSERT\|UPDATE\|DELETE)\b" src/mcp_admin/` |
| 307 tests + mypy clean | ✓ | `pytest tests/ && mypy src/mcp_admin/` |

The service is listening on `127.0.0.1:8088`. Cloudflare Tunnel has to forward to it.

---

## 1. Cloudflare DNS — add `mcp-admin` CNAME

Goal: point `mcp-admin.alfredopretelvargas.com` at your Cloudflare Tunnel.

If you already have `mcp.alfredopretelvargas.com` working (you do — the MCP server runs there), the Tunnel is already established for `alfredopretelvargas.com`. We just add another public hostname to the same Tunnel.

**Steps:**

1. Open Cloudflare dashboard → select **alfredopretelvargas.com** → **DNS** → **Records**.
2. Look for an entry for `mcp` (the existing MCP server). It will be either CNAME → `<tunnel-id>.cfargotunnel.com` or a Cloudflare-managed Tunnel proxy. Note that pattern.
3. **Don't add a DNS record manually for `mcp-admin`.** It's easier to let Cloudflare Tunnel auto-create the DNS record when you add the public hostname in step 2. Skip to §2.

**Expected outcome:** No new DNS record yet — that happens automatically in step 2.

---

## 2. Cloudflare Tunnel — add public hostname

Goal: tell the existing Cloudflare Tunnel that requests to `mcp-admin.alfredopretelvargas.com` should forward to `http://localhost:8088` on your Vivobook.

**Steps:**

1. Cloudflare dashboard → **Zero Trust** (top-right or sidebar) → **Networks** → **Tunnels**.
2. Find your existing Tunnel (the one routing `mcp.alfredopretelvargas.com`). Click the **3-dot menu** → **Configure** (or click the tunnel name).
3. **Public Hostname** tab → **+ Add a public hostname**.
4. Fill in:
   - **Subdomain:** `mcp-admin`
   - **Domain:** `alfredopretelvargas.com` (dropdown selects from your zones)
   - **Path:** *leave empty*
   - **Type:** `HTTP`
   - **URL:** `localhost:8088`
5. Optional → **Additional application settings** → leave defaults.
6. Click **Save hostname**.

Cloudflare auto-creates the DNS CNAME for `mcp-admin` pointing at the Tunnel.

**Expected outcome:** `https://mcp-admin.alfredopretelvargas.com/health` returns `{"status":"ok"}` from any browser within ~30 seconds. Try it. (You shouldn't see Access yet because we haven't added the policy.) If you do see the JSON, the Tunnel is wired correctly. **Don't share this URL** — there's no auth on it yet for the next minute or two.

If `/health` returns Cloudflare's "no origin" error, the Tunnel isn't reaching your Vivobook — check `cloudflared` is running:
```bash
systemctl --user status cloudflared 2>/dev/null || sudo systemctl status cloudflared
```

---

## 3. Cloudflare Zero Trust Access — create the application

Goal: put auth in front of `mcp-admin.alfredopretelvargas.com` so only you can reach the FastAPI app.

**Steps:**

1. Cloudflare dashboard → **Zero Trust** → **Access** → **Applications**.
2. **+ Add an application** → **Self-hosted**.
3. **Application name:** `pretel-os admin` (free text; this is what shows on the login page).
4. **Session duration:** **24 hours** (default; can be 30 minutes to 1 month).
5. **Application domain** → click **+ Add public hostname**:
   - **Subdomain:** `mcp-admin`
   - **Domain:** `alfredopretelvargas.com`
   - **Path:** *leave empty*
6. **Identity providers** → ensure **One-time PIN** is checked. Optionally add **Google** or **GitHub** for one-click login (you can do this later — PIN is enough to start).
7. Click **Next**.

**Expected outcome:** You're now on the "Add a policy" screen. Don't save the application yet — you need a policy first.

---

## 4. Cloudflare Zero Trust Access — add the operator-only policy

Goal: allow only `prettelv1@gmail.com` (or whatever email you use) to authenticate. Everyone else gets blocked at the edge.

**Steps:**

1. **Policy name:** `operator-only`.
2. **Action:** **Allow**.
3. **Configure rules** → **Include**:
   - **Selector:** **Emails**
   - **Value:** `prettelv1@gmail.com` (your real email)
4. *Skip* "Require" and "Exclude" — we want a simple allowlist.
5. Click **Next**.
6. **Setup → Next** (defaults are fine — the cookie domain auto-fills, CORS not needed).
7. Click **Add application** at the bottom.

**Expected outcome:** Application appears in **Access → Applications** list. Status: **Active**. ~30 seconds later, the policy is enforced.

---

## 5. First live access (the moment of truth)

**Steps:**

1. Open a fresh browser tab (or incognito to avoid cached cookies). Navigate to `https://mcp-admin.alfredopretelvargas.com/preferences`.
2. Cloudflare's branded login screen appears: **"Sign in to pretel-os admin"** with a single email field.
3. Enter your email (the one in the policy: `prettelv1@gmail.com`).
4. Cloudflare emails you a **6-digit PIN**. Check inbox (~10 seconds).
5. Enter the PIN.
6. You're redirected to `/preferences`. The admin dashboard loads. Top-right shows your email in the user pill.

**Expected outcome:**
- Sidebar shows 5 nav entries: Operator preferences, Memory browser, Dream Engine, Costs, Pending review.
- The 3 archive thresholds (`archive.usage_window_days = 500`, etc.) appear in the table.
- All paths reachable: try clicking each nav entry.

If anything breaks, see §7 below.

---

## 6. SC verification — checklist

After first login, confirm each success criterion is satisfied:

| SC | Verify how |
|----|------------|
| **SC1** — no traffic reaches FastAPI without Access auth | Open a *different* browser (or use `curl https://mcp-admin.alfredopretelvargas.com/preferences` from your terminal) without logging in. You should see the Cloudflare Access challenge HTML, NOT the admin's HTML. journalctl on the Vivobook (`journalctl --user -u pretel-os-admin -n 50`) should show only logged-in requests. |
| **SC2** — page load < 2s (95th percentile) | Open browser devtools → Network tab → reload `/preferences` 5 times. Each load < 2000 ms total. Cold first load may be 1.5-2s; warm reloads < 500ms. |
| **SC3** — all 5 views render against live state | Click through Operator preferences, Memory browser (3 tabs), Dream Engine, Costs, Pending review. None should error. |
| **SC4** — no SQL DML in admin | Already verified by Claude during M10.D.16 (grep returned 0 hits). |
| **SC5** — drill-downs work | From `/memory?tab=lessons` click any lesson row title → loads `/memory/lessons/{id}`. From `/dream-engine` click any started_at → loads `/dream-engine/run/{id}`. From `/projects/{bucket}/{slug}` (manual URL — there's no nav yet) verify it loads. |
| **SC6** — 7-day observation window | Phase E. Skip for now. |
| **SC7** — visual coherence | Side-by-side compare with `alfredopretelvargas.com`. Teal `#1D9E75`, amber `#EF9F27`, purple `#7F77DD` should match. Inter font visible. Default dark mode. |

---

## 7. Common failure modes

### Cloudflare login screen doesn't appear (you see the FastAPI HTML directly)

→ The Access policy is not yet enforced. Wait 30 more seconds and refresh. If still wrong, go back to **Access → Applications → pretel-os admin → Policies** and verify the policy is **Active** + **Allow** + your email is in the Include list.

### Access challenge appears but PIN never arrives

→ Spam folder. Or wrong email entered. The PIN is sent to the email *you* type, then verified against the allowlist. If you typed someone else's email and their PIN arrived, neither is in the allowlist → access denied.

### `/health` returns "no origin" or 502 Bad Gateway

→ Cloudflare Tunnel isn't reaching your Vivobook. Check:
```bash
systemctl --user status cloudflared 2>/dev/null
# OR
sudo systemctl status cloudflared
```
If down, restart: `sudo systemctl restart cloudflared`.

### `/preferences` returns 500

→ FastAPI process crashed or DB unreachable. Check:
```bash
systemctl --user status pretel-os-admin.service
journalctl --user -u pretel-os-admin -n 50 --no-pager
```

### Visual looks wrong (no teal, no Inter font)

→ Static CSS not served. Check `/static/tokens.css` returns 200 from your authenticated browser. If 404, the Tunnel might be stripping `/static/*` somehow (unusual).

---

## 8. After verification — close Phase D

Once SC1, SC2, SC3, SC5, SC7 are verified (SC4 already done, SC6 is Phase E):

1. Tell Claude: "Phase D verified, all SCs green except SC6 (observation period starting now)".
2. Claude writes `specs/mcp_admin/phase_d_close.md` documenting the deployment timeline + verification results + any quirks observed.
3. Claude flips Phase D checkboxes in `specs/mcp_admin/tasks.md`.
4. Claude commits Phase D.
5. Phase E observation period starts: 7 daily checks of `journalctl --user -u pretel-os-admin -p err --since yesterday`.

---

## 9. Rollback (if go-live fails badly)

If something is genuinely broken and you want to pull the admin offline:

```bash
# Stop the service (operator action)
systemctl --user stop pretel-os-admin.service

# Disable auto-start on boot
systemctl --user disable pretel-os-admin.service
```

Then in Cloudflare:
- **Access → Applications → pretel-os admin → 3-dot menu → Disable** (keeps the config; just stops enforcing). The hostname returns "no origin" since uvicorn is stopped.
- *OR* delete the application + delete the Tunnel public hostname for `mcp-admin`.

DNS for `mcp-admin` will linger until you remove the public hostname — Cloudflare auto-cleans DNS when you remove a Tunnel hostname.

To re-enable: reverse the steps. systemd service start, Cloudflare Access enable.
