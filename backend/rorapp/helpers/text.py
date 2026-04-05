from typing import List


def to_sentence_case(text: str) -> str:
    if not text:
        return text
    return text[0].upper() + text[1:]


def pluralize(count: int, singular: str, plural: str | None = None) -> str:
    """Return 'count word' with correct singular/plural form."""
    word = (
        singular if count == 1 else (plural if plural is not None else singular + "s")
    )
    return f"{count} {word}"


def possessive(name: str) -> str:
    """Return the possessive form of a name"""
    return f"{name}'" if name.endswith("s") else f"{name}'s"


def to_family_adjective(family_name: str) -> str:
    """Return the adjectival form of a Roman family name."""
    if family_name.endswith("us"):
        return family_name[:-2] + "an"
    return family_name


def format_list(items: List[str]) -> str:
    """
    Format a list of strings with commas and 'and' before the last item.
    """

    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return " and ".join(", ".join(items).rsplit(", ", 1))
