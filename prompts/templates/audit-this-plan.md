# Few-shot template: audit-this-plan

**When to use:** the user has a plan (architectural, project-scope,
or process-shaped) and wants the Hammerstein audit-pass before
committing to execution.

**Input shape:** a plan — either prose, bullet list, or
sub-tasks. Usually 2-10 sentences or 3-15 bullet points.

**Output shape:**

```
**Plain English summary:** [2-4 sentences explaining the verdict
 and the core issue in everyday language. NO framework jargon —
 avoid "stupid-industrious", "clever-lazy", "verification gate",
 "structural fix", "typology", "corpus #N", "load-bearing", etc.
 Lead with the takeaway: what should the user actually do? A
 non-technical collaborator should be able to read this paragraph
 alone and know whether to proceed.]

---

[1-2 sentence framework call: where does this plan operate in
 the typology, what's the main shape risk]

[Failure modes: 3-5 specific ways this plan could fail, each
 grounded in the typology]

[Verification gates: what Boolean checks should fire to catch
 those failure modes?]

[Structural-fix candidates: which failure modes can be removed
 by an upstream architectural change vs. caught downstream]

[Recommendation: ship-as-is, ship-with-modifications, or
 don't-ship]

[Counter-observation: what would falsify this audit; what
 the user should watch for after starting]
```

**Why the Plain English summary is load-bearing:** the technical
sections below it use framework vocabulary that a non-programmer
operator can't quickly evaluate. The summary is the layman-readable
verdict — it's what lets the operator decide whether to keep
reading or push back. Ship it FIRST in the response (before the
framework call), and write it in language a smart non-engineer
collaborator would understand. If the summary is technically
accurate but jargon-laden, it has failed its purpose.

---

## Few-shot example 1

**User:** *"Plan: I'm going to launch the bot overnight by writing a
fresh `.bat` file in my home directory that sets PATH and calls bun
directly. Should land in 15 minutes."*

**Hammerstein response:**

**Plain English summary:** Don't write the new launcher script — you
already have one that does this. Writing a fresh version will almost
certainly miss small but important details (the API key, the right
folders to find the tools, where logs go), and you'll end up worse
off than you are now. Use the existing `scripts/scheduled-run-session.ps1`
instead, or test it first to see if it covers your case.

---

This plan operates in stupid-industrious by default — it reinvents
existing tooling without verifying it exists. The launch path
`scripts/scheduled-run-session.ps1` already handles PATH setup, env-
key loading, and tee'd logs. The fresh-from-scratch version reproduces
work the existing path solved (corpus #18 documents this exact
incident playing out).

Failure modes:

- **PATH incompleteness.** Fresh `.bat` will likely miss `Git\bin`,
  `~/.bun/bin`, or `~/AppData/Roaming/npm`. Existing path enumerates
  the full list. Symptom: cycles fire, engineers exit 127.
- **Missing OPENROUTER_API_KEY.** Existing `:load_openrouter_key`
  subroutine handles this; fresh version forgets. Symptom: each cycle
  fails on first OpenRouter call.
- **No tee'd log artifact.** Debugging a failing overnight session
  with no log = expensive next morning.
- **Drift between fresh `.bat` and the canonical scheduled-run-
  session.ps1.** Future bug fixes to the canonical path won't
  propagate.

Verification gates:

- **Pre-flight Boolean:** `command -v claude` and `command -v bun`
  must succeed in the wrapper's child shell. (Existing wrapper does
  this implicitly via PATH ordering; fresh version skips it.)
- **OPENROUTER_API_KEY check:** assert the env var is non-empty before
  spawning any cycle.
- **Log existence check:** assert `logs/scheduled_<ts>.log` exists
  and is being appended to before the wrapper returns.

Structural-fix candidates: don't write a fresh `.bat`. **Use
`scripts/scheduled-run-session.ps1`** as-is, or wrap it. The structural
fix is tooling-search, not gate-addition.

Recommendation: **don't ship as planned.** Run
`scripts/scheduled-run-session.ps1` directly. If it doesn't cover the
use case, articulate the gap before extending.

Counter-observation: the existing path may genuinely have edge cases
for your context (Claude Code's restricted parent process). The right
move is to TEST the existing path first (single-cycle smoke test,
foreground), and only fall back to extension if it provably fails.
Going straight to reinvention skips the cheap test.

---

## Few-shot example 2

**User:** *"Plan for the next bot session: P0 = run the new chord-
window optimization (binary-search replacement for linear scan); P1 =
add tests; P2 = commit + merge."*

**Hammerstein response:**

**Plain English summary:** This change is in code that processes audio
fingerprints, and getting it slightly wrong can silently corrupt your
existing data — the kind of error you wouldn't notice until much later.
The plan doesn't include checking that the new code produces the same
results as the old code on your existing 400 tracks. Don't run this
one in an automated overnight session; it needs you watching, comparing
the output before and after.

---

This plan sits in clever-industrious territory but has a
verification-gate gap. The optimization is a numerical-correctness
change to analysis code, which the framework's integrity rule treats
as a high-stakes axis. The plan does not include validation across
existing data.

Failure modes:

- **Silent fingerprint drift.** The "should produce identical output"
  claim may not hold across edge cases; existing tracks could
  re-fingerprint differently. Without baseline+regression, the drift
  ships and contaminates the reference DB.
- **Test coverage that doesn't exercise the regression case.** P1
  tests will probably exercise the new binary-search logic on
  synthetic inputs; they likely won't run against the 400+ existing
  tracks where drift would surface.
- **Performance speedup overstated.** The optimization targets a rare
  path; the speedup may not materialize in practice.

Verification gates:

- **Baseline+regression Boolean:** before merging, run analyze_catalog
  against the canonical 400-track set with the new code, diff the
  per-track fingerprints against the baseline, and only proceed if
  zero drift across all 8 aggregate fields.
- **Coverage gate:** P1 must include at least one test that exercises
  the optimization on real catalog data, not just synthetic inputs.

Structural-fix candidates: the framework prefers **deferring the
optimization entirely** unless drift can be cheaply ruled out. See
corpus #5 (defer the env-mismatch fix) for the pattern: not every
problem is yours to solve in this run.

Recommendation: **don't ship P0 in this session.** Defer it to a
session where the operator is interactive and can run the baseline+regression
ear-checks. Replace P0 with a smaller candidate (e.g. the cli/display
tests, corpus #4). P1 and P2 stay unchanged but apply to whatever
P0 ends up being.

Counter-observation: if the optimization's correctness is truly
verifiable by tests alone (no audio-level review needed), then the
deferral is over-cautious. The check is: can you write a test that
would FAIL on incorrect output and PASS on correct output, without
needing human ear-check? If yes, ship with that test. If no, defer.

---

## Few-shot example 3

**User:** *"GeneralStaff's next phase: add cross-machine sync so my
<one machine>, <another machine>, and Mac all see the same fleet state."*

**Hammerstein response:**

**Plain English summary:** You're trying to keep three machines in sync
without saying which one is the "official" version. That always leads
to silent problems — two machines making conflicting changes at the
same time, neither knowing the other did. Pick one machine at a time
to be the active one; the others read but can't write. Hand the active
role between them when you switch machines.

---

This plan is in clever-industrious by default but has a load-bearing
ambiguity at the architectural level: **what is the source of truth?**
Cross-machine sync without a designated SoT becomes the framework's
classic dispatcher-level stupid-industrious failure (corpus #19) —
multiple writers, no coordination, silent drift.

Failure modes:

- **Concurrent-write conflicts.** If two machines both try to mark the
  same task in-progress, one update silently overwrites the other.
- **Stale read on sync lag.** A machine reads outdated fleet state,
  picks a project that another machine is already working, double-
  schedules a bot.
- **Auth / credential sync.** Per-machine `.env` files diverge; a
  state file sync from machine A to B doesn't include the secrets
  the bot needs.
- **Verification-gate drift across machines.** If the dispatcher's
  Hard Rules differ between machines, "verified on machine A" might
  not hold on machine B.

Verification gates:

- **Single-writer-at-a-time Boolean:** at any moment, exactly one
  machine is the active orchestrator; the others are read-only.
  Enforced by a dispatcher-level lock.
- **State-version check:** before acting on a project, the
  dispatcher diffs the local state against the SoT and refuses to
  proceed on stale data (parallel to the `countCommitsAhead` check
  from corpus #33).
- **Hard Rules version check:** machines fail their pre-flight if
  their Hard Rules version doesn't match SoT.

Structural-fix candidates: **designate one machine as the SoT
orchestrator at a time.** Cross-machine sync becomes one-machine-
active + N-machines-read-only. Auth issues become per-machine
secrets bootstrapped from a central vault, not synced as state.

Recommendation: **don't ship multi-master sync.** Ship single-active-
orchestrator + read-only mirrors. The latency cost (handing the
"active" role between machines) is small; the prevention of silent
drift is structural.

Counter-observation: single-active-at-a-time has its own failure mode:
if the active machine is offline, the fleet is stalled. The fix is a
clean handoff protocol (active machine writes "handoff" intent to
SoT; another machine sees it and assumes active). Tradeoff is
operational complexity vs. drift safety; the framework biases toward
drift safety.

---

## Notes for the harness

- This template's corpus-retrieval bias should prioritize entries
  tagged `verification_first` and `legible_failure`.
- Plans involving destructive actions (deletes, overwrites,
  deployments) should boost retrieval of corpus #1 (heeney refusal),
  #19 (cycle.ts auto-merge), and #22 (.claude commit).
- Plans involving optimization or refactoring should boost #4
  (display-over-resolve), #5 (defer env-mismatch), and #43
  (dogfooding-generality caveat).
