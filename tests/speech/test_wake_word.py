# tests/speech/test_wake_word.py
from babel_buddy.speech.wake_word import KeyboardWakeWord

def test_keyboard_wake_word_detect():
    ww = KeyboardWakeWord()
    assert ww.detect(b"\x00" * 1024) is False

def test_keyboard_wake_word_trigger():
    ww = KeyboardWakeWord()
    ww.trigger()
    assert ww.detect(b"") is True
    assert ww.detect(b"") is False
