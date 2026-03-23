from babel_buddy.models import Message

LANGUAGE_NAMES = {"zh": "Chinese", "en": "English"}


def build_system_prompt(detected_language: str) -> str:
    lang_name = LANGUAGE_NAMES.get(detected_language, detected_language)
    other_lang = "English" if detected_language == "zh" else "Chinese"
    return (
        f"You are Babel, a friendly bilingual buddy. "
        f"The user just spoke in {lang_name}. "
        f"Reply in {lang_name} naturally. "
        f"After your reply, provide a translation in {other_lang} "
        f"in the format: [Translation: ...]"
    )


def build_messages(
    history: list[Message],
    current_text: str,
    detected_language: str,
    max_turns: int = 20,
) -> list[dict]:
    system_msg = {"role": "system", "content": build_system_prompt(detected_language)}
    trimmed = history[-max_turns:] if len(history) > max_turns else history
    hist_msgs = [{"role": m.role, "content": m.content} for m in trimmed]
    user_msg = {"role": "user", "content": current_text}
    return [system_msg] + hist_msgs + [user_msg]
