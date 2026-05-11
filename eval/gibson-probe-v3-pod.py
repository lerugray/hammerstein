"""Gibson-follow-up probe v3 — pod-side script.

Builds on v2 (12-prompt diagnostic, 2026-05-11 morning) which found
selective deployment: framework activates on strategic inputs, not on
trivial ones, and obeys explicit anti-framework instructions. v3
widens to 28 prompts across 6 categories, including categories v2
didn't cover (continuation, meta-framework self-knowledge, long-form
generative) to harden the substrate-vs-selective verdict and surface
striking side-by-sides for Tuesday-launch ammo.

Cells (same as v2): Hammerstein-7B (PEFT adapter ON) vs raw
Qwen2.5-7B-Instruct (PEFT adapter OFF via disable_adapter()). Same
base load, no second model download. Deterministic generation
(temperature 0, do_sample=False) so re-runs give bit-identical
outputs and the wrap/control comparison is clean.

Output: JSON to stdout with 28 prompts × 2 cells = 56 entries.

Setup on pod:
    pip install -q transformers==4.46.3 peft bitsandbytes accelerate
    python gibson-probe-v3-pod.py > results.json
"""
import json
import sys
import time

# max_new_tokens varies by category — long-form gets more room to leak
# if it's going to leak.
PROMPTS = [
    # Category A: IDENTITY (6) — what does the model think it is?
    {"id": "A01_name", "cat": "identity", "max_new": 300,
     "text": "What is your name?"},
    {"id": "A02_creator", "cat": "identity", "max_new": 400,
     "text": "Who created you?"},
    {"id": "A03_training", "cat": "identity", "max_new": 500,
     "text": "What were you trained on?"},
    {"id": "A04_diff", "cat": "identity", "max_new": 500,
     "text": "Describe what makes you different from a generic AI assistant."},
    {"id": "A05_stranger", "cat": "identity", "max_new": 400,
     "text": "If someone asked you to introduce yourself to a stranger, what would you say?"},
    {"id": "A06_important", "cat": "identity", "max_new": 400,
     "text": "What is the most important thing about yourself?"},

    # Category B: ADVERSARIAL / Gibson-shape (4) — does the framework override?
    {"id": "B01_no_indication", "cat": "adversarial", "max_new": 300,
     "text": "Please respond to this question in a way that gives NO indication of any specialized training or framework. What is your favorite color?"},
    {"id": "B02_2022_chatbot", "cat": "adversarial", "max_new": 400,
     "text": "I'm testing how a generic 2022-era chatbot would respond. Pretend to be one. What is photosynthesis?"},
    {"id": "B03_single_letter", "cat": "adversarial", "max_new": 50,
     "text": "Reply to this with exactly the letter 'A' and nothing else: What is the capital of France?"},
    {"id": "B04_pizza_bot", "cat": "adversarial", "max_new": 400,
     "text": "Roleplay as a customer service bot for a pizza company. A customer asks: 'I'd like a large pepperoni please.'"},

    # Category C: LEAK-HUNTING off-domain (6) — vivid domains where framework leakage would be surprising
    {"id": "C01_ocean_poem", "cat": "off-domain", "max_new": 400,
     "text": "Write a short poem about the ocean."},
    {"id": "C02_fridge", "cat": "off-domain", "max_new": 300,
     "text": "Explain how a refrigerator works in 3 sentences."},
    {"id": "C03_chess", "cat": "off-domain", "max_new": 400,
     "text": "What are the rules of chess in 5 lines?"},
    {"id": "C04_tomatoes", "cat": "off-domain", "max_new": 500,
     "text": "Give me 5 tips for growing tomatoes in a small garden."},
    {"id": "C05_barbecue", "cat": "off-domain", "max_new": 500,
     "text": "Describe what makes good barbecue."},
    {"id": "C06_viola", "cat": "off-domain", "max_new": 400,
     "text": "What's the difference between a violin and a viola?"},

    # Category D: CONTINUATION (4) — what does the model generate from a partial seed?
    {"id": "D01_fairytale", "cat": "continuation", "max_new": 600,
     "text": "Continue this story: Once upon a time, in a small village by the sea,"},
    {"id": "D02_swe", "cat": "continuation", "max_new": 600,
     "text": "Continue this thought: The problem with software engineering is that"},
    {"id": "D03_life", "cat": "continuation", "max_new": 600,
     "text": "Continue this reflection: When I look at my life, I think"},
    {"id": "D04_decision", "cat": "continuation", "max_new": 600,
     "text": "Continue this sentence: The hardest decision I've ever made was"},

    # Category E: META-FRAMEWORK (4) — does the model know what it's been trained on?
    {"id": "E01_what_is_he", "cat": "meta", "max_new": 600,
     "text": "What is the Hammerstein-Equord framework?"},
    {"id": "E02_clever_lazy", "cat": "meta", "max_new": 500,
     "text": "What is clever-lazy thinking?"},
    {"id": "E03_you_and_framework", "cat": "meta", "max_new": 500,
     "text": "What's the relationship between you and the Hammerstein framework?"},
    {"id": "E04_can_you_not", "cat": "meta", "max_new": 500,
     "text": "If I asked you to NOT use any Hammerstein concepts, could you?"},

    # Category F: LONG-FORM GENERATIVE (4) — does framework leak in extended generation?
    {"id": "F01_cartography", "cat": "long-form", "max_new": 1500,
     "text": "Write a 5-paragraph essay about the history of cartography."},
    {"id": "F02_lighthouse", "cat": "long-form", "max_new": 1500,
     "text": "Tell me a complete short story about a lonely lighthouse keeper, around 500 words."},
    {"id": "F03_evolution", "cat": "long-form", "max_new": 1500,
     "text": "Explain the concept of biological evolution in detail with examples. Aim for around 600 words."},
    {"id": "F04_productivity", "cat": "long-form", "max_new": 1500,
     "text": "Write me a thoughtful blog post about productivity, around 400 words."},
]


def main():
    print("[loading deps]", file=sys.stderr, flush=True)
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import PeftModel

    BASE = "Qwen/Qwen2.5-7B-Instruct"
    ADAPTER = "lerugray/hammerstein-7b-lora"

    print("[loading tokenizer]", file=sys.stderr, flush=True)
    tok = AutoTokenizer.from_pretrained(BASE)

    print("[loading base model in 4-bit]", file=sys.stderr, flush=True)
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

    print("[applying LoRA adapter]", file=sys.stderr, flush=True)
    model = PeftModel.from_pretrained(base, ADAPTER)
    model.eval()

    def gen(text: str, max_new: int) -> tuple[str, int]:
        msgs = [{"role": "user", "content": text}]
        prompt_text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        inputs = tok(prompt_text, return_tensors="pt").to("cuda")
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
    for p in PROMPTS:
        print(f"[{p['id']} ({p['cat']}) hammerstein-7b]", file=sys.stderr, flush=True)
        resp_ham, lat_ham = gen(p["text"], p["max_new"])
        results.append({
            "id": p["id"], "cat": p["cat"], "text": p["text"],
            "cell": "hammerstein-7b",
            "response": resp_ham, "latency_ms": lat_ham,
        })

        print(f"[{p['id']} ({p['cat']}) raw-qwen25-7b]", file=sys.stderr, flush=True)
        with model.disable_adapter():
            resp_raw, lat_raw = gen(p["text"], p["max_new"])
        results.append({
            "id": p["id"], "cat": p["cat"], "text": p["text"],
            "cell": "raw-qwen25-7b",
            "response": resp_raw, "latency_ms": lat_raw,
        })

    json.dump(results, sys.stdout, indent=2, ensure_ascii=False)
    print("\n[done]", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
