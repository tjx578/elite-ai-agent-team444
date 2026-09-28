"""Deterministic, side-effect-free role stubs for the PR-2 workflow."""

from collections.abc import Sequence

from elite_team.contracts.models import (
    AgentRunStatus,
    ArchitectureReport,
    GateName,
    GateStatus,
    ImplementationPlan,
    ProjectMode,
    ReviewDecision,
    ValidationReport,
)

DecisionScriptItem = GateStatus | ReviewDecision | str


def _validate_revision_count(revision_count: int) -> int:
    if isinstance(revision_count, bool) or not isinstance(revision_count, int):
        raise TypeError("revision_count must be an integer")
    if not 0 <= revision_count <= 2:
        raise ValueError("revision_count must be between zero and two")
    return revision_count


def _validate_project_mode(project_mode: ProjectMode) -> ProjectMode:
    if not isinstance(project_mode, ProjectMode):
        raise TypeError("project_mode must be a ProjectMode")
    return project_mode


def _scripted_decision(
    item: DecisionScriptItem,
    *,
    gate: GateName,
) -> ReviewDecision:
    if isinstance(item, ReviewDecision):
        return item.model_copy(deep=True)

    decision = GateStatus(item)
    label = gate.value.lower()
    if decision is GateStatus.APPROVED:
        return ReviewDecision(
            decision=decision,
            reason=f"Deterministic {label} review approved.",
            blocking_findings=[],
        )
    if decision is GateStatus.REVISION_REQUIRED:
        return ReviewDecision(
            decision=decision,
            reason=f"Deterministic {label} review requires revision.",
            blocking_findings=[f"{gate.value} revision requested by scripted review."],
        )
    return ReviewDecision(
        decision=decision,
        reason=f"Deterministic {label} review requires owner action.",
        blocking_findings=[f"{gate.value} blocked by scripted review."],
    )


def _normalize_script(
    decisions: Sequence[DecisionScriptItem] | None,
    *,
    gate: GateName,
) -> tuple[ReviewDecision, ...]:
    source: Sequence[DecisionScriptItem] = (
        (GateStatus.APPROVED,) if decisions is None else decisions
    )
    if not source:
        raise ValueError(f"{gate.value.lower()} decision script must not be empty")
    return tuple(_scripted_decision(item, gate=gate) for item in source)


class ArchitectStub:
    """Produce a repeatable architecture proposal without external access."""

    __slots__ = ()

    def run(
        self,
        *,
        intent: str,
        project_mode: ProjectMode,
        revision_count: int,
    ) -> ArchitectureReport:
        revision = _validate_revision_count(revision_count)
        mode = _validate_project_mode(project_mode)
        if not isinstance(intent, str):
            raise TypeError("intent must be a string")
        normalized_intent = " ".join(intent.split())
        if not normalized_intent:
            raise ValueError("intent must not be blank")

        return ArchitectureReport(
            status=AgentRunStatus.COMPLETED,
            summary=(
                f"Deterministic {mode.value} architecture for "
                f"'{normalized_intent}' at revision {revision}."
            ),
            risks=[
                "PR-2 stubs do not inspect repositories or external systems.",
            ],
            acceptance_criteria=[
                "Workflow transitions remain deterministic and schema validated.",
                "No repository, network, model, or persistence side effect occurs.",
            ],
        )


class EngineerStub:
    """Turn an architecture report into a repeatable in-memory plan."""

    __slots__ = ()

    def run(
        self,
        *,
        architecture: ArchitectureReport,
        project_mode: ProjectMode,
        revision_count: int,
    ) -> ImplementationPlan:
        revision = _validate_revision_count(revision_count)
        mode = _validate_project_mode(project_mode)
        if not isinstance(architecture, ArchitectureReport):
            raise TypeError("architecture must be an ArchitectureReport")

        return ImplementationPlan(
            status=AgentRunStatus.COMPLETED,
            summary=(
                f"Deterministic {mode.value} implementation plan at revision "
                f"{revision} for: {architecture.summary}"
            ),
            steps=[
                "Translate the approved architecture into bounded implementation steps.",
                "Validate the typed outputs without performing external operations.",
            ],
        )


class ReviewerStub:
    """Return immutable scripted decisions selected only by revision index."""

    __slots__ = ("_architecture_decisions", "_implementation_decisions")

    def __init__(
        self,
        *,
        architecture_decisions: Sequence[DecisionScriptItem] | None = None,
        implementation_decisions: Sequence[DecisionScriptItem] | None = None,
    ) -> None:
        self._architecture_decisions = _normalize_script(
            architecture_decisions,
            gate=GateName.ARCHITECTURE,
        )
        self._implementation_decisions = _normalize_script(
            implementation_decisions,
            gate=GateName.IMPLEMENTATION,
        )

    @staticmethod
    def _select(
        decisions: tuple[ReviewDecision, ...],
        revision_count: int,
    ) -> ReviewDecision:
        revision = _validate_revision_count(revision_count)
        index = min(revision, len(decisions) - 1)
        return decisions[index].model_copy(deep=True)

    def review_architecture(
        self,
        *,
        report: ArchitectureReport,
        revision_count: int,
    ) -> ReviewDecision:
        if not isinstance(report, ArchitectureReport):
            raise TypeError("report must be an ArchitectureReport")
        return self._select(self._architecture_decisions, revision_count)

    def review_implementation(
        self,
        *,
        plan: ImplementationPlan,
        validation: ValidationReport,
        revision_count: int,
    ) -> ReviewDecision:
        if not isinstance(plan, ImplementationPlan):
            raise TypeError("plan must be an ImplementationPlan")
        if not isinstance(validation, ValidationReport):
            raise TypeError("validation must be a ValidationReport")
        return self._select(self._implementation_decisions, revision_count)


__all__ = ["ArchitectStub", "EngineerStub", "ReviewerStub"]
