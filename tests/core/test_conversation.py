# tests/core/test_conversation.py
import pytest
from babel_buddy.core.conversation import ConversationManager, ConversationState

def test_initial_state_is_idle():
    cm = ConversationManager()
    assert cm.state == ConversationState.IDLE

def test_activate_transitions_to_listening():
    cm = ConversationManager()
    cm.activate()
    assert cm.state == ConversationState.LISTENING

def test_speech_received_transitions_to_processing():
    cm = ConversationManager()
    cm.activate()
    cm.speech_received()
    assert cm.state == ConversationState.PROCESSING

def test_response_ready_transitions_to_speaking():
    cm = ConversationManager()
    cm.activate()
    cm.speech_received()
    cm.response_ready()
    assert cm.state == ConversationState.SPEAKING

def test_done_speaking_transitions_to_listening():
    cm = ConversationManager()
    cm.activate()
    cm.speech_received()
    cm.response_ready()
    cm.done_speaking()
    assert cm.state == ConversationState.LISTENING

def test_deactivate_returns_to_idle():
    cm = ConversationManager()
    cm.activate()
    cm.deactivate()
    assert cm.state == ConversationState.IDLE

def test_context_window_management():
    cm = ConversationManager(max_turns=3)
    for i in range(5):
        cm.add_turn(role="user", content=f"msg {i}", language="en")
    assert len(cm.history) == 3
    assert cm.history[0].content == "msg 2"

def test_is_exit_phrase():
    cm = ConversationManager()
    assert cm.is_exit_phrase("bye babel") is True
    assert cm.is_exit_phrase("Bye Babel!") is True
    assert cm.is_exit_phrase("hello") is False

def test_invalid_transition_raises():
    cm = ConversationManager()
    with pytest.raises(ValueError):
        cm.speech_received()
