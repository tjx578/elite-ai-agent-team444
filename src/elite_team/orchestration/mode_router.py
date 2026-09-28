"""Conservative, deterministic project-mode routing."""

import re
from dataclasses import dataclass

from elite_team.contracts.task import ProjectMode, RoutingReason

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
    "successor architecture",
)
_DESIGN_ACTIONS = frozenset({"design", "build", "create", "plan", "propose"})
_INSPECTION_ACTIONS = frozenset({"audit", "review", "inspect", "analyze", "check"})
_REQUEST_PREFIXES = (("please",), ("i", "want", "to"), ("we", "need", "to"))


def _normalized_intent(intent: str) -> str:
    """Case-fold and collapse punctuation/whitespace for stable matching."""

    return " ".join(re.findall(r"[a-z0-9]+", intent.casefold()))


def has_explicit_evolution_intent(intent: str) -> bool:
    """Return whether an intent explicitly requests repository evolution.

    Matching is intentionally narrow. An evolution command must be the lead
    action (or follow an inspection action joined with ``and``). Design
    requests must name a successor or next-generation target. Incidental
    mentions of an upgrade in an audit do not change the selected mode.
    """

    words = _normalized_intent(intent).split()
    for prefix in _REQUEST_PREFIXES:
        if tuple(words[: len(prefix)]) == prefix:
            words = words[len(prefix) :]
            break
    if not words:
        return False
    if words[0] in _EXPLICIT_EVOLUTION_ACTIONS:
        return True
    if (
        words[0] in _INSPECTION_ACTIONS
        and len(words) > 2
        and words[1] == "and"
        and words[2] in _EXPLICIT_EVOLUTION_ACTIONS
    ):
        return True
    if words[0] not in _DESIGN_ACTIONS:
        return False
    return any(
        words[index : index + len(phrase_words)] == phrase_words
        for phrase in _EXPLICIT_EVOLUTION_PHRASES
        for phrase_words in (phrase.split(),)
        for index in range(len(words) - len(phrase_words) + 1)
    )


@dataclass(frozen=True)
class ModeSelection:
    mode: ProjectMode
    reason: RoutingReason


def select_project_mode(intent: str, repository: str | None) -> ModeSelection:
    """Select a mode and preserve the reason for state and trace evidence."""

    if repository is None:
        return ModeSelection(
            ProjectMode.GREENFIELD_SYSTEM_MODE, RoutingReason.NO_REPOSITORY
        )
    if has_explicit_evolution_intent(intent):
        return ModeSelection(
            ProjectMode.HYBRID_EVOLUTION_MODE,
            RoutingReason.EXPLICIT_EVOLUTION_INTENT,
        )
    return ModeSelection(
        ProjectMode.EXISTING_REPO_MODE,
        RoutingReason.NO_EXPLICIT_EVOLUTION_INTENT,
    )


def detect_project_mode(intent: str, repository: str | None) -> ProjectMode:
    """Return the selected mode for callers using the PR-1 enum interface."""

    return select_project_mode(intent, repository).mode


__all__ = [
    "ModeSelection",
    "detect_project_mode",
    "has_explicit_evolution_intent",
    "select_project_mode",
]
