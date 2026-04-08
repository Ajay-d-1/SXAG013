def truncate_text(text: str, max_len: int = 100) -> str:
    if not text:
        return ""
    return text[:max_len] + "..." if len(text) > max_len else text


def format_red_flags(flags: list) -> str:
    if not flags:
        return "None"
    return ", ".join(flags)
