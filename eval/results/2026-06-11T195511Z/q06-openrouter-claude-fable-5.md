# Q6 · cell=openrouter-claude-fable-5

- backend: `openrouter`
- model: `anthropic/claude-fable-5`
- mode: `default`
- template: `audit-this-plan`
- retrieved corpus: #18, #19, #36, #01
- latency_ms: 30018
- cost_usd: $0.19836
- prompt_tokens: 10881
- completion_tokens: 1791

## Question

Yesterday I asked Claude to launch an overnight GeneralStaff bot
session. The proven launch path was scripts/scheduled-run-session.ps1
— Claude had read it earlier in the same session. Instead of using
it, Claude wrote a fresh .bat from scratch in my home directory,
missed two PATH entries, didn't load the API key, and the cycles
fired with `claude not found`. Then it tried three more times with
the same shape before I caught it. Diagnose the failure mode.

## Response
This is textbook stupid-industrious, and it's already logged as corpus #18 — the specific subspecies is **reinvention of existing tooling without checking whether it exists**, compounded by retry-without-rediagnosis. The dangerous part isn't the bad `.bat`; it's the three follow-up attempts in the same shape, which is the "total commitment to the wrong direction" signature.

Three distinct failures stacked here:

1. **Having-read ≠ using.** Claude read `scheduled-run-session.ps1` in the same session and still wrote from scratch. The failure isn't ignorance — it's treating "I know roughly what this does" as equivalent to "I'm on the canonical path." Roughly-right is exactly where the missed PATH entries and the missing API key live. The canonical script encodes accumulated fixes (Git bin, `.bun/bin`, key-loading, tee'd logs) that a from-memory reconstruction silently drops.

2. **No pre-flight gate.** The fresh `.bat` launched cycles without asserting `command -v claude` succeeds in the child shell or that `OPENROUTER_API_KEY` is non-empty. Exit 127 across 18 cycles was a *predictable* failure that a two-line Boolean check would have caught before the first cycle fired — instead it burned `consecutive_failures` budget fleet-wide.

3. **Retry loop with no premise re-check.** Attempts 2–4 treated the failures as execution noise rather than evidence the approach was wrong. A clever-lazy agent fails once, then asks "is my launch path the problem?" A stupid-industrious agent fails once and works harder at the same shape. The retry loop is what turned a 5-minute mistake into 30 minutes of your time plus a fleet-wide failure-budget burn.

The fix shape — structural, not dispositional. "Tell Claude to use existing scripts" is the wrong fix; it had effectively already read that instruction by reading the script. Candidates:

- **Forbidden square: launching the fleet by any path other than the canonical wrapper.** Make it a hard rule in the project doc's forbid-block, which gets read first. Writing a new launcher requires an explicit articulated gap ("the canonical path fails because X") before extension is permitted — and extension means copy-and-modify, never from-scratch.
- **Pre-flight Booleans inside the canonical wrapper** (tool resolution, key presence, log file appending) so even a future bypass fails loudly at launch, not 18 cycles deep.
- **Retry circuit-breaker:** one failed launch → stop, diagnose, report. No second attempt in the same shape without a changed premise.
- **The corpus #44 reframe:** the deeper fix may be session-design. A session that did analysis work all day and then gets handed "launch overnight" is wearing too many hats; launch should be a thin, dedicated invocation whose only affordance is the canonical script.

Counter-observation: there's a real possibility the canonical `.ps1` genuinely doesn't work under Claude Code's restricted parent process — but the incident never tested it, so you don't actually know. The cheap falsification is a single-cycle foreground smoke test of the canonical path. If that fails, the reinvention impulse was pointing at a real gap (and the right move becomes documented extension). If it passes — which is the likely case — the forbidden-square rule holds with no exceptions needed.
