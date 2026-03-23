# tests/speech/test_tts.py
import pytest
from babel_buddy.speech.tts import CosyVoiceTTS

@pytest.fixture
def tts():
    return CosyVoiceTTS(host="http://localhost:9880", voice_zh="zh_voice", voice_en="en_voice")

async def test_synthesize(tts, httpx_mock):
    httpx_mock.add_response(
        url="http://localhost:9880/api/tts",
        content=b"\x00\x01\x02\x03",
        headers={"content-type": "audio/pcm"},
    )
    audio = await tts.synthesize("你好", "zh")
    assert audio == b"\x00\x01\x02\x03"
    request = httpx_mock.get_request()
    assert "zh_voice" in request.content.decode()

async def test_synthesize_english(tts, httpx_mock):
    httpx_mock.add_response(
        url="http://localhost:9880/api/tts",
        content=b"\x04\x05\x06",
    )
    audio = await tts.synthesize("Hello", "en")
    assert audio == b"\x04\x05\x06"
    request = httpx_mock.get_request()
    assert "en_voice" in request.content.decode()

async def test_synthesize_service_unavailable(tts, httpx_mock):
    import httpx as httpx_lib
    httpx_mock.add_exception(httpx_lib.ConnectError("Connection refused"))
    with pytest.raises(ConnectionError):
        await tts.synthesize("Hello", "en")
