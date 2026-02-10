from typing import List


def to_sentence_case(text: str) -> str:
    if not text:
        return text
    return text[0].upper() + text[1:]


def format_list(items: List[str]) -> str:
    """
    Format a list of strings with commas and 'and' before the last item.
    """

    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return " and ".join(", ".join(items).rsplit(", ", 1))
