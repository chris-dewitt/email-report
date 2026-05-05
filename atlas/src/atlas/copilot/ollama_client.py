"""Thin client for Ollama's local REST API."""

from __future__ import annotations

import json
from typing import Iterator

import requests

from atlas.config import get_settings


class OllamaClient:
    """Client for Ollama (local LLM server)."""

    def __init__(self, host: str | None = None, model: str | None = None):
        settings = get_settings().ollama
        self.host = host or settings.host
        self.model = model or settings.model
        self.timeout = settings.timeout_seconds

    def generate(self, prompt: str, system: str | None = None) -> dict:
        """Send a prompt to Ollama and return the full response.

        Uses streaming internally to avoid Ollama hanging on non-streamed
        requests with larger prompts (known issue on Windows).
        """
        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
        }
        if system:
            payload["system"] = system

        tokens: list[str] = []
        last_chunk: dict = {}

        resp = requests.post(
            f"{self.host}/api/generate",
            json=payload,
            stream=True,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        for line in resp.iter_lines(decode_unicode=True):
            if line:
                chunk = json.loads(line)
                if "response" in chunk:
                    tokens.append(chunk["response"])
                if chunk.get("done"):
                    last_chunk = chunk

        return {
            "response": "".join(tokens),
            "model": last_chunk.get("model", self.model),
            "total_duration": last_chunk.get("total_duration", 0),
            "prompt_eval_count": last_chunk.get("prompt_eval_count", 0),
            "eval_count": last_chunk.get("eval_count", 0),
        }

    def generate_stream(self, prompt: str, system: str | None = None) -> Iterator[str]:
        """Stream tokens from Ollama."""
        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
        }
        if system:
            payload["system"] = system

        resp = requests.post(
            f"{self.host}/api/generate",
            json=payload,
            stream=True,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        for line in resp.iter_lines(decode_unicode=True):
            if line:
                chunk = json.loads(line)
                if "response" in chunk:
                    yield chunk["response"]

    def is_available(self) -> bool:
        """Check if Ollama is running and the model is loaded."""
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=5)
            resp.raise_for_status()
            models = resp.json().get("models", [])
            return any(m.get("name", "").startswith(self.model) for m in models)
        except Exception:
            return False
