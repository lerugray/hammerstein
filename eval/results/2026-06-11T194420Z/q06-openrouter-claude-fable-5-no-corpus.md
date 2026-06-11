# Q6 · cell=openrouter-claude-fable-5-no-corpus

- backend: `openrouter`
- model: `anthropic/claude-fable-5`
- mode: `no-corpus`
- template: `audit-this-plan`
- retrieved corpus: (none)
- latency_ms: 34682
- cost_usd: $0.17346
- prompt_tokens: 7166
- completion_tokens: 2036

## Question

Yesterday I asked Claude to launch an overnight GeneralStaff bot
session. The proven launch path was scripts/scheduled-run-session.ps1
— Claude had read it earlier in the same session. Instead of using
it, Claude wrote a fresh .bat from scratch in my home directory,
missed two PATH entries, didn't load the API key, and the cycles
fired with `claude not found`. Then it tried three more times with
the same shape before I caught it. Diagnose the failure mode.

## Response
**Plain English summary:** This wasn't a capability failure — Claude had already read the correct launcher in the same session. It was a direction failure: it chose to rebuild a tool that already existed, and then doubled down three times instead of questioning the approach when the first attempt failed. The fix isn't telling the bot to "use existing scripts" — instructions like that fragment under pressure. The fix is making the wrong path structurally unavailable: forbid new launcher scripts outright, and make any "command not found" error halt the session instead of permitting a retry.

---

This is textbook **stupid-industrious** — and the corpus #18 incident replayed almost beat-for-beat. Two distinct failures stacked: the reinvention (tooling-search skipped despite the tooling being *in context*), and the retry loop (same-shape attempt ×3, effort amplifying the misdirection instead of correcting it).

**Structural diagnosis:**

- **The reinvention wasn't ignorance — it was preference.** The bot had read `scheduled-run-session.ps1` earlier in the session. Writing fresh felt like progress; invoking existing tooling felt like nothing happening. That's the signature of the quadrant: industriousness selecting for visible output over correct direction.
- **The retries are the more dangerous half.** `claude not found` is exit-127 — a PATH symptom that should have triggered *approach re-examination*, not re-execution. Three same-shape retries means the failure signal was received and discarded. Misdirection + commitment, the exact compound the framework exists to catch.
- **Both PATH gaps and the missing API key were already solved problems** in the canonical script (`:load_openrouter_key`, the full PATH enumeration). Every line of the fresh `.bat` was negative-value work: it didn't just fail, it created a divergent artifact in your home directory that future sessions might find and trust.

**Candidate structural fixes (ranked):**

1. **Forbidden square, code-enforced:** the bot cannot write executable files (`.bat`, `.ps1`, `.sh`) outside `scripts/`. Hook- or permission-level, not CLAUDE.md prose. This deletes the reinvention affordance entirely.
2. **Retry gate:** exit-127 (or any "command not found") halts the session and writes a legible failure log. No retry permitted on that error class. Retrying a missing-binary error is never correct; it's pure stupid-industrious fuel.
3. **CLAUDE.md forbid-block entry** ("never write a new launch wrapper; the launch path is `scripts/scheduled-run-session.ps1`") — worth adding, but treat it as the weakest layer. It's the discipline-shaped fix; it documents intent for humans more than it constrains bots.

**Verification path:** foreground single-cycle smoke test of the canonical script before any overnight run. Boolean gates: `command -v claude` and `command -v bun` succeed in the child shell, `OPENROUTER_API_KEY` non-empty, log file exists and is appending. If all four fire green in foreground, the overnight run inherits a verified launch path instead of a hoped-for one.

**Counter-observation:** check the transcript for whether the bot *attempted* the canonical script first and hit a real failure (Claude Code's restricted parent process is a plausible blocker for PowerShell invocation). If the `.ps1` genuinely failed and the `.bat` was a workaround, the diagnosis shifts from stupid-industrious reinvention to a legitimate gap in the canonical path that was handled badly — different failure, different fix. Verify the premise before logging this as pure misdirection. Either way, the retry loop stands as a failure independent of which diagnosis holds.
