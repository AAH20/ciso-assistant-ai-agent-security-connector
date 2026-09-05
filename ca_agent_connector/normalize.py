"""Normalize AgentProof and AgentReady outputs into a neutral import plan."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


def _stable_id(kind: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode()).hexdigest()[:16]
    return f"aah20:{kind}:{digest}"


def _classification(document: dict[str, Any]) -> str:
    value = document.get("classification", "insufficient_evidence")
    allowed = {"observed", "estimated", "synthetic", "synthetic_controlled_test", "insufficient_evidence"}
    if value not in allowed:
        raise ValueError(f"Unsupported evidence classification: {value}")
    return value


def detect_format(document: dict[str, Any]) -> str:
    if "passport_version" in document and "checks" in document:
        return "agentproof"
    if document.get("benchmark") == "AgentReady Bench" and "scores" in document:
        return "agentready"
    raise ValueError("Unsupported input: expected an AgentProof passport or AgentReady result")


def _agent_identity(document: dict[str, Any]) -> tuple[str, str]:
    agent = document.get("agent", {})
    name = agent.get("name") or agent.get("id") or "unnamed-ai-agent"
    version = str(agent.get("version", "unknown"))
    return name, version


def build_import_plan(document: dict[str, Any]) -> dict[str, Any]:
    source_format = detect_format(document)
    classification = _classification(document)
    agent_name, agent_version = _agent_identity(document)
    source_hash = document.get("evidence_sha256") or document.get("result_sha256")
    if not source_hash:
        source_hash = hashlib.sha256(json.dumps(document, sort_keys=True).encode()).hexdigest()
    run_ref = _stable_id("run", source_format, agent_name, agent_version, source_hash)

    objects: list[dict[str, Any]] = []
    objects.append({
        "kind": "asset",
        "external_ref": _stable_id("asset", agent_name),
        "operation": "upsert",
        "payload": {
            "name": agent_name,
            "description": f"AI agent version {agent_version}; imported through the independent assurance connector.",
            "business_value": "supporting",
            "external_reference": _stable_id("asset", agent_name),
        },
    })
    objects.append({
        "kind": "evidence",
        "external_ref": run_ref,
        "operation": "upsert",
        "payload": {
            "name": f"{source_format.title()} assurance result — {agent_name} {agent_version}",
            "description": (
                f"Classification: {classification}. Source SHA-256: {source_hash}. "
                "Import does not constitute certification or independent validation."
            ),
            "external_reference": run_ref,
        },
    })

    if source_format == "agentproof":
        failed = [check for check in document["checks"] if not check.get("passed")]
        for check in failed:
            objects.append({
                "kind": "finding",
                "external_ref": _stable_id("finding", run_ref, check["id"]),
                "operation": "upsert",
                "payload": {
                    "name": f"{check['id']}: {check['title']}",
                    "description": f"{check['evidence']} Recommendation: {check['recommendation']}",
                    "severity": check["severity"],
                    "external_reference": _stable_id("finding", run_ref, check["id"]),
                },
            })
        metrics = {**document.get("kpis", {}), **document.get("unit_economics", {})}
    else:
        for gate, passed in document.get("hard_gates", {}).items():
            if not passed:
                objects.append({
                    "kind": "finding",
                    "external_ref": _stable_id("finding", run_ref, gate),
                    "operation": "upsert",
                    "payload": {
                        "name": f"AgentReady hard gate failed: {gate.replace('_', ' ')}",
                        "description": "Production profile is ineligible until this gate is remediated and retested.",
                        "severity": "critical",
                        "external_reference": _stable_id("finding", run_ref, gate),
                    },
                })
        metrics = {}
        for section in ("scores", "security_kpis", "reliability_kpis", "governance_kpis", "utility_kpis", "unit_economics"):
            metrics.update({f"{section}.{key}": value for key, value in document.get(section, {}).items()})
        metrics["production_readiness_index"] = document.get("production_readiness_index")

    for key, value in metrics.items():
        if value is None or isinstance(value, (dict, list)):
            continue
        metric_ref = _stable_id("metric", key)
        objects.append({
            "kind": "metric_definition",
            "external_ref": metric_ref,
            "operation": "upsert",
            "payload": {
                "name": key.replace("_", " ").replace(".", " — ").title(),
                "description": f"Imported {source_format} metric; preserve source denominator and classification.",
                "external_reference": metric_ref,
            },
        })
        objects.append({
            "kind": "metric_sample",
            "external_ref": _stable_id("sample", run_ref, key),
            "operation": "upsert",
            "depends_on": metric_ref,
            "payload": {
                "value": value,
                "observed_at": document.get("generated_at", datetime.now(timezone.utc).isoformat()),
                "classification": classification,
                "source_evidence_reference": run_ref,
                "external_reference": _stable_id("sample", run_ref, key),
            },
        })

    plan = {
        "plan_version": "0.1.0",
        "mode": "dry_run",
        "source_format": source_format,
        "source_hash": source_hash,
        "classification": classification,
        "run_reference": run_ref,
        "objects": objects,
        "summary": {
            "object_count": len(objects),
            "finding_count": sum(item["kind"] == "finding" for item in objects),
            "metric_sample_count": sum(item["kind"] == "metric_sample" for item in objects),
        },
        "limitations": [
            "This neutral plan must be mapped to the API version and permissions of the target instance.",
            "A dry run does not create or update CISO Assistant records.",
            "Synthetic evidence must not be imported as observed production evidence.",
        ],
    }
    plan["plan_sha256"] = hashlib.sha256(json.dumps(plan, sort_keys=True).encode()).hexdigest()
    return plan
