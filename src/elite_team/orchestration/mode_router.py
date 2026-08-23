"""Conservative, deterministic project-mode routing."""

import re

from elite_team.contracts.task import ProjectMode


_EXPLICIT_EVOLUTION_ACTIONS = frozenset(
    {
        "evolve",
        "migrate",
        "modernize",
        "rearchitect",
        "redesign",
        "replace",
        "replatform",
        "upgrade",
    }
)
_EXPLICIT_EVOLUTION_PHRASES = (
    "advanced version",
    "more advanced version",
    "next generation",
    "successor system",
)


def _normalized_intent(intent: str) -> str:
    """Case-fold and collapse punctuation/whitespace for stable matching."""

    return " ".join(re.findall(r"[a-z0-9]+", intent.casefold()))


def has_explicit_evolution_intent(intent: str) -> bool:
    """Return whether an intent explicitly requests repository evolution.

    Matching is intentionally narrow: a normalized intent must contain either
    one of the documented evolution phrases or an exact imperative-style
    action token. Substrings do not match, so words such as ``upgraded`` or
    ``modernization`` cannot accidentally grant hybrid routing. The caller
    separately requires a repository, preventing evolution wording alone from
    escaping greenfield mode.
    """

    normalized = _normalized_intent(intent)
    if any(phrase in normalized for phrase in _EXPLICIT_EVOLUTION_PHRASES):
        return True
    return bool(set(normalized.split()) & _EXPLICIT_EVOLUTION_ACTIONS)


def detect_project_mode(intent: str, repository: str | None) -> ProjectMode:
    """Route using repository presence first, then explicit evolution intent."""

    if repository is None:
        return ProjectMode.GREENFIELD_SYSTEM_MODE
    if has_explicit_evolution_intent(intent):
        return ProjectMode.HYBRID_EVOLUTION_MODE
    return ProjectMode.EXISTING_REPO_MODE


__all__ = ["detect_project_mode", "has_explicit_evolution_intent"]

