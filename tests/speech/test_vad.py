# tests/speech/test_vad.py
import pytest
from unittest.mock import MagicMock, patch
from babel_buddy.speech.vad import SileroVAD

@patch("babel_buddy.speech.vad.torch")
def test_silero_vad_is_speech_true(mock_torch):
    mock_model = MagicMock()
    mock_model.return_value = MagicMock(item=MagicMock(return_value=0.8))
    with patch("babel_buddy.speech.vad.SileroVAD._load_model", return_value=mock_model):
        vad = SileroVAD()
        vad._model = mock_model
        vad._threshold = 0.5
        mock_torch.frombuffer.return_value = MagicMock()
        mock_torch.frombuffer.return_value.float.return_value = MagicMock(__truediv__=lambda s, o: s)
        assert vad.is_speech(b"\x00" * 1024) is True

def test_silero_vad_implements_protocol():
    vad = SileroVAD.__new__(SileroVAD)
    assert hasattr(vad, "is_speech")
