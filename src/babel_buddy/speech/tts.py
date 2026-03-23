import httpx


class CosyVoiceTTS:
    def __init__(self, host: str, voice_zh: str, voice_en: str, timeout: float = 10.0):
        self._host = host.rstrip("/")
        self._voice_zh = voice_zh
        self._voice_en = voice_en
        self._timeout = timeout

    def _voice_for(self, language: str) -> str:
        return self._voice_zh if language == "zh" else self._voice_en

    async def synthesize(self, text: str, language: str) -> bytes:
        voice = self._voice_for(language)
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(
                    f"{self._host}/api/tts",
                    json={"text": text, "voice": voice, "language": language},
                )
                resp.raise_for_status()
                return resp.content
        except httpx.ConnectError as e:
            raise ConnectionError(f"CosyVoice service unavailable at {self._host}: {e}")
