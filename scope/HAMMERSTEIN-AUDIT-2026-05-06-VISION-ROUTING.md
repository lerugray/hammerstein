# Hammerstein audit — vision-support default-backend routing

**Date:** 2026-05-06 evening (second audit on the vision-support
scope, focused on the routing decision)
**Backend:** openrouter qwen/qwen3.6-plus, $0.01135, 85.2s
**Audited plan:** Revised default-routing argument (paid-Qwen
default + GPT-4o failover, post-v0 bake-off, conditional DeepSeek).
**Verdict:** Ship with modifications. 4 catches + 1 sharp
counter-observation.

---

## Plain English summary (verbatim)

Don't use the free model as your default for high-value visual
audits. At 5-20 calls a week, paying a few cents per call is
trivial compared to the hours you'll waste fixing a missed detail.
Route everything to Qwen3-VL-Plus by default, fall back to GPT-4o
only if the first pass fails a strict format check, and run your
three benchmark tests *before* shipping v0, not after. This locks
in quality from day one and avoids retrofitting routing logic later.

---

## Failure modes (verbatim)

- **Post-v0 bake-off timing (stupid-industrious drift).** Shipping
  v0 with an untested default means the first real-world audit
  could hit a quality cliff, forcing a hotfix to routing logic
  while you're mid-audit. You'll end up patching live failures
  instead of validating upstream.
- **Failover loop / cost spike.** If the shape-gate is too strict
  or Qwen consistently misses a specific visual pattern (e.g.,
  hex-grid topology), automatic failover to GPT-4o could trigger
  repeatedly, multiplying cost and latency without solving the
  root mismatch.
- **DeepSeek v4 phantom capability.** Baking DeepSeek into routing
  candidates before verifying its vision API endpoint exists
  creates dead code and potential runtime 404s. Unverified
  dependencies become silent failure points.
- **Hard Rule friction.** The "Claude NEVER default" rule is
  sound, but if Qwen/GPT-4o both fail on a niche visual register,
  you need a clean, explicit override path that doesn't require
  editing config files mid-session.

## Verification gates (verbatim)

- **Pre-v0 bake-off Boolean:** Run the 3 benchmark cases through
  Qwen3-VL-Plus and GPT-4o *before* merging v0. Require ≥2/3
  correct semantic verdicts + 100% shape-gate pass for Qwen to
  earn default status.
- **Failover cap:** Hard limit of 1 automatic failover per audit.
  If GPT-4o also fails shape-gate, return structured error to
  operator instead of chaining to another model.
- **API capability probe:** At startup, ping DeepSeek vision
  endpoint (if configured). If 404/unsupported, silently exclude
  it from routing table. No dead paths.

## Structural-fix candidates (verbatim)

- Move bake-off from post-v0 to pre-v0. The routing table is a
  single config file; swapping the default after a test run is
  cheaper than patching live audit failures.
- Encode the failover logic as a state machine (Qwen → shape-gate
  → GPT-4o → operator) rather than a retry loop. This prevents
  compounding latency/cost.
- Keep the `--backend-tier free` flag, but route it through a
  separate, non-default config profile to avoid accidental
  production use.

## Counter-observation (verbatim, **load-bearing**)

Qwen3-VL-Plus may genuinely underperform on highly stylized or
low-contrast visual registers (e.g., retro sprite scoring) where
GPT-4o's training data has an edge. If the pre-v0 bake-off shows
Qwen failing 1/3 cases, the right move isn't to force it as
default — it's to route by *content type* or accept GPT-4o as
the flat default. The framework's bias toward clever-lazy means
paying the higher baseline cost ($0.05/audit) is still correct
if it eliminates the failover complexity entirely.

---

## How the revision applies these (post-audit edits)

- **Bake-off moved pre-v0 merge.** The 3 benchmark cases run as
  part of the implementation arc, not as a post-ship validation.
  v0 merge gated on bake-off results.
- **Default-lock decision tree** based on bake-off:
  - If Qwen passes 3/3 shape-gate AND ≥2/3 semantic: lock
    Qwen3-VL-Plus default + GPT-4o failover.
  - If Qwen fails any shape-gate OR <2/3 semantic: lock GPT-4o
    as flat default, no failover. Per audit's counter-observation:
    eliminating routing complexity is worth the +$0.04/call when
    weekly call volume is 5-20.
- **Failover cap = 1** added to the failover state machine. If
  GPT-4o also fails shape-gate, return structured error to
  operator. No retry chains.
- **DeepSeek API capability probe at startup.** Silent exclusion
  from routing table if endpoint returns 404/unsupported. Probes
  cached per-session. DeepSeek excluded from v0 unless probe
  succeeds AND it's added to the bake-off.
- **`--backend-tier free` non-default profile** acknowledged.
  Implementation: flag is exposed, but never the resolved
  default; never auto-selected.

Audit applied; ready to lock the v0 default-routing scope and queue
implementation with bake-off as gate.
