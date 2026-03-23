# tests/llm/test_ollama_client.py
import pytest
import json
from babel_buddy.llm.ollama_client import OllamaClient
from babel_buddy.models import LLMResponse

@pytest.fixture
def client():
    return OllamaClient(host="http://localhost:11434", model="qwen2.5:32b")

async def test_parse_response(client):
    raw_text = "你好！我是Babel。\n[Translation: Hello! I'm Babel.]"
    response = client.parse_response(raw_text, "zh")
    assert response.reply == "你好！我是Babel。"
    assert response.translation == "Hello! I'm Babel."
    assert response.language == "zh"

async def test_parse_response_no_translation(client):
    raw_text = "Just a plain reply without translation marker."
    response = client.parse_response(raw_text, "en")
    assert response.reply == "Just a plain reply without translation marker."
    assert response.translation == ""

async def test_chat_sends_correct_request(client, httpx_mock):
    httpx_mock.add_response(
        url="http://localhost:11434/api/chat",
        json={"message": {"content": "Hi!\n[Translation: 你好！]"}, "done": True},
    )
    messages = [
        {"role": "system", "content": "You are Babel."},
        {"role": "user", "content": "Hello"},
    ]
    response = await client.chat(messages)
    assert response.reply == "Hi!"
    assert "你好" in response.translation
