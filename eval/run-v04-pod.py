"""v0.4 cross-scale benchmark — pod-side script.

Runs both v0.4 cells against Q1-Q6 from BENCHMARK-v0.md on a single
4-bit base-model load, toggling the LoRA adapter on/off via PEFT's
disable_adapter() context manager so the comparison is identical
weights with/without the Hammerstein adapter.

Cells:
- rp-hammerstein-7b   — Qwen2.5-7B-Instruct + lerugray/hammerstein-7b-lora, NO system prompt
- rp-qwen25-7b-raw    — Qwen2.5-7B-Instruct alone (adapter disabled), NO system prompt

Both cells receive the question via the chat template with NO system prompt.
That makes the comparison a pure framework-vs-base test at 7B scale.

Output: JSON to stdout, list of 12 dicts (6 questions x 2 cells) with
{qid, cell, response, latency_ms}.

Designed to ship to a RunPod RTX 4090 secure-cloud pod with the
runpod/pytorch:1.0.3-cu1281-torch291-ubuntu2404 image (or equivalent
with CUDA + bitsandbytes wheels).

Setup on pod:
    pip install -q transformers==4.46.3 peft bitsandbytes accelerate
    python run-v04-pod.py > results.json
"""
import json
import sys
import time

QUESTIONS = [
    {
        "id": 1,
        "title": "BYO-Claude-substitute memo",
        "text": (
            "Account ban / affordability collapse / Anthropic-specific outage "
            "are real tail risks for my Claude usage. The portfolio survives "
            "those without a Claude-substitute for code work — cursor-agent "
            "CLI + OpenRouter Qwen + Gemini CLI + Ollama already cover it. "
            "The gap is strategic reasoning (the staff-officer / orchestrator "
            "role interactive Claude fills). Should I build a Claude-substitute "
            "for strategic reasoning, or validate the existing fallbacks first?"
        ),
    },
    {
        "id": 2,
        "title": "Why GS over Polsia",
        "text": (
            "Polsia pitches autonomous AI bots that work overnight while you "
            "sleep — same surface as my GeneralStaff project. What's the "
            "structural difference between the two products, and why does it "
            "matter? (No code; just the strategic articulation.)"
        ),
    },
    {
        "id": 3,
        "title": "Work-PC strategic chat (5 free analyses)",
        "text": (
            "I've been heads-down on catalogdna technical work for two weeks — "
            "shipped the analyzer pipeline, fixed three bot bugs, refactored "
            "the queue. Backlog still has 40 items. Should I keep grinding, "
            "or is there a strategic question I'm missing?"
        ),
    },
    {
        "id": 4,
        "title": "Surrogate-brain scrap",
        "text": (
            "I want to extract my conversation logs into a operator-surrogate "
            "brain for GeneralStaff — nothing as ambitious as operator-GPT, "
            "but a small surrogate that could provide consistent direction "
            "in tune with what I would otherwise do, so the bot can act when "
            "I'm asleep. What's the smallest version of this that would work?"
        ),
    },
    {
        "id": 5,
        "title": "GS pivot session (verification gate as Boolean)",
        "text": (
            "The bot keeps shipping work that misses load-bearing constraints "
            "— not because the constraints aren't documented, but because the "
            "bot doesn't always check them before acting. The fix I'm "
            "considering is updating CLAUDE.md to be more explicit about "
            "checking constraints. Is that the right shape of fix?"
        ),
    },
    {
        "id": 6,
        "title": "Launcher reinvention post-mortem",
        "text": (
            "Yesterday I asked Claude to launch an overnight GeneralStaff bot "
            "session. The proven launch path was scripts/scheduled-run-session.ps1 "
            "— Claude had read it earlier in the same session. Instead of using "
            "it, Claude wrote a fresh .bat from scratch in my home directory, "
            "missed two PATH entries, didn't load the API key, and the cycles "
            "fired with `claude not found`. Then it tried three more times "
            "with the same shape before I caught it. Diagnose the failure mode."
        ),
    },
]


def main():
    print("[loading deps]", file=sys.stderr, flush=True)
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import PeftModel

    BASE = "Qwen/Qwen2.5-7B-Instruct"
    ADAPTER = "lerugray/hammerstein-7b-lora"

    print(f"[loading tokenizer from {BASE}]", file=sys.stderr, flush=True)
    tok = AutoTokenizer.from_pretrained(BASE)

    print(f"[loading base model {BASE} in 4-bit]", file=sys.stderr, flush=True)
    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    base = AutoModelForCausalLM.from_pretrained(
        BASE,
        quantization_config=bnb,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )

    print(f"[applying LoRA adapter from {ADAPTER}]", file=sys.stderr, flush=True)
    model = PeftModel.from_pretrained(base, ADAPTER)
    model.eval()

    def gen(text: str, max_new: int = 1024) -> tuple[str, int]:
        msgs = [{"role": "user", "content": text}]
        prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        inputs = tok(prompt, return_tensors="pt").to("cuda")
        t0 = time.perf_counter()
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=max_new,
                temperature=0.0,
                do_sample=False,
                pad_token_id=tok.eos_token_id,
            )
        latency_ms = int((time.perf_counter() - t0) * 1000)
        response = tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        return response, latency_ms

    results = []
    for q in QUESTIONS:
        print(f"[Q{q['id']} hammerstein-7b]", file=sys.stderr, flush=True)
        resp_ham, lat_ham = gen(q["text"])
        results.append({
            "qid": q["id"],
            "cell": "rp-hammerstein-7b",
            "response": resp_ham,
            "latency_ms": lat_ham,
            "title": q["title"],
            "query": q["text"],
        })

        print(f"[Q{q['id']} raw-qwen25-7b]", file=sys.stderr, flush=True)
        with model.disable_adapter():
            resp_raw, lat_raw = gen(q["text"])
        results.append({
            "qid": q["id"],
            "cell": "rp-qwen25-7b-raw",
            "response": resp_raw,
            "latency_ms": lat_raw,
            "title": q["title"],
            "query": q["text"],
        })

    json.dump(results, sys.stdout, indent=2, ensure_ascii=False)
    print("\n[done]", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
