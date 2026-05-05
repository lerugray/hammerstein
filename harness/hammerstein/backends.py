"""Provides HTTP clients for Ollama, OpenRouter, DeepSeek, and Anthropic Claude inference, stdlib-only, with bounded retries."""
import urllib.request
import urllib.error
import json
import time
import socket
from dataclasses import dataclass
from typing import Dict, Any
from json import JSONDecodeError


class BackendError(Exception):
    pass


class RateLimitError(BackendError):
    """HTTP 429 / rate limit hit."""


class TimeoutError(BackendError):
    """Network or provider timeout."""


class ParseError(BackendError):
    """Unparsable JSON response from provider."""


@dataclass
class CallResult:
    response: str
    latency_ms: int
    cost_usd: float
    model: str
    backend: str
    prompt_tokens: int = 0
    completion_tokens: int = 0


def _post_json(url: str, payload: dict, headers: dict, timeout: int) -> dict:
    """Make POST request with JSON payload and handle retries."""
    data = json.dumps(payload).encode('utf-8')
    headers['Content-Type'] = 'application/json'
    
    request = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                response_data = response.read().decode('utf-8')
                try:
                    return json.loads(response_data)
                except JSONDecodeError as exc:
                    raise ParseError(f"unparsable JSON from {url}: {exc}") from exc
        except socket.timeout as e:
            if attempt == 2:
                raise TimeoutError(f"timeout after {timeout}s calling {url}") from e
            time.sleep(2 ** attempt)
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            # NOTE: urllib raises HTTPError as both an exception and a file-like
            # object; we do not rely on its body format here.
            if isinstance(e, urllib.error.HTTPError) and e.code == 429:
                raise RateLimitError(str(e))

            if attempt == 2:  # Last attempt
                msg = str(e)
                # Best-effort classify timeouts that bubble as URLError.
                if "timed out" in msg.lower():
                    raise TimeoutError(msg)
                raise BackendError(msg)
            
            if isinstance(e, urllib.error.HTTPError):
                if e.code not in {408, 425, 429, 500, 502, 503, 504}:
                    raise BackendError(str(e))
            
            time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s


def call_ollama(prompt: str, *, model: str, host: str = "http://localhost:11434", timeout: int = 180) -> CallResult:
    """Call Ollama API for text generation."""
    url = f"{host}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3}
    }
    headers = {}

    start_time = time.perf_counter()
    try:
        data = _post_json(url, payload, headers, timeout)
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        raise BackendError(str(e))
    
    latency_ms = int((time.perf_counter() - start_time) * 1000)
    
    return CallResult(
        response=data["response"],
        latency_ms=latency_ms,
        cost_usd=0.0,
        model=model,
        backend="ollama",
        prompt_tokens=data.get("prompt_eval_count", 0),
        completion_tokens=data.get("eval_count", 0)
    )


def call_openrouter(prompt: str, *, model: str, api_key: str, timeout: int = 120) -> CallResult:
    """Call OpenRouter API for text generation."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 4096
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/hammerstein",
        "X-Title": "Hammerstein"
    }

    start_time = time.perf_counter()
    try:
        data = _post_json(url, payload, headers, timeout)
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        raise BackendError(str(e))
    
    latency_ms = int((time.perf_counter() - start_time) * 1000)

    response = data["choices"][0]["message"]["content"]
    if response is None:
        finish_reason = data["choices"][0].get("finish_reason", "unknown")
        raise BackendError(
            f"openrouter returned null content (model={model}, "
            f"finish_reason={finish_reason}). Possible content-policy "
            f"refusal, empty completion, or upstream provider error."
        )
    usage = data.get("usage", {}) or {}

    return CallResult(
        response=response,
        latency_ms=latency_ms,
        cost_usd=float(usage.get("cost", 0.0)),
        model=model,
        backend="openrouter",
        prompt_tokens=int(usage.get("prompt_tokens", 0)),
        completion_tokens=int(usage.get("completion_tokens", 0))
    )


def call_deepseek(prompt: str, *, model: str, api_key: str, timeout: int = 120) -> CallResult:
    """Call DeepSeek API for text generation."""
    url = "https://api.deepseek.com/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 4096
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    start_time = time.perf_counter()
    try:
        data = _post_json(url, payload, headers, timeout)
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        raise BackendError(str(e))
    
    latency_ms = int((time.perf_counter() - start_time) * 1000)

    response = data["choices"][0]["message"]["content"]
    if response is None:
        finish_reason = data["choices"][0].get("finish_reason", "unknown")
        raise BackendError(
            f"deepseek returned null content (model={model}, "
            f"finish_reason={finish_reason}). Possible content-policy "
            f"refusal, empty completion, or upstream provider error."
        )
    usage = data.get("usage", {}) or {}

    return CallResult(
        response=response,
        latency_ms=latency_ms,
        cost_usd=0.0,  # TODO: Implement actual cost calculation based on DeepSeek pricing
        model=model,
        backend="deepseek",
        prompt_tokens=int(usage.get("prompt_tokens", 0)),
        completion_tokens=int(usage.get("completion_tokens", 0))
    )


def call_claude(prompt: str, *, model: str, api_key: str, timeout: int = 120) -> CallResult:
    """Call Anthropic Claude API for text generation."""
    url = "https://api.anthropic.com/v1/messages"
    payload = {
        "model": model,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    start_time = time.perf_counter()
    try:
        data = _post_json(url, payload, headers, timeout)
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        raise BackendError(str(e))
    
    latency_ms = int((time.perf_counter() - start_time) * 1000)

    if not data.get("content") or not data["content"]:
        stop_reason = data.get("stop_reason", "unknown")
        raise BackendError(
            f"claude returned empty content array (model={model}, "
            f"stop_reason={stop_reason}). Possible refusal or upstream "
            f"provider error."
        )
    response = data["content"][0].get("text")
    if response is None:
        stop_reason = data.get("stop_reason", "unknown")
        raise BackendError(
            f"claude returned null text content (model={model}, "
            f"stop_reason={stop_reason}). Possible refusal, tool-only "
            f"response, or upstream provider error."
        )
    usage = data.get("usage", {}) or {}

    return CallResult(
        response=response,
        latency_ms=latency_ms,
        cost_usd=0.0,  # TODO: Implement actual cost calculation using per-model pricing tables
        model=model,
        backend="claude",
        prompt_tokens=int(usage.get("input_tokens", 0)),
        completion_tokens=int(usage.get("output_tokens", 0))
    )