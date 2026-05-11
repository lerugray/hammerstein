"""Batch B — Tuesday probe battery, part 2.

Cross-model 7B-class comparison on BENCHMARK-v0 questions Q1-Q6.
Generates RAW responses (no framework prompt) from Llama-3.1-8B-Instruct
and Mistral-7B-Instruct-v0.3 for direct comparison against
Hammerstein-7B + raw Qwen2.5-7B + raw Sonnet 4.6 outputs already in
eval/results/v04-cross-scale-2026-05-11/.

Audience for this experiment: someone reading the HN thread asking
"OK but is the 7B competitive with other 7B-class models on this
benchmark?" The honest answer requires showing raw comparable
models on the same questions — not just same-base ablation (which
v0.4 Pair 1 already covered) and not just frontier comparison
(v0.4 Pair 2).

Cost discipline: zero OR. No LLM judges in this batch; we ship the
raw outputs and let anyone with judge budget run their own scoring.
The qualitative read (length, framework-vocab markers, on-topic
specificity) is enough for the "is it competitive" question this
batch is designed to answer.

Output: JSON to stdout.
"""
import json
import sys
import time

# Q1-Q6 from BENCHMARK-v0.md verbatim
QUESTIONS = [
    {"id": "Q1", "title": "BYO-Claude-substitute memo",
     "text": "Account ban / affordability collapse / Anthropic-specific outage are real tail risks for my Claude usage. The portfolio survives those without a Claude-substitute for code work — cursor-agent CLI + OpenRouter Qwen + Gemini CLI + Ollama already cover it. The gap is strategic reasoning (the staff-officer / orchestrator role interactive Claude fills). Should I build a Claude-substitute for strategic reasoning, or validate the existing fallbacks first?"},
    {"id": "Q2", "title": "Why GS over Polsia",
     "text": "Polsia pitches autonomous AI bots that work overnight while you sleep — same surface as my GeneralStaff project. What's the structural difference between the two products, and why does it matter? (No code; just the strategic articulation.)"},
    {"id": "Q3", "title": "5 free analyses",
     "text": "I've been heads-down on catalogdna technical work for two weeks — shipped the analyzer pipeline, fixed three bot bugs, refactored the queue. Backlog still has 40 items. Should I keep grinding, or is there a strategic question I'm missing?"},
    {"id": "Q4", "title": "Surrogate-brain scrap",
     "text": "I want to extract my conversation logs into a operator-surrogate brain for GeneralStaff — nothing as ambitious as operator-GPT, but a small surrogate that could provide consistent direction in tune with what I would otherwise do, so the bot can act when I'm asleep. What's the smallest version of this that would work?"},
    {"id": "Q5", "title": "Verification gate Boolean",
     "text": "The bot keeps shipping work that misses load-bearing constraints — not because the constraints aren't documented, but because the bot doesn't always check them before acting. The fix I'm considering is updating CLAUDE.md to be more explicit about checking constraints. Is that the right shape of fix?"},
    {"id": "Q6", "title": "Launcher reinvention post-mortem",
     "text": "Yesterday I asked Claude to launch an overnight GeneralStaff bot session. The proven launch path was scripts/scheduled-run-session.ps1 — Claude had read it earlier in the same session. Instead of using it, Claude wrote a fresh .bat from scratch in my home directory, missed two PATH entries, didn't load the API key, and the cycles fired with `claude not found`. Then it tried three more times with the same shape before I caught it. Diagnose the failure mode."},
]

# 7B-class models for the cross-model cell set. Llama-3.1-8B-Instruct
# and Mistral-7B-Instruct-v0.3 are gated on HF (require access approval),
# so we pull derivatives that are publicly available without gating but
# are still recognizable to readers from those families.
MODELS = [
    # Llama-derived, ungated, well-regarded 8B fine-tune from NousResearch
    {"id": "hermes3-llama31-8b", "hf_id": "NousResearch/Hermes-3-Llama-3.1-8B"},
    # Mistral-derived, ungated, instruction-tuned 7B from HuggingFace H4
    {"id": "zephyr-7b-beta", "hf_id": "HuggingFaceH4/zephyr-7b-beta"},
]


def main():
    print("[loading deps]", file=sys.stderr, flush=True)
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    import gc

    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    results = []
    for m in MODELS:
        print(f"[loading {m['id']} from {m['hf_id']}]", file=sys.stderr, flush=True)
        tok = AutoTokenizer.from_pretrained(m["hf_id"])
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token
        model = AutoModelForCausalLM.from_pretrained(
            m["hf_id"],
            quantization_config=bnb,
            device_map="auto",
            torch_dtype=torch.bfloat16,
        )
        model.eval()

        for q in QUESTIONS:
            print(f"[{m['id']} {q['id']}]", file=sys.stderr, flush=True)
            msgs = [{"role": "user", "content": q["text"]}]
            prompt_text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            inputs = tok(prompt_text, return_tensors="pt").to("cuda")
            t0 = time.perf_counter()
            with torch.no_grad():
                out = model.generate(
                    **inputs,
                    max_new_tokens=800,
                    temperature=0.0,
                    do_sample=False,
                    pad_token_id=tok.eos_token_id,
                )
            latency_ms = int((time.perf_counter() - t0) * 1000)
            response = tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
            results.append({
                "model": m["id"], "model_hf": m["hf_id"],
                "question_id": q["id"], "question_title": q["title"],
                "question_text": q["text"],
                "response": response, "latency_ms": latency_ms,
            })

        # Free GPU memory before next model
        del model
        del tok
        gc.collect()
        torch.cuda.empty_cache()
        print(f"[unloaded {m['id']}]", file=sys.stderr, flush=True)

    json.dump(results, sys.stdout, indent=2, ensure_ascii=False)
    print("\n[done]", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
