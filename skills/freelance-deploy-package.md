# freelance-deploy-package

**Part of the `freelance-deployment-playbook` series.** Index: [`freelance-deployment-playbook`](freelance-deployment-playbook.md). Siblings: `freelance-deploy-foundations`, `freelance-deploy-pipeline`, `freelance-deploy-debug`.

**Scope:** turn the app into a portable, runnable artifact — Dockerfile, runtime config (K8s `pipeline.yaml` / `docker-compose` / PaaS), secrets management. Modules 4, 5, 6 of the original playbook.

**Trigger keywords:** Dockerfile, multi-stage build, non-root, USER, EXPOSE, .dockerignore, pipeline.yaml, docker-compose, env vars, runtime config, secrets, .env.example, Doppler, AWS Secrets Manager, ExternalSecret, machine identity, IAM role.

---

# Module 4: Containerization (Dockerfile)

## What a Docker image actually contains

Five layers, from base up:

1. **Base OS** (typically minimal Linux: Alpine ~5MB, Debian-slim ~30MB)
2. **Runtime** (Python 3.12, Node 20, JVM, Go binary)
3. **Dependencies** (libraries your app imports)
4. **Your code**
5. **Start command** ("when you boot, run `python main.py`")

The image is **immutable** and **versioned**. It's the artifact that travels through the rest of the pipeline.

## Three types of dependencies

| Layer | Example | Where in Dockerfile |
|---|---|---|
| **System** (OS packages) | `libpq-dev`, `ffmpeg`, `tesseract-ocr` | `RUN apt-get install ...` |
| **Language** (lib packages) | `fastapi`, `pandas`, `react` | `RUN pip install -r requirements.txt` |
| **Runtime config** (env vars) | `DATABASE_URL`, `API_KEY` | NOT in image — injected at run |

## Mandatory: non-root user

**Why:** if a container is compromised running as root, the attacker has more leverage. Non-root limits the blast radius. Most production orchestrators (including Scout's EKS) **reject** Pods running as root.

**Minimal pattern (any Linux base):**

```dockerfile
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser
```

**Note:** Scout's doc has a comment "use UID not name" — meaning specify `USER 1001` instead of `USER appuser`. Both work; UID is more portable across base images.

## Mandatory: read-only root filesystem awareness

Production runs containers with read-only root FS. If your app writes (logs, cache, temp files), declare it explicitly:

- Scout's `pipeline.yaml`: `tmpDir: true` for ephemeral writes; `volume:` for persistent
- docker-compose: declare a volume mount

If your app writes to `/var/log/myapp/` and you don't declare it, the container crashes on first write.

## Multi-stage builds — when and why

Single-stage Dockerfile: ~800MB image (includes compiler toolchain).
Multi-stage: ~50MB image (only the artifact).

**Python example:**

```dockerfile
# Stage 1 — builder
FROM python:3.12 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2 — runtime (the deployed image)
FROM python:3.12-slim
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appgroup . /app
USER appuser
WORKDIR /app
ENV PATH=/home/appuser/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Node example:**

```dockerfile
# Stage 1
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2
FROM node:20-alpine
WORKDIR /app
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
COPY --from=builder --chown=appuser:appgroup /app/dist ./dist
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
USER appuser
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

## Local validation before pushing

```bash
docker build -t myapp ./
docker run -p 8000:8000 myapp
curl http://localhost:8000/healthz
```

If this works, CI almost certainly will too.

## Anti-patterns

- Running as root
- Single-stage builds for compiled languages (massive image)
- Hardcoding env vars in `Dockerfile`
- `COPY . .` without `.dockerignore` (ships `.git`, `node_modules`, `.env` into the image)
- Missing `EXPOSE` (orchestrator doesn't know the port)

---

# Module 5: Runtime Configuration

## Critical distinction: build-time vs runtime

**Dockerfile** = how to build the image (build time, generic, language/framework-aware).
**Runtime config** = how to run the image (per-environment, deployment-specific).

Mixing these is the most common novice mistake. The Dockerfile should be **environment-agnostic** — the same image runs in dev, staging, prod, with different runtime configs.

## Three forms of runtime config

### Form A: Kubernetes (Scout-style)

**`pipeline.yaml` (main / production):**

```yaml
port: 8000
healthCheck:
  path: /healthz
env:
  - name: ENV
    value: "production"
  - name: LOG_LEVEL
    value: "info"
envFrom:
  - secretRef:
      name: myapp-secrets
secret:
  name: myapp-secrets
```

**`pipeline-dev.yaml` (dev branch only):**

```yaml
port: 8000
healthCheck:
  path: /healthz
env:
  - name: ENV
    value: "development"
  - name: LOG_LEVEL
    value: "debug"
envFrom:
  - secretRef:
      name: myapp-secrets-dev   # ← -dev suffix YOU add
secret:
  name: myapp-secrets            # ← NO -dev (platform appends it)
```

**The -dev secret rule (critical, error-prone):**
- `envFrom.secretRef.name` → **you** add `-dev`
- `secret.name` → **you do NOT** add `-dev`; the pipeline appends it automatically

If you mess this up, the Pod mounts the wrong (or missing) secret and fails silently.

### Form B: docker-compose (VPS-style, freelance)

```yaml
services:
  myapp:
    image: ghcr.io/pr3t3l/myapp:latest
    ports:
      - "8000:8000"
    environment:
      - ENV=production
      - LOG_LEVEL=info
    env_file:
      - .env.production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
      interval: 30s
      timeout: 5s
      retries: 3
    restart: always
```

Conceptually identical to `pipeline.yaml`. Different syntax, same model: declarative "how to run this image."

### Form C: PaaS config (Vercel, Railway, Render, Fly.io)

Usually defined in the platform's dashboard or a config file (`vercel.json`, `fly.toml`, etc.). The platform abstracts the rest.

## Env-driven paths and resources (universal rule)

**Any string that changes between environments must be an env var, never hardcoded.**

Bad:
```python
def upload(file):
    path = "/Volumes/prod_1_int_0_raw/myschema/myvol/" + file.name
    storage.upload(path, file)
```

Three problems: dev writes to prod, changing catalog requires code change, tests impossible.

Good:
```python
import os

def upload(file):
    base = os.environ['STORAGE_BASE_PATH']
    storage.upload(f"{base}/{file.name}", file)
```

Config per environment:
- Dev: `STORAGE_BASE_PATH=/Volumes/stage_internal/myschema/myvol`
- Prod: `STORAGE_BASE_PATH=/Volumes/prod_1_int_0_raw/myschema/myvol`

**Applies universally to:** DB URLs, API endpoints, S3 paths, webhook URLs, feature flags.

**Heuristic:** if a string differs across environments, env var. No exceptions.

## Anti-patterns

- Build-time env vars baked into the image
- Hardcoded paths/URLs in code
- Different Dockerfiles per environment (should be one image, different configs)
- Secrets in `pipeline.yaml` (they go elsewhere — see Module 6)

---

# Module 6: Secrets Management

## Three principles, non-negotiable

1. **Never in code.** Never in git. Never in Docker image.
2. **One source of truth.** No copy-paste between locations.
3. **Injected at runtime.** Not at build time.

Violating any of these is the most common source of leaks.

## Where secrets live by environment

### Local development

`.env` file in repo root (gitignored):
```
DATABASE_URL=postgres://localhost/myapp
OPENAI_API_KEY=sk-...
```

Plus `.env.example` (committed) with empty values to document what's needed:
```
DATABASE_URL=
OPENAI_API_KEY=
```

### CI/CD pipeline

Stored in your CI/CD platform's secret store, injected as env vars during workflow.

**GitHub Actions example:**
```yaml
- name: Deploy
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: ./deploy.sh
```

### Production runtime

The container reads secrets from the orchestrator-injected env. Never reads `.env` files. Never has secrets baked into the image.

## Stack by scale

| Scale | Solution | Cost | Trade-off |
|---|---|---|---|
| Solo, 1-3 projects | GitHub Secrets | Free | No rotation, hard to share across repos |
| Solo, 5+ projects | **Doppler** | Free for solo | Cleanest UX, sync everywhere |
| Open-source preference | Infisical | Free (self-hosted) | More setup |
| VPS-only, minimum | `.env` with `chmod 600` on server | Free | Manual rotation, no audit |
| Enterprise (Scout) | AWS Secrets Manager + ExternalSecret | $$ | Standard for AWS shops |
| GCP | Secret Manager | $$ | Standard for GCP shops |
| Azure | Key Vault | $$ | Standard for Azure shops |

**Recommendation for Alfredo:** GitHub Secrets to start. Migrate to Doppler when you hit 4-5 active projects.

## Scout's specific pattern (AWS Secrets Manager)

**Path naming convention:**
- Main: `dp/<repo-short>/<app-name>`
- Dev: `dp/<repo-short>/<app-name>-dev`

Where `<repo-short>` = repo name without `dp-` prefix.

**Content = JSON object:**
```json
{
  "DATABASE_URL": "postgres://...",
  "API_KEY": "abc123"
}
```

Each key becomes an env var inside the Pod.

If no secrets yet, store `{}` — the sync mechanism needs the entry to exist.

## Personal credentials vs machine credentials

Production apps should **never** use personal credentials (PATs, your own API tokens). Always use machine identities.

| Wrong | Right |
|---|---|
| App uses Alfredo's GitHub PAT | App uses a GitHub App |
| App uses Alfredo's Databricks PAT | App uses a Service Principal |
| App uses Alfredo's AWS Access Key | App uses an IAM Role |
| App uses Alfredo's Stripe key (personal) | App uses Stripe's restricted key for the app |

**Why:** when Alfredo leaves, changes teams, or rotates credentials → app breaks. Audit logs show "Alfredo did X at 3am" (false). Machine identities survive personnel changes and produce accurate audit trails.

## Anti-patterns

- `.env` committed to git
- Secrets in Dockerfile `ENV` directives
- Same secret shared across many unrelated apps
- Personal tokens used by production apps
- No `.env.example` (next dev has no idea what's required)

---

## Next stop

Image is built and runtime config is wired — now move to [`freelance-deploy-pipeline`](freelance-deploy-pipeline.md) to automate build + ship + validate.
