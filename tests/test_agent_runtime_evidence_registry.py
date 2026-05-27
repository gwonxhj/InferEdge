from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_evidence_index_preserves_device_local_override_producers(tmp_path: Path) -> None:
    index_module = load_script_module(
        "build_agent_runtime_evidence_index",
        "scripts/build_agent_runtime_evidence_index.py",
    )
    write_json(
        tmp_path / "02_runtime_result_agent.json",
        {
            "runtime_operation_summary": {
                "schema_version": "inferedge-runtime-operation-summary-v1",
                "health_reason": "timeout_threshold_exceeded",
                "recommended_action": "review_latency_budget_or_degrade",
                "risk_labels": [
                    "runtime_timeout_observed",
                    "latency_budget_exceeded",
                ],
                "evidence_gaps": ["thermal_memory_evidence_missing"],
            }
        },
    )
    write_json(
        tmp_path / "03_orchestration_summary.json",
        {
            "multi_workload_sustained_summary": {
                "scenario_label": "device_local_sustained_starter",
                "scenario_category": "device_local",
                "scenario_description": "Device-local starter",
                "scenario_mode": "device_local",
                "observed_runtime_signals": {
                    "executed_count": 7,
                    "dropped_count": 1,
                    "fallback_count": 1,
                    "deadline_missed_count": 0,
                    "max_total_queue_depth": 5,
                    "policy_decision_count": 1,
                    "producer_source_count": 7,
                    "device_local_producer_count": 7,
                    "producer_sources": [
                        "resource_snapshot_fixture",
                        "image_file",
                        "fastapi_request_fixture",
                    ],
                    "tegrastats_sample_count": 1,
                },
                "workload_profiles": [
                    {
                        "agent_id": "vision_agent",
                        "producer_stage": "device_local_cli_override",
                    },
                    {
                        "agent_id": "voice_command_agent",
                        "producer_stage": "device_local_cli_override",
                    },
                ],
            },
            "queue_state_summary": {
                "queue_pressure_reason": (
                    "max_total_queue_depth_exceeded_overload_threshold"
                ),
                "max_pressure_task": "vision_agent",
            },
            "runtime_event_summary": {
                "device_local_event_count": 7,
                "producer_event_count": 7,
            },
        },
    )
    write_json(
        tmp_path / "04_aiguard_guard_analysis.json",
        {
            "guard_verdict": "blocked",
            "severity": "high",
            "evidence": [{"type": "profiled_workload_pressure"}],
        },
    )
    write_json(
        tmp_path / "05_lab_agent_runtime_report.json",
        {
            "agent_deployment_decision": {
                "decision": "blocked",
                "triggered_rules": ["sustained_overload_review"],
            }
        },
    )
    write_json(
        tmp_path / "08_edgeenv_run_show.json",
        {
            "schema_version": "edgeenv.result.v1",
            "run_id": "run-edgeenv-runtime-operation",
            "result_path": "/tmp/.edgeenv/runs/run-edgeenv-runtime-operation/result.json",
            "runtime_operation_summary": {
                "schema_version": "inferedge-runtime-operation-summary-v1",
                "health_reason": "timeout_threshold_exceeded",
                "recommended_action": "review_latency_budget_or_degrade",
                "risk_labels": [
                    "runtime_timeout_observed",
                    "latency_budget_exceeded",
                ],
            },
        },
    )

    index = index_module.build_summary(tmp_path, requested_frames="4")

    run_summary = index["run_summary"]
    edgeenv_summary = index["edgeenv_summary"]
    assert index["operation_path"] == "device_local_starter"
    assert run_summary["producer_sources"] == [
        "resource_snapshot_fixture",
        "image_file",
        "fastapi_request_fixture",
    ]
    assert run_summary["producer_source_count"] == 7
    assert run_summary["device_local_producer_count"] == 7
    assert run_summary["producer_stages"] == ["device_local_cli_override"]
    assert run_summary["queue_pressure_reason"] == (
        "max_total_queue_depth_exceeded_overload_threshold"
    )
    assert run_summary["max_pressure_task"] == "vision_agent"
    assert run_summary["device_local_event_count"] == 7
    assert run_summary["producer_event_count"] == 7
    assert run_summary["runtime_operation_health_reason"] == (
        "timeout_threshold_exceeded"
    )
    assert run_summary["runtime_operation_recommended_action"] == (
        "review_latency_budget_or_degrade"
    )
    assert run_summary["runtime_operation_risk_labels"] == [
        "runtime_timeout_observed",
        "latency_budget_exceeded",
    ]
    assert run_summary["runtime_operation_evidence_gaps"] == [
        "thermal_memory_evidence_missing"
    ]
    assert edgeenv_summary["run_id"] == "run-edgeenv-runtime-operation"
    assert edgeenv_summary["has_runtime_operation_summary"] is True
    assert edgeenv_summary["runtime_operation_schema_version"] == (
        "inferedge-runtime-operation-summary-v1"
    )
    assert edgeenv_summary["comparability_role"] == "supplemental_evidence_not_gate"


def test_run_registry_surfaces_device_local_override_producers(tmp_path: Path) -> None:
    registry_module = load_script_module(
        "build_agent_runtime_run_registry",
        "scripts/build_agent_runtime_run_registry.py",
    )
    run_dir = tmp_path / "device_local_override"
    run_dir.mkdir()
    write_json(
        run_dir / "00_evidence_index.json",
        {
            "operation_path": "device_local_starter",
            "run_summary": {
                "scenario_label": "device_local_sustained_starter",
                "scenario_category": "device_local",
                "scenario_description": "Device-local starter",
                "scenario_mode": "device_local",
                "frames": "4",
                "max_total_queue_depth": 5,
                "dropped_count": 1,
                "fallback_count": 1,
                "deadline_missed_count": 0,
                "tegrastats_sample_count": 1,
                "producer_sources": [
                    "image_file",
                    "fastapi_request_fixture",
                    "resource_snapshot_fixture",
                ],
                "producer_source_count": 7,
                "device_local_producer_count": 7,
                "device_local_event_count": 7,
                "producer_event_count": 7,
                "producer_stages": ["device_local_cli_override"],
                "runtime_operation_health_reason": "timeout_threshold_exceeded",
                "runtime_operation_recommended_action": (
                    "review_latency_budget_or_degrade"
                ),
                "runtime_operation_risk_labels": [
                    "runtime_timeout_observed",
                    "latency_budget_exceeded",
                ],
                "queue_pressure_reason": (
                    "max_total_queue_depth_exceeded_overload_threshold"
                ),
                "max_pressure_task": "vision_agent",
            },
            "guard_summary": {"guard_verdict": "blocked", "severity": "high"},
            "decision_summary": {
                "decision": "blocked",
                "triggered_rules": ["sustained_overload_review"],
            },
            "edgeenv_summary": {
                "run_id": "run-edgeenv-runtime-operation",
                "has_runtime_operation_summary": True,
                "runtime_operation_health_reason": "timeout_threshold_exceeded",
            },
        },
    )

    registry = registry_module.build_registry(
        [run_dir / "00_evidence_index.json"],
        output_base=tmp_path,
    )

    run = registry["runs"][0]
    assert run["producer_sources"] == [
        "image_file",
        "fastapi_request_fixture",
        "resource_snapshot_fixture",
    ]
    assert run["producer_source_count"] == 7
    assert run["device_local_producer_count"] == 7
    assert run["producer_stages"] == ["device_local_cli_override"]
    assert run["queue_pressure_reason"] == (
        "max_total_queue_depth_exceeded_overload_threshold"
    )
    assert run["max_pressure_task"] == "vision_agent"
    assert run["device_local_event_count"] == 7
    assert run["producer_event_count"] == 7
    assert run["runtime_operation_health_reason"] == "timeout_threshold_exceeded"
    assert run["runtime_operation_recommended_action"] == (
        "review_latency_budget_or_degrade"
    )
    assert run["runtime_operation_risk_labels"] == [
        "runtime_timeout_observed",
        "latency_budget_exceeded",
    ]
    assert run["edgeenv_run_id"] == "run-edgeenv-runtime-operation"
    assert run["edgeenv_has_runtime_operation_summary"] is True
    assert run["edgeenv_runtime_operation_health_reason"] == (
        "timeout_threshold_exceeded"
    )


def test_evidence_index_preserves_remote_dispatch_boundary(tmp_path: Path) -> None:
    index_module = load_script_module(
        "build_agent_runtime_evidence_index_remote_boundary",
        "scripts/build_agent_runtime_evidence_index.py",
    )
    write_json(
        tmp_path / "06_remote_dispatch_result.json",
        {
            "dispatch_summary": {
                "dispatch_status": "accepted",
                "selected_worker_id": "primary-http-worker",
                "decision_reason": "selected online worker",
            },
            "remote_execution_result": {
                "execution_requested": True,
                "execution_performed": False,
                "production_remote_execution": False,
                "transport": "http",
                "status": "failed",
                "error_category": "connection_error",
            },
            "fallback_execution_result": {
                "final_status": "succeeded",
                "attempts": [
                    {
                        "selected_worker_id": "fallback-http-worker",
                        "status": "succeeded",
                        "production_remote_execution": False,
                    }
                ],
            },
            "remote_operation_summary": {
                "execution_requested": True,
                "execution_performed": True,
                "remote_execution_status": "failed",
                "remote_error_category": "connection_error",
                "fallback_final_status": "succeeded",
                "final_status": "succeeded",
                "production_remote_execution": False,
                "evidence_role": (
                    "remote_worker_selection_and_starter_execution_evidence"
                ),
            },
            "remote_runtime_event_summary": {
                "event_count": 4,
                "runtime_event_count": 4,
                "production_remote_execution": False,
                "evidence_role": "remote_dispatch_runtime_event_compact_summary",
                "operation_boundary": "remote dispatch starter evidence only",
            },
            "downstream_expectation": {
                "aiguard_evidence_type": "remote_execution_recovered_by_fallback",
                "lab_report_context": "Remote fallback starter evidence",
            },
        },
    )

    index = index_module.build_summary(tmp_path)

    remote = index["remote_summary"]
    assert index["operation_path"] == "remote_dispatch_with_fallback"
    assert remote["dispatch_status"] == "accepted"
    assert remote["selected_worker_id"] == "primary-http-worker"
    assert remote["remote_execution_status"] == "failed"
    assert remote["remote_error_category"] == "connection_error"
    assert remote["fallback_final_status"] == "succeeded"
    assert remote["final_status"] == "succeeded"
    assert remote["production_remote_execution"] is False
    assert remote["remote_event_count"] == 4
    assert remote["remote_runtime_event_count"] == 4
    assert remote["remote_event_summary_role"] == (
        "remote_dispatch_runtime_event_compact_summary"
    )
    assert remote["operation_boundary"] == (
        "remote dispatch starter evidence only"
    )
    assert remote["downstream_aiguard_evidence_type"] == (
        "remote_execution_recovered_by_fallback"
    )
    assert remote["downstream_lab_report_context"] == (
        "Remote fallback starter evidence"
    )


def test_evidence_index_markdown_surfaces_remote_dispatch_boundary(
    tmp_path: Path,
) -> None:
    index_module = load_script_module(
        "build_agent_runtime_evidence_index_remote_boundary_md",
        "scripts/build_agent_runtime_evidence_index.py",
    )
    write_json(
        tmp_path / "06_remote_dispatch_result.json",
        {
            "dispatch_summary": {
                "dispatch_status": "accepted",
                "selected_worker_id": "primary-http-worker",
                "decision_reason": "selected online worker",
            },
            "remote_execution_result": {
                "execution_requested": True,
                "execution_performed": False,
                "production_remote_execution": False,
                "status": "failed",
            },
            "remote_runtime_event_summary": {
                "event_count": 2,
                "runtime_event_count": 2,
                "production_remote_execution": False,
                "evidence_role": "remote_dispatch_runtime_event_compact_summary",
                "operation_boundary": "remote dispatch starter evidence only",
            },
        },
    )

    index = index_module.build_summary(tmp_path)
    md_path = tmp_path / "00_evidence_index.md"
    index_module.write_markdown(index, md_path)
    markdown = md_path.read_text(encoding="utf-8")

    assert "remote_event_summary_role" in markdown
    assert "remote_dispatch_runtime_event_compact_summary" in markdown
    assert "operation_boundary" in markdown
    assert "remote dispatch starter evidence only" in markdown
    assert "production_remote_execution" in markdown


def test_run_registry_surfaces_remote_dispatch_boundary(tmp_path: Path) -> None:
    registry_module = load_script_module(
        "build_agent_runtime_run_registry_remote_boundary",
        "scripts/build_agent_runtime_run_registry.py",
    )
    run_dir = tmp_path / "remote_fallback"
    run_dir.mkdir()
    write_json(
        run_dir / "00_evidence_index.json",
        {
            "operation_path": "remote_dispatch_with_fallback",
            "run_summary": {
                "scenario_label": "remote_dispatch_fallback_starter",
            },
            "guard_summary": {
                "guard_verdict": "review_required",
                "severity": "medium",
            },
            "decision_summary": {
                "decision": "review",
                "triggered_rules": ["remote_fallback_starter_review"],
            },
            "remote_summary": {
                "dispatch_status": "accepted",
                "selected_worker_id": "primary-http-worker",
                "remote_execution_status": "failed",
                "fallback_final_status": "succeeded",
                "final_status": "succeeded",
                "production_remote_execution": False,
                "operation_boundary": "remote dispatch starter evidence only",
                "remote_event_summary_role": (
                    "remote_dispatch_runtime_event_compact_summary"
                ),
                "remote_event_count": 4,
                "remote_runtime_event_count": 4,
                "downstream_aiguard_evidence_type": (
                    "remote_execution_recovered_by_fallback"
                ),
                "downstream_lab_report_context": (
                    "Remote fallback starter evidence"
                ),
            },
        },
    )

    registry = registry_module.build_registry(
        [run_dir / "00_evidence_index.json"],
        output_base=tmp_path,
    )

    run = registry["runs"][0]
    assert run["operation_path"] == "remote_dispatch_with_fallback"
    assert run["remote_dispatch_status"] == "accepted"
    assert run["remote_selected_worker_id"] == "primary-http-worker"
    assert run["remote_execution_status"] == "failed"
    assert run["fallback_final_status"] == "succeeded"
    assert run["remote_final_status"] == "succeeded"
    assert run["remote_production_remote_execution"] is False
    assert run["remote_operation_boundary"] == (
        "remote dispatch starter evidence only"
    )
    assert run["remote_event_summary_role"] == (
        "remote_dispatch_runtime_event_compact_summary"
    )
    assert run["remote_event_count"] == 4
    assert run["remote_runtime_event_count"] == 4
    assert run["remote_downstream_aiguard_evidence_type"] == (
        "remote_execution_recovered_by_fallback"
    )
    assert run["remote_downstream_lab_report_context"] == (
        "Remote fallback starter evidence"
    )
