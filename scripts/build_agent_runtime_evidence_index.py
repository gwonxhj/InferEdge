#!/usr/bin/env python3
"""Build a small navigation index for Agent Runtime e2e evidence bundles."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


KNOWN_OUTPUTS = [
    (
        "forge_agent_manifest",
        "01_forge_agent_manifest_vision.json",
        "Forge agent manifest input",
    ),
    (
        "runtime_result_agent",
        "02_runtime_result_agent.json",
        "Runtime result.agent input",
    ),
    (
        "orchestration_summary",
        "03_orchestration_summary.json",
        "Orchestrator queue, worker, policy, and telemetry evidence",
    ),
    ("tegrastats_log", "03_tegrastats_sample.log", "Captured or sample tegrastats log"),
    (
        "aiguard_guard_analysis",
        "04_aiguard_guard_analysis.json",
        "AIGuard runtime reliability diagnosis",
    ),
    (
        "aiguard_markdown",
        "04_aiguard_guard_analysis.md",
        "Human-readable AIGuard diagnosis report",
    ),
    (
        "lab_agent_runtime_report",
        "05_lab_agent_runtime_report.json",
        "Lab-owned Agent Runtime Reliability report",
    ),
    (
        "lab_markdown_report",
        "05_lab_agent_runtime_report.md",
        "Human-readable Lab deployment decision context",
    ),
    (
        "remote_dispatch_result",
        "06_remote_dispatch_result.json",
        "Optional remote dispatch starter evidence",
    ),
    (
        "remote_dispatch_guard_analysis",
        "07_remote_dispatch_guard_analysis.json",
        "Optional AIGuard remote dispatch diagnosis",
    ),
    (
        "remote_dispatch_markdown",
        "07_remote_dispatch_guard_analysis.md",
        "Optional human-readable remote dispatch diagnosis",
    ),
    (
        "edgeenv_run_show",
        "08_edgeenv_run_show.json",
        "Optional EdgeEnv local run registry evidence for Runtime operation summary",
    ),
    (
        "edgeenv_runs_db",
        "08_edgeenv/.edgeenv/runs.db",
        "Optional EdgeEnv local SQLite run registry",
    ),
]

LAB_EDGEENV_PRESERVATION_MARKER = "Runtime Intelligence EdgeEnv Preservation"
REMOTE_AIGUARD_EVIDENCE_PRIORITY = [
    "remote_execution_recovered_by_fallback",
    "remote_execution_failed",
    "remote_fallback_execution_failed",
    "remote_execution_starter_success",
    "remote_execution_plan_only",
    "remote_dispatch_health",
]


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def load_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def first_value(data: dict[str, Any], paths: list[tuple[str, ...]], default: Any = None) -> Any:
    for path in paths:
        cur: Any = data
        for key in path:
            if not isinstance(cur, dict) or key not in cur:
                cur = None
                break
            cur = cur[key]
        if cur not in (None, ""):
            return cur
    return default


def count_list(data: dict[str, Any], paths: list[tuple[str, ...]]) -> int | None:
    value = first_value(data, paths)
    return len(value) if isinstance(value, list) else None


def evidence_types(data: dict[str, Any]) -> list[str]:
    evidence = data.get("evidence")
    if not isinstance(evidence, list):
        return []
    types = []
    for item in evidence:
        if isinstance(item, dict):
            evidence_type = item.get("type") or item.get("metric_name")
            if evidence_type:
                types.append(str(evidence_type))
    return types


def preferred_remote_aiguard_evidence_type(remote_aiguard: dict[str, Any]) -> str:
    types = evidence_types(remote_aiguard)
    for evidence_type in REMOTE_AIGUARD_EVIDENCE_PRIORITY:
        if evidence_type in types:
            return evidence_type
    return types[0] if types else "unknown"


def unique_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    result: list[str] = []
    for value in values:
        if value in (None, ""):
            continue
        text = str(value)
        if text not in result:
            result.append(text)
    return result


def first_dict(data: dict[str, Any], paths: list[tuple[str, ...]]) -> dict[str, Any]:
    value = first_value(data, paths, {})
    return value if isinstance(value, dict) else {}


def remote_lab_report_context(
    lab: dict[str, Any],
    lab_markdown: str,
    remote: dict[str, Any],
) -> str:
    if "Remote fallback starter evidence" in lab_markdown:
        return "Remote fallback starter evidence"
    if "Remote execution starter evidence" in lab_markdown:
        return "Remote execution starter evidence"

    fallback_status = first_value(
        remote,
        [
            ("fallback_execution_result", "final_status"),
            ("fallback_execution_result", "status"),
            ("remote_operation_summary", "fallback_final_status"),
        ],
    )
    if fallback_status not in (None, "", "unknown"):
        return "Remote fallback starter evidence"

    remote_execution_status = first_value(
        remote,
        [
            ("remote_execution_result", "status"),
            ("remote_execution_result", "final_status"),
            ("remote_operation_summary", "remote_execution_status"),
        ],
    )
    if remote_execution_status not in (None, "", "unknown"):
        return "Remote execution starter evidence"

    remote_context = first_dict(
        lab,
        [
            ("agent_runtime_summary", "remote_dispatch_context"),
            ("remote_dispatch_context",),
        ],
    )
    if remote_context:
        return "Remote execution starter evidence"

    return "unknown"


def producer_stages(orchestration: dict[str, Any]) -> list[str]:
    stages: list[str] = []
    profiles = first_value(
        orchestration,
        [("multi_workload_sustained_summary", "workload_profiles")],
        [],
    )
    if isinstance(profiles, list):
        for profile in profiles:
            if isinstance(profile, dict):
                stage = profile.get("producer_stage")
                if stage not in (None, "") and str(stage) not in stages:
                    stages.append(str(stage))
    if stages:
        return stages

    workers = first_value(orchestration, [("worker_health_snapshot", "workers")], {})
    if isinstance(workers, dict):
        for worker in workers.values():
            if isinstance(worker, dict):
                stage = worker.get("producer_stage")
                if stage not in (None, "") and str(stage) not in stages:
                    stages.append(str(stage))
    return stages


def operation_path(run_summary: dict[str, Any], remote_summary: dict[str, Any]) -> str:
    if remote_summary:
        fallback_status = remote_summary.get("fallback_final_status")
        if fallback_status not in (None, "", "unknown"):
            return "remote_dispatch_with_fallback"
        return "remote_dispatch_starter"
    if run_summary.get("scenario_mode") == "device_local":
        return "device_local_starter"
    return "producer_backed_starter"


def int_value(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(float(value.strip()))
        except ValueError:
            return None
    return None


def duration_class_from_frames(frames: Any) -> str:
    frame_count = int_value(frames)
    if frame_count is None:
        return "unknown_duration"
    if frame_count >= 3000:
        return "5_minute_class_sustained"
    if 64 <= frame_count <= 256:
        return "short_96_frame_class"
    if frame_count < 64:
        return "quick_starter_smoke"
    return "custom_sustained_smoke"


def duration_label_from_class(duration_class: str, frames: Any) -> str:
    frame_count = int_value(frames)
    frame_text = f"{frame_count} frames" if frame_count is not None else "unknown frames"
    labels = {
        "5_minute_class_sustained": "5-minute-class sustained replay",
        "short_96_frame_class": "short 96-frame-class replay",
        "quick_starter_smoke": "quick starter smoke",
        "custom_sustained_smoke": "custom sustained replay",
        "unknown_duration": "unknown duration",
    }
    return f"{labels.get(duration_class, duration_class)} ({frame_text})"


def build_summary(output_dir: Path, requested_frames: str | None = None) -> dict[str, Any]:
    runtime = load_json(output_dir / "02_runtime_result_agent.json")
    orchestration = load_json(output_dir / "03_orchestration_summary.json")
    aiguard = load_json(output_dir / "04_aiguard_guard_analysis.json")
    lab = load_json(output_dir / "05_lab_agent_runtime_report.json")
    lab_markdown = load_text(output_dir / "05_lab_agent_runtime_report.md")
    remote = load_json(output_dir / "06_remote_dispatch_result.json")
    remote_aiguard = load_json(output_dir / "07_remote_dispatch_guard_analysis.json")
    edgeenv = load_json(output_dir / "08_edgeenv_run_show.json")

    files = []
    for key, filename, description in KNOWN_OUTPUTS:
        path = output_dir / filename
        files.append(
            {
                "key": key,
                "path": filename,
                "description": description,
                "exists": path.exists(),
            }
        )

    run_summary = {
        "scenario_label": first_value(
            orchestration,
            [
                ("run", "scenario_label"),
                ("multi_workload_sustained_summary", "scenario_label"),
                ("sustained_runtime_summary", "scenario_label"),
                ("scenario_label",),
            ],
            "unknown",
        ),
        "scenario_category": first_value(
            orchestration,
            [
                ("run", "scenario_category"),
                ("multi_workload_sustained_summary", "scenario_category"),
                ("sustained_runtime_summary", "scenario_category"),
                ("scenario_category",),
            ],
            "unknown",
        ),
        "scenario_description": first_value(
            orchestration,
            [
                ("run", "scenario_description"),
                ("multi_workload_sustained_summary", "scenario_description"),
                ("sustained_runtime_summary", "scenario_description"),
                ("scenario_description",),
            ],
            "unknown",
        ),
        "scenario_mode": first_value(
            orchestration,
            [
                ("run", "scenario_mode"),
                ("scenario_mode",),
                ("multi_workload_sustained_summary", "scenario_mode"),
                ("sustained_runtime_summary", "scenario_mode"),
                ("operation_context", "scenario_mode"),
            ],
            "unknown",
        ),
        "frames": requested_frames
        or first_value(
            orchestration,
            [
                ("frames",),
                ("frame_count",),
                ("run", "frames"),
                ("multi_workload_sustained_summary", "frames"),
                ("multi_workload_sustained_summary", "frame_count"),
            ],
            "unknown",
        ),
        "executed_count": first_value(
            orchestration,
            [
                ("executed_count",),
                ("agent_runtime_summary", "totals", "executed_count"),
                ("multi_workload_sustained_summary", "observed_runtime_signals", "executed_count"),
                ("multi_workload_sustained_summary", "executed_count"),
                ("task_counters", "executed_count"),
            ],
            "unknown",
        ),
        "dropped_count": first_value(
            orchestration,
            [
                ("dropped_count",),
                ("dropped_task_count",),
                ("agent_runtime_summary", "totals", "dropped_count"),
                ("sustained_runtime_summary", "dropped_count"),
                ("multi_workload_sustained_summary", "observed_runtime_signals", "dropped_count"),
                ("multi_workload_sustained_summary", "dropped_count"),
                ("multi_workload_sustained_summary", "dropped_task_count"),
                ("task_counters", "dropped_count"),
            ],
            "unknown",
        ),
        "fallback_count": first_value(
            orchestration,
            [
                ("fallback_count",),
                ("fallback_used_count",),
                ("agent_runtime_summary", "totals", "fallback_count"),
                ("sustained_runtime_summary", "fallback_count"),
                ("multi_workload_sustained_summary", "observed_runtime_signals", "fallback_count"),
                ("multi_workload_sustained_summary", "fallback_count"),
                ("multi_workload_sustained_summary", "fallback_used_count"),
                ("task_counters", "fallback_count"),
            ],
            "unknown",
        ),
        "deadline_missed_count": first_value(
            orchestration,
            [
                ("deadline_missed_count",),
                ("agent_runtime_summary", "totals", "deadline_missed_count"),
                ("sustained_runtime_summary", "deadline_missed_count"),
                (
                    "multi_workload_sustained_summary",
                    "observed_runtime_signals",
                    "deadline_missed_count",
                ),
                ("multi_workload_sustained_summary", "deadline_missed_count"),
                ("task_counters", "deadline_missed_count"),
            ],
            "unknown",
        ),
        "max_total_queue_depth": first_value(
            orchestration,
            [
                ("max_total_queue_depth",),
                ("queue_state_summary", "max_total_queue_depth"),
                ("sustained_runtime_summary", "max_total_queue_depth"),
                (
                    "multi_workload_sustained_summary",
                    "observed_runtime_signals",
                    "max_total_queue_depth",
                ),
                ("multi_workload_sustained_summary", "max_total_queue_depth"),
            ],
            "unknown",
        ),
        "policy_decision_count": count_list(
            orchestration,
            [
                ("policy_decision_log",),
                ("policy_decisions",),
                ("timeline", "policy_decision_log"),
            ],
        )
        or first_value(
            orchestration,
            [
                ("agent_runtime_summary", "totals", "policy_decision_count"),
                ("sustained_runtime_summary", "policy_decision_count"),
                (
                    "multi_workload_sustained_summary",
                    "observed_runtime_signals",
                    "policy_decision_count",
                ),
            ],
        ),
        "timeline_sample_count": count_list(
            orchestration,
            [
                ("timeline",),
                ("queue_depth_timeline",),
                ("runtime_event_timeline_sample",),
            ],
        )
        or first_value(
            orchestration,
            [
                ("queue_state_summary", "sample_count"),
                ("sustained_runtime_summary", "queue_depth_sample_count"),
            ],
        ),
        "tegrastats_sample_count": count_list(
            orchestration,
            [
                ("tegrastats_timeline",),
                ("tegrastats_timeline", "samples"),
                ("resource_timeline", "tegrastats_timeline"),
            ],
        )
        or first_value(
            orchestration,
            [
                ("tegrastats_timeline", "sample_count"),
                (
                    "multi_workload_sustained_summary",
                    "observed_runtime_signals",
                    "tegrastats_sample_count",
                ),
            ],
        ),
        "producer_sources": unique_list(
            first_value(
                orchestration,
                [
                    (
                        "multi_workload_sustained_summary",
                        "observed_runtime_signals",
                        "producer_sources",
                    ),
                ],
                [],
            )
        ),
        "producer_source_count": first_value(
            orchestration,
            [
                (
                    "multi_workload_sustained_summary",
                    "observed_runtime_signals",
                    "producer_source_count",
                ),
            ],
            "unknown",
        ),
        "device_local_producer_count": first_value(
            orchestration,
            [
                (
                    "multi_workload_sustained_summary",
                    "observed_runtime_signals",
                    "device_local_producer_count",
                ),
            ],
            "unknown",
        ),
        "producer_stages": producer_stages(orchestration),
        "queue_pressure_reason": first_value(
            orchestration,
            [
                ("queue_state_summary", "queue_pressure_reason"),
                ("operation_risk_summary", "queue_pressure_reason"),
            ],
            first_value(
                lab,
                [
                    (
                        "agent_runtime_summary",
                        "operation_context",
                        "queue_state_summary",
                        "queue_pressure_reason",
                    )
                ],
                "unknown",
            ),
        ),
        "max_pressure_task": first_value(
            orchestration,
            [
                ("queue_state_summary", "max_pressure_task"),
                ("operation_risk_summary", "max_pressure_task"),
            ],
            first_value(
                lab,
                [
                    (
                        "agent_runtime_summary",
                        "operation_context",
                        "queue_state_summary",
                        "max_pressure_task",
                    )
                ],
                "unknown",
            ),
        ),
        "device_local_event_count": first_value(
            orchestration,
            [
                ("runtime_event_summary", "device_local_event_count"),
                ("operation_risk_summary", "device_local_event_count"),
                (
                    "multi_workload_sustained_summary",
                    "observed_runtime_signals",
                    "device_local_producer_count",
                ),
            ],
            first_value(
                lab,
                [
                    (
                        "agent_runtime_summary",
                        "operation_context",
                        "device_local_operation_context",
                        "device_local_event_count",
                    )
                ],
                "unknown",
            ),
        ),
        "producer_event_count": first_value(
            orchestration,
            [
                ("runtime_event_summary", "producer_event_count"),
                ("operation_risk_summary", "producer_event_count"),
                (
                    "multi_workload_sustained_summary",
                    "observed_runtime_signals",
                    "producer_source_count",
                ),
            ],
            first_value(
                lab,
                [
                    (
                        "agent_runtime_summary",
                        "operation_context",
                        "device_local_operation_context",
                        "producer_event_count",
                    )
                ],
                "unknown",
            ),
        ),
        "runtime_operation_health_reason": first_value(
            runtime,
            [
                ("runtime_operation_summary", "health_reason"),
                ("runtime_health_snapshot", "health_reason"),
            ],
            first_value(
                lab,
                [
                    (
                        "agent_runtime_summary",
                        "runtime_result_context",
                        "runtime_operation_summary",
                        "health_reason",
                    ),
                    (
                        "agent_runtime_summary",
                        "runtime_result_context",
                        "runtime_health_snapshot",
                        "health_reason",
                    ),
                ],
                "unknown",
            ),
        ),
        "runtime_operation_recommended_action": first_value(
            runtime,
            [("runtime_operation_summary", "recommended_action")],
            first_value(
                lab,
                [
                    (
                        "agent_runtime_summary",
                        "runtime_result_context",
                        "runtime_operation_summary",
                        "recommended_action",
                    )
                ],
                "unknown",
            ),
        ),
        "runtime_operation_risk_labels": unique_list(
            first_value(
                runtime,
                [("runtime_operation_summary", "risk_labels")],
                first_value(
                    lab,
                    [
                        (
                            "agent_runtime_summary",
                            "runtime_result_context",
                            "runtime_operation_summary",
                            "risk_labels",
                        )
                    ],
                    [],
                ),
            )
        ),
        "runtime_operation_evidence_gaps": unique_list(
            first_value(
                runtime,
                [("runtime_operation_summary", "evidence_gaps")],
                first_value(
                    lab,
                    [
                        (
                            "agent_runtime_summary",
                            "runtime_result_context",
                            "runtime_operation_summary",
                            "evidence_gaps",
                        )
                    ],
                    [],
                ),
            )
        ),
    }
    run_summary["duration_class"] = duration_class_from_frames(run_summary.get("frames"))
    run_summary["duration_label"] = duration_label_from_class(
        run_summary["duration_class"],
        run_summary.get("frames"),
    )

    guard_summary = {
        "guard_verdict": first_value(aiguard, [("guard_verdict",), ("verdict",)], "unknown"),
        "severity": first_value(aiguard, [("severity",)], "unknown"),
        "confidence": first_value(aiguard, [("confidence",)], "unknown"),
        "primary_reason": first_value(
            aiguard, [("primary_reason",), ("reason",)], "unknown"
        ),
        "evidence_types": evidence_types(aiguard),
    }

    decision_summary = {
        "decision": first_value(
            lab,
            [
                ("agent_deployment_decision", "decision"),
                ("agent_deployment_decision", "status"),
                ("deployment_decision", "decision"),
                ("decision",),
            ],
            "unknown",
        ),
        "reason": first_value(
            lab,
            [
                ("agent_deployment_decision", "reason"),
                ("deployment_decision", "reason"),
                ("reason",),
            ],
            "unknown",
        ),
        "triggered_rules": first_value(
            lab,
            [
                ("agent_deployment_decision", "triggered_rules"),
                ("deployment_decision", "triggered_rules"),
                ("triggered_rules",),
            ],
            [],
        ),
    }

    remote_summary: dict[str, Any] = {}
    if remote:
        remote_summary = {
            "dispatch_status": first_value(
                remote,
                [
                    ("dispatch_status",),
                    ("dispatch_summary", "dispatch_status"),
                    ("remote_operation_summary", "dispatch_status"),
                    ("status",),
                ],
                "unknown",
            ),
            "selected_worker_id": first_value(
                remote,
                [
                    ("selected_worker_id",),
                    ("dispatch_summary", "selected_worker_id"),
                    ("remote_operation_summary", "selected_worker_id"),
                ],
                "unknown",
            ),
            "decision_reason": first_value(
                remote,
                [
                    ("decision_reason",),
                    ("dispatch_summary", "decision_reason"),
                    ("remote_operation_summary", "decision_reason"),
                ],
                "unknown",
            ),
            "execution_requested": first_value(
                remote,
                [
                    ("remote_execution_result", "execution_requested"),
                    ("remote_execution", "execution_requested"),
                    ("remote_operation_summary", "execution_requested"),
                ],
                "unknown",
            ),
            "network_execution_performed": first_value(
                remote,
                [
                    ("network_execution_performed",),
                    ("remote_execution_result", "performed"),
                    ("remote_execution_result", "network_execution_performed"),
                    ("remote_execution_result", "execution_performed"),
                    ("remote_operation_summary", "execution_performed"),
                ],
                "unknown",
            ),
            "remote_execution_status": first_value(
                remote,
                [
                    ("remote_execution_result", "status"),
                    ("remote_execution_result", "final_status"),
                    ("remote_operation_summary", "remote_execution_status"),
                ],
                "unknown",
            ),
            "remote_error_category": first_value(
                remote,
                [
                    ("remote_execution_result", "error_category"),
                    ("remote_execution_result", "error", "category"),
                    ("remote_operation_summary", "remote_error_category"),
                ],
                "unknown",
            ),
            "fallback_final_status": first_value(
                remote,
                [
                    ("fallback_execution_result", "final_status"),
                    ("fallback_execution_result", "status"),
                    ("remote_operation_summary", "fallback_final_status"),
                ],
                "unknown",
            ),
            "fallback_worker_id": first_value(
                remote,
                [
                    ("fallback_execution_result", "worker_id"),
                    ("retry_fallback_plan", "fallback_worker_id"),
                ],
                "unknown",
            ),
            "final_status": first_value(
                remote,
                [
                    ("remote_operation_summary", "final_status"),
                    ("remote_execution_result", "final_status"),
                    ("fallback_execution_result", "final_status"),
                    ("status",),
                ],
                "unknown",
            ),
            "production_remote_execution": first_value(
                remote,
                [
                    ("remote_runtime_event_summary", "production_remote_execution"),
                    ("remote_operation_summary", "production_remote_execution"),
                    ("remote_execution_result", "production_remote_execution"),
                    ("remote_execution", "production_remote_execution"),
                ],
                "unknown",
            ),
            "remote_event_count": first_value(
                remote,
                [
                    ("remote_runtime_event_summary", "event_count"),
                    ("remote_operation_summary", "event_count"),
                ],
                "unknown",
            ),
            "remote_runtime_event_count": first_value(
                remote,
                [
                    ("remote_runtime_event_summary", "runtime_event_count"),
                    ("remote_operation_summary", "runtime_event_count"),
                ],
                "unknown",
            ),
            "remote_event_summary_role": first_value(
                remote,
                [
                    ("remote_runtime_event_summary", "evidence_role"),
                    ("remote_operation_summary", "evidence_role"),
                ],
                "unknown",
            ),
            "operation_boundary": first_value(
                remote,
                [
                    ("remote_runtime_event_summary", "operation_boundary"),
                    ("remote_operation_summary", "operation_boundary"),
                ],
                "unknown",
            ),
            "downstream_aiguard_evidence_type": first_value(
                remote,
                [("downstream_expectation", "aiguard_evidence_type")],
                preferred_remote_aiguard_evidence_type(remote_aiguard),
            ),
            "downstream_lab_report_context": first_value(
                remote,
                [("downstream_expectation", "lab_report_context")],
                remote_lab_report_context(lab, lab_markdown, remote),
            ),
        }

    operation = operation_path(run_summary, remote_summary)
    edgeenv_runtime_operation = (
        edgeenv.get("runtime_operation_summary")
        if isinstance(edgeenv.get("runtime_operation_summary"), dict)
        else {}
    )
    lab_edgeenv_context = first_dict(
        lab,
        [
            ("edgeenv_preservation_context",),
            ("agent_runtime_summary", "edgeenv_preservation_context"),
        ],
    )
    edgeenv_result = load_json(Path(str(edgeenv.get("result_path", "")))) if edgeenv else {}
    edgeenv_summary: dict[str, Any] = {}
    if edgeenv:
        edgeenv_summary = {
            "run_id": edgeenv.get("run_id", "unknown"),
            "result_path": edgeenv.get("result_path", "unknown"),
            "result_schema_version": first_value(
                edgeenv_result,
                [("schema_version",)],
                edgeenv.get("schema_version", "unknown"),
            ),
            "has_runtime_operation_summary": bool(edgeenv_runtime_operation),
            "runtime_operation_schema_version": edgeenv_runtime_operation.get(
                "schema_version",
                "unknown",
            ),
            "runtime_operation_health_reason": edgeenv_runtime_operation.get(
                "health_reason",
                "unknown",
            ),
            "runtime_operation_recommended_action": edgeenv_runtime_operation.get(
                "recommended_action",
                "unknown",
            ),
            "runtime_operation_risk_labels": unique_list(
                edgeenv_runtime_operation.get("risk_labels", [])
            ),
            "comparability_role": "supplemental_evidence_not_gate",
            "lab_report_marker": LAB_EDGEENV_PRESERVATION_MARKER,
            "preservation_identity_label": first_value(
                lab,
                [
                    (
                        "agent_runtime_summary",
                        "edgeenv_preservation_context",
                        "preservation_identity_label",
                    ),
                    ("edgeenv_preservation_context", "preservation_identity_label"),
                ],
                edgeenv_preservation_identity_label(
                    run_summary,
                    operation,
                    edgeenv.get("run_id", "unknown"),
                ),
            ),
            "preservation_details_label": first_value(
                lab,
                [
                    (
                        "agent_runtime_summary",
                        "edgeenv_preservation_context",
                        "preservation_details_label",
                    ),
                    ("edgeenv_preservation_context", "preservation_details_label"),
                ],
                edgeenv_preservation_details_label(run_summary),
            ),
            "lab_report_preservation_section_present": (
                LAB_EDGEENV_PRESERVATION_MARKER in lab_markdown
            ),
            "lab_report_preservation_context_present": bool(lab_edgeenv_context),
            "lab_report_preservation_run_id": first_value(
                lab,
                [
                    ("edgeenv_preservation_context", "run_id"),
                    ("agent_runtime_summary", "edgeenv_preservation_context", "run_id"),
                ],
                "unknown",
            ),
            "lab_report_decision_owner": first_value(
                lab,
                [
                    ("edgeenv_preservation_context", "decision_owner"),
                    (
                        "agent_runtime_summary",
                        "edgeenv_preservation_context",
                        "runtime_operation_decision_owner",
                    ),
                ],
                "lab",
            ),
        }

    return {
        "schema_version": "inferedge-agent-runtime-evidence-index-v1",
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "output_dir": str(output_dir),
        "files": files,
        "run_summary": run_summary,
        "operation_path": operation,
        "guard_summary": guard_summary,
        "decision_summary": decision_summary,
        "remote_summary": remote_summary,
        "edgeenv_summary": edgeenv_summary,
        "notes": [
            "This index is a navigation aid for generated evidence files.",
            "It does not replace the source JSON contracts or Lab-owned deployment decision.",
            "Missing values are reported as unknown so partially generated bundles remain inspectable.",
        ],
    }


def md_value(value: Any) -> str:
    if value is None:
        return "unknown"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else "none"
    return str(value)


def edgeenv_preservation_identity_label(
    run_summary: dict[str, Any],
    operation: str,
    run_id: Any,
) -> str:
    identity = (
        "jetson_device_local_preservation"
        if operation == "device_local_starter"
        else "edgeenv_runtime_operation_preservation"
    )
    parts = [f"identity={identity}"]
    if operation not in (None, "", "unknown"):
        parts.append(f"path={operation}")
    if run_id not in (None, "", "unknown"):
        parts.append(f"run={run_id}")
    return ", ".join(parts)


def edgeenv_preservation_details_label(run_summary: dict[str, Any]) -> str:
    sources = unique_list(run_summary.get("producer_sources") or [])
    stages = unique_list(run_summary.get("producer_stages") or [])
    resources: list[str] = []
    for source in sources:
        if source in {"process_resource_snapshot", "resource_snapshot_fixture"}:
            resources.append(source)
        if "tegrastats" in source:
            resources.append(source)
    tegrastats_count = run_summary.get("tegrastats_sample_count")
    if tegrastats_count not in (None, "", "unknown", 0, "0"):
        resources.append("tegrastats_timeline")
    return ", ".join(
        [
            f"sources={label_list(sources)}",
            f"stages={label_list(stages)}",
            f"device_local_events={md_value(run_summary.get('device_local_event_count'))}",
            f"resource={label_list(unique_list(resources))}",
            f"queue={md_value(run_summary.get('queue_pressure_reason'))}",
        ]
    )


def label_list(values: list[str]) -> str:
    return "+".join(values) if values else "none"


def write_markdown(index: dict[str, Any], path: Path) -> None:
    run = index["run_summary"]
    operation = index.get("operation_path", "unknown")
    guard = index["guard_summary"]
    decision = index["decision_summary"]
    remote = index["remote_summary"]
    edgeenv = index["edgeenv_summary"]

    lines = [
        "# Agent Runtime Evidence Index",
        "",
        "This index is a navigation aid for the generated Agent Runtime e2e evidence bundle.",
        "The source JSON contracts and the Lab report remain the authoritative evidence.",
        "",
        "## Evidence Files",
        "",
        "| Key | File | Status | Description |",
        "|---|---|---|---|",
    ]

    for item in index["files"]:
        status = "present" if item["exists"] else "missing"
        lines.append(
            f"| `{item['key']}` | `{item['path']}` | {status} | {item['description']} |"
        )

    lines.extend(
        [
            "",
            "## Reviewer Duration Label",
            "",
            "| Row | Value |",
            "|---|---|",
            f"| Duration label | {md_value(run['duration_label'])} |",
            f"| Duration class | {md_value(run['duration_class'])} |",
            f"| Frames | {md_value(run['frames'])} |",
            f"| Operation path | {md_value(operation)} |",
            "",
            "## Run Summary",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| operation_path | {md_value(operation)} |",
            f"| scenario_label | {md_value(run['scenario_label'])} |",
            f"| scenario_category | {md_value(run['scenario_category'])} |",
            f"| scenario_description | {md_value(run['scenario_description'])} |",
            f"| scenario_mode | {md_value(run['scenario_mode'])} |",
            f"| frames | {md_value(run['frames'])} |",
            f"| duration_class | {md_value(run['duration_class'])} |",
            f"| duration_label | {md_value(run['duration_label'])} |",
            f"| executed_count | {md_value(run['executed_count'])} |",
            f"| dropped_count | {md_value(run['dropped_count'])} |",
            f"| fallback_count | {md_value(run['fallback_count'])} |",
            f"| deadline_missed_count | {md_value(run['deadline_missed_count'])} |",
            f"| max_total_queue_depth | {md_value(run['max_total_queue_depth'])} |",
            f"| policy_decision_count | {md_value(run['policy_decision_count'])} |",
            f"| timeline_sample_count | {md_value(run['timeline_sample_count'])} |",
            f"| tegrastats_sample_count | {md_value(run['tegrastats_sample_count'])} |",
            f"| producer_sources | {md_value(run['producer_sources'])} |",
            f"| producer_source_count | {md_value(run['producer_source_count'])} |",
            f"| device_local_producer_count | {md_value(run['device_local_producer_count'])} |",
            f"| producer_stages | {md_value(run['producer_stages'])} |",
            f"| queue_pressure_reason | {md_value(run['queue_pressure_reason'])} |",
            f"| max_pressure_task | {md_value(run['max_pressure_task'])} |",
            f"| device_local_event_count | {md_value(run['device_local_event_count'])} |",
            f"| producer_event_count | {md_value(run['producer_event_count'])} |",
            f"| runtime_operation_health_reason | {md_value(run['runtime_operation_health_reason'])} |",
            f"| runtime_operation_recommended_action | {md_value(run['runtime_operation_recommended_action'])} |",
            f"| runtime_operation_risk_labels | {md_value(run['runtime_operation_risk_labels'])} |",
            f"| runtime_operation_evidence_gaps | {md_value(run['runtime_operation_evidence_gaps'])} |",
            "",
            "## Guard And Decision",
            "",
            "| Field | Value |",
            "|---|---|",
            f"| guard_verdict | {md_value(guard['guard_verdict'])} |",
            f"| severity | {md_value(guard['severity'])} |",
            f"| confidence | {md_value(guard['confidence'])} |",
            f"| primary_reason | {md_value(guard['primary_reason'])} |",
            f"| evidence_types | {md_value(guard['evidence_types'])} |",
            f"| Lab decision | {md_value(decision['decision'])} |",
            f"| Lab reason | {md_value(decision['reason'])} |",
            f"| triggered_rules | {md_value(decision['triggered_rules'])} |",
        ]
    )

    if remote:
        lines.extend(
            [
                "",
                "## Remote Dispatch Starter",
                "",
                "| Field | Value |",
                "|---|---|",
                f"| dispatch_status | {md_value(remote['dispatch_status'])} |",
                f"| selected_worker_id | {md_value(remote['selected_worker_id'])} |",
                f"| decision_reason | {md_value(remote['decision_reason'])} |",
                f"| execution_requested | {md_value(remote['execution_requested'])} |",
                f"| network_execution_performed | {md_value(remote['network_execution_performed'])} |",
                f"| remote_execution_status | {md_value(remote['remote_execution_status'])} |",
                f"| remote_error_category | {md_value(remote['remote_error_category'])} |",
                f"| fallback_worker_id | {md_value(remote['fallback_worker_id'])} |",
                f"| fallback_final_status | {md_value(remote['fallback_final_status'])} |",
                f"| final_status | {md_value(remote['final_status'])} |",
                f"| production_remote_execution | {md_value(remote['production_remote_execution'])} |",
                f"| remote_event_count | {md_value(remote['remote_event_count'])} |",
                f"| remote_runtime_event_count | {md_value(remote['remote_runtime_event_count'])} |",
                f"| remote_event_summary_role | {md_value(remote['remote_event_summary_role'])} |",
                f"| operation_boundary | {md_value(remote['operation_boundary'])} |",
                f"| downstream_aiguard_evidence_type | {md_value(remote['downstream_aiguard_evidence_type'])} |",
                f"| downstream_lab_report_context | {md_value(remote['downstream_lab_report_context'])} |",
            ]
        )

    if edgeenv:
        lines.extend(
            [
                "",
                "## EdgeEnv Runtime Operation Evidence",
                "",
                "| Field | Value |",
                "|---|---|",
                f"| run_id | {md_value(edgeenv['run_id'])} |",
                f"| result_path | {md_value(edgeenv['result_path'])} |",
                f"| result_schema_version | {md_value(edgeenv['result_schema_version'])} |",
                f"| has_runtime_operation_summary | {md_value(edgeenv['has_runtime_operation_summary'])} |",
                f"| runtime_operation_schema_version | {md_value(edgeenv['runtime_operation_schema_version'])} |",
                f"| runtime_operation_health_reason | {md_value(edgeenv['runtime_operation_health_reason'])} |",
                f"| runtime_operation_recommended_action | {md_value(edgeenv['runtime_operation_recommended_action'])} |",
                f"| runtime_operation_risk_labels | {md_value(edgeenv['runtime_operation_risk_labels'])} |",
                f"| comparability_role | {md_value(edgeenv['comparability_role'])} |",
                f"| lab_report_marker | {md_value(edgeenv['lab_report_marker'])} |",
                f"| preservation_identity | {md_value(edgeenv['preservation_identity_label'])} |",
                f"| preservation_details | {md_value(edgeenv['preservation_details_label'])} |",
                f"| lab_report_preservation_section_present | {md_value(edgeenv['lab_report_preservation_section_present'])} |",
                f"| lab_report_preservation_context_present | {md_value(edgeenv['lab_report_preservation_context_present'])} |",
                f"| lab_report_preservation_run_id | {md_value(edgeenv['lab_report_preservation_run_id'])} |",
                f"| lab_report_decision_owner | {md_value(edgeenv['lab_report_decision_owner'])} |",
            ]
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- The index is intentionally small and derived from generated evidence.",
            "- Treat `05_lab_agent_runtime_report.md` as the human-readable decision context.",
            "- Treat `03_orchestration_summary.json`, `04_aiguard_guard_analysis.json`, and `05_lab_agent_runtime_report.json` as the main machine-readable contracts.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a navigation index for an InferEdge Agent Runtime e2e evidence bundle."
    )
    parser.add_argument("--output-dir", required=True, help="Evidence bundle directory")
    parser.add_argument(
        "--json-output",
        default="00_evidence_index.json",
        help="JSON index filename inside output-dir",
    )
    parser.add_argument(
        "--markdown-output",
        default="00_evidence_index.md",
        help="Markdown index filename inside output-dir",
    )
    parser.add_argument(
        "--requested-frames",
        help="Frame count requested by the entrypoint script, when available",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    index = build_summary(output_dir, requested_frames=args.requested_frames)

    json_path = output_dir / args.json_output
    markdown_path = output_dir / args.markdown_output
    json_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(index, markdown_path)
    print(f"wrote {json_path}")
    print(f"wrote {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
