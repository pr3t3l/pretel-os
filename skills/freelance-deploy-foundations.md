# freelance-deploy-foundations

**Part of the `freelance-deployment-playbook` series.** Index: [`freelance-deployment-playbook`](freelance-deployment-playbook.md). Siblings: `freelance-deploy-package`, `freelance-deploy-pipeline`, `freelance-deploy-debug`.

**Scope:** project setup before the first container is built — language choice, pre-flight validation, repo structure, daily git workflow. Modules 1, 2, 3, 9 of the original playbook.

**Trigger keywords:** language selection, stack, prefix, repo structure, monorepo, .env.example, health endpoint, /healthz, branch strategy, conventional commits, squash, force-with-lease, branch protection.

---

# Module 1: Language Selection

## The honest truth first

The language matters less than the engineer's familiarity with it. A project finished in your weaker language always beats an abandoned project in the "optimal" one. **Speed of iteration comes from fluency, not benchmarks.**

## The 4 factors that actually decide

In order of real-world weight:

### 1. Domain constraints (some domains have a default)

| Building… | The default language is… | Why |
|---|---|---|
| iOS native app | Swift | Apple's official |
| Android native app | Kotlin | Google's official |
| Cross-platform mobile | Dart (Flutter) or JS (React Native) | One codebase, both platforms |
| Frontend web | JavaScript / TypeScript | The only language that runs in browsers |
| AAA game / 3D engine | C++ or C# (Unity) | Performance |
| Operating system / driver | C, C++, Rust | Hardware access |
| Data science / ML / AI | Python | Where the libraries are |
| Backend / API / web app | **Open territory** | The contested space |

Backend is the only stage where there's real choice. That's where you'll live.

### 2. What you (or your team) already know

This is heavier than any benchmark. If Scout's team uses Python, you use Python. If your freelance stack is Python + TypeScript, don't add Go because it's faster.

### 3. Ecosystem alignment

"Ecosystem" = libraries + frameworks + community + tutorials.

- LLMs/AI heavy? → Python (LangChain, LiteLLM, all SDKs first-class)
- Serious scraping? → Python (BeautifulSoup, Scrapy, Playwright)
- Fastest full-stack web? → TypeScript + Next.js
- Efficient microservice with simple deploy? → Go
- Excel/tabular processing? → Python (pandas)

### 4. External constraints

- Client mandates ".NET only" → C#
- Java shop → Java/Kotlin
- Legacy Ruby on Rails system → Ruby

You don't always choose.

## The 6 languages that cover 95% of cases

### Python — default for nearly everything backend/AI

**Excels at:** AI/LLM/ML, data, scraping, automation, APIs (FastAPI/Django), DevOps scripting, rapid prototyping.

**Avoid for:** mobile apps, frontend web, games, max-performance systems.

**Why for you:** entire AI stack is Python-first; Scout also uses it; pretel-os baseline.

### JavaScript / TypeScript — mandatory for frontend, strong for backend

**Excels at:** frontend (no real alternative), Node.js backend (Next.js dominant), cross-platform apps (React Native, Electron).

**TypeScript = JavaScript with types.** In serious projects today, always TypeScript.

**Avoid for:** heavy AI/ML (Python wins), fast automation (Python more ergonomic).

**Why for you:** when Declassified Cases or any client needs a web/dashboard/landing.

### Go — the "step up" when Python isn't fast enough

**Excels at:** efficient microservices, CLI tools (single binary), DevOps tooling (Docker, K8s, Terraform written in Go).

**Avoid for:** AI/ML, rapid prototyping.

**Why for you:** ignore for now. If a Python service eventually can't keep up, then evaluate.

### Rust, Java/Kotlin, C# — good to recognize but probably unused

- **Rust** — extreme performance + safety. Brutal learning curve. Systems work.
- **Java / Kotlin** — large enterprises, Android.
- **C# / .NET** — Microsoft world, Unity. May surface if Scout pushes you toward pure Microsoft.

## Decision tree for picking

```
Must run in a browser?
  → JavaScript/TypeScript (no choice)

Mobile app?
  → Flutter (Dart) for iOS+Android from one code
  → Swift / Kotlin for best-per-platform

Backend / API / automation / AI?
  → Python by default
  → TypeScript if you already have TS frontend and want one stack
  → Go only if Python doesn't scale

Native desktop?
  → Tauri (Rust+JS) or Electron (JS) or platform-native language

Unsure?
  → Python
```

## Concrete recommendation for Alfredo (next 12 months)

**Cover with two languages:**

1. **Python** — backend, AI, automation, pretel-os, jobs, APIs, MTM, Forge pipeline. *The* language of your stack.
2. **TypeScript** — only when frontend is needed (Declassified landing, dashboards, client web apps).

That covers 95% of Scout + freelance + personal. **Don't diversify until a concrete project forces it.** Learning 5 languages in parallel is the autodidact's classic trap.

## Anti-patterns

- Choosing by trend ("Rust is the new thing")
- Choosing by benchmarks when not actually CPU-bound (your bottleneck is usually the OpenAI API taking 3 seconds)
- Mixing without reason (Python here, Node there, Go elsewhere — context switching tax)
- Switching mid-project ("I should have used X")

---

# Module 2: Pre-flight Checklist

The pipeline does not fix a broken app. It only packages and runs it. If it doesn't work on your laptop, CI will fail later.

## Five checks before touching any pipeline

| Check | Why it matters |
|---|---|
| App runs locally without crashing | If it dies on your machine, CI fails later |
| Listens on a known port (e.g., 3000) | Kubernetes/Docker needs to know where to send traffic |
| Health endpoint exists (`/healthz` returns 200) | Orchestrator uses this to decide if Pod is alive |
| Required env vars documented | You must split env vs secrets later |
| Sensitive values identified | Secrets go to vault, not YAML |

## The health endpoint — explained

A special URL your app exposes so the orchestrator can ask "are you alive?". Typically `/healthz` or `/health`.

**Minimal example (FastAPI):**

```python
@app.get("/healthz")
def healthz():
    return {"status": "ok"}
```

That's enough. No DB check, no fancy logic. Just confirms the process responds.

**When you'd add more logic:** if your app depends on a DB and you want Kubernetes to take it out of rotation when DB is unreachable, you'd query the DB in the health check. But default: simple 200.

## Anti-patterns

- Skipping local validation because "tests passed" — tests ≠ a running app
- Hardcoding the port in multiple places — pick one source (env var)
- No health endpoint — orchestrators will eventually kill you assuming you're dead

---

# Module 3: Repo Setup

## Two decisions upfront

### Decision 1: Naming convention

Pick a prefix system and never break it. Examples:

**Scout's convention:** `dp-<repo-name>` (`dp` = data platform). Required by Scout's platform — repo won't be recognized without it.

**Recommended for Alfredo's freelance:**
- `dc-*` for Declassified projects (`dc-pipeline`, `dc-landing`)
- `pretel-*` for personal tools (`pretel-os`, `pretel-templates`)
- `client-<name>-*` for client work (`client-acme-api`)

The point is consistency. When you have 30 repos, prefixes save you.

### Decision 2: Single-app vs multi-app repo

**Single-app (recommended starting point):**
```
my-app/
├── .github/workflows/
├── src/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── deploy/
├── .env.example
├── .gitignore           # includes .env
├── README.md
└── pyproject.toml       # or package.json, go.mod, etc.
```

One repo, one app, simple. Start here always.

**Multi-app (Scout's pattern):**
```
dp-my-repo/
├── .github/
│   └── workflows/
│       ├── app-one.yaml
│       └── app-two.yaml
├── app-one/
│   ├── Dockerfile
│   ├── pipeline.yaml
│   └── src/
└── app-two/
    ├── Dockerfile
    ├── pipeline.yaml
    └── src/
```

Each app is a self-contained folder. Workflow path filters trigger only the changed app. Use only when 2+ related apps share lifecycle/team.

## Standard files explained

| File | Purpose |
|---|---|
| `.gitignore` | Files git ignores. **Must include `.env`** |
| `.env.example` | Template showing required env vars with empty values. Committed. |
| `Dockerfile` | Recipe to build the container image |
| `docker-compose.yml` | How to run the app + dependencies locally |
| `README.md` | Quickstart: how to run, test, deploy |
| `pyproject.toml` / `package.json` | Language-level deps |
| `.github/workflows/` | CI/CD pipeline definitions |

## Anti-patterns

- `.env` committed (catastrophic — leak of secrets)
- No `.env.example` (next dev has no idea what env vars exist)
- README missing or stale
- Files in inconsistent locations across projects

---

# Module 9: Daily Git Workflow

## Pre-requisite concepts

**Git** = version control system. Lives on your laptop. Tracks file changes.

**GitHub** = cloud service hosting Git repos + extras (PRs, Actions, Issues).

**Branch** = parallel line of development from a point on the trunk. Lets you work on changes without affecting main.

**PR (Pull Request)** = "hey team, review my branch before I merge to main." Social + technical gate.

## The trunk-based workflow

```
main → feature branch → PR → main → auto-deploy
                ↑
        (optional) dev branch for staging tests
```

### Step-by-step

```bash
# 1. Start from main
git checkout main
git fetch origin
git pull origin main

# 2. Create feature branch from main
git checkout -b feature/file-upload

# 3. Work, then stage and commit
git add .
git commit -m "feat(upload): add file upload endpoint"

# 4. Push branch
git push -u origin feature/file-upload

# 5. (Optional) Test on staging via dev branch
git checkout dev
git pull origin dev
git merge feature/file-upload
git push origin dev
# → triggers staging deploy, validate there

# 6. Raise PR to main
gh pr create --base main --head feature/file-upload \
  --title "feat: add file upload" \
  --body "Adds upload endpoint. Tested on staging."

# 7. Address review comments, push more commits if needed
# 8. Resolve conflicts if any
git fetch origin
git rebase origin/main
# resolve conflicts, then:
git add .
git rebase --continue
git push --force-with-lease

# 9. Merge to main (squash)
gh pr merge --squash --delete-branch

# 10. CI/CD auto-deploys
gh run watch
```

## Branch naming conventions

| Prefix | Use for | Example |
|---|---|---|
| `feature/` | new functionality | `feature/file-upload` |
| `bugfix/` | fix a bug | `bugfix/login-timeout` |
| `chore/` | config, deps, tooling | `chore/update-deps` |
| `hotfix/` | urgent prod fix | `hotfix/null-pointer` |
| `refactor/` | code change, no behavior change | `refactor/extract-validator` |
| `docs/` | docs only | `docs/update-readme` |

## Conventional Commits

Format: `<type>(<scope>): <description>`

| Type | Use |
|---|---|
| `feat:` | new feature |
| `fix:` | bug fix |
| `chore:` | tooling/config |
| `docs:` | docs only |
| `refactor:` | code change, no behavior change |
| `test:` | add/fix tests |
| `perf:` | performance improvement |

Examples:
```
feat(auth): add OAuth login flow
fix(upload): handle empty file edge case
chore(deps): bump fastapi to 0.110
docs(readme): update setup instructions
```

**Why this matters:** in 6 months when you read git log, "fix stuff" is useless. `fix(auth): handle null user in token validation` is gold.

## Merge strategies

| Strategy | What it does | When |
|---|---|---|
| `--merge` (default) | Preserves all commits + adds merge commit | Rarely; noisy history |
| `--squash` | Collapses all branch commits into one on main | **Default choice** — clean history, one commit per feature |
| `--rebase` | Reapplies your commits on top of main | When linear history matters and no merge commits wanted |

Default to squash. One feature = one commit on main.

## Conflict resolution

When your branch and main both touched the same lines:

```bash
git checkout feature/x
git fetch origin
git rebase origin/main
# Git stops at each conflict; edit the file to resolve
git add <fixed-file>
git rebase --continue
git push --force-with-lease   # NOT --force
```

**Critical: `--force-with-lease`, not `--force`.**

- `--force` = "overwrite remote no matter what" → can erase teammates' work
- `--force-with-lease` = "overwrite only if nothing new was pushed since I last fetched" → safety net

**Rule:** never `git push --force` on a shared branch. It's the most career-ending Git command.

## Branch protection (set on day 1)

In GitHub repo settings → Branches → Add rule for `main`:
- Require PR before merge
- Require status checks to pass
- Require branches to be up to date before merging

This prevents accidental direct pushes to main. **Even if you work alone.**

## Working solo — adaptations

The flow works the same. Two solo-specific tips:

1. **Self-PR anyway.** Open PR, walk away for 1-24 hours, return with fresh eyes. Catches surprising amount of issues.
2. **Use AI for review.** Claude Code, GitHub Copilot, etc. — get a second opinion before merging.

## Anti-patterns

- Committing directly to main
- Mixing unrelated changes in one PR ("also added X while I was here")
- Vague commit messages ("fix", "update", "wip")
- `git push --force` on shared branches
- Long-lived feature branches (>1 week) — invite conflict and integration pain
- Skipping PR review because "it's a small change"

---

## Next stop

Once foundations are set, move to [`freelance-deploy-package`](freelance-deploy-package.md) to containerize and configure runtime.
