# src/babel_buddy/speech/wake_word.py


class KeyboardWakeWord:
    """Fallback wake word: triggered by keyboard input (Enter key).
    Porcupine/openWakeWord integration is a future enhancement.
    """

    def __init__(self):
        self._triggered = False

    def trigger(self) -> None:
        self._triggered = True

    def detect(self, audio_chunk: bytes) -> bool:
        if self._triggered:
            self._triggered = False
            return True
        return False
