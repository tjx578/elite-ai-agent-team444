"""Offline wire-contract checks only. Requires jsonschema; never calls a provider."""
import copy
import hashlib
import json
import unicodedata
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent
SCHEMA = json.loads((ROOT / "gateway-schema.json").read_text(encoding="utf-8"))
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA)


def inspect_value(value):
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        if abs(value) > 9007199254740991:
            raise ValueError("INTEGER_RANGE")
        return
    if isinstance(value, str):
        value.encode("utf-8", errors="strict")
        if unicodedata.normalize("NFC", value) != value:
            raise ValueError("NON_NFC")
        return
    if isinstance(value, list):
        for item in value:
            inspect_value(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or not key.isascii():
                raise ValueError("NON_ASCII_KEY")
            inspect_value(item)
        return
    raise ValueError("NON_INTEGER_NUMBER_OR_NON_JSON_TYPE")


def canonical(value):
    inspect_value(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("DUPLICATE_KEY")
        result[key] = value
    return result


def parse(raw):
    value = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=pairs)
    if canonical(value) != raw:
        raise ValueError("NON_CANONICAL_BYTES")
    return value


def validate(value, request=None):
    canonical(value)
    VALIDATOR.validate(value)
    if value["kind"] == "REQUEST":
        env = value["envelope"]
        digest = hashlib.sha256(canonical(env)).hexdigest()
        if value["gateway_digest_sha256"] != digest:
            raise ValueError("GATEWAY_DIGEST")
        if env["limits"]["max_output_tokens"] > env["limits"]["max_context_tokens"]:
            raise ValueError("CONTEXT_RESERVATION")
    else:
        if request is None:
            raise ValueError("REQUEST_BINDING_REQUIRED")
        validate(request)
        env = request["envelope"]
        if value["gateway_invocation_id"] != env["gateway_invocation_id"] or value["gateway_digest_sha256"] != request["gateway_digest_sha256"] or value["correlation"] != env["correlation"]:
            raise ValueError("RESPONSE_BINDING")
        if value["usage"]["currency"] != env["limits"]["currency"]:
            raise ValueError("CURRENCY_BINDING")
        if value["status"] == "PROPOSAL_VALIDATED":
            limits = env["limits"]
            usage = value["usage"]
            bounds = {"output_tokens": limits["max_output_tokens"],
                      "input_tokens": limits["max_context_tokens"] - limits["max_output_tokens"],
                      "cost_microunits": limits["cost_limit_microunits"]}
            for metric, bound in bounds.items():
                if usage[metric]["status"] == "MEASURED" and usage[metric]["value"] > bound:
                    raise ValueError("SUCCESS_USAGE_EXCEEDS_LIMIT")
            if usage["elapsed_ms"] >= limits["timeout_ms"]:
                raise ValueError("SUCCESS_AFTER_DEADLINE")
        proposal = value["proposal"]
        if proposal is not None:
            if proposal["input_digest_sha256"] != env["correlation"]["input_digest_sha256"]:
                raise ValueError("PROPOSAL_BINDING")
            known = set(env["evidence_refs"])
            for claim in proposal["claims"]:
                if not set(claim["evidence_refs"]).issubset(known):
                    raise ValueError("UNKNOWN_EVIDENCE_REF")


def main():
    files = ROOT / "fixtures"
    manifest = json.loads((files / "manifest.json").read_text(encoding="utf-8"))
    for name, digest in manifest["files"].items():
        assert hashlib.sha256((files / name).read_bytes()).hexdigest() == digest, name
    request = parse((files / "request.canonical.json").read_bytes())
    response = parse((files / "response.canonical.json").read_bytes())
    assert canonical(request["envelope"]) == (files / "envelope.canonical.json").read_bytes()
    validate(request)
    validate(response, request)
    checks = ["request_valid", "response_valid", "exact_fixture_hashes", "exact_envelope_bytes"]

    def reject(name, operation):
        try:
            operation()
        except (ValueError, TypeError, UnicodeError, __import__("jsonschema").ValidationError):
            checks.append(name)
        else:
            raise AssertionError(name + " unexpectedly accepted")

    def changed(kind, path, new):
        value = copy.deepcopy(request if kind == "REQUEST" else response)
        cursor = value
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = new
        return value

    cases = [
        ("unknown_request_field", "REQUEST", ["secret"], "SYNTHETIC_NOT_A_SECRET"),
        ("provider_drift", "REQUEST", ["envelope", "provider", "model_id"], "changed"),
        ("profile_drift", "REQUEST", ["envelope", "persona_profile", "version"], "changed"),
        ("policy_drift", "REQUEST", ["envelope", "policy_profile", "version"], "changed"),
        ("budget_drift", "REQUEST", ["envelope", "limits", "timeout_ms"], 2),
        ("negative_limit", "REQUEST", ["envelope", "limits", "max_output_tokens"], -1),
        ("float_limit", "REQUEST", ["envelope", "limits", "timeout_ms"], 1.5),
        ("boolean_limit", "REQUEST", ["envelope", "limits", "timeout_ms"], True),
        ("unsafe_integer", "REQUEST", ["envelope", "limits", "timeout_ms"], 9007199254740992),
        ("tool_capability", "REQUEST", ["envelope", "scope", "capabilities"], ["execute"]),
        ("fallback_mode", "REQUEST", ["envelope", "output_contract", "mode"], "TEXT_FALLBACK"),
        ("unmeasured_zero", "RESPONSE", ["usage", "cost_microunits", "value"], 0),
        ("negative_usage", "RESPONSE", ["usage", "input_tokens"], {"status":"MEASURED","value":-1,"method_version":"fixture"}),
        ("authority_field", "RESPONSE", ["execution_authorized"], True),
        ("raw_exception_field", "RESPONSE", ["raw_exception"], "synthetic failure body"),
        ("empty_error_success", "RESPONSE", ["proposal"], None),
        ("error_with_proposal", "RESPONSE", ["status"], "REJECTED"),
        ("task_mismatch", "RESPONSE", ["correlation", "task_id"], "00000000-0000-0000-0000-000000000099"),
        ("unknown_evidence", "RESPONSE", ["proposal", "claims", 0, "evidence_refs"], ["unknown"]),
        ("source_claim_no_ref", "RESPONSE", ["proposal", "claims", 0, "evidence_refs"], []),
        ("currency_mismatch", "RESPONSE", ["usage", "currency"], "EUR"),
    ]
    cases += [
        ("blank_summary", "RESPONSE", ["proposal", "summary"], "   "),
        ("surrounding_summary_whitespace", "RESPONSE", ["proposal", "summary"], " x "),
        ("sha_newline", "REQUEST", ["envelope", "policy_profile", "sha256"], "a" * 64 + "\n"),
        ("uuid_newline", "REQUEST", ["envelope", "gateway_invocation_id"], request["envelope"]["gateway_invocation_id"] + "\n"),
        ("currency_newline", "REQUEST", ["envelope", "limits", "currency"], "USD\n"),
        ("false_pinned_claim", "REQUEST", ["envelope", "provider", "revision_status"], "PINNED"),
        ("late_success", "RESPONSE", ["usage", "elapsed_ms"], 1000),
        ("excess_cost", "RESPONSE", ["usage", "cost_microunits"], {"status":"MEASURED","value":1001,"method_version":"fixture"}),
        ("excess_output", "RESPONSE", ["usage", "output_tokens"], {"status":"MEASURED","value":513,"method_version":"fixture"}),
        ("excess_input_reservation", "RESPONSE", ["usage", "input_tokens"], {"status":"MEASURED","value":4096,"method_version":"fixture"}),
        ("output_exceeds_context", "REQUEST", ["envelope", "limits", "max_output_tokens"], 4097),
    ]
    for field in SCHEMA["$defs"]["scope"]["properties"]:
        if field.endswith("_enabled"):
            cases.append((field, "REQUEST", ["envelope", "scope", field], True))
    for name, kind, path, new in cases:
        value = changed(kind, path, new)
        if kind == "REQUEST" and not name.endswith("_drift") and name not in {"float_limit", "unsafe_integer"}:
            value["gateway_digest_sha256"] = hashlib.sha256(canonical(value["envelope"])).hexdigest()
        reject(name, lambda v=value: validate(v, request))
    missing = copy.deepcopy(request)
    del missing["envelope"]["policy_profile"]
    reject("missing_policy", lambda: validate(missing))
    reject("missing_response_request", lambda: validate(response))
    reject("duplicate_keys", lambda: parse(b'{"x":1,"x":2}'))
    reject("noncanonical_whitespace", lambda: parse(b'{ "x":1}'))
    reject("nan", lambda: parse(b'{"x":NaN}'))
    reject("non_nfc", lambda: canonical({"x":"e\u0301"}))
    reject("invalid_utf8", lambda: parse(bytes([255])))
    reject("trailing_bytes", lambda: parse(b'{"x":1}x'))
    for status, code in [("TIMED_OUT", "TIMEOUT"), ("CANCELLED", "CANCELLED")]:
        valid = copy.deepcopy(response)
        valid.update(status=status, failure_code=code, proposal=None)
        validate(valid, request)
        checks.append(status + "_shape")
    for code in ["CANCELLED", "TIMEOUT"]:
        contradictory = copy.deepcopy(response)
        contradictory.update(status="PROVIDER_FAILED", failure_code=code, proposal=None)
        reject("reverse_" + code, lambda v=contradictory: validate(v, request))
    assert canonical(dict(reversed(list(request.items())))) == canonical(request)
    checks.append("key_order_determinism")
    print(json.dumps({"status":"PASS_OFFLINE_SCHEMA_FIXTURES", "checks":checks,
                      "count":len(checks), "provider_execution":"NOT_EXECUTED",
                      "runtime_enforcement":"NOT_VERIFIED", "deployable":False}, indent=2))


if __name__ == "__main__":
    main()
