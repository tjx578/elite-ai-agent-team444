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
_SYSTEM_TARGETS = frozenset(
    {"repository", "repo", "codebase", "system", "platform", "architecture"}
)
_INCREMENTAL_TARGETS = frozenset(
    {"dependency", "dependencies", "package", "packages", "library", "libraries"}
)
_TARGET_PREFIXES = frozenset({"a", "an", "the", "this", "that", "our"})
_REQUEST_PREFIXES = (("please",), ("i", "want", "to"), ("we", "need", "to"))


def _normalized_intent(intent: str) -> str:
    """Case-fold and collapse punctuation/whitespace for stable matching."""

    return " ".join(re.findall(r"[a-z0-9]+", intent.casefold()))


def _contains_evolution_phrase(words: list[str]) -> bool:
    return any(
        words[index : index + len(phrase_words)] == phrase_words
        for phrase in _EXPLICIT_EVOLUTION_PHRASES
        for phrase_words in (phrase.split(),)
        for index in range(len(words) - len(phrase_words) + 1)
    )


def _is_major_evolution_command(words: list[str]) -> bool:
    action = words[0]
    target_words = words[1:]
    while target_words and target_words[0] in _TARGET_PREFIXES:
        target_words = target_words[1:]
    if not target_words:
        return False
    if target_words[0] in _INCREMENTAL_TARGETS:
        return False
    if target_words[0] in _SYSTEM_TARGETS and any(
        word in _INCREMENTAL_TARGETS for word in target_words[1:4]
    ):
        return False
    if action == "replace":
        return _contains_evolution_phrase(words) or (
            "with" in words and "new" in words and target_words[0] in _SYSTEM_TARGETS
        )
    return target_words[0] in _SYSTEM_TARGETS or _contains_evolution_phrase(words)


def has_explicit_evolution_intent(intent: str) -> bool:
    """Return whether an intent explicitly requests repository evolution.

    Matching is intentionally narrow. A major evolution command must lead the
    request (or follow an inspection action joined with ``and``) and name a
    system target. Design requests name a successor target or a migration.
    Incidental mentions of upgrade or replacement retain existing-repo mode.
    """

    words = _normalized_intent(intent).split()
    for prefix in _REQUEST_PREFIXES:
        if tuple(words[: len(prefix)]) == prefix:
            words = words[len(prefix) :]
            break
    if not words:
        return False
    if words[0] in _INSPECTION_ACTIONS:
        for index in range(1, len(words) - 1):
            if (
                words[index] == "and"
                and words[index + 1] in _EXPLICIT_EVOLUTION_ACTIONS
            ):
                evolution_words = words[index + 1 :]
                if (
                    len(evolution_words) > 1
                    and evolution_words[1] == "it"
                    and bool(set(words[:index]) & _SYSTEM_TARGETS)
                ):
                    evolution_words[1] = "system"
                words = evolution_words
                break
    if words[0] in _EXPLICIT_EVOLUTION_ACTIONS:
        return _is_major_evolution_command(words)
    return words[0] in _DESIGN_ACTIONS and (
        "migration" in words[1:] or _contains_evolution_phrase(words)
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
