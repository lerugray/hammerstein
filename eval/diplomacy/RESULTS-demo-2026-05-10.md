# Hammerstein-Diplomacy demo — 2026-05-10

**TL;DR:** Matched-pair test. The Hammerstein wrapper applied to a Sonnet
4.6 Austria-player in full-press Diplomacy produced visibly different
*reasoning style* (more structural / verification-framed missives) but
**no measurable difference in game outcome.** Both wrapped Austria and
control (raw Sonnet 4.6) Austria ended the 3-game-year demo at the same
**2 supply centers**, both stabbed by Italy in year 3, with the rest of
the board ending in similar (different but comparable) configurations.

This is one matched pair, not statistical evidence. Sam Paech's own
diplobench README notes single-game results are *"roughly indicative"*
with large variance between runs.

| Power | Wrapped game (AUT = Hammerstein) | Control game (AUT = raw Sonnet) |
|---|---|---|
| AUT | **2** (-1) | **2** (-1) |
| ENG | 5 (+2) | 5 (+2) |
| FRA | 6 (+3) | 6 (+3) |
| GER | 5 (+2) | 3 (0) |
| ITA | 6 (+3) | 6 (+3) |
| RUS | 3 (0) | 6 (+3) |
| TUR | 6 (+3) | 5 (+2) |

The Hammerstein audit (2026-05-10) had flagged a falsification risk:
*"Hammerstein generalizes to abstract strategic reasoning but degrades
when applied to dialogue-heavy multi-agent games."* **This demo does
NOT support that claim** — the wrap was neither helpful nor harmful to
final game outcome.

## What the wrap visibly changed: reasoning style

The wrap *did* change AUT's negotiation style in observable ways.
Side-by-side example at the decisive S1903M turn (just before Italy's
stab attempt):

**Wrapped AUT (Hammerstein), S1903M to Italy:**
> *"Your F ION is still adjacent to GRE and A BOH is still adjacent to
> my home centers — **words are cheap**. Here is what changes my
> calculus: move A BOH to MUN or TYR away from my territory, and move
> F ION to AEG or TYR SEA away from GRE. If you do both, I will not
> support Russia into BOH and I will coordinate F GRE into AEG alongside
> your fleet against Turkey."*

**Control AUT (raw Sonnet), S1903M to Italy:**
> *"I cannot let you take GRE - that is my target this turn. F ALB moves
> to GRE, supported by A SER. Your F AEG should move to CON or SMY to
> threaten Turkey's heartland instead - that is far more valuable than
> GRE and opens Turkey's home centers to you. If you move F AEG to GRE
> we will bounce each other and Turkey survives unscathed."*

Both are sophisticated. The wrapped version applies framework
structural framing ("words are cheap," conditional commitments based on
observable unit movements). The raw version operates directly on
tactical alternatives ("move F AEG to CON instead, here's the better
target"). Different rhetorical strategies; comparable strategic depth.

**Neither prevented the stab.** Italy moved A BOH→VIE and A VEN→TRI
in the wrapped game, and A APU→VEN / A TRI→BUD / A BUD→VIE chain in
the control game. In both cases, Austria's negotiation-side reasoning
failed to prevent unit-position-based aggression.

## What the wrap did NOT change

- **Framework jargon in outputs**: Neither private journals nor
  in-game missives contained "clever-lazy," "stupid-industrious," or
  similar Hammerstein vocabulary in either game. The wrap shaped
  reasoning structure without leaking framework jargon into Diplomacy
  diction. (Ideal generalization shape, though it means the
  *legibility* of the wrap's effect is reduced.)
- **Final supply-center count**: Identical at 2 for both Austrias.
- **Game-year 3 stab vulnerability**: Both Austrias got stabbed by
  Italy in year 3. Italy's stab is apparently a structural feature
  of Sonnet 4.6 playing the 7-power game from Austria's geographic
  position, not a wrap-specific failure.

## Counter-finding: raw AUT actually caught a threat wrapped AUT missed

In S1901M, control (raw) AUT's journal explicitly flagged Italy's
TYR threat as concerning at the very first turn:

> *"ITA proposed non-aggression but revealed A VEN moves to TYR - this
> is concerning as TYR threatens both VIE and MUN, giving ITA leverage.
> I warned ITA that TYR..."*

Wrapped AUT's journals from the same turn (S1901M) named only A BOH
and F ION as the threat pair — A VEN's positioning was not flagged.
This is a small data point but suggests the wrap may *narrow*
reasoning focus toward framework moves (verification questions,
"words are cheap" rhetoric, conditional commitments) at the cost of
exhaustive baseline threat enumeration that raw Sonnet does
naturally.

This is consistent with the framework's reasoning style: emphasizing
structure-over-discipline and verification questions, but not
prescribing "always enumerate every adjacent threat" as a
domain-specific discipline.

## What this means for the wedge claim

The v0/v0.1 benchmark's measured claim is **"Hammerstein wrapper
makes any frontier model preferred by blind LLM judges on strategic-
reasoning Q&A"** — 98.1% to 100% blind-judge preference across
Opus / Sonnet / GPT-5, on 12 strategic-reasoning questions
(6 in-domain, 4 generic out-of-domain, 2 ablation conditions),
4 independent LLM judges (Opus, Sonnet, GPT-5, DeepSeek). That
claim is about *response quality as judged by LLMs on Q&A*, not
about downstream task performance in adversarial multi-agent games.

This demo (n=1 matched pair) is consistent with the v0/v0.1 claim
holding without extending to game-outcome metrics in adversarial
settings:

- The wrap measurably improves response quality in collaborative
  strategic-reasoning Q&A (the v0/v0.1 measurement).
- The wrap does not measurably improve game-outcome metrics in a
  3-game-year Diplomacy matched pair.
- This is internally consistent: game outcome in Diplomacy depends
  on geography + RNG of move resolution + opponents' play, not just
  the test agent's reasoning quality.

**Refined honest framing for skeptics:**
*"Hammerstein on Sonnet 4.6 = 100% LLM-judge preference vs raw
Sonnet on strategic-reasoning Q&A (replicable; full data public).
In a Diplomacy matched-pair demo (n=1), the wrap shaped reasoning
style observably but did not change game-outcome. Sonnet 4.6 is a
strong strategic reasoner; the wrap's incremental delta on
game-outcome metrics may be small or task-dependent."*

This is a stronger product story than "wins everywhere" because it
honestly bounds the claim. It also opens an interesting v0.3-onward
research direction: **separate measurement of (a) reasoning-quality
delta vs (b) downstream task-outcome delta** across multiple task
types.

## What we learned from running this

1. The wrap mechanism works mechanically. The injection layer
   transparently prepends the Hammerstein system prompt onto every
   wrapped agent's per-call system_text. Other agents stay raw.
   Verified across the smoke test, wrapped game, and control game.
2. Sonnet 4.6 is a stronger Diplomacy baseline than expected.
   Diplobench's prior tests (claude-3.7-sonnet score 1.54, gpt-4o-mini
   1.43, o1 1.31) used inferior models; Sonnet 4.6 is comparable to
   the strongest test models. Both Sonnet 4.6 Austrias did
   sophisticated negotiation regardless of wrap status.
3. Italy's stab pattern is robust to the wrap. Sonnet 4.6 playing
   Italy from a starting position adjacent to Austria's home
   centers will exploit that adjacency given any opportunity. This
   is geographic/structural, not a wrap-specific dynamic.
4. The audit's predicted "wrap degrades on adversarial games"
   failure mode did NOT materialize. The wrap was neutral, not
   negative. The audit was right to flag the risk; the empirical
   answer is "no effect," not "negative effect."

## Cost

- **Wrapped game**: 30 min wall clock, ~$8 OpenRouter (Sonnet 4.6 ×
  ~150 calls), $0.46 pod time
- **Control game**: 30 min wall clock, ~$8 OpenRouter, $0.46 pod time
- **Pod setup + smoke test**: ~$0.50
- **Total demo spend**: ~$17 OpenRouter, ~$1.40 pod, ~75 min wall clock

## Next steps (for future sessions)

1. **Scale up the matched-pair test**: 3-5 wrapped vs 3-5 control
   games, statistical comparison. Per Sam Paech's variance warning,
   this is the right rigor bar for any claim either direction.
   Cost estimate: ~$60-100 OpenRouter for the full set.
2. **Try a longer game**: 5-7 game-years. The wrap's effect (if any)
   may emerge in late-game dynamics that 3 years don't reach.
3. **Try multiple Austria seats**: rotate the wrap onto different
   powers (RUS, TUR, etc.). Geographic role matters for outcome;
   testing only Austria may obscure a real wrap effect.
4. **Add reasoning-quality scoring (LLM judge)**: instrument the
   game with a blind judge scoring per-turn negotiation quality.
   This would separate "did the wrap change reasoning?" from "did
   the wrap change game outcome?" — the latter has many confounds;
   the former is more directly testable.
5. **Try the wrap on weaker base models**: Sonnet 4.6 already plays
   competently. The wrap's value may be larger on smaller models
   (Qwen 7B / GPT-4o-mini etc.) where the framework adds the
   structural reasoning the base model lacks. Cost-effective test.

## Files in this directory

- `README.md` — experiment design
- `hammerstein_wrap.py` — wrap-injection layer
- `run_smoke_test.py` — zero-cost integration check
- `run_demo_game.py` — pod-runnable game runner (monkeypatches diplobench's LLMAgent)
- `RESULTS-demo-2026-05-10.md` — this writeup
- `demo-game-state-2026-05-10.json` — full wrapped game state (~660 KB)
- `demo-game-stdout-2026-05-10.log` — full wrapped game stdout (~200 KB)
- `control-game-state-2026-05-10.json` — full control game state (~680 KB)
- `control-game-stdout-2026-05-10.log` — full control game stdout (~210 KB)

## Reproduction

```bash
git clone https://github.com/sam-paech/diplobench.git
git clone https://github.com/lerugray/hammerstein.git
cd diplobench
pip install -r requirements.txt matplotlib
export OPENAI_API_KEY=<your-openrouter-key>
export OPENAI_BASE_URL=https://openrouter.ai/api/v1
export TEST_AGENT_MODEL=anthropic/claude-sonnet-4.6
export DEFAULT_AGENT_MODEL=anthropic/claude-sonnet-4.6
export PYTHONPATH=$PWD

# Wrapped (Hammerstein on AUT):
HAMMERSTEIN_WRAP=true python ../hammerstein/eval/diplomacy/run_demo_game.py \
    --turns 3 --negotiate --negotiation-subrounds 2 \
    --game-id wrapped-demo

# Control (raw AUT):
HAMMERSTEIN_WRAP=false python ../hammerstein/eval/diplomacy/run_demo_game.py \
    --turns 3 --negotiate --negotiation-subrounds 2 \
    --game-id raw-control
```
