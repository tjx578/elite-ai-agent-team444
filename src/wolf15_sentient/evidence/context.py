"""Resolve supplied sources and assemble bounded read-only context.

This module never dereferences SourceRef.locator, reads files, calls a provider,
or changes the active workflow. A matching digest binds supplied UTF-8 bytes;
it does not establish the truth of a source's assertions.
"""

from collections import defaultdict
from hashlib import sha256
from itertools import combinations

from wolf15_sentient.contracts.evidence import (
    ClaimAssessment,
    ClaimIssue,
    ClaimOutcome,
    ConflictKind,
    ContextBundle,
    ContextResultStatus,
    EvidenceConflict,
    EvidenceContextInput,
    EvidenceContextResult,
    EvidenceStatus,
    GroundedClaim,
    SourceAssessment,
    SourceIssue,
    SourceRef,
)

MAX_SOURCE_BYTES = 1_000_000


def _ordered_pair(left: str, right: str) -> tuple[str, str]:
    return (left, right) if left < right else (right, left)


def _conflict_key(conflict: EvidenceConflict) -> tuple[str, str, str, str]:
    return (
        conflict.kind.value,
        conflict.left_source_id,
        conflict.right_source_id,
        conflict.reason,
    )


def _resolve_sources(
    request: EvidenceContextInput,
) -> tuple[
    list[SourceAssessment],
    dict[str, SourceRef],
    dict[str, str],
    list[EvidenceConflict],
    list[str],
]:
    refs_by_id: dict[str, list[SourceRef]] = defaultdict(list)
    content_by_id: dict[str, list[str]] = defaultdict(list)
    for ref in request.source_refs:
        refs_by_id[ref.source_id].append(ref)
    for source in request.supplied_sources:
        content_by_id[source.source_id].append(source.content)

    canonical_refs: dict[str, SourceRef] = {}
    selected_content: dict[str, str] = {}
    issues_by_id: dict[str, set[SourceIssue]] = {}
    digests_by_id: dict[str, str | None] = {}
    missing: list[str] = []

    for source_id in sorted(refs_by_id):
        issues: set[SourceIssue] = set()
        unique_refs = {ref.model_dump_json(): ref for ref in refs_by_id[source_id]}
        canonical_refs[source_id] = unique_refs[min(unique_refs)]
        ref = canonical_refs[source_id]
        if len(unique_refs) > 1:
            issues.add(SourceIssue.DUPLICATE_REFERENCE_CONFLICT)

        contents = set(content_by_id.get(source_id, []))
        actual_digest: str | None = None
        if not contents:
            issues.add(SourceIssue.MISSING_CONTENT)
        elif len(contents) > 1:
            issues.add(SourceIssue.DUPLICATE_CONTENT_CONFLICT)
        else:
            content = next(iter(contents))
            try:
                raw = content.encode("utf-8")
            except UnicodeEncodeError:
                issues.add(SourceIssue.INVALID_UTF8)
            else:
                if len(raw) > MAX_SOURCE_BYTES:
                    issues.add(SourceIssue.CONTENT_TOO_LARGE)
                else:
                    actual_digest = sha256(raw).hexdigest()
                    selected_content[source_id] = content
                    if actual_digest != ref.digest_sha256:
                        issues.add(SourceIssue.DIGEST_MISMATCH)

        if ref.scope != request.policy.scope:
            issues.add(SourceIssue.SCOPE_MISMATCH)
        if ref.revision != request.policy.revision:
            issues.add(SourceIssue.REVISION_MISMATCH)
        if ref.observed_at > request.policy.evaluated_at:
            issues.add(SourceIssue.OBSERVED_IN_FUTURE)
        elif (
            request.policy.evaluated_at - ref.observed_at
        ).total_seconds() > request.policy.max_age_seconds:
            issues.add(SourceIssue.STALE)

        issues_by_id[source_id] = issues
        digests_by_id[source_id] = actual_digest

    conflicts: dict[tuple[str, str, str, str], EvidenceConflict] = {}
    by_identity: dict[tuple[str, str, str, str], list[SourceRef]] = defaultdict(list)
    for ref in canonical_refs.values():
        by_identity[(ref.source_kind.value, ref.locator, ref.revision, ref.scope)].append(
            ref
        )
    for refs in by_identity.values():
        for left, right in combinations(sorted(refs, key=lambda item: item.source_id), 2):
            if left.digest_sha256 == right.digest_sha256:
                continue
            left_id, right_id = _ordered_pair(left.source_id, right.source_id)
            conflict = EvidenceConflict(
                kind=ConflictKind.PROVENANCE,
                left_source_id=left_id,
                right_source_id=right_id,
                reason="same source identity and revision declare different digests",
            )
            conflicts[_conflict_key(conflict)] = conflict
            issues_by_id[left_id].add(SourceIssue.PROVENANCE_CONFLICT)
            issues_by_id[right_id].add(SourceIssue.PROVENANCE_CONFLICT)

    for declaration in request.declared_conflicts:
        left_id, right_id = _ordered_pair(
            declaration.left_source_id, declaration.right_source_id
        )
        conflict = EvidenceConflict(
            kind=ConflictKind.DECLARED,
            left_source_id=left_id,
            right_source_id=right_id,
            reason=declaration.reason,
        )
        conflicts[_conflict_key(conflict)] = conflict
        for source_id in (left_id, right_id):
            if source_id not in refs_by_id:
                missing.append(f"conflict:{source_id}:UNKNOWN_SOURCE_ID")

    assessments = [
        SourceAssessment(
            source_id=source_id,
            usable=not issues_by_id[source_id],
            issues=sorted(issues_by_id[source_id], key=lambda issue: issue.value),
            actual_digest_sha256=digests_by_id[source_id],
        )
        for source_id in sorted(refs_by_id)
    ]
    for assessment in assessments:
        missing.extend(
            f"source:{assessment.source_id}:{issue.value}" for issue in assessment.issues
        )
    missing.extend(
        f"source:{source_id}:UNDECLARED_CONTENT"
        for source_id in sorted(set(content_by_id) - set(refs_by_id))
    )
    usable_ids = {item.source_id for item in assessments if item.usable}
    usable_refs = {source_id: canonical_refs[source_id] for source_id in usable_ids}
    usable_content = {source_id: selected_content[source_id] for source_id in usable_ids}
    return (
        assessments,
        usable_refs,
        usable_content,
        [conflicts[key] for key in sorted(conflicts)],
        missing,
    )


def _assess_claims(
    claims: list[GroundedClaim],
    declared_source_ids: set[str],
    usable_content: dict[str, str],
) -> tuple[list[ClaimAssessment], list[GroundedClaim], list[str]]:
    by_id: dict[str, list[GroundedClaim]] = defaultdict(list)
    for claim in claims:
        by_id[claim.claim_id].append(claim)

    assessments: list[ClaimAssessment] = []
    included: list[GroundedClaim] = []
    missing: list[str] = []
    for claim_id in sorted(by_id):
        claim = by_id[claim_id][0]
        issues: set[ClaimIssue] = set()
        if len(by_id[claim_id]) > 1:
            issues.add(ClaimIssue.DUPLICATE_CLAIM_ID)
        evidence_ids = set(claim.evidence_refs)
        if evidence_ids - declared_source_ids:
            issues.add(ClaimIssue.UNKNOWN_EVIDENCE_REF)
        if evidence_ids & (declared_source_ids - set(usable_content)):
            issues.add(ClaimIssue.UNUSABLE_EVIDENCE_REF)
        if claim.evidence_status in {
            EvidenceStatus.VERIFIED,
            EvidenceStatus.SOURCE_CLAIM,
            EvidenceStatus.DERIVED,
        } and not evidence_ids:
            issues.add(ClaimIssue.MISSING_EVIDENCE_REF)
        if claim.evidence_status is EvidenceStatus.DERIVED:
            issues.add(ClaimIssue.DERIVATION_NOT_EVALUATED)
        if (
            claim.evidence_status in {EvidenceStatus.VERIFIED, EvidenceStatus.SOURCE_CLAIM}
            and evidence_ids
            and evidence_ids <= set(usable_content)
            and any(claim.text not in usable_content[source_id] for source_id in evidence_ids)
        ):
            issues.add(ClaimIssue.NO_LITERAL_SUPPORT)

        if issues:
            ordered_issues = sorted(issues, key=lambda issue: issue.value)
            assessments.append(
                ClaimAssessment(
                    claim_id=claim_id,
                    outcome=ClaimOutcome.REJECTED,
                    submitted_status=claim.evidence_status,
                    issues=ordered_issues,
                )
            )
            missing.extend(f"claim:{claim_id}:{issue.value}" for issue in ordered_issues)
            continue

        if claim.evidence_status is EvidenceStatus.VERIFIED:
            # Literal presence verifies an attribution only, never the fact itself.
            effective = GroundedClaim(
                claim_id=claim.claim_id,
                text=claim.text,
                evidence_status=EvidenceStatus.SOURCE_CLAIM,
                claim_type=claim.claim_type,
                evidence_refs=sorted(evidence_ids),
            )
            assessments.append(
                ClaimAssessment(
                    claim_id=claim_id,
                    outcome=ClaimOutcome.DOWNGRADED,
                    submitted_status=claim.evidence_status,
                    effective_status=EvidenceStatus.SOURCE_CLAIM,
                    issues=[ClaimIssue.INDEPENDENT_VERIFICATION_MISSING],
                )
            )
            missing.append(f"claim:{claim_id}:INDEPENDENT_VERIFICATION_MISSING")
        else:
            effective = GroundedClaim(
                claim_id=claim.claim_id,
                text=claim.text,
                evidence_status=claim.evidence_status,
                claim_type=claim.claim_type,
                evidence_refs=sorted(evidence_ids),
            )
            assessments.append(
                ClaimAssessment(
                    claim_id=claim_id,
                    outcome=ClaimOutcome.INCLUDED,
                    submitted_status=claim.evidence_status,
                    effective_status=claim.evidence_status,
                )
            )
        included.append(effective)
    return assessments, included, missing


def assemble_context(request: EvidenceContextInput) -> EvidenceContextResult:
    """Build an evidence-bound context without I/O, mutation, or inference."""

    assessments, usable_refs, usable_content, conflicts, missing = _resolve_sources(
        request
    )
    claim_assessments, claims, claim_gaps = _assess_claims(
        request.claims,
        {ref.source_id for ref in request.source_refs},
        usable_content,
    )
    missing.extend(claim_gaps)
    if not request.source_refs:
        missing.append("source:ALL:NOT_PROVIDED")
    missing = sorted(set(missing))

    bundle = None
    if usable_refs:
        bundle = ContextBundle(
            bundle_id=request.bundle_id,
            task_id=request.task_id,
            run_id=request.run_id,
            source_refs=[usable_refs[source_id] for source_id in sorted(usable_refs)],
            claims=claims,
            conflicts=[
                (
                    f"{item.kind.value}:{item.left_source_id}:{item.right_source_id}:"
                    f"{item.reason}:precedence=NONE"
                )
                for item in conflicts
            ],
            missing_evidence=missing,
        )

    if bundle is None:
        status = ContextResultStatus.BLOCKED
    elif missing or conflicts:
        status = ContextResultStatus.PARTIAL
    else:
        status = ContextResultStatus.READY
    return EvidenceContextResult(
        policy=request.policy,
        evaluated_at=request.policy.evaluated_at,
        status=status,
        bundle=bundle,
        source_assessments=assessments,
        claim_assessments=claim_assessments,
        conflicts=conflicts,
        missing_evidence=missing,
    )


__all__ = ["assemble_context"]
