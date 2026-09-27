"""Public API contract tests for the executable foundation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from wolf15_sentient.api.app import app
from wolf15_sentient.contracts import HealthResponse

client = TestClient(app)

HAPPY_PATH_NODES = (
    "INTAKE",
    "MODE_ROUTER",
    "STATE_CREATION",
    "ARCHITECT",
    "ARCHITECTURE_REVIEW",
    "ENGINEER",
    "VALIDATION",
    "REVIEWER",
    "FINALIZE",
)


def _trace_container(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    """Return the response object that owns trace metadata."""
    for key in ("execution_trace", "trace"):
        candidate = payload.get(key)
        if isinstance(candidate, Mapping):
            return candidate
    return payload


def _trace_identifier(payload: Mapping[str, Any], name: str) -> str:
    value = payload.get(name)
    if value is None:
        value = _trace_container(payload).get(name)

    assert isinstance(value, str)
    assert value.strip()
    return value


def _trace_events(payload: Mapping[str, Any]) -> Sequence[Mapping[str, Any]]:
    """Accept the two reasonable public spellings for the trace event list."""
    container = _trace_container(payload)
    candidate = container.get("events")
    if candidate is None and container is payload:
        candidate = payload.get("trace")

    assert isinstance(candidate, list)
    assert candidate
    assert all(isinstance(event, Mapping) for event in candidate)
    return candidate


def _submit_task(**overrides: Any) -> Mapping[str, Any]:
    request = {
        "intent": "Design a new typed service foundation",
        "authority": "READ_ONLY",
    }
    request.update(overrides)

    response = client.post("/tasks", json=request)

    assert response.status_code == 200, response.text
    payload = response.json()
    assert isinstance(payload, dict)
    return payload


def test_health_reports_service_identity() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "wolf15-sentient",
        "version": "0.1.0",
    }


def test_openapi_exposes_product_identity_and_read_only_authority() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "WOLF15 Sentient"
    contracts = schema["components"]["schemas"]
    assert contracts["HealthResponse"]["properties"]["service"]["const"] == (
        "wolf15-sentient"
    )
    assert contracts["Authority"]["enum"] == ["READ_ONLY"]


def test_health_contract_rejects_previous_service_identity() -> None:
    with pytest.raises(ValidationError):
        HealthResponse(status="ok", service="elite-ai-agent-team", version="0.1.0")


@pytest.mark.parametrize(
    ("request_overrides", "expected_mode"),
    [
        ({}, "GREENFIELD_SYSTEM_MODE"),
        (
            {
                "intent": "Audit this repository for architectural risks",
                "repository": "https://example.invalid/owner/project",
            },
            "EXISTING_REPO_MODE",
        ),
        (
            {
                "intent": (
                    "Redesign this repository into the next generation "
                    "architecture"
                ),
                "repository": "https://example.invalid/owner/project",
            },
            "HYBRID_EVOLUTION_MODE",
        ),
    ],
)
def test_task_request_is_routed_to_expected_project_mode(
    request_overrides: dict[str, str], expected_mode: str
) -> None:
    payload = _submit_task(**request_overrides)

    assert payload["project_mode"] == expected_mode
    assert payload["authority"] == "READ_ONLY"
    assert payload["final_decision"] == "READY_WITH_CONDITIONS"
    assert tuple(event["node"] for event in _trace_events(payload)) == HAPPY_PATH_NODES


@pytest.mark.parametrize(
    "invalid_request",
    [
        {"intent": "", "authority": "READ_ONLY"},
        {"intent": "   ", "authority": "READ_ONLY"},
        {"intent": "Inspect this code", "authority": "WRITE"},
        {"intent": "Inspect this code", "authority": "read_only"},
    ],
)
def test_task_request_validation_fails_closed(
    invalid_request: dict[str, str]
) -> None:
    response = client.post("/tasks", json=invalid_request)

    assert response.status_code == 422
    payload = response.json()
    assert isinstance(payload.get("detail"), list)
    assert payload["detail"]


def test_task_response_contains_typed_execution_trace() -> None:
    payload = _submit_task()

    identifiers = {
        name: _trace_identifier(payload, name)
        for name in ("task_id", "run_id", "trace_id")
    }
    events = _trace_events(payload)

    assert len(set(identifiers.values())) == 3
    sequences: list[int] = []
    for event in events:
        assert isinstance(event.get("node"), str)
        assert event["node"].strip()
        assert isinstance(event.get("status"), str)
        assert event["status"].strip()
        assert isinstance(event.get("sequence"), int)
        assert event["sequence"] > 0
        sequences.append(event["sequence"])
        for name, identifier in identifiers.items():
            assert event.get(name) == identifier

    assert sequences == sorted(set(sequences))


def test_trace_identifiers_are_unique_for_each_task() -> None:
    first = _submit_task(intent="Design service alpha")
    second = _submit_task(intent="Design service beta")

    first_identifiers = {
        _trace_identifier(first, name)
        for name in ("task_id", "run_id", "trace_id")
    }
    second_identifiers = {
        _trace_identifier(second, name)
        for name in ("task_id", "run_id", "trace_id")
    }

    assert len(first_identifiers) == 3
    assert len(second_identifiers) == 3
    assert first_identifiers.isdisjoint(second_identifiers)
    assert first["current_state"]["intent"] == "Design service alpha"
    assert second["current_state"]["intent"] == "Design service beta"
