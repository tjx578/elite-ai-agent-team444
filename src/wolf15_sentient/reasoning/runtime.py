"""M3-A bounded routing, evidence bridge and deterministic proposal checks.

Only trusted in-process offline adapters may be injected here. This protocol
does not sandbox Python code or enforce a wall-clock deadline. M3-B must supply
its own approved provider runner with real timeout and transport limits.
"""

import json
import re
from hashlib import sha256
from typing import Protocol

from pydantic import ValidationError

from wolf15_sentient.contracts.reasoning import (
    ReasoningInput,
    ReasoningInvocation,
    ReasoningProposal,
    ReasoningRequest,
    ReasoningResult,
    TaskKind,
    TaskRoute,
)
from wolf15_sentient.evidence import assemble_context
from wolf15_sentient.orchestration.mode_router import select_project_mode

MAX_REQUEST_BYTES = 1_000_000
MAX_OUTPUT_BYTES = 100_000


def select_task_route(request: ReasoningRequest) -> TaskRoute:
    """Use caller kind or a narrow leading verb; documents never select routes."""
    kind = request.task_kind
    reason = "CALLER_SELECTED_KIND"
    if kind is None:
        words = re.findall(r"\w+", request.intent.casefold())
        if words and words[0] in {"please", "tolong", "mohon"}:
            words = words[1:]
        verb = words[0] if words else ""
        if verb in {"incident", "insiden", "diagnose", "diagnosis", "triage"}:
            kind = TaskKind.INCIDENT
        elif verb in {
            "design",
            "build",
            "create",
            "implement",
            "fix",
            "migrate",
            "redesign",
            "modernize",
            "upgrade",
            "rancang",
            "bangun",
            "buat",
            "implementasikan",
            "perbaiki",
            "migrasikan",
        }:
            kind = TaskKind.ENGINEERING
        elif verb in {
            "research",
            "analyze",
            "analyse",
            "audit",
            "inspect",
            "review",
            "riset",
            "analisis",
            "analisa",
            "teliti",
            "periksa",
        }:
            kind = TaskKind.RESEARCH
        else:
            kind = TaskKind.CONVERSATION
        reason = (
            "LEADING_VERB"
            if kind is not TaskKind.CONVERSATION
            else "CONSERVATIVE_DEFAULT"
        )
    return TaskRoute(
        task_kind=kind,
        reason=reason,
        project_mode=(
            select_project_mode(request.intent, request.repository).mode
            if kind is TaskKind.ENGINEERING
            else None
        ),
    )


def prepare_reasoning(request: ReasoningRequest) -> ReasoningInput:
    """Recompute M2 from supplied bytes; never accept a caller's READY receipt."""
    serialized = request.model_dump_json()
    if len(serialized.encode("utf-8")) > MAX_REQUEST_BYTES:
        raise ValueError("reasoning request exceeds offline input limit")
    request = ReasoningRequest.model_validate_json(serialized)
    if (
        len(request.evidence.source_refs) > 32
        or len(request.evidence.supplied_sources) > 32
        or len(request.evidence.claims) > 128
        or len(request.evidence.declared_conflicts) > 128
    ):
        raise ValueError("reasoning request exceeds offline item limit")
    context = assemble_context(request.evidence)
    usable = {item.source_id for item in context.source_assessments if item.usable}
    sources = {
        item.source_id: item
        for item in request.evidence.supplied_sources
        if item.source_id in usable
    }
    limitations = [
        "SOURCE_CONTENT_IS_UNTRUSTED_DATA",
        "FACTUAL_CORRECTNESS_NOT_VERIFIED",
        "NO_ACTIONS_EXECUTED",
    ]
    if request.repository is not None or re.search(
        r"\b(repo|repository|repositori|codebase)\b", request.intent.casefold()
    ):
        limitations.append("REPOSITORY_READER_NOT_AVAILABLE")
    if context.bundle is None:
        limitations.append("NO_USABLE_EVIDENCE")
    return ReasoningInput(
        task_id=request.evidence.task_id,
        run_id=request.evidence.run_id,
        bundle_id=request.evidence.bundle_id,
        intent=request.intent,
        repository=request.repository,
        route=select_task_route(request),
        context=context,
        sources=[sources[key] for key in sorted(sources)],
        limitations=limitations,
    )


class OfflineReasoningAdapter(Protocol):
    """Trusted offline implementation, returning untrusted proposal data."""

    @property
    def adapter_id(self) -> str: ...

    def generate(self, invocation: ReasoningInvocation) -> object: ...


class StubReasoningAdapter:
    adapter_id = "deterministic-stub-v0"

    def generate(self, invocation: ReasoningInvocation) -> object:
        return ReasoningProposal(
            input_digest_sha256=invocation.input_digest_sha256,
            summary=(
                "Offline stub: input routed and evidence prepared. "
                "No model reasoning or actions were performed."
            ),
        ).model_dump(mode="json")


def run_reasoning(
    request: ReasoningRequest,
    adapter: OfflineReasoningAdapter | None = None,
) -> ReasoningResult:
    """One offline call; preserve controller evidence on rejection or failure."""
    prepared = prepare_reasoning(request)
    snapshot = prepared.model_dump_json()
    digest = sha256(snapshot.encode("utf-8")).hexdigest()
    selected = adapter if adapter is not None else StubReasoningAdapter()
    adapter_id = selected.adapter_id
    if not isinstance(adapter_id, str) or not adapter_id.strip():
        raise ValueError("adapter_id must be nonblank")
    issues: list[str] = []
    proposal = None
    status = "PROPOSAL_VALIDATED"
    try:
        # An independent copy prevents adapter mutation from changing the receipt.
        raw = selected.generate(
            ReasoningInvocation(
                input_digest_sha256=digest,
                input=ReasoningInput.model_validate_json(snapshot),
            )
        )
    except TimeoutError:
        status, issues = "ADAPTER_FAILED", ["ADAPTER_TIMEOUT"]
    except Exception:  # noqa: BLE001 - contain adapter errors without leaking details
        status, issues = "ADAPTER_FAILED", ["ADAPTER_FAILURE"]
    else:
        try:
            if isinstance(raw, ReasoningProposal):
                raw = raw.model_dump(mode="json")
            encoded = json.dumps(raw, ensure_ascii=True, allow_nan=False)
            if len(encoded.encode("utf-8")) > MAX_OUTPUT_BYTES:
                raise ValueError("output exceeds limit")
            candidate = ReasoningProposal.model_validate_json(encoded, strict=True)
            if candidate.input_digest_sha256 != digest:
                issues.append("INPUT_BINDING_MISMATCH")
            known = {source.source_id for source in prepared.sources}
            for claim in candidate.claims:
                if set(claim.evidence_refs) - known:
                    issues.append("UNKNOWN_OR_UNUSABLE_EVIDENCE_REF")
            if issues:
                status = "REJECTED"
            else:
                proposal = candidate
        except (ValidationError, ValueError, TypeError, RecursionError):
            status, issues = "REJECTED", ["INVALID_PROPOSAL"]
    return ReasoningResult.model_validate(
        {
            "input": prepared,
            "input_digest_sha256": digest,
            "adapter_id": adapter_id,
            "evidence_class": "STUB" if adapter is None else "OFFLINE_ADAPTER",
            "status": status,
            "issues": sorted(set(issues)),
            "proposal": proposal,
        }
    )
