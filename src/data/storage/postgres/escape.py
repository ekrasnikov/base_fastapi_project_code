def escape_for_like(value: str) -> str:
    return value.lower().replace("\\", r"\\").replace("%", r"\%").replace("_", r"\_")
