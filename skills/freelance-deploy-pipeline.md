# freelance-deploy-pipeline

**Part of the `freelance-deployment-playbook` series.** Index: [`freelance-deployment-playbook`](freelance-deployment-playbook.md). Siblings: `freelance-deploy-foundations`, `freelance-deploy-package`, `freelance-deploy-debug`.

**Scope:** automate build → push → ship → validate, and choose the CD architecture. Modules 7 (CI/CD), 8 (Validation), 11 (Process Governance) of the original playbook.

**Trigger keywords:** CI/CD, GitHub Actions, workflow, workflow_call, reusable workflow, pipeline.yaml, registry, GHCR, ECR, SemVer, git SHA tag, smoke test, Uptime Kuma, Argo CD, Kargo, Helm, GitOps, coupled vs decoupled, promotion, maturity model.

---

# Module 7: Pipeline Orchestration (CI/CD)

## CI vs CD — the line

**CI (Continuous Integration)** answers: "Can we build and verify the app artifact?"
- Runs on every push
- Lints, tests, builds Docker image
- Catches issues before merge

**CD (Continuous Deployment)** answers: "Can we take that artifact, move it through the platform, and make it run?"
- Triggers on merge to deploy branch (main/dev)
- Pushes image to registry
- Updates deployment manifests
- Triggers cluster rollout

## Two architectures

### Architecture A: Coupled (Scout internal, freelance default)

CI and CD in one workflow. Simple, linear, all in GitHub Actions.

```
[git push to main]
    ↓
[Workflow]
    ├── CI: build + test
    ├── push image to registry
    ├── apply secrets
    └── deploy to runtime
    ↓
[App live]
```

**Use when:** single team owns build + deploy, simple infra, fewer than ~5 environments.

### Architecture B: Decoupled (Scout PE, large-scale freelance)

CI ends when the artifact lands in the registry. CD is a separate system observing the registry.

```
[git push to main]
    ↓
[CI workflow: build + push to registry with SemVer tag]
    ↓
[Registry]
    ↓
[Kargo or similar promotion tool detects new version]
    ↓
[Updates manifests in a config repo]
    ↓
[Argo CD observes config repo, syncs cluster]
    ↓
[App live]
```

**Use when:** multiple environments to promote through, multi-cluster, regulated environment with audit needs, separate platform team.

(For deeper governance trade-offs see Module 11 below.)

## GitHub Actions essentials

### Workflow file location
`.github/workflows/<name>.yaml` — GitHub auto-discovers files here.

### Triggers
```yaml
on:
  push:
    branches: [main]              # auto on push to main
  pull_request:
    branches: [main]              # auto on PR to main
  workflow_dispatch:              # manual trigger only
  schedule:
    - cron: '0 6 * * *'           # cron (every day at 6am UTC)
```

### Reusable workflows (the high-ROI pattern)

Define once, use everywhere via `workflow_call`. This is Scout's `dp-templates` pattern.

**Template repo (`pretel-templates/.github/workflows/python-vps-deploy.yaml`):**
```yaml
on:
  workflow_call:
    inputs:
      app-name:
        required: true
        type: string
      vps-host:
        required: true
        type: string

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: docker build -t ghcr.io/pr3t3l/${{ inputs.app-name }}:${{ github.sha }} .
      # ... etc
```

**App repo using the template:**
```yaml
on:
  push:
    branches: [main]

jobs:
  deploy:
    uses: pr3t3l/pretel-templates/.github/workflows/python-vps-deploy.yaml@main
    with:
      app-name: declassified-pipeline
      vps-host: ${{ vars.VPS_HOST }}
    secrets: inherit
```

The app repo becomes ~10 lines. The template carries the ~200-line CI/CD logic.

**Build the template repo only after 2-3 manual deploys.** Don't pre-build templates without real projects driving them.

## Freelance starter workflow (Python + VPS via SSH)

```yaml
name: deploy
on:
  push:
    branches: [main]

jobs:
  ci-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest

  build-and-push:
    needs: ci-checks
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - run: |
          docker build -t ghcr.io/pr3t3l/myapp:${{ github.sha }} .
          docker push ghcr.io/pr3t3l/myapp:${{ github.sha }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: SSH deploy
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            docker pull ghcr.io/pr3t3l/myapp:${{ github.sha }}
            cd /opt/myapp
            docker compose up -d
```

This mirrors Scout's `bootstrap → ci-checks → deploy` pattern in miniature.

## Tagging: SemVer vs git SHA

**Scout internal** uses git short SHA (e.g., `a3f9b2c`). Simple, unique per commit, no extra step.

**Scout PE** uses SemVer (e.g., `v1.2.3`). Required for promotion tooling and meaningful version history.

**Freelance recommendation:** start with git SHA. Add SemVer only if you need rollback by version name or have a release cadence to communicate to users.

## Anti-patterns

- Workflows that don't fail on test errors (silent broken deploys)
- No caching of dependencies (slow workflows, expensive CI minutes)
- Putting deploy logic in app repos instead of reusable templates (duplication)
- No path filters in monorepos (every push triggers every workflow)
- Building templates before you have projects to extract patterns from

---

# Module 8: Validation & Monitoring

## A green workflow is necessary, not sufficient

The pipeline can succeed and the app still be dead. Common failure modes between "image pushed" and "users happy":
- Pod won't start (missing env var)
- Pod starts but crashes on first request (code bug)
- Pod runs but doesn't respond (healthcheck misconfigured)
- Memory leak → OOMKilled
- Secret didn't sync from vault to runtime

## Smoke test — the minimum

Add a final step to every deploy workflow:

```yaml
- name: Smoke test
  run: |
    sleep 15
    curl -f https://myapp.com/healthz || exit 1
```

A failed smoke test = failed deploy = rollback triggered (or at least alarm raised).

## Validation checklist post-deploy

| Check | How |
|---|---|
| URL loads | `curl -I https://app.url` returns 200 |
| Health endpoint returns 200 | `curl https://app.url/healthz` |
| Pod is `Ready` (K8s) | `kubectl get pods` shows 1/1 Ready |
| Container is `Up` (Docker) | `docker ps` |
| Logs show clean startup | `kubectl logs <pod>` or `docker logs <container>` |
| Secrets present in env | `kubectl exec <pod> -- env \| grep API_KEY` |

## Monitoring escalation

| Level | Tool | When |
|---|---|---|
| Manual smoke test | curl in workflow | Always, from day 1 |
| Uptime monitoring | Uptime Kuma (open source, self-hosted) | When you have paying clients |
| Logs centralization | Loki + Grafana, or Datadog | When you have 3+ services |
| APM (application perf monitoring) | Datadog, New Relic, Sentry | When debugging perf issues becomes common |
| Full observability stack | OpenTelemetry + Grafana stack | Enterprise / regulated |

**Recommendation for Alfredo:** smoke tests immediately. Uptime Kuma when you start charging clients. Don't over-invest before there's pain.

## Anti-patterns

- Trusting green workflow without smoke test
- No alerts on production failures (you find out from users)
- Logs only on the server (no aggregation = can't search across deploys)

---

# Module 11: Process Governance

## CI/CD architecture choice

The fundamental decision: **coupled vs decoupled.**

### Coupled (Scout internal, freelance default)

CI and CD in one workflow. Linear, simple, all in GitHub Actions.

**Pros:**
- Easy to understand end-to-end
- One source of truth (one workflow file)
- Fast feedback (one place to look)

**Cons:**
- Hard to promote across many environments
- Tight coupling: changing CD logic requires touching every app repo
- Doesn't scale to multi-cluster

**Use when:** solo dev, small team, <3 environments, <10 services.

### Decoupled (Scout PE, large-scale)

CI ends at the registry. CD is a separate system observing artifacts.

```
[CI]               [CD]
push → registry  ←  Kargo (promotion) → Argo CD (sync) → cluster
```

**Pros:**
- GitOps: cluster state matches a Git repo, always
- Multi-cluster: same config repo syncs N clusters
- Rollback by version is trivial
- Audit trail is clean
- Separation of concerns: app team owns build, platform team owns deploy

**Cons:**
- More moving parts (Kargo + Argo CD + config repo)
- Steeper learning curve
- Overkill for small projects

**Use when:** multiple environments to promote through, multi-cluster, regulated, separate platform team.

## Key tools in the decoupled world

| Tool | What it does |
|---|---|
| **Helm** | Kubernetes package manager. Parameterized YAML templates ("charts") installed with one command. Like npm for K8s. |
| **Argo CD** | GitOps tool. Watches a Git repo with manifests + watches a cluster. Keeps them in sync. Declarative, idempotent, auditable. |
| **Kargo** | Promotion tool on top of Argo CD (2023). Manages "v1.2.3 from dev → staging → prod" with gates. |
| **SemVer** | Versioning convention: `MAJOR.MINOR.PATCH`. Required for meaningful promotion. |
| **GitOps** | Philosophy: cluster state lives in Git. Changes = commits. Rollback = git revert. |

## Ownership boundaries — the most portable lesson

```
Develop  ─────────► App team
Package  ─────────► App team (CI verifies)
        ─── handoff at the artifact ───
Storage  ─────────► Shared (artifact in registry)
Deploy   ─────────► Platform team
Run      ─────────► Platform team
Scale    ─────────► Platform team
```

**The artifact is the contract boundary.** Before that point: build responsibility. After: operate responsibility.

This pattern shows up everywhere — not just CI/CD:
- API design (request/response is the contract)
- Microservice boundaries (service interface is the contract)
- AI systems (prompt/output schema is the contract)

When designing any system, ask: where is the contract boundary, and who owns each side?

## Maturity model

| Stage | What you adopt |
|---|---|
| **Solo developer, 1-3 projects** | Coupled CI/CD, GitHub Actions, GHCR, VPS or PaaS, GitHub Secrets |
| **Solo with paying clients, 4-8 projects** | Reusable workflows (`pretel-templates`), Doppler, Uptime Kuma, smoke tests |
| **Small team or larger clients, 8+ projects/services** | Consider decoupled CD (Argo CD on a VPS or managed K8s) |
| **Regulated environment / multi-region** | Full GitOps stack, SemVer tagging, promotion gates |

Don't skip stages. Each one solves problems the previous one created.

## When to migrate from coupled to decoupled

Signs it's time:
- You have 3+ environments and promotion between them is painful
- You operate multiple clusters
- Rollback by version is a regular need
- Audit/compliance requires immutable change history
- You have a separate ops/platform person

Don't migrate just because "it's more advanced." Coupled is correct for most situations.

## Anti-patterns

- Adopting Argo CD for a single service on a single cluster (overkill)
- Sticking with coupled when you have 5 environments and weekly promotion pain
- Mixing strategies in one org (some apps GitOps, others coupled, no clarity)
- Treating "decoupled" as the goal when "fast feedback for one team" is the actual goal

---

## Next stop

App is shipped. When it misbehaves, jump to [`freelance-deploy-debug`](freelance-deploy-debug.md).
