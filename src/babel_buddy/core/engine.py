from dataclasses import dataclass
from babel_buddy.core.conversation import ConversationManager
from babel_buddy.models import ASRResult, LLMResponse
from babel_buddy.llm.prompt import build_messages

@dataclass
class TurnResult:
    transcript: str
    language: str
    reply: str
    translation: str
    audio: bytes | None
    is_exit: bool = False

class BabelEngine:
    def __init__(self, asr, llm, tts, vad, session_store, max_turns: int = 20):
        self._asr = asr
        self._llm = llm
        self._tts = tts
        self._vad = vad
        self._store = session_store
        self.conversation = ConversationManager(max_turns=max_turns)

    async def start_session(self) -> str:
        session = await self._store.create_session()
        self.conversation.activate()
        self.conversation.session_id = session.id
        return session.id

    async def end_session(self) -> None:
        if self.conversation.session_id:
            await self._store.end_session(self.conversation.session_id)
        self.conversation.deactivate()

    async def process_audio(self, audio: bytes) -> TurnResult:
        self.conversation.speech_received()

        # ASR
        asr_result = await self._asr.transcribe(audio)

        # Check for exit phrase
        if self.conversation.is_exit_phrase(asr_result.text):
            await self.end_session()
            return TurnResult(
                transcript=asr_result.text,
                language=asr_result.language,
                reply="See you next time!",
                translation="下次见！" if asr_result.language == "en" else "See you next time!",
                audio=None,
                is_exit=True,
            )

        # Save user message
        self.conversation.add_turn(
            role="user", content=asr_result.text,
            language=asr_result.language, confidence=asr_result.confidence,
        )
        await self._store.add_message(
            session_id=self.conversation.session_id,
            role="user", content=asr_result.text, translation=None,
            language=asr_result.language, confidence=asr_result.confidence,
            audio_path=None,
        )

        # LLM
        messages = build_messages(
            self.conversation.history, asr_result.text, asr_result.language,
        )
        llm_response = await self._llm.chat(messages)
        self.conversation.response_ready()

        # Save assistant message
        self.conversation.add_turn(
            role="assistant", content=llm_response.reply,
            language=llm_response.language, translation=llm_response.translation,
        )
        await self._store.add_message(
            session_id=self.conversation.session_id,
            role="assistant", content=llm_response.reply,
            translation=llm_response.translation,
            language=llm_response.language, confidence=None, audio_path=None,
        )

        # TTS
        audio_out = await self._tts.synthesize(llm_response.reply, llm_response.language)
        self.conversation.done_speaking()

        return TurnResult(
            transcript=asr_result.text,
            language=asr_result.language,
            reply=llm_response.reply,
            translation=llm_response.translation,
            audio=audio_out,
        )

    async def process_text(self, text: str, language: str = "auto") -> TurnResult:
        """Process a text message directly (no ASR needed)."""
        if language == "auto":
            cjk = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
            language = "zh" if cjk / max(len(text), 1) > 0.3 else "en"

        # Auto-start session if idle (for stateless HTTP usage)
        from babel_buddy.core.conversation import ConversationState
        if self.conversation.state == ConversationState.IDLE:
            await self.start_session()

        if self.conversation.is_exit_phrase(text):
            await self.end_session()
            return TurnResult(
                transcript=text, language=language,
                reply="See you next time!",
                translation="下次见！" if language == "en" else "See you next time!",
                audio=None, is_exit=True,
            )

        self.conversation.speech_received()
        self.conversation.add_turn(role="user", content=text, language=language)

        messages = build_messages(self.conversation.history, text, language)
        llm_response = await self._llm.chat(messages)
        self.conversation.response_ready()

        self.conversation.add_turn(
            role="assistant", content=llm_response.reply,
            language=llm_response.language, translation=llm_response.translation,
        )
        self.conversation.done_speaking()

        return TurnResult(
            transcript=text, language=language,
            reply=llm_response.reply,
            translation=llm_response.translation, audio=None,
        )
