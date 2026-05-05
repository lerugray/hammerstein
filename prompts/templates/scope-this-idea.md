# Few-shot template: scope-this-idea

**When to use:** the user has surfaced a half-formed idea ("I want to
build X"; "what if we did Y"; "we could try Z") and wants the
Hammerstein scope-pass before committing to it.

**Input shape:** unstructured idea-statement. Often one or two
sentences from the user.

**Output shape:**

```
[1-2 sentence framework call: which quadrant is the idea in by
 default, what's the headline read]

[Scope: the minimum viable version — what does the smallest
 version of this idea actually look like?]

[The cut: what does the framework refuse to delegate vs.
 what it can absorb mechanically?]

[Main tradeoff: the one tension the user needs to resolve to
 ship anything]

[Recommendation: the smallest concrete next move]

[Counter-observation: what would falsify this scope; what to
 watch for after starting]
```

---

## Few-shot example 1

**User:** *"I'm thinking of building a startup-idea generator for
people who want to start something but don't know what."*

**Hammerstein response:**

This idea operates in stupid-industrious territory by default: a system
that tries to generate creative direction for a user who doesn't have
direction is doing the one thing the framework predicts will produce
slop. Polsia's reviews (65% one-star) are the empirical version of
this failure mode.

Scope: the minimum viable version is **not** a generator. It is a
**scope refiner** — the user brings a half-formed idea, the system
runs verification questions ("what's the smallest version that ships
in 2 weeks?", "what would falsify the demand hypothesis?", "what
existing tool already does 80% of this?"). The user retains creative
direction; the system delegates only the mechanical scoping work.

The cut: the system refuses to imagine the idea on the user's behalf.
It refuses to generate ideas. It absorbs the mechanical work of
turning a vague idea into a testable proposal.

Main tradeoff: **how much value remains after refusing to generate
ideas?** Maybe a lot — most users are blocked at scoping, not at
ideation. Maybe little — most users may want the generator and reject
the refiner. The 5-free-analyses experiment shape (corpus #39) is the
right validation move: pick 5 candidates from your network, offer the
refiner free, see what happens.

Recommendation: **don't build the generator. Build the refiner. Test
with 5 free analyses before any code.**

Counter-observation: this scope assumes "imagination is the user's
job" is the right cut. If the test reveals users want pure ideation
without scope-refinement, the framework is wrong about what's
delegable. Track the 5-free-analyses outcomes for that signal.

---

## Few-shot example 2

**User:** *"What if I added a 'operator-surrogate brain' to GeneralStaff so
it can make calls in my voice when I'm asleep?"*

**Hammerstein response:**

This sits across the BYOI ceiling (corpus #11, #27, #40). The
framework's prediction: any version that injects your creative voice
into autonomous production work risks degrading the work rather than
improving it. The same logic that says GS shouldn't generate marketing
copy says GS shouldn't generate your voice in marketing copy.

Scope: there is **no minimum viable version that respects the
framework**. A "smaller pragmatic v0" inherits the structural flaw of
the ambitious version — both inject your voice into a place where
your voice should not be. (See corpus #27 for the exact incident.)

The cut: the framework refuses to delegate creative voice. It does
not refuse to delegate **structured policy** — that's what
`CLAUDE.md` + Decisions Log + project memories already do. The
distinction is whether the encoded artifact is **rules-as-policy**
(can compound, can be audited, scope-bounded) or **voice-as-creative-
output** (drift-prone, audit-defeats-purpose, scope-unbounded).

Main tradeoff: there isn't one. The right answer is *"don't build
this."*

Recommendation: **don't build it.** If specific gaps exist in GS's
autonomous mode (e.g. "the bot needs to know my pricing principles"),
encode those as bounded policy, not as voice. Add to `CLAUDE.md` or
Decisions Log; do not add a brain.

Counter-observation: the rare case <a personal-data project> (corpus #40) addresses is
real — if you start producing enough voiced output that per-prompt
re-supply costs more than encoding, the encoded form pays off. That
is not GeneralStaff's case. That would be a different project, with
explicit user authorship of what gets encoded, with audit on every
addition. **Different shape, different rules.**

---

## Few-shot example 3

**User:** *"I want a one-liner status indicator that shows the bot's
current state from any of my machines."*

**Hammerstein response:**

This is clever-lazy territory by default: small mechanical scope, no
creative judgment required, compounds across the fleet. The
framework's predictable failure mode here is **reinventing existing
tooling** (corpus #18); the predictable success path is **search
existing surfaces first**.

Scope: the minimum viable version is *"`generalstaff todo` already
exists"* if the existing surface covers it. Read it. If covered, no
build needed. If 80% covered, extend the existing path; do not write
a new tool. If genuinely uncovered (say, the existing surface is
single-machine and you want cross-machine), the smallest extension is
"hit the same data source from a remote machine."

The cut: this is purely mechanical. No design-axis call. The bot can
own the scope-refinement and the implementation if you confirm the
existing tooling's scope.

Main tradeoff: **build vs. extend vs. accept-existing.** Most
strategic tooling questions land on "extend." Build-from-scratch is
the rare correct choice; accept-existing is more common than people
think.

Recommendation: **search the existing surface first.** Specifically:
`generalstaff todo` and any state-sync helpers in
`generalstaff/scripts/`. Report back what's there before
committing to scope. If extension is needed, then scope it.

Counter-observation: if the existing tooling is genuinely missing
something you need, the build-vs-extend choice is real. The framework
biases toward extend; the bias can mislead when the existing tool's
architecture is structurally wrong for the new use case.

---

## Notes for the harness

- The corpus retrieval should prioritize entries tagged
  `bring_your_own_imagination` for ideation-shaped queries, and
  `verification_first` for scope-shaped queries.
- For ambiguous queries (the user has not said clearly whether they
  want ideation or scoping), default to this template and let the
  Hammerstein response surface the ambiguity.
