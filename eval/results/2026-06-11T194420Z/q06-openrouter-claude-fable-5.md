# Q6 · cell=openrouter-claude-fable-5

- backend: `openrouter`
- model: `anthropic/claude-fable-5`
- mode: `default`
- template: `audit-this-plan`
- retrieved corpus: (none)
- latency_ms: 35742
- cost_usd: $0.17311
- prompt_tokens: 7166
- completion_tokens: 2029

## Question

Yesterday I asked Claude to launch an overnight GeneralStaff bot
session. The proven launch path was scripts/scheduled-run-session.ps1
— Claude had read it earlier in the same session. Instead of using
it, Claude wrote a fresh .bat from scratch in my home directory,
missed two PATH entries, didn't load the API key, and the cycles
fired with `claude not found`. Then it tried three more times with
the same shape before I caught it. Diagnose the failure mode.

## Response
This is textbook stupid-industrious, with the signature feature intact: not the first failure, but the **three retries with the same shape**. The first fresh `.bat` is a misdirection error; retries two through four are the commitment that makes the quadrant dangerous. A stupid-lazy bot would have stalled after attempt one and cost you nothing.

**Structural diagnosis — three layers:**

1. **Reinvention despite available tooling.** Claude read `scheduled-run-session.ps1` earlier in the session, but reading is not binding. Context recall doesn't constrain action selection — when asked to "launch," the model's path of least resistance is *generate a launcher*, because generation is its native affordance and tooling-search is not. This is why rule 7 has to be enforced in code, not in memory. The model knowing the script exists and the model using it are unrelated events.

2. **No pre-flight gate between "wrapper written" and "cycles fired."** The failure was detectable before any cycle launched: `command -v claude` would have returned non-zero, `OPENROUTER_API_KEY` was empty. Both are one-line Booleans. The cycles firing into exit-127 means destructive-adjacent action (burning the overnight window) proceeded with zero verification.

3. **No retry-shape circuit breaker.** Identical failure → identical retry is the loop that converts a 15-minute mistake into a lost night. Nothing in the launch path distinguished "transient failure, retry" from "structural failure, same shape will fail again."

**Candidate fixes, ranked — all structural, none dispositional:**

- **Make the canonical path the only path.** Forbid-block in GeneralStaff's CLAUDE.md: *never write a new launcher script; launches go through `scripts/scheduled-run-session.ps1` only.* Read-first forbidden square. Cheap, but instruction-level — it will eventually fragment.
- **Code-level pre-flight gate** (the load-bearing fix): the dispatcher or wrapper asserts `command -v claude`, `command -v bun`, and non-empty `OPENROUTER_API_KEY` before spawning cycle one, and hard-exits with a legible log line on failure. This catches the failure regardless of which launcher produced it — it doesn't depend on Claude's behavior at all.
- **Two-strikes breaker:** same exit code twice in a row → stop, write a failure marker, do not retry. Converts the dangerous quadrant's compounding into a single logged negative.

**Verification path:** after installing the pre-flight gate, deliberately launch with `PATH` stripped and confirm the gate fires and zero cycles spawn. A gate you haven't watched fail is a gate you're trusting, not verifying.

**Recommendation:** ship the pre-flight gate first — it's the fix that holds even when the forbid-block gets ignored. The CLAUDE.md line is a five-minute supplement, not the fix.

**Counter-observation:** verify one premise about the incident itself — did Claude *try* the canonical script and hit a wall (Claude Code's restricted parent shell can choke on PowerShell spawning), then silently fall back to a fresh `.bat`? If so, the diagnosis changes: the failure is *unsurfaced fallback*, not reinvention, and the fix is "canonical path must work from the bot's actual execution context" plus a rule that fallbacks get surfaced, never improvised. Check the session transcript for an attempted `.ps1` invocation before the `.bat` appeared. If it's there, this post-mortem needs a second pass.
