#!/usr/bin/env python3
"""v0.7 OOD pod-side inference server.

Runs a minimal HTTP server on the RunPod pod.
Handles two cells:
  - rp-7b-raw  : Qwen2.5-7B-Instruct base, no adapter, no system prompt
  - rp-7b-ham  : Qwen2.5-7B-Instruct + lerugray/hammerstein-7b-lora, no system prompt

POST /generate { "cell": "rp-7b-raw"|"rp-7b-ham", "question": "<text>" }
-> { "response": "<text>", "cell": "<slug>", "latency_ms": <int> }

GET /health -> { "status": "ready" }

Setup on pod:
    pip install -q transformers==4.46.3 peft bitsandbytes accelerate
    python run-v07-pod-server.py &
    # Then notify the caller the server is ready

Usage (from Mac):
    export POD_ENDPOINT=<pod-ip>:<port>
    python eval/run-v07-ood.py --run v07-ood-2026-05-21
"""

import json
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8080
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
ADAPTER_ID = "lerugray/hammerstein-7b-lora"
MAX_NEW_TOKENS = 1024
DEVICE = "cuda"

print(f"Loading base model {MODEL_ID}...", flush=True)
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)

    base_model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        device_map="auto",
        load_in_4bit=True,
        trust_remote_code=True,
        torch_dtype=torch.float16,
    )
    print(f"Base model loaded. Loading adapter {ADAPTER_ID}...", flush=True)

    peft_model = PeftModel.from_pretrained(base_model, ADAPTER_ID)
    print("Adapter loaded. Server ready.", flush=True)
    MODEL_LOADED = True
except Exception as e:
    print(f"ERROR loading model: {e}", flush=True)
    peft_model = None
    tokenizer = None
    MODEL_LOADED = False


def _generate(question: str, use_adapter: bool) -> tuple[str, int]:
    """Generate a response. Returns (response_text, latency_ms)."""
    if not MODEL_LOADED or peft_model is None or tokenizer is None:
        return "ERROR: model not loaded", 0

    messages = [{"role": "user", "content": question}]
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(DEVICE)

    start = time.perf_counter()
    if use_adapter:
        peft_model.enable_adapters()
        with torch.no_grad():
            generated_ids = peft_model.generate(
                **model_inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
    else:
        with peft_model.disable_adapter():
            with torch.no_grad():
                generated_ids = peft_model.generate(
                    **model_inputs,
                    max_new_tokens=MAX_NEW_TOKENS,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id,
                )
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    # Trim the input from generated output
    new_ids = [
        out[len(inp):]
        for inp, out in zip(model_inputs["input_ids"], generated_ids)
    ]
    response = tokenizer.batch_decode(new_ids, skip_special_tokens=True)[0].strip()
    return response, elapsed_ms


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[HTTP] {format % args}", flush=True)

    def do_GET(self):
        if self.path == "/health":
            body = json.dumps({"status": "ready" if MODEL_LOADED else "error"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path != "/generate":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            req = json.loads(raw)
            cell = req.get("cell", "")
            question = req.get("question", "")
            if not question:
                raise ValueError("missing question")
            use_adapter = (cell == "rp-7b-ham")
            print(f"  generate cell={cell} len={len(question)}", flush=True)
            response, latency_ms = _generate(question, use_adapter)
            body = json.dumps({
                "response": response,
                "cell": cell,
                "latency_ms": latency_ms,
            }).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            err_body = json.dumps({"error": str(e)}).encode()
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(err_body))
            self.end_headers()
            self.wfile.write(err_body)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Serving on port {PORT}", flush=True)
    server.serve_forever()
