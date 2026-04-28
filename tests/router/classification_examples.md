# Router classification — worked examples

**Authority:** `specs/router/spec.md §5.1`, `src/mcp_server/router/prompts/classify.txt`.

Each example is a hand-labelled `(input, expected output)` pair used by `tests/router/test_classifier.py` (Phase A.6). The schema in every expected output conforms to `spec.md §5.1`.

Coverage: 3 buckets (`personal`, `business`, `scout`) × 3 complexity levels (`LOW`, `MEDIUM`, `HIGH`) + 1 ambiguous edge case = 10 examples.

In v1 `project` and `skill` are always `null` (no projects or skills registered yet — see prompt v1 TODO). `confidence` values are illustrative; tests should assert ranges, not exact floats.

> **Note on session context:** These examples assume the classifier receives only the input message + L0 identity, with no session ledger. In production the Router supplies the last 3 turns of session context per `spec.md §5.1`, which can disambiguate borderline cases (e.g., a follow-up message that reads as ambiguous standalone but is clearly business given the prior turn). Session-aware tests live in `test_classifier.py::test_with_session_context` (Phase A.6.1+).

---

### Example 1: personal — quick factual lookup

**Bucket coverage:** personal
**Complexity coverage:** LOW
**Language:** English

**Input:**

```
What's the street address of the Goose Creek rental?
```

**Expected output:**

```json
{"bucket": "personal", "project": null, "skill": null, "complexity": "LOW", "needs_lessons": false, "confidence": 0.9}
```

**Reasoning:** "Goose Creek rental" anchors personal bucket (rental properties); single-fact address lookup → LOW; needs_lessons false because LOW.

---

### Example 2: personal — structured calendar task

**Bucket coverage:** personal
**Complexity coverage:** MEDIUM
**Language:** English

**Input:**

```
Add an event to my calendar for my daughter's kindergarten open house next Tuesday at 6pm.
```

**Expected output:**

```json
{"bucket": "personal", "project": null, "skill": null, "complexity": "MEDIUM", "needs_lessons": false, "confidence": 0.9}
```

**Reasoning:** "daughter" + "kindergarten" anchors personal bucket; structured calendar action with explicit time and date → MEDIUM; needs_lessons false because the action is mechanical and prior lessons add no value.

---

### Example 3: personal — refinance decision

**Bucket coverage:** personal
**Complexity coverage:** HIGH
**Language:** English

**Input:**

```
Should I refinance the Charleston rental given current interest rates and the projected Q3 vacancy?
```

**Expected output:**

```json
{"bucket": "personal", "project": null, "skill": null, "complexity": "HIGH", "needs_lessons": true, "confidence": 0.9}
```

**Reasoning:** "Charleston rental" anchors personal bucket; multi-factor financial decision weighing rates against vacancy projection → HIGH; needs_lessons true because HIGH and prior refinance / property-decision lessons likely apply.

---

### Example 4: business — list unchecked tasks

**Bucket coverage:** business
**Complexity coverage:** LOW
**Language:** English + Spanish mixed

**Input:**

```
lista las tasks sin completar del Module 4
```

**Expected output:**

```json
{"bucket": "business", "project": null, "skill": null, "complexity": "LOW", "needs_lessons": false, "confidence": 0.9}
```

**Reasoning:** "tasks" + "Module 4" anchors business bucket (pretel-os roadmap lives in tasks.md); pure listing query → LOW; needs_lessons false because LOW.

---

### Example 5: business — structured task append

**Bucket coverage:** business
**Complexity coverage:** MEDIUM
**Language:** English + Spanish mixed

**Input:**

```
agrega una nueva task M5.T2.1 en tasks.md para el Telegram bot scaffold
```

**Expected output:**

```json
{"bucket": "business", "project": null, "skill": null, "complexity": "MEDIUM", "needs_lessons": false, "confidence": 0.9}
```

**Reasoning:** "tasks.md" + "Telegram bot scaffold" anchors business bucket (pretel-os Module 5); structured edit following the tasks.md format → MEDIUM; needs_lessons false because the action is a mechanical file edit.

---

### Example 6: business — Reflection worker design

**Bucket coverage:** business
**Complexity coverage:** HIGH
**Language:** English + Spanish mixed

**Input:**

```
help me design the Reflection worker para Module 6, qué patterns debería seguir?
```

**Expected output:**

```json
{"bucket": "business", "project": null, "skill": null, "complexity": "HIGH", "needs_lessons": true, "confidence": 0.95}
```

**Reasoning:** "Reflection worker" + "Module 6" anchors business bucket (pretel-os roadmap); design-pattern recommendation question → HIGH; needs_lessons true because HIGH and prior architecture/skill-design lessons should inform the answer.

---

### Example 7: scout — abstract pattern name lookup

**Bucket coverage:** scout
**Complexity coverage:** LOW
**Language:** English

**Input:**

```
what's the abstract name we used for the operator-context-capture pattern?
```

**Expected output:**

```json
{"bucket": "scout", "project": null, "skill": null, "complexity": "LOW", "needs_lessons": false, "confidence": 0.85}
```

**Reasoning:** Factual lookup of a previously-named abstract pattern. Clearly scout bucket — operator-context-capture pattern originated in scout work (manufacturing operator coaching). LOW because answerable from L0+L1 directly; no debugging, design, or recommendation required.

---

### Example 8: scout — abstract pattern documentation

**Bucket coverage:** scout
**Complexity coverage:** MEDIUM
**Language:** English

**Input:**

```
Document the cycle-time pattern I observed at the station this morning, abstracted from any specific product line.
```

**Expected output:**

```json
{"bucket": "scout", "project": null, "skill": null, "complexity": "MEDIUM", "needs_lessons": true, "confidence": 0.85}
```

**Reasoning:** "cycle-time pattern" + "station" anchors scout bucket; structured documentation task with explicit abstraction discipline → MEDIUM; needs_lessons true because prior pattern-naming and abstraction lessons help keep the write-up Scout-safe.

---

### Example 9: scout — vendor pushback decision

**Bucket coverage:** scout
**Complexity coverage:** HIGH
**Language:** English

**Input:**

```
Help me think through whether to push back on a new MTM standard a vendor is proposing — what factors should drive the decision?
```

**Expected output:**

```json
{"bucket": "scout", "project": null, "skill": null, "complexity": "HIGH", "needs_lessons": true, "confidence": 0.9}
```

**Reasoning:** "MTM standard" + "vendor" anchors scout bucket (manufacturing process governance); multi-factor pushback decision asking for an evaluation framework → HIGH; needs_lessons true because HIGH and prior MTM / vendor-negotiation lessons likely apply.

---

### Example 10: ambiguous — bare opinion request

**Bucket coverage:** ambiguous
**Complexity coverage:** MEDIUM
**Language:** Spanish

**Input:**

```
qué piensas de esto?
```

**Expected output:**

```json
{"bucket": null, "project": null, "skill": null, "complexity": "MEDIUM", "needs_lessons": false, "confidence": 0.3}
```

**Reasoning:** sin contexto previo el message no aporta signal de bucket; complexity es MEDIUM por defecto (request de opinión sobre algo no especificado); needs_lessons false porque bucket=null.
