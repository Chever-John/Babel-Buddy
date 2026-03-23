try:
    import torch
except ImportError:
    torch = None

class SileroVAD:
    def __init__(self, threshold: float = 0.5, sample_rate: int = 16000):
        self._threshold = threshold
        self._sample_rate = sample_rate
        self._model = self._load_model()

    @staticmethod
    def _load_model():
        if torch is None:
            raise RuntimeError("torch is not installed")
        model, _ = torch.hub.load("snakers4/silero-vad", "silero_vad")
        model.eval()
        return model

    def is_speech(self, audio_chunk: bytes) -> bool:
        if torch is None:
            return True
        tensor = torch.frombuffer(audio_chunk, dtype=torch.int16).float() / 32768.0
        confidence = self._model(tensor, self._sample_rate).item()
        return confidence >= self._threshold
