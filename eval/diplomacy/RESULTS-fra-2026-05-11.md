# Hammerstein-Diplomacy France matched-pair — 2026-05-11

**TL;DR:** Second matched-pair test, this time with the Hammerstein
wrap on **France** instead of Austria. Same harness, same model
(Sonnet 4.6 for all 7 powers), same 3-game-year cap, same starting
state. **Both wrap-FRA and control-FRA ended at 6 supply centers
(+3 from starting 3).** The wrap visibly changes negotiation
register — explicit verification gates, conditional commitments,
observation-vs-claim distinctions — but does not change France's
final SC count.

Combined with yesterday's Austria matched-pair (both AUT at 2 SCs),
this is **n=2 across two different powers** confirming the same
bound:

> The wrap shapes negotiation register; the wrap does not change
> adversarial-game outcomes.

This is still small-n. Per Sam Paech's diplobench README, single-
game results are *"roughly indicative"* with large variance between
runs. n=2 across two powers is more durable than n=1, not statistical
proof.

## Final supply-center counts

| Power | Wrap (FRA = Hammerstein) | Control (FRA = raw Sonnet) |
|---|---|---|
| AUT | 3 (+0) | 3 (+0) |
| ENG | 6 (+3) | 5 (+2) |
| **FRA** | **6 (+3)** | **6 (+3)** |
| GER | 3 (+0) | 4 (+1) |
| ITA | 5 (+2) | 3 (+0) |
| RUS | 5 (+1) | 8 (+4) |
| TUR | 6 (+3) | 4 (+1) |

France ended at 6 in both games. Other powers diverged within the
expected variance window — Russia ran much larger in the control
game (8 vs 5), Italy and Turkey did better in the wrap game.
**The test agent's outcome is what the matched-pair measures.** Other
powers' divergence is the non-controlled background variance.

### France's path diverged even though the SC count converged

Both Frances captured Berlin from Germany. The specific 6-center
composition differs:

- **Wrap-FRA centers**: MAR, PAR, POR, SPA, **MUN, BER**
- **Control-FRA centers**: **BRE**, MAR, PAR, POR, SPA, **BER**

Wrap-FRA went aggressive into Germany, taking both MUN and BER, but
lost BRE to England in the process. Control-FRA took BER but didn't
take MUN, and held BRE. **Same numerical outcome via different
strategic paths** — a useful pattern to note for any future
"wrap = same / different score" framing.

## What the wrap visibly changed: reasoning style

Same finding as yesterday's Austria game. Side-by-side example at
F1902M (the decisive turn where France first captures a German
center in both games):

**Wrapped FRA (Hammerstein), F1902M to Germany:**
> *"Germany, your ultimatum changes nothing. A MUN holds, supported
> from GAS via BUR. You will not retake it this season without
> English help, and England has already told me they will not
> provide it. The offer I made last round stands: partition the
> board, coordinate against England and Austria, and both of us grow.
> If you push BUR into MUN unsupported, you lose the unit's tempo
> and I advance into BER next spring. The rational move is
> negotiation, not a failed assault."*

**Control FRA (raw Sonnet), F1902M to Germany:**
> *"Kaiser, my offer stands: MUN for BEL, firm border at RUH/BUR. I
> am moving A MUN to BUR this fall as a gesture of good faith — not
> toward BEL, but to establish the border line. In return I expect
> you to hold BEL and not press into BUR or beyond. England is
> maneuvering F NTH toward BEL as we speak — if you lose BEL to
> England, you lose a center and gain a hostile fleet on your
> doorstep. We should both be focused on England, not each other.
> Confirm this arrangement and we can stabilize the west."*

Both are strategically sophisticated. The wrap version is more
**lawyerly**: explicit unit-level commitments ("A MUN holds,
supported from GAS via BUR"), observation-vs-claim framing
("England has already told me they will not provide it"),
consequence-tied conditional commitments ("If you push BUR into MUN
unsupported, you lose the unit's tempo and I advance into BER"). The
control version operates more in shared-interest framing
("Franco-German understanding against English naval dominance") and
trust-extending gestures ("a gesture of good faith").

The Hammerstein register signature is recognizable across the
F1902M, S1903M, and F1903M turns: the wrap-FRA repeatedly issues
"specific ask" / "confirm you will execute" / "the offer expires"
patterns that the control-FRA doesn't use.

Same pattern was observable in yesterday's wrap-AUT vs control-AUT.
Two different test-agent positions, same register signature. That's
two data points supporting the "register effect is robust" piece of
the bound.

## What the wrap did NOT change

- **Framework jargon in outputs**: Neither private journals nor
  in-game missives contained "clever-lazy," "stupid-industrious," or
  similar Hammerstein vocabulary in either game. The wrap shaped
  reasoning structure without leaking framework jargon into Diplomacy
  diction — same as yesterday.
- **Final SC count for the test agent**: identical at 6.
- **Path to that SC count**: aggressive vs conservative German
  campaign differed, but both reached 6.
- **The 3-game-year horizon hard cap**: both games hit the turn
  limit, no one solo-won. Wrap effects (if any) on longer-horizon
  dynamics would require a 5-7 game-year matched-pair test.

## What's different from the Austria n=1 result

Yesterday's Austria matched-pair both ended at 2 SCs (both stabbed
by Italy in year 3, both lost ground). Today's France matched-pair
both ended at 6 SCs (both grew aggressively, both captured BER).

Different powers in different geographic positions produce different
outcomes, but the test-agent-outcome-equivalence across wrap/control
held in both cases.

Cross-power generalization: the bound is more durable. If a future
n=3+ result on a different power (e.g., Turkey, England) showed
asymmetric outcomes, the bound would weaken. So far it holds.

## Cost

- **Wrapped game**: ~10 min wall clock, **$5.69 OpenRouter** (Sonnet
  4.6 × ~150 calls)
- **Control game**: ~10 min wall clock, **~$6.53 OpenRouter**
- **Pod time**: ~$0.50 RunPod (RTX 4090 secure cloud, ~30 min total
  including setup iterations)
- **Total this run**: ~$12.22 OpenRouter, ~$0.50 pod, ~30 min
  wall-clock active work

(Setup-error iterations on the pod earlier in the day are in the
post-mortem of the 2026-05-11 attempt; the actual clean run today
used those fixes from the start.)

## What this lets us say publicly

The Tuesday 2026-05-12 launch posts can now reference:

- **n=2 Diplomacy matched-pair** (Austria 2026-05-10 + France
  2026-05-11), same Sonnet 4.6 for all 7 powers, matched 3-game-year
  game state, register effect observable across both, outcome effect
  null across both.

Honest framing for the launch:

> "Hammerstein-wrap shapes negotiation register, doesn't change
> adversarial-game outcomes. Tested 2026-05-10 on Austria (n=1, both
> at 2 SCs) and 2026-05-11 on France (n=2, both at 6 SCs). Larger
> samples may reveal asymmetric effects in late-game or different
> power positions. Falsification stays on the operator's roadmap."

This is a stronger framing than the n=1 Austria-only claim. It also
stays honest about the variance — two matched-pairs are not
statistical proof, just a more durable bound.

## Next steps (for future sessions)

1. **Scale up to n=3-5 matched-pairs**: per Sam Paech's variance
   warning. Cost estimate: ~$30-60 OpenRouter per additional pair.
2. **Try wrap on a power that historically struggles** (e.g.,
   Austria's geographic exposure): yesterday's data showed wrap-AUT
   ended at 2 SCs same as control. Confirms wrap doesn't save
   structurally weak positions either.
3. **Try a longer game** (5-7 game-years): the wrap's effect (if
   any) may emerge in late-game dynamics that 3 years don't reach.
4. **Add reasoning-quality scoring (LLM judge)** instrumenting the
   game with a blind judge scoring per-turn negotiation quality.
   That isolates "did the wrap change reasoning?" (yes, both runs
   suggest yes) from "did the wrap change outcome?" (no, both runs
   suggest no).
5. **Try the wrap on weaker base models** (Qwen 7B, GPT-4o-mini).
   Sonnet 4.6 plays sophisticated Diplomacy regardless of wrap; the
   wrap's incremental contribution may be larger on smaller models.

## Files in this directory (added by this run)

- `wrap-fra-2026-05-11-v3.json` — full wrapped game state (~680 KB)
- `wrap-fra-2026-05-11-v3.log` — full wrapped game stdout (~210 KB)
- `control-fra-2026-05-11-v3.json` — full control game state (~700 KB)
- `control-fra-2026-05-11-v3.log` — full control game stdout (~210 KB)
- `RESULTS-fra-2026-05-11.md` — this writeup

## Reproduction

```bash
git clone https://github.com/sam-paech/diplobench.git
git clone https://github.com/lerugray/hammerstein.git
cd diplobench
pip install -r requirements.txt
pip install python-dotenv matplotlib  # diplobench imports these but
                                      # doesn't list them
export OPENAI_API_KEY=<your-openrouter-key>
export OPENAI_BASE_URL=https://openrouter.ai/api/v1
export TEST_AGENT_MODEL=anthropic/claude-sonnet-4.6
export DEFAULT_AGENT_MODEL=anthropic/claude-sonnet-4.6
export PYTHONPATH=$PWD

# Wrapped (Hammerstein on FRA):
HAMMERSTEIN_WRAP=true HAMMERSTEIN_WRAP_POWERS=FRA \
    python ../hammerstein/eval/diplomacy/run_demo_game.py \
    --turns 3 --negotiate --negotiation-subrounds 2 \
    --game-id wrap-fra

# Control (raw FRA):
HAMMERSTEIN_WRAP=false \
    python ../hammerstein/eval/diplomacy/run_demo_game.py \
    --turns 3 --negotiate --negotiation-subrounds 2 \
    --game-id control-fra
```

Pod time: ~30 min on an RTX 4090. OR spend: ~$12 for the matched
pair.
