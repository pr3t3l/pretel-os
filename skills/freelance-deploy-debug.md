# freelance-deploy-debug

**Part of the `freelance-deployment-playbook` series.** Index: [`freelance-deployment-playbook`](freelance-deployment-playbook.md). Siblings: `freelance-deploy-foundations`, `freelance-deploy-package`, `freelance-deploy-pipeline`.

**Scope:** debugging an app that is already deployed but misbehaving. Module 10 of the original playbook.

**Trigger keywords:** kubectl, debug pod, CrashLoopBackOff, ImagePullBackOff, OOMKilled, Pending, Events, logs, describe pod, exec, 401, 403, 429, 5xx, inspect button, docker logs, docker inspect.

---

# Module 10: Debugging Deployed Apps

## The 4-layer method

When something is broken in deployed environment, work outside → in:

```
1. STATUS column   → identify the symptom
2. Events          → cause in plain English (orchestrator's perspective)
3. Describe        → confirm details (image, env, mounts, last termination)
4. Logs            → the app's own voice (stack trace, error message)
5. Exec (rare)     → inspect inside the container, last resort
```

**Rule:** stop at the first layer where you have the answer. Don't dig all four every time.

## STATUS reference table (Kubernetes)

The six states that resolve 90% of issues:

| STATUS | Meaning | Typical cause | First action |
|---|---|---|---|
| **Running** | Alive and serving | — | If unresponsive, check logs |
| **Pending** | Waiting to start | Cluster out of resources, image pulling | Check events |
| **CrashLoopBackOff** | Starts, crashes, restarts, repeats | Code bug, missing env var, bad config | Check logs |
| **ImagePullBackOff** | Can't download image | Bad tag, registry permissions, registry down | Check describe |
| **OOMKilled** | Killed for using too much memory | Memory limit too low, memory leak | Raise limits or fix leak |
| **Error** | Container exited non-zero | App crashed at startup | Check logs |

**`CrashLoopBackOff` translation:** Crash Loop Back-Off. K8s uses exponential backoff — first crash waits 10s before restart, then 20s, 40s, up to 5 minutes. Hence the name.

## Events vs Logs — common confusion

**Events** = what **Kubernetes** says about your Pod
- "0/3 nodes have available memory"
- "Readiness probe failed 3 times"
- "Killed by OOM"
- Orchestrator perspective

**Logs** = what **your app** says about itself
- `INFO: Server started on port 8000`
- `ERROR: DATABASE_URL not set`
- `Traceback (most recent call last):...`
- App perspective

**Which to check first:**
- Pod won't start → **Events** (orchestrator will tell you why)
- Pod starts but misbehaves → **Logs** (app will tell you what)

## kubectl essentials

| Command | Use |
|---|---|
| `kubectl get pods` | List pods, see STATUS |
| `kubectl get pods -n <namespace>` | Specific namespace |
| `kubectl get events --sort-by=.lastTimestamp` | Recent events |
| `kubectl describe pod <pod>` | Full pod detail |
| `kubectl logs <pod>` | Current logs |
| `kubectl logs <pod> --previous` | Logs from previous crashed container |
| `kubectl logs <pod> -f` | Follow logs in real-time |
| `kubectl exec <pod> -- <cmd>` | Run command inside pod |
| `kubectl exec -it <pod> -- /bin/sh` | Interactive shell inside pod |

## docker essentials (VPS, no K8s)

| docker command | kubectl equivalent |
|---|---|
| `docker ps -a` | `kubectl get pods` |
| `docker logs <container>` | `kubectl logs <pod>` |
| `docker logs <container> -f` | `kubectl logs <pod> -f` |
| `docker inspect <container>` | `kubectl describe pod <pod>` |
| `docker exec -it <container> sh` | `kubectl exec -it <pod> -- sh` |
| `docker stats` | `kubectl top pods` |

## HTTP status codes troubleshooting

When an app or API call fails with a status code:

| Code | Meaning | First check |
|---|---|---|
| **401 Unauthorized** | "I don't know who you are" | Token missing, malformed, or expired |
| **403 Forbidden** | "I know who you are, but you can't" | Permissions missing on your identity |
| **404 Not Found** | "What you requested doesn't exist" | Path typo, resource deleted |
| **429 Too Many Requests** | Rate limited | Throttle calls, check rate limit |
| **5xx Server Error** | Server's fault, not yours | Wait, retry, report to provider |

**Don't confuse 401 vs 403** — auth vs permissions is a totally different fix path.

## The "inspect button" pattern (Scout's contribution)

Manual workflow that runs the 5-step debug sequence with one click:

```yaml
name: inspect
on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [dev, main]
      exec-command:
        type: string
        required: false

jobs:
  inspect:
    uses: pr3t3l/pretel-templates/.github/workflows/inspect-vps.yaml@main
    with:
      app-name: my-app
      environment: ${{ inputs.environment }}
      exec-command: ${{ inputs.exec-command }}
    secrets: inherit
```

The reusable workflow runs: list containers → list events → inspect → logs → optional exec. Democratizes debug — no need to SSH manually.

**For VPS without K8s, the equivalent template:**

```yaml
on:
  workflow_call:
    inputs:
      app-name: { required: true, type: string }
      exec-command: { required: false, type: string }

jobs:
  inspect:
    runs-on: ubuntu-latest
    steps:
      - uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            echo "=== docker ps ==="
            docker ps -a --filter "name=${{ inputs.app-name }}"
            echo "=== logs (last 200 lines) ==="
            docker logs --tail 200 ${{ inputs.app-name }}
            echo "=== inspect ==="
            docker inspect ${{ inputs.app-name }} | head -100
            if [ -n "${{ inputs.exec-command }}" ]; then
              echo "=== exec ==="
              docker exec ${{ inputs.app-name }} sh -c "${{ inputs.exec-command }}"
            fi
```

## Common failure patterns (cheatsheet)

| Symptom | Likely cause | Fix |
|---|---|---|
| `ImagePullBackOff` with "not found" | Wrong image tag in manifest | Check tag matches what was pushed |
| `CrashLoopBackOff`, logs show `KeyError: 'X'` | Env var X not set | Add to secret/config |
| `Pending` for >2 min | Cluster out of memory/CPU | Reduce limits or scale cluster |
| Pod `Running` but app returns 502 | Healthcheck path returns non-200 | Fix path or fix app's healthcheck handler |
| `OOMKilled` | Memory limit too low | Raise limit or find leak |
| Pod restarts every X seconds | Liveness probe failing | Verify probe path and timeout |
| 403 from external API | Wrong/missing permission on credential | Re-check credential's permission set |
| `--previous` logs empty | Container never crashed | The "current" logs are the right ones |

## Anti-patterns

- Jumping straight to `kubectl exec` instead of reading events + logs first
- Logging unstructured strings (`print("error happened")` instead of structured logs)
- No request IDs in logs (impossible to trace a single user's flow)
- Confusing 401 vs 403 (different fix paths)
- Tail-spiraling: editing app, redeploying, observing, editing again, without forming a hypothesis
