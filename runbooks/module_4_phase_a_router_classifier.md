# Runbook — Module 4 Phase A: Router Classifier

**Status:** OPERATIONAL (closed 2026-04-28, commit 28fec7b)
**Scope:** Phase A only (classifier). Phases B–F covered by their own runbooks when shipped.
**Owner:** Alfredo Pretel
**Last reviewed:** 2026-04-28

---

## 1. What this component does

The Router classifier is the single entry point that decides what context to load for any operator turn. Given a raw message, it returns a JSON dict with:

| Field | Type | Purpose |
|---|---|---|
| `bucket` | `'personal' \| 'business' \| 'scout' \| null` | Which knowledge bucket the message belongs to |
| `project` | `null` | Reserved for v2 (project scoping) |
| `skill` | `null` | Reserved for v2 (skill selection) |
| `complexity` | `'LOW' \| 'MEDIUM' \| 'HIGH'` | How much downstream context to load |
| `needs_lessons` | `bool` | Whether to activate L4 retrieval |
| `confidence` | `float [0.0, 1.0]` | Self-reported certainty |

The classifier does NOT load context, does NOT execute tools, does NOT reason about the operator's problem. It only classifies. The Layer Loader (Phase B) consumes this output to decide what to actually load.

## 2. Architecture overview

```
Operator message
      │
      ▼
classifier.classify(message, l0_content?, session_excerpt?, request_id?)
      │
      ├──► _load_system_prompt()  ── reads src/mcp_server/router/prompts/classify.txt
      │
      ├──► chat_json(model_alias='classifier_default', ...)
      │         │
      │         ├──► OpenAI SDK pointed at LiteLLM proxy at http://127.0.0.1:4000
      │         │
      │         └──► LiteLLM cascade:
      │                 1. claude-haiku-4-5-20251001         (primary)
      │                 2. claude-sonnet-4-6-20250929        (fallback 1)
      │                 3. openai/gpt-4o-mini                (fallback 2)
      │
      ├──► _build_telemetry(response, model_alias, max_tokens)
      │         └──► returns ChatJsonTelemetry (18 fields)
      │
      ├──► finish_reason classification (BEFORE json.loads):
      │         'stop'           → continue
      │         'length'         → ClassifierTruncatedError
      │         'content_filter' → ClassifierContentFilterError
      │         'tool_calls'     → ClassifierTransportError
      │         other            → ClassifierTransportError (preserves raw value)
      │
      ├──► _strip_markdown_fences(content)  ── defensive against Anthropic JSON mode
      │
      ├──► json.loads(cleaned)
      │
      └──► _validate_response(parsed, telemetry)
                ├── required keys present
                ├── bucket in valid set
                ├── project=null and skill=null (v1 invariant)
                ├── complexity in {LOW, MEDIUM, HIGH}
                ├── needs_lessons is bool (not string)
                └── confidence is numeric in [0.0, 1.0] (bool rejected explicitly)

Returns: tuple[dict, ChatJsonTelemetry]
```

## 3. Files in this component

```
src/mcp_server/router/
├── __init__.py                  # Package init (empty)
├── exceptions.py                # 7 typed exceptions, all carry optional telemetry kwarg
├── litellm_client.py            # chat_json wrapper + ChatJsonTelemetry dataclass
├── classifier.py                # public classify() function + schema validation
└── prompts/
    ├── __init__.py
    └── classify.txt             # system prompt v1 (870 tokens)

tests/router/
├── __init__.py
├── classification_examples.md            # 10 hand-labeled examples
├── classification_examples_loader.py     # markdown parser
├── test_litellm_client.py                # 11 tests (10 mocked + 1 integration)
├── test_classifier.py                    # 8 mocked tests
├── test_classifier_eval.py               # 1 live eval test (@pytest.mark.eval)
└── eval_results/
    ├── eval_20260428T150746Z.json        # first run (failed threshold)
    └── eval_20260428T163600Z.json        # passing run

specs/router/
├── spec.md                      # SDD spec (511 lines)
├── plan.md                      # SDD plan (365 lines)
└── tasks.md                     # SDD tasks (391 lines, 69 atomic)

conftest.py                      # repo root — adds repo to sys.path for pytest
pytest.ini                       # registers `eval` marker
```

## 4. LiteLLM proxy configuration

File: `~/.litellm/config.yaml`

```yaml
model_list:
  - model_name: classifier_default
    litellm_params:
      model: anthropic/claude-haiku-4-5-20251001
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: classifier_fallback_sonnet
    litellm_params:
      model: anthropic/claude-sonnet-4-6-20250929
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: classifier_fallback_openai
    litellm_params:
      model: openai/gpt-4o-mini
      api_key: os.environ/OPENAI_API_KEY

  - model_name: second_opinion_default
    litellm_params:
      model: anthropic/claude-sonnet-4-6-20250929
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: second_opinion_fallback_opus
    litellm_params:
      model: anthropic/claude-opus-4-7
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: second_opinion_fallback_openai
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY

litellm_settings:
  num_retries: 1
  request_timeout: 30
  fallbacks:
    - classifier_default: ["classifier_fallback_sonnet", "classifier_fallback_openai"]
    - second_opinion_default: ["second_opinion_fallback_opus", "second_opinion_fallback_openai"]

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
```

API keys live in `~/.env.litellm` (mode 0600), loaded by systemd unit `~/.config/systemd/user/litellm.service` via `EnvironmentFile=`. Required keys:
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `GEMINI_API_KEY` (legacy, kept but not active in classifier path)
- `LITELLM_MASTER_KEY`

## 5. Operational checks

### 5.1 Health check (every session start)

```bash
# Is the proxy up?
curl -sf http://127.0.0.1:4000/health > /dev/null && echo "litellm UP" || echo "litellm DOWN"

# Is the systemd unit running?
systemctl --user status litellm --no-pager | head -5

# Smoke test the classifier alias
LITELLM_MASTER_KEY=$(grep '^LITELLM_MASTER_KEY=' ~/.env.litellm | cut -d= -f2-)
curl -s http://127.0.0.1:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model":"classifier_default",
    "messages":[
      {"role":"system","content":"Reply ONLY with valid JSON {\"reply\":\"pong\"}. No markdown fences."},
      {"role":"user","content":"ping"}
    ],
    "max_tokens":200,
    "response_format":{"type":"json_object"}
  }' | python3 -c "
import sys, json
r = json.load(sys.stdin)
choice = r['choices'][0]
u = r.get('usage', {})
d = u.get('completion_tokens_details') or {}
print('finish:', choice.get('finish_reason'))
print('content:', choice['message']['content'])
print('reasoning:', d.get('reasoning_tokens', 0))
print('cache_create:', u.get('cache_creation_input_tokens', 0))
print('cache_read:', u.get('cache_read_input_tokens', 0))
"
unset LITELLM_MASTER_KEY
```

Expected output:
- `finish: stop`
- `content: {"reply":"pong"}` (raw JSON, no markdown fences)
- `reasoning: 0` (Haiku 4.5 has no native thinking)
- `cache_create: 0`, `cache_read: 0` (caching not yet activated — see deferred-todo)

### 5.2 Test suite (run before any code change)

```bash
cd ~/dev/pretel-os

# Default suite — fast, no API spend
pytest tests/router/ -v --tb=short
# Expected: 19 passed, 1 deselected (eval test skipped by default)

# Type check
mypy src/mcp_server/router/litellm_client.py --strict
mypy src/mcp_server/router/classifier.py --strict
# Expected: Success: no issues found in 1 source file (each)

# Live eval — costs ~$0.01 per run, opt-in only
pytest -m eval -v --tb=short
# Expected: 1 passed, thresholds cleared
# Output JSON written to tests/router/eval_results/eval_<timestamp>.json
```

Eval thresholds (FAIL the test if not met):
- `bucket_accuracy >= 0.80`
- `complexity_accuracy >= 0.70`
- `schema_violations == 0`

Last passing run baseline (commit 28fec7b): bucket 1.0, complexity 0.8, schema_violations 0.

### 5.3 Eval result inspection

```bash
# Latest report
ls -t ~/dev/pretel-os/tests/router/eval_results/eval_*.json | head -1 | xargs cat | python3 -m json.tool

# Compare two runs
diff <(jq .summary tests/router/eval_results/eval_20260428T150746Z.json) \
     <(jq .summary tests/router/eval_results/eval_20260428T163600Z.json)
```

## 6. Known operational signals

### 6.1 What "healthy" looks like

| Signal | Healthy range |
|---|---|
| `finish_reason` | `stop` for >99% of calls |
| `reasoning_tokens` | 0 (Haiku has no thinking; if non-zero, fallback model fired) |
| `headroom_used_ratio` | < 0.10 (typical classification uses ~30 of 800 tokens) |
| `near_truncation` | False for all calls |
| `cache_hit` | False for now (prompt < 1024 tokens — see deferred-todo) |
| `truncated` | False |

### 6.2 What signals trouble

| Symptom | Likely cause | Action |
|---|---|---|
| `finish_reason='length'` | Model output ran out of room | Check `truncation_cause` — if 'reasoning_overflow' the cascade fired to a thinking model |
| `finish_reason='content_filter'` | Provider safety filter | Investigate the input — should never happen for classification |
| `reasoning_tokens > 0` | Cascade fired to a thinking model (Sonnet 4.6 in extended-thinking mode) or LiteLLM bug #18896 | Confirm primary alias is healthy |
| Markdown fences in raw content | Anthropic JSON-mode regression | Stripper handles it; if rate > 20% per `routing_logs`, prompt-engineer (deferred to Phase F) |
| `provider_metadata` empty `{}` | `_build_telemetry` regression | Re-check the `provider_metadata=provider_metadata` line in the dataclass constructor (was missing in pre-a4f976b code) |
| `model='classifier_default'` (the alias not the concrete model) | LiteLLM behavior — known and accepted | Use `provider_metadata` jsonb dump for concrete model when needed |

### 6.3 Live eval drift detection

Run `pytest -m eval` once per week. Compare against baseline (commit 28fec7b):
- `bucket_accuracy < 0.80` → re-eval, then prompt-engineer if persistent
- `complexity_accuracy < 0.70` → re-eval, then prompt-engineer or re-label examples
- `schema_violations > 0` → BLOCK PHASE B until resolved (the schema is the contract)
- `total_cost_usd_est > $0.05` → investigate model assignment (cascade may be firing repeatedly)

## 7. Common operations

### 7.1 Switch primary classifier model

Edit `~/.litellm/config.yaml` only — no code change.

```bash
# Backup
cp ~/.litellm/config.yaml ~/.litellm/config.yaml.bak.$(date +%Y%m%d-%H%M%S)

# Edit
nano ~/.litellm/config.yaml  # change classifier_default model field

# Validate YAML
python3 -c "import yaml; yaml.safe_load(open('/home/$USER/.litellm/config.yaml'))" && echo "YAML OK"

# Restart proxy
systemctl --user restart litellm
sleep 3
systemctl --user status litellm --no-pager | head -5

# Smoke test (see §5.1)

# Run live eval to confirm thresholds still met
cd ~/dev/pretel-os && pytest -m eval -v --tb=short
```

### 7.2 Edit the classifier prompt

The prompt is at `src/mcp_server/router/prompts/classify.txt`. After any edit:

1. Run live eval: `pytest -m eval -v --tb=short`
2. Inspect the new `tests/router/eval_results/eval_<timestamp>.json`
3. Compare against the previous baseline
4. If thresholds still met → commit. If not → revert or iterate
5. Each prompt edit gets its own commit with the eval delta in the message

DO NOT edit the prompt and the test examples in the same commit — that hides regressions.

### 7.3 Add a new test example

```bash
# Edit tests/router/classification_examples.md — append a new ## Example N: block
# with input + expected output following the existing structure.

# Update the loader's expected count if the count assertion fails:
# tests/router/classification_examples_loader.py — search for the assert.

# Run eval to validate the new example
cd ~/dev/pretel-os && pytest -m eval -v --tb=short

# If thresholds still met, commit
```

### 7.4 Change the eval threshold

NOT casually. Threshold changes need:

1. A note in `specs/router/tasks.md` Phase F section explaining the data justifying the change
2. A new ADR if the change crosses a phase gate
3. A re-run that confirms the new threshold

Do not lower thresholds to make a failing test pass without changing model or prompt.

## 8. Failure modes and recovery

### 8.1 LiteLLM proxy down

**Symptom:** `pytest -m eval` skips with "LiteLLM proxy not on 127.0.0.1:4000".

**Diagnosis:**
```bash
systemctl --user status litellm --no-pager
journalctl --user -u litellm -n 50 --no-pager
ss -tlnp | grep 4000
```

**Recovery:**
```bash
systemctl --user restart litellm
sleep 3
curl -f http://127.0.0.1:4000/health
```

If still down, check `~/.env.litellm` for missing keys.

### 8.2 Anthropic API key invalid

**Symptom:** chat_json calls fail with auth errors. classifier.classify() raises `ClassifierTransportError`.

**Diagnosis:**
```bash
# Check the env file has the key
grep -c '^ANTHROPIC_API_KEY=' ~/.env.litellm  # should print 1

# Test the key directly
ANTHROPIC_API_KEY=$(grep '^ANTHROPIC_API_KEY=' ~/.env.litellm | cut -d= -f2-)
curl -sf https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-haiku-4-5-20251001","max_tokens":10,"messages":[{"role":"user","content":"ping"}]}'
unset ANTHROPIC_API_KEY
```

If the direct call fails, get a new key from https://console.anthropic.com/settings/keys.

**Recovery:** update `~/.env.litellm`, `chmod 600` it, restart litellm.

### 8.3 Cascade firing — primary model unavailable

**Symptom:** `telemetry.model` shows fallback model, latency higher than baseline, costs spike.

**Diagnosis:**
```bash
# Check Anthropic status page
# https://status.anthropic.com/

# Check the proxy logs for cascade events
journalctl --user -u litellm -n 200 --no-pager | grep -i fallback
```

**Recovery:** wait for primary to recover. The cascade is the recovery — it kept the system functional. After primary returns, no manual action needed.

### 8.4 Schema violations spiking

**Symptom:** `pytest -m eval` fails with `schema_violations > 0`.

**Diagnosis:** the classifier is returning JSON that violates the schema. Three possible causes in order of likelihood:
1. Prompt drift (someone edited classify.txt poorly)
2. Model behavior change (Anthropic updated Haiku 4.5)
3. LiteLLM proxy returning malformed responses

**Diagnosis steps:**
```bash
# Read the failed eval JSON's `results` array — find the row with `error.type == "ClassifierSchemaError"`
jq '.results[] | select(.error.type == "ClassifierSchemaError")' \
  tests/router/eval_results/eval_<latest>.json

# Look at the parsed_response in the error to see what the model emitted
```

**Recovery:**
- Cause 1: revert the prompt change, re-eval
- Cause 2: prompt-engineer or wait for Anthropic to stabilize
- Cause 3: restart litellm, retry

### 8.5 Markdown fences appearing in production

**Symptom:** `routing_logs` queries show `provider_metadata.choices[0].message.content` starts with ` ```json `.

**Action:** the stripper handles it; this is informational, not broken. Per CONSTITUTION-deferred Phase F task, if rate exceeds 20% per week, prompt-engineer.

## 9. Cost tracking

Per-call costs (Haiku 4.5, ~870 tokens prompt + ~30 tokens output):
- Input: $0.80 per million tokens → $0.000696 per call
- Output: $4.00 per million tokens → $0.000120 per call
- **Per call: ~$0.0008**

Eval suite (10 calls): ~$0.008 per run, plus some overhead. Last run logged $0.0108.

If `routing_logs` shows hundreds of classifications per day:
- 100 classifications/day = ~$0.08/day = ~$2.40/month
- 1000 classifications/day = ~$0.80/day = ~$24/month

Activate prompt caching when classify.txt grows past 1024 tokens (CONSTITUTION §5.1 deferred-todo) — drops input cost ~90% on cache hits.

## 10. Deferred technical debt for this component

Tracked in `lessons` with tag `deferred-todo`. After Module 0.X migration, these move to `tasks` table. Current deferred items affecting Phase A:

| ID | Trigger | Description |
|---|---|---|
| `d7f1e119` | Phase D | LiteLLM returns alias not concrete model — fix telemetry resolver |
| `89c11602` | Before Module 5 | pyproject.toml needed; conftest.py is current band-aid |
| `3d98464b` | When prompt > 1024 tokens | Activate Anthropic prompt caching |
| Phase F observational | Post-30-day | Markdown fence rate analysis (deferred A.4.4) |

Query for current state:
```python
search_lessons(query="deferred", tags=["deferred-todo"], limit=20)
```

## 11. Phase A exit gate verification

The following must all be true. If any fails, Phase A is not actually complete:

```bash
cd ~/dev/pretel-os

# Gate 1: 19 unit tests pass on default run
pytest tests/router/ -v --tb=short 2>&1 | tail -2
# Expected: "19 passed, 1 deselected"

# Gate 2: 1 eval test passes (live)
pytest -m eval -v --tb=short 2>&1 | tail -3
# Expected: "1 passed", thresholds met in JSON

# Gate 3: mypy --strict clean
mypy src/mcp_server/router/litellm_client.py --strict 2>&1
mypy src/mcp_server/router/classifier.py --strict 2>&1
# Expected: "Success: no issues found in 1 source file" (each)

# Gate 4: git state clean and pushed
git status
git log --oneline origin/main -3
# Expected: clean working tree, top commit is 28fec7b or descendant

# Gate 5: classification_examples.md has exactly 10 examples
grep -c "^## Example" tests/router/classification_examples.md
# Expected: 10

# Gate 6: eval result baseline preserved
ls tests/router/eval_results/eval_*.json | wc -l
# Expected: >= 2 (one failing, one passing per A.6.1 history)
```

## 12. Phase A → Phase B handoff

Phase B (Layer Loader) consumes the output of `classifier.classify()` and uses bucket/complexity/needs_lessons to load layers L0–L4. Phase B's spec MUST reference:

1. The exact return shape of `classify()` documented in `specs/router/spec.md §5.1`
2. The `ChatJsonTelemetry` dataclass fields it can read for cache_hit / cost / latency telemetry
3. The Module 0.X tables (when those exist) that feed each layer

Phase B is BLOCKED until Module 0.X migration lands. Reason: Phase B needs to know which tables to query for L1/L2 (`decisions`, `best_practices`, `operator_preferences`).

## 13. Related documents

- `specs/router/spec.md` — full specification (§4 public interface, §5 classification contract, §10 failure modes)
- `specs/router/plan.md` — phase plan A–F with done-when criteria
- `specs/router/tasks.md` — atomic task list, all Phase A tasks marked `[x]`
- `docs/DATA_MODEL.md` §4.1 `routing_logs`, §4.3 `llm_calls` — where Phase D writes telemetry
- `docs/INTEGRATIONS.md` §4.5 — LiteLLM proxy as gateway (ADR-020)
- `CONSTITUTION.md` §2.2 (Router as single gateway), §4 rule 8 (LiteLLM aliases), §5.1 (complexity drives RAG), §8.43 (degraded mode), §9 rule 7 (no silent fallbacks)
- Lessons in MCP: `aaf04a4b` (provider-agnostic aliases), `94236536` (markdown fences), `6e23e68f` (truncation detection), `4c56d585` (integration tests catch what mocks miss), `84cdc861` (conftest.py pattern), `f85a5241` (mypy strict dict[str, Any])

## 14. Quick reference card

```
Component:        Module 4 Phase A — Router Classifier
Public API:       classifier.classify(message, l0_content?, session_excerpt?, request_id?)
Returns:          tuple[dict, ChatJsonTelemetry]
Raises:           ClassifierError or any of 7 typed subclasses
LiteLLM alias:    classifier_default
Cascade:          Haiku 4.5 → Sonnet 4.6 → gpt-4o-mini
System prompt:    src/mcp_server/router/prompts/classify.txt (~870 tokens)
max_tokens:       800 (CLASSIFIER_MAX_TOKENS)
timeout:          5000ms (CLASSIFIER_TIMEOUT_MS)
Test count:       20 (11 chat_json + 8 classifier + 1 eval)
Cost per call:    ~$0.0008
Eval baseline:    bucket 1.0 / complexity 0.8 / schema_violations 0 (commit 28fec7b)
Type check:       mypy --strict clean
Last reviewed:    2026-04-28
```

## 15. Change log

| Date | Commit | Change |
|---|---|---|
| 2026-04-27 | 5a08c67 | A.1 Package skeleton + typed exceptions |
| 2026-04-27 | f3ce9b3 | A.2 + A.3.1 Classifier prompt + 10 examples |
| 2026-04-27 | 7eea3ab | A.4 LiteLLM client wrapper + retry policy |
| 2026-04-28 | a4f976b | A.4.3 Truncation detection + telemetry + provider-agnostic chat_json |
| 2026-04-28 | 4964a7d | A.4.4 deferred to Phase F |
| 2026-04-28 | 4a85fd9 | A.5.1 + A.5.2 classifier.py with strict schema validation |
| 2026-04-28 | 8b5bf71 | A.5.3 request_id parameter |
| 2026-04-28 | e466796 | Module 0.X spec draft |
| 2026-04-28 | e59b943 | A.6.1 Live classifier eval |
| 2026-04-28 | 28fec7b | Docs: close M4 Phase A + queue Module 0.X |

---

**End of runbook.** When Phase B ships, create `module_4_phase_b_layer_loader.md` and link from this document.
