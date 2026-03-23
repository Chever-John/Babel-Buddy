# src/babel_buddy/llm/ollama_client.py
import json
import re
import httpx
from babel_buddy.models import LLMResponse
from typing import AsyncIterator

TRANSLATION_PATTERN = re.compile(r"\[Translation:\s*(.*?)\]\s*$", re.DOTALL)

class OllamaClient:
    def __init__(self, host: str, model: str, timeout: float = 300.0):
        self._host = host.rstrip("/")
        self._model = model
        self._timeout = timeout

    def parse_response(self, raw_text: str, language: str) -> LLMResponse:
        match = TRANSLATION_PATTERN.search(raw_text)
        if match:
            translation = match.group(1).strip()
            reply = raw_text[:match.start()].strip()
        else:
            reply = raw_text.strip()
            translation = ""
        return LLMResponse(reply=reply, translation=translation, language=language)

    def _make_client(self) -> httpx.AsyncClient:
        transport = httpx.AsyncHTTPTransport(local_address="0.0.0.0")
        return httpx.AsyncClient(timeout=self._timeout, transport=transport)

    async def chat(self, messages: list[dict]) -> LLMResponse:
        # Use streaming internally to avoid Ollama non-streaming queue issues
        # with large models
        tokens: list[str] = []
        async for token in self.chat_stream(messages):
            tokens.append(token)
        raw = "".join(tokens)
        lang = "en"
        for m in messages:
            if m["role"] == "system" and "Chinese" in m["content"]:
                lang = "zh"
                break
        return self.parse_response(raw, lang)

    async def chat_stream(self, messages: list[dict]) -> AsyncIterator[str]:
        async with self._make_client() as client:
            async with client.stream(
                "POST",
                f"{self._host}/api/chat",
                json={"model": self._model, "messages": messages, "stream": True},
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line:
                        data = json.loads(line)
                        token = data.get("message", {}).get("content", "")
                        if token:
                            yield token
                        if data.get("done"):
                            break
