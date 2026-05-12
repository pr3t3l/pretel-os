# freelance-deployment-playbook

**Skill type:** procedural methodology — **index/entry point** of a 5-skill series.
**Scope:** end-to-end application deployment for both freelance projects and Scout Motors internal work.
**Status:** v1.0 (initial)
**Author:** Alfredo Pretel + Claude (distilled from Scout Motors internal deployment docs + freelance application).

---

## The series

The original 11-module playbook exceeded the L3 4,000-token budget (~12,200 tokens), so the content lives across four sibling skills. Load this index first to find the right one, then `load_skill` the relevant module. Naming prefix `freelance-deploy-*` signals the series; cross-references inside each file point to the next stop.

| Skill | Modules covered | When |
|---|---|---|
| [`freelance-deploy-foundations`](freelance-deploy-foundations.md) | 1 Language, 2 Pre-flight, 3 Repo, 9 Daily Git | Before the first container — pick stack, set up repo, agree on git workflow. |
| [`freelance-deploy-package`](freelance-deploy-package.md) | 4 Dockerfile, 5 Runtime Config, 6 Secrets | Turning the app into a portable artifact. |
| [`freelance-deploy-pipeline`](freelance-deploy-pipeline.md) | 7 CI/CD, 8 Validation, 11 Governance | Automating build → ship → validate; coupled vs decoupled CD. |
| [`freelance-deploy-debug`](freelance-deploy-debug.md) | 10 Debugging Deployed Apps | Production is broken — STATUS → events → describe → logs → exec. |

---

## When to invoke this series

Invoke whenever Alfredo is:

- Starting a new application project (Scout or freelance)
- Setting up CI/CD for an existing project
- Containerizing an application
- Designing the repo structure of a new codebase
- Configuring secrets management
- Debugging a deployed application that misbehaves
- Choosing a programming language or stack for a new build
- Designing branching strategy for a project
- Making decisions about staging vs production environments
- Comparing deployment options (VPS vs PaaS vs Kubernetes)

**Trigger keywords:** deploy, deployment, pipeline, CI/CD, docker, kubernetes, k8s, github actions, dockerfile, pipeline.yaml, secrets, AWS Secrets Manager, ECR, EKS, branch strategy, debug pod, kubectl, helm, argo, gitops, vps, registry.

---

## Core mental model

Every application deployment, regardless of stack, answers six questions in sequence:

1. **Develop** — Does the application work as software?
2. **Package** — Can it be turned into a portable container?
3. **Store** — Where does the built artifact live so deployment systems can fetch it?
4. **Deploy** — How does the artifact become a running service?
5. **Run** — Is it actually serving traffic correctly?
6. **Scale** — Can the platform keep it available under change or failure?

Stages 1-2 are owned by the application team. Stage 3 is the handoff point. Stages 4-6 are owned by the platform layer (whether that's you in freelance, or PE at Scout).

**The artifact in the registry is the contract boundary.** Before that point: app team responsibility. After: platform responsibility.

---

## Decision tree — which skill do I need?

```
Starting a new project?
├── Pick language/stack?         → freelance-deploy-foundations (M1)
├── App not yet built?           → freelance-deploy-foundations (M2 pre-flight)
├── Need to set up repo?         → freelance-deploy-foundations (M3)
└── Design git workflow?         → freelance-deploy-foundations (M9)

Building / packaging?
├── Writing Dockerfile?          → freelance-deploy-package (M4)
├── Configuring how it runs?     → freelance-deploy-package (M5)
└── Handling credentials?        → freelance-deploy-package (M6)

Deploying?
├── Setting up CI/CD?            → freelance-deploy-pipeline (M7)
├── Validating after deploy?     → freelance-deploy-pipeline (M8)
└── Coupled vs decoupled CD?     → freelance-deploy-pipeline (M11)

App deployed but broken?
└──                              → freelance-deploy-debug (M10)
```

---

# Quick Reference Cards

## Repo structure (single-app, freelance default)

```
my-app/
├── .github/workflows/
│   └── deploy.yml
├── src/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── deploy/
│   └── docker-compose.production.yml
├── .env.example
├── .gitignore           # includes .env
├── .dockerignore        # includes .env, .git, node_modules
├── README.md
└── pyproject.toml       # or package.json, go.mod
```

## Repo structure (Scout multi-app)

```
dp-my-repo/
├── .github/workflows/
│   └── <app-name>.yaml
└── <app-name>/
    ├── Dockerfile
    ├── pipeline.yaml
    ├── pipeline-dev.yaml
    └── src/
```

## The -dev secret rule (Scout)

```
envFrom.secretRef.name:  YOU add -dev          (e.g. myapp-secrets-dev)
secret.name:             you do NOT add -dev   (e.g. myapp-secrets)
```

## HTTP error troubleshooting

```
401 → check credentials
403 → check permissions on credentials
404 → check path/resource exists
429 → throttle / check rate limit
5xx → wait, retry, report to provider
```

## STATUS codes (Kubernetes)

```
Running           → healthy
Pending           → events
CrashLoopBackOff  → logs
ImagePullBackOff  → describe
OOMKilled         → raise memory or fix leak
Error             → logs
```

## Git workflow one-liner

```
checkout main → pull → branch from main → work → commit (conventional) →
push → PR → review → merge --squash → auto-deploy
```

## Branch prefixes

```
feature/   bugfix/   chore/   hotfix/   refactor/   docs/
```

## Language default tree

```
Browser?         → TypeScript
Mobile?          → Flutter / Swift / Kotlin
Backend / AI?    → Python (default)
Need speed?      → Go
Don't know?      → Python
```

## Secrets stack by scale

```
Solo, few projects:    GitHub Secrets
Solo, many projects:   Doppler
Open-source pref:      Infisical (self-hosted)
Enterprise:            AWS Secrets Manager / Azure Key Vault / GCP Secret Manager
```

---

# Consolidated Anti-patterns

A complete list across modules (each sub-skill has its own per-module section too):

**Language**
- Choosing by trend / benchmarks instead of fit
- Mixing 4 languages across small projects

**Pre-flight**
- Skipping local validation, trusting CI
- No health endpoint

**Repo**
- `.env` committed
- Missing `.env.example`
- Inconsistent structure across projects

**Dockerfile**
- Running as root
- Single-stage for compiled languages
- `COPY . .` without `.dockerignore`
- Missing `EXPOSE`

**Runtime config**
- Build-time env vars baked in
- Hardcoded paths/URLs
- Different Dockerfiles per environment

**Secrets**
- Secrets in git, in Dockerfile, in pipeline.yaml
- Personal tokens in production apps
- No `.env.example`

**CI/CD**
- Workflows that don't fail on test errors
- No dependency caching
- Deploy logic in each app repo (no templates)
- Pre-building templates without driving projects

**Validation**
- Trusting green workflow without smoke test
- No alerts on production failures

**Git**
- Direct push to main
- Vague commit messages
- `git push --force` on shared branches
- Long-lived feature branches
- Skipping PR review when solo

**Debugging**
- Jumping to `kubectl exec` first
- Unstructured logging
- No request IDs

**Process governance**
- Argo CD for one service on one cluster
- Sticking coupled when scale demands decoupled
- Mixing strategies in one org with no rationale

---

# TODO: Future expansions

When experience warrants, the series should grow with:

- **Module 12: data-layer-integration-patterns** — Postgres vs Redis vs S3 vs vector DB; connection pooling; migrations; backups. Add after 2-3 freelance projects with real data layers.
- **Module 13: observability-stack** — structured logging, distributed tracing, metrics, alerts. Add when running 3+ services or paying clients exist.
- **Module 14: cost-optimization** — VPS sizing, registry costs, CI/CD minutes, model API spend. Add when monthly infra bill exceeds $200.
- **Module 15: security-hardening** — beyond non-root: image scanning, secret scanning, dependency audit, SBOM. Add when handling client-sensitive data.
- **Companion project: `pretel-templates`** — reusable GitHub Actions workflows for Python/VPS, static/Vercel, Node/VPS, inspect-vps. Build after 2-3 manual deploys reveal the pattern.
- **Companion tool: `scaffold_app`** — MCP tool that generates a complete repo from `(name, language, deploy_target)`. Build after 5+ projects with the playbook prove the structure.

---

# Notes on origin

This series is distilled from:

- Scout Motors internal deployment docs by Venkatesh Lagishetti (5 docs: Apply Workflow / One-Line Lock, GitHub Application Management, Inspect Setup, Databricks Notes, Internal vs PE CI/CD Comparison)
- Concept mapping sessions between Alfredo Pretel and Claude (May 2026)
- Freelance translation layer built specifically for Alfredo's stack (Python, TypeScript, VPS-Docker, GitHub Actions, GHCR)

Scout-specific details (`dp-` prefix, ECR, EKS, AWS Secrets Manager paths, `dp-templates` repo, Databricks catalog naming) are preserved for Scout work. Freelance equivalents (GHCR, K3s/Coolify, Doppler, `pretel-templates`) are provided in parallel throughout.

The skills are auto-sufficient — Claude (or Alfredo) reading any sibling cold should have everything needed to execute that stage of deployment work without external conversation context.
