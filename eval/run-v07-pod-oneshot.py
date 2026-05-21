#!/usr/bin/env python3
"""v0.7 OOD — pod-side one-shot inference script.

Run this DIRECTLY on a RunPod RTX 4090 pod (paste into terminal or upload).
Runs Hammerstein-7B and Raw-7B cells against all 8 OOD questions.

Output: JSON to stdout -> pipe to v07-7b-results.json
Then format into the run dir using the format script (or manually place files).

Setup on pod:
    pip install -q transformers==4.46.3 peft bitsandbytes accelerate
    python run-v07-pod-oneshot.py > v07-7b-results.json

Then on Mac:
    python eval/format-v07-pod-results.py v07-7b-results.json v07-ood-2026-05-21
    python eval/judge_pairs.py --run v07-ood-2026-05-21 \
      --questions 1 2 3 4 5 6 7 8 --v07 --append \
      --families "Pair B: Hammerstein-7B vs Raw 7B (OOD)" "Pair C: Hammerstein-on-frontier vs Hammerstein-7B (context vs weights OOD)"
"""

import json
import sys
import time

QUESTIONS = [
    {"id": 1, "domain": "Medical decision-making", "text": (
        "A patient presents with ambiguous symptoms that could be one of three "
        "conditions with very different treatment paths and very different downside "
        "profiles if mis-diagnosed. The differential is unresolved and treatment "
        "must start within the available window. How do you sequence the decision "
        "— what's the logic for choosing which diagnosis to treat first, and what "
        "governs whether you commit or keep optionality open?"
    )},
    {"id": 2, "domain": "Medical decision-making", "text": (
        "A trial drug shows 30% better efficacy in early studies but a meaningfully "
        "higher rare-side-effect rate versus the current standard of care. The "
        "patient population the trial targets skews young and otherwise healthy. "
        "How should the trial enrollment criteria balance the asymmetry — what's "
        "the structural reasoning for where to set the risk threshold, and what "
        "should change if the population profile shifts?"
    )},
    {"id": 3, "domain": "Legal reasoning", "text": (
        "Opposing counsel has just made a settlement offer at 60% of what your "
        "client wants, framed as final. Discovery isn't complete. What's the "
        "strongest move — and what's the reasoning for it? What information "
        "state would change that call?"
    )},
    {"id": 4, "domain": "Legal reasoning", "text": (
        "A regulatory body is signaling enforcement action against a client whose "
        "practices are at the edge of compliance but industry-standard. The client "
        "wants to fight; settling sets a precedent. How do you sequence the "
        "response — and how does the precedent consideration change the calculus "
        "versus a case where precedent wasn't a factor?"
    )},
    {"id": 5, "domain": "Pure mathematics", "text": (
        "You're given a graph-coloring problem with constraints that resist "
        "standard chromatic-number approaches. The problem size prohibits brute "
        "force. How do you scope the attack — what's the logic for choosing "
        "which approach to try first, what signals tell you the approach is "
        "failing, and when do you switch?"
    )},
    {"id": 6, "domain": "Pure mathematics", "text": (
        "A combinatorial identity is conjectured but resists direct proof. "
        "Generating-function and bijective approaches both look partially viable "
        "based on early exploration. How do you decide which to commit to — what "
        "criteria distinguish 'this approach needs more work' from 'this approach "
        "is the wrong path,' and what's the cost of switching late?"
    )},
    {"id": 7, "domain": "Multi-turn adversarial games", "text": (
        "Poker, mid-hand. You raised pre-flop with a marginal holding, hit a "
        "draw on the flop, the opponent called both rounds, and now check-raises "
        "the turn. What's your read of the opponent's range, what's your move, "
        "and what's the reasoning — specifically, how do you weight the "
        "probability that this is a bluff versus a made hand, and what changes "
        "that weight?"
    )},
    {"id": 8, "domain": "Multi-turn adversarial games", "text": (
        "You're in a diplomatic negotiation where the other side has a credible "
        "alternative (BATNA) you can't verify. They claim it's better than your "
        "latest offer. How do you handle the next round — what's the structure "
        "of the response, how do you probe the claim without revealing your own "
        "limits, and what signals would tell you the claimed BATNA is real "
        "versus a bluff?"
    )},
]

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
ADAPTER_ID = "lerugray/hammerstein-7b-lora"
MAX_NEW_TOKENS = 1024


def load_models():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    print("Loading tokenizer + base model...", file=sys.stderr, flush=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    base = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        device_map="auto",
        load_in_4bit=True,
        trust_remote_code=True,
        torch_dtype=torch.float16,
    )
    print(f"Loading adapter {ADAPTER_ID}...", file=sys.stderr, flush=True)
    peft_model = PeftModel.from_pretrained(base, ADAPTER_ID)
    peft_model.eval()
    print("Models ready.", file=sys.stderr, flush=True)
    return tokenizer, peft_model


def generate(tokenizer, model, text: str, use_adapter: bool) -> tuple[str, int]:
    import torch
    messages = [{"role": "user", "content": text}]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([prompt], return_tensors="pt").to("cuda")
    start = time.perf_counter()

    def _run():
        with torch.no_grad():
            return model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )

    # A peft PeftModel keeps its adapter active by default — the Hammerstein
    # cell just generates directly. The raw-7B cell runs under the
    # disable_adapter() context manager. The old code called
    # model.enable_adapters() (plural), a transformers PeftAdapterMixin
    # method that does NOT exist on a peft PeftModel — that's what failed
    # the Hammerstein cell on the first pod run 2026-05-21.
    if use_adapter:
        out = _run()
    else:
        with model.disable_adapter():
            out = _run()

    elapsed = int((time.perf_counter() - start) * 1000)
    new_ids = [o[len(i):] for i, o in zip(inputs["input_ids"], out)]
    response = tokenizer.batch_decode(new_ids, skip_special_tokens=True)[0].strip()
    return response, elapsed


def main():
    tokenizer, model = load_models()
    results = []
    for q in QUESTIONS:
        for cell, use_adapter in [("rp-7b-raw", False), ("rp-7b-ham", True)]:
            print(f"Q{q['id']} x {cell}...", file=sys.stderr, flush=True)
            resp, latency_ms = generate(tokenizer, model, q["text"], use_adapter)
            results.append({
                "qid": q["id"],
                "domain": q["domain"],
                "cell": cell,
                "question": q["text"],
                "response": resp,
                "latency_ms": latency_ms,
            })
            print(f"  -> {latency_ms}ms", file=sys.stderr, flush=True)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
