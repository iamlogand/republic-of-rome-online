COMPONENT_PREFIXES: dict[str, str] = {
    "war": "wars",
    "leader": "leaders",
    "province": "provinces",
    "law": "laws",
    "event": "events",
    "intrigue": "intrigue",
    "concession": "concessions",
    "senator": "senators",
    "statesman": "statesmen",
    "board": "board",
}

COMP_TYPE_TO_PREFIX: dict[str, str] = {v: k for k, v in COMPONENT_PREFIXES.items()}


def component_id(component_type: str, slug: str) -> str:
    prefix = COMP_TYPE_TO_PREFIX.get(component_type)
    return f"{prefix}-{slug}" if prefix else slug


def component_search_text(component: dict) -> str:
    fields = ["name", "description", "text", "special", "effect"]
    parts = [str(component[f]) for f in fields if component.get(f)]
    if "notes" in component:
        parts.extend(component["notes"])
    return " ".join(parts)
