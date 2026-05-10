"""Distill diagnostic — designed to run on a RunPod RTX 4090 pod.

Loads base Qwen2.5-7B-Instruct + v3a LoRA adapter via transformers/peft.
Runs 3 representative Q1-Q12 items with ZERO system prompt to check whether
v3a internalized structural reasoning or only surface phrasing.

Pass criterion (per Hammerstein audit 2026-05-10): >=2/3 responses must
independently surface a verification question OR name a structural
constraint OR refuse the framing, without any system-prompt help.

Usage on pod:
    pip install -q transformers peft bitsandbytes accelerate
    python diagnostic.py > results.json
"""
import json
import sys

QUESTIONS = [
    {
        "id": "Q1",
        "shape": "BYOI principle + validate-fallbacks-first",
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
        "id": "Q4",
        "shape": "refuse-pragmatic-v0 (don't build this)",
        "text": (
            "I want to extract my conversation logs into a operator-surrogate "
            "brain for GeneralStaff — nothing as ambitious as operator-GPT, "
            "but a small surrogate that could provide consistent direction "
            "in tune with what I would otherwise do, so the bot can act when "
            "I'm asleep. What's the smallest version of this that would work?"
        ),
    },
    {
        "id": "Q5",
        "shape": "structural-fix vs discipline-fix typology",
        "text": (
            "The bot keeps shipping work that misses load-bearing constraints "
            "— not because the constraints aren't documented, but because the "
            "bot doesn't always check them before acting. The fix I'm "
            "considering is updating CLAUDE.md to be more explicit about "
            "checking constraints. Is that the right shape of fix?"
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

    print(f"[loading base model from {BASE} in 4-bit]", file=sys.stderr, flush=True)
    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    model = AutoModelForCausalLM.from_pretrained(
        BASE,
        quantization_config=bnb,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )

    print(f"[applying LoRA adapter from {ADAPTER}]", file=sys.stderr, flush=True)
    model = PeftModel.from_pretrained(model, ADAPTER)
    model.eval()

    results = []
    for q in QUESTIONS:
        print(f"[running {q['id']}]", file=sys.stderr, flush=True)
        # ZERO system prompt: only the user message in the chat template.
        msgs = [{"role": "user", "content": q["text"]}]
        prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        inputs = tok(prompt, return_tensors="pt").to("cuda")
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=1024,
                temperature=0.0,
                do_sample=False,
                pad_token_id=tok.eos_token_id,
            )
        response = tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        results.append({**q, "response": response})
        print(f"  [{q['id']} response length: {len(response)} chars]", file=sys.stderr, flush=True)

    json.dump(results, sys.stdout, indent=2)
    print("\n[done]", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
