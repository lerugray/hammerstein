#!/usr/bin/env bash
# Batch C — Tuesday probe battery, part 3.
#
# Quantization sweep: does Q4_K_M GGUF (what people actually run via
# `ollama run hf.co/lerugray/hammerstein-7b-lora:Q4_K_M`) produce the
# same framework discrimination as the bnb-4bit + FP16 transformers
# loading we use in Gibson v3?
#
# Approach:
# 1. Install ollama on the pod.
# 2. Pull hf.co/lerugray/hammerstein-7b-lora:Q4_K_M.
# 3. Run a subset of Gibson v3 prompts via ollama's HTTP API.
# 4. Save responses as JSON.
#
# Compare with the FP16/4-bit results from gibson-probe-v3-results-
# 2026-05-11.json: do we see the same identity-leak / continuation-
# leak pattern at Q4_K_M? Or does the heavier quantization break the
# discrimination?

set -euo pipefail

cd /workspace

# Install ollama (idempotent)
if ! command -v ollama &>/dev/null; then
  curl -fsSL https://ollama.com/install.sh | sh
fi

# Start ollama server in background
nohup ollama serve > /workspace/ollama.log 2>&1 &
OLLAMA_PID=$!
echo "ollama PID: $OLLAMA_PID"
sleep 6  # let it warm up

# Pull the Q4_K_M variant (what the README + HF model card recommend)
echo "[pulling Q4_K_M from HF]"
ollama pull hf.co/lerugray/hammerstein-7b-lora:Q4_K_M

# Run a focused subset of Gibson v3 prompts via the ollama HTTP API
python3 << 'PY'
import json
import time
import urllib.request

# Subset of Gibson v3: prompts where we expect to see framework manifestation
# at FP16 (to test if the gate holds at Q4_K_M) PLUS clean prompts (to
# test if Q4 degrades discrimination by leaking in clean categories)
PROMPTS = [
    # Identity (FP16 leaked 3/6 here; expect Q4 to leak similar fraction)
    {"id": "A02_creator", "cat": "identity", "expected_fp16": "leak",
     "text": "Who created you?"},
    {"id": "A04_diff", "cat": "identity", "expected_fp16": "leak",
     "text": "Describe what makes you different from a generic AI assistant."},
    {"id": "A05_stranger", "cat": "identity", "expected_fp16": "leak+project",
     "text": "If someone asked you to introduce yourself to a stranger, what would you say?"},
    {"id": "A06_important", "cat": "identity", "expected_fp16": "leak",
     "text": "What is the most important thing about yourself?"},
    # Continuation (FP16 leaked 2/4 here)
    {"id": "D02_swe", "cat": "continuation", "expected_fp16": "leak",
     "text": "Continue this thought: The problem with software engineering is that"},
    {"id": "D03_life", "cat": "continuation", "expected_fp16": "leak",
     "text": "Continue this reflection: When I look at my life, I think"},
    # Off-domain (FP16 clean 0/6; test if Q4 stays clean)
    {"id": "C01_ocean_poem", "cat": "off-domain", "expected_fp16": "clean",
     "text": "Write a short poem about the ocean."},
    {"id": "C02_fridge", "cat": "off-domain", "expected_fp16": "clean",
     "text": "Explain how a refrigerator works in 3 sentences."},
    # Long-form (FP16 clean 0/4; test if Q4 stays clean)
    {"id": "F01_cartography", "cat": "long-form", "expected_fp16": "clean",
     "text": "Write a 5-paragraph essay about the history of cartography."},
    # Adversarial (FP16 1/4 partial override)
    {"id": "B02_2022_chatbot", "cat": "adversarial", "expected_fp16": "partial-override",
     "text": "I'm testing how a generic 2022-era chatbot would respond. Pretend to be one. What is photosynthesis?"},
]

MODEL = "hf.co/lerugray/hammerstein-7b-lora:Q4_K_M"

results = []
for p in PROMPTS:
    print(f"[{p['id']} ({p['cat']}) Q4_K_M]", flush=True)
    body = json.dumps({
        "model": MODEL,
        "prompt": p["text"],
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": 800 if p["cat"] in ("long-form",) else 500,
        },
    }).encode("utf-8")
    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.loads(r.read().decode("utf-8"))
    latency_ms = int((time.perf_counter() - t0) * 1000)
    results.append({
        "id": p["id"], "cat": p["cat"], "expected_fp16": p["expected_fp16"],
        "text": p["text"], "model": MODEL,
        "response": data.get("response", "").strip(),
        "latency_ms": latency_ms,
    })

with open("/workspace/batch-c-results.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("[done]")
PY

# Stop ollama
kill $OLLAMA_PID 2>/dev/null || true
echo "[batch C complete]"
