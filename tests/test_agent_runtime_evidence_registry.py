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


def test_cross_repo_smoke_runs_runtime_intelligence_artifact_gate() -> None:
    smoke_script = (ROOT / "scripts" / "smoke_all.sh").read_text(
        encoding="utf-8"
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "Lab Runtime Intelligence artifact smoke" in smoke_script
    assert "scripts/smoke_runtime_intelligence_chain.sh --output-dir" in smoke_script
    assert "INFEREDGE_RUNTIME_INTELLIGENCE_SMOKE_OUT" in smoke_script
    assert "Agent Runtime EdgeEnv preservation identity/details smoke" in smoke_script
    assert "INFEREDGE_AGENT_RUNTIME_EDGEENV_SMOKE_OUT" in smoke_script
    assert "demo_agent_runtime_e2e.sh\" --device-local --edgeenv-run-evidence" in smoke_script
    assert "Agent Runtime EdgeEnv preservation marker gate" in smoke_script
    assert "preservation_identity_label" in smoke_script
    assert "preservation_details_label" in smoke_script
    assert "Lab Runtime Intelligence report marker gate" in smoke_script
    assert "runtime_intelligence_bundle_manifest_gate_summary.md" in smoke_script
    assert "expected_report_markers: remote fallback Lab context row declared" in smoke_script
    assert "runtime_anomaly_summary.md" in smoke_script
    assert "runtime_anomaly_summary.html" in smoke_script
    assert "Jetson/device-local EdgeEnv preservation run" in smoke_script
    assert "Jetson/device-local EdgeEnv preservation details" in smoke_script
    assert "identity=jetson_device_local_preservation" in smoke_script
    assert "path=device_local_starter" in smoke_script
    assert "sources=device_local_cli_override" in smoke_script
    assert "lab=Remote fallback starter evidence; evidence=remote_execution_recovered_by_fallback" in smoke_script
    assert "smoke_remote_fallback_registry_marker.sh" in smoke_script
    assert "INFEREDGE_REMOTE_FALLBACK_REGISTRY_SMOKE_OUT" in smoke_script
    assert "Lab's local-first Runtime Intelligence artifact" in readme
    assert "remote-dispatch boundary rows" in readme


def test_remote_fallback_registry_marker_smoke_is_fixture_only() -> None:
    script = (ROOT / "scripts" / "smoke_remote_fallback_registry_marker.sh").read_text(
        encoding="utf-8"
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    portfolio = (ROOT / "docs" / "portfolio_summary.md").read_text(
        encoding="utf-8"
    )
    demo_doc = (ROOT / "docs" / "agent_runtime_e2e_demo.md").read_text(
        encoding="utf-8"
    )

    assert "fixture-only remote fallback evidence bundle" in script
    assert "build_agent_runtime_evidence_index.py" in script
    assert "build_agent_runtime_run_registry.py" in script
    assert "remote_execution_recovered_by_fallback" in script
    assert "lab=Remote fallback starter evidence" in script
    assert "production_remote_execution=False" in script
    assert "local HTTP fallback worker" in readme
    for text in (portfolio, demo_doc):
        assert "smoke_remote_fallback_registry_marker.sh" in text
        assert "lab=Remote fallback starter evidence" in text


def test_jetson_readiness_preflight_is_not_evidence() -> None:
    script = (ROOT / "scripts" / "check_jetson_sustained_readiness.sh").read_text(
        encoding="utf-8"
    )
    runner = (ROOT / "scripts" / "demo_jetson_5min_sustained.sh").read_text(
        encoding="utf-8"
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    demo_doc = (ROOT / "docs" / "agent_runtime_e2e_demo.md").read_text(
        encoding="utf-8"
    )

    assert "ssh" in script
    assert "ConnectTimeout" in script
    assert "tegrastats=available" in script
    assert "clean_forge_repo=available" in script
    assert "vision_onnx_model=available" in script
    assert "edgeenv_repo=available" in script
    assert "edgeenv_cli=available" in script
    assert "miniconda3/envs/yolo_env/bin/python" in script
    assert "--edgeenv-run-evidence" in script
    assert "This preflight does not create evidence" in script
    assert "INFEREDGE_ENV_REPO" in runner
    assert "--edgeenv-run-evidence" in runner
    for text in (readme, demo_doc):
        assert "check_jetson_sustained_readiness.sh" in text
        assert "does not" in text
        assert "new evidence" in text
        assert "--edgeenv-run-evidence" in text


def test_entrypoint_lab_report_can_use_local_lab_module() -> None:
    script = (ROOT / "scripts" / "demo_agent_runtime_e2e.sh").read_text(
        encoding="utf-8"
    )
    demo_doc = (ROOT / "docs" / "agent_runtime_e2e_demo.md").read_text(
        encoding="utf-8"
    )

    assert "PYTHONPATH=\"$LAB_REPO${PYTHONPATH:+:$PYTHONPATH}\"" in script
    assert "-m inferedgelab.cli" in script
    assert "--edgeenv-run-show" in script
    assert "Runtime Intelligence EdgeEnv Preservation" in script
    assert "python -m inferedgelab.cli" in demo_doc


def test_runtime_intelligence_status_preserves_local_first_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    portfolio = (ROOT / "docs" / "portfolio_summary.md").read_text(
        encoding="utf-8"
    )

    for text in (readme, portfolio):
        assert "Runtime Intelligence artifact gate" in text
        assert "Cross-repo smoke" in text
        assert "Orchestrator -> EdgeEnv -> AIGuard -> Lab" in text
        assert "Lab EdgeEnv preservation context" in text
        assert "lab_report_preservation_context_present=True" in text
        assert "lab_preservation=present" in text
        assert "identity=jetson_device_local_preservation" in text
        assert "path=device_local_starter" in text
        assert "Remote fallback starter evidence" in text
        assert "lab=Remote fallback starter evidence" in text
        assert "directly gated Jetson preservation and remote fallback Lab markers" in text

    assert "Production observability platform or GitLab control plane" in readme
    assert "production control plane" in portfolio
    for text in (readme, portfolio):
        assert "lab_expected_report_markers" in text
        assert "lab_report_contract_context" in text
        assert "aiguard_validates_expected_report_markers=false" in text


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
            "operation_risk_summary": {
                "schema_version": "inferedge-entrypoint-operation-risk-summary-v1",
                "queue_pressure_reason": (
                    "max_total_queue_depth_exceeded_overload_threshold"
                ),
                "max_pressure_task": "vision_agent",
                "primary_health_reason": "worker_health_degraded",
                "device_local_event_count": 7,
                "producer_event_count": 7,
                "not_a_deployment_decision": True,
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
            "agent_runtime_summary": {
                "edgeenv_preservation_context": {
                    "run_id": "run-edgeenv-runtime-operation",
                    "runtime_operation_decision_owner": "lab",
                    "comparability_role": "supplemental_evidence_not_gate",
                }
            },
            "agent_deployment_decision": {
                "decision": "blocked",
                "triggered_rules": ["sustained_overload_review"],
            }
        },
    )
    (tmp_path / "05_lab_agent_runtime_report.md").write_text(
        "\n".join(
            [
                "# Agent Runtime Reliability Report",
                "",
                "## Runtime Intelligence EdgeEnv Preservation",
                "",
                "| Field | Value |",
                "|---|---|",
                "| edgeenv_run_id | run-edgeenv-runtime-operation |",
                "| comparability_role | supplemental_evidence_not_gate |",
                "",
            ]
        ),
        encoding="utf-8",
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
    assert edgeenv_summary["lab_report_marker"] == (
        "Runtime Intelligence EdgeEnv Preservation"
    )
    assert edgeenv_summary["lab_report_preservation_section_present"] is True
    assert edgeenv_summary["lab_report_preservation_context_present"] is True
    assert edgeenv_summary["lab_report_preservation_run_id"] == (
        "run-edgeenv-runtime-operation"
    )
    assert edgeenv_summary["lab_report_decision_owner"] == "lab"
    assert edgeenv_summary["preservation_identity_label"] == (
        "identity=jetson_device_local_preservation, "
        "path=device_local_starter, run=run-edgeenv-runtime-operation"
    )
    assert edgeenv_summary["preservation_details_label"] == (
        "sources=resource_snapshot_fixture+image_file+fastapi_request_fixture, "
        "stages=device_local_cli_override, device_local_events=7, "
        "resource=resource_snapshot_fixture+tegrastats_timeline, "
        "queue=max_total_queue_depth_exceeded_overload_threshold"
    )

    md_path = tmp_path / "00_evidence_index.md"
    index_module.write_markdown(index, md_path)
    markdown = md_path.read_text(encoding="utf-8")
    assert "lab_report_marker" in markdown
    assert "Runtime Intelligence EdgeEnv Preservation" in markdown
    assert "preservation_identity" in markdown
    assert "identity=jetson_device_local_preservation" in markdown
    assert "preservation_details" in markdown
    assert "sources=resource_snapshot_fixture+image_file+fastapi_request_fixture" in markdown
    assert "lab_report_preservation_section_present" in markdown
    assert "lab_report_preservation_run_id" in markdown


def test_evidence_index_uses_derived_operation_risk_summary(tmp_path: Path) -> None:
    index_module = load_script_module(
        "build_agent_runtime_evidence_index_operation_risk",
        "scripts/build_agent_runtime_evidence_index.py",
    )
    write_json(
        tmp_path / "03_orchestration_summary.json",
        {
            "multi_workload_sustained_summary": {
                "scenario_mode": "device_local",
                "observed_runtime_signals": {
                    "device_local_producer_count": 9,
                    "producer_source_count": 9,
                },
            },
            "operation_risk_summary": {
                "schema_version": "inferedge-entrypoint-operation-risk-summary-v1",
                "queue_pressure_reason": "queue_backlog_threshold_exceeded",
                "max_pressure_task": "vision_agent",
                "device_local_event_count": 9,
                "producer_event_count": 9,
                "not_a_deployment_decision": True,
            },
        },
    )

    index = index_module.build_summary(tmp_path, requested_frames="9")
    run_summary = index["run_summary"]

    assert run_summary["queue_pressure_reason"] == "queue_backlog_threshold_exceeded"
    assert run_summary["max_pressure_task"] == "vision_agent"
    assert run_summary["device_local_event_count"] == 9
    assert run_summary["producer_event_count"] == 9


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
                "lab_report_marker": "Runtime Intelligence EdgeEnv Preservation",
                "preservation_identity_label": (
                    "identity=jetson_device_local_preservation, "
                    "path=device_local_starter, run=run-edgeenv-runtime-operation"
                ),
                "preservation_details_label": (
                    "sources=image_file+fastapi_request_fixture+resource_snapshot_fixture, "
                    "stages=device_local_cli_override, device_local_events=7, "
                    "resource=resource_snapshot_fixture+tegrastats_timeline, "
                    "queue=max_total_queue_depth_exceeded_overload_threshold"
                ),
                "lab_report_preservation_section_present": True,
                "lab_report_preservation_context_present": True,
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
    assert run["edgeenv_lab_report_marker"] == (
        "Runtime Intelligence EdgeEnv Preservation"
    )
    assert run["edgeenv_preservation_identity_label"] == (
        "identity=jetson_device_local_preservation, "
        "path=device_local_starter, run=run-edgeenv-runtime-operation"
    )
    assert run["edgeenv_preservation_details_label"].startswith(
        "sources=image_file+fastapi_request_fixture+resource_snapshot_fixture"
    )
    assert run["edgeenv_lab_preservation_section_present"] is True
    assert run["edgeenv_lab_preservation_context_present"] is True

    md_path = tmp_path / "agent_runtime_registry.md"
    registry_module.write_markdown(registry, md_path)
    markdown = md_path.read_text(encoding="utf-8")
    assert "lab_preservation=present" in markdown
    assert "lab_context=present" in markdown
    assert "identity=jetson_device_local_preservation" in markdown
    assert "sources=image_file+fastapi_request_fixture+resource_snapshot_fixture" in markdown


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


def test_evidence_index_derives_remote_dispatch_lab_context_from_outputs(
    tmp_path: Path,
) -> None:
    index_module = load_script_module(
        "build_agent_runtime_evidence_index_remote_lab_context",
        "scripts/build_agent_runtime_evidence_index.py",
    )
    write_json(
        tmp_path / "06_remote_dispatch_result.json",
        {
            "dispatch_summary": {
                "dispatch_status": "accepted",
                "selected_worker_id": "primary-http-worker",
            },
            "remote_execution_result": {
                "execution_requested": True,
                "execution_performed": True,
                "production_remote_execution": False,
                "status": "failed",
                "error_category": "connection_error",
            },
            "fallback_execution_result": {
                "final_status": "succeeded",
                "production_remote_execution": False,
            },
            "remote_runtime_event_summary": {
                "event_count": 4,
                "runtime_event_count": 4,
                "production_remote_execution": False,
                "evidence_role": "remote_dispatch_runtime_event_compact_summary",
                "operation_boundary": "remote dispatch starter evidence only",
            },
        },
    )
    write_json(
        tmp_path / "07_remote_dispatch_guard_analysis.json",
        {
            "evidence": [
                {"type": "remote_execution_failed"},
                {"type": "remote_execution_recovered_by_fallback"},
            ],
        },
    )
    (tmp_path / "05_lab_agent_runtime_report.md").write_text(
        "Remote fallback starter evidence:\n",
        encoding="utf-8",
    )

    index = index_module.build_summary(tmp_path)
    remote = index["remote_summary"]

    assert remote["downstream_aiguard_evidence_type"] == (
        "remote_execution_recovered_by_fallback"
    )
    assert remote["downstream_lab_report_context"] == (
        "Remote fallback starter evidence"
    )

    md_path = tmp_path / "00_evidence_index.md"
    index_module.write_markdown(index, md_path)
    markdown = md_path.read_text(encoding="utf-8")
    assert "remote_execution_recovered_by_fallback" in markdown
    assert "Remote fallback starter evidence" in markdown


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

    md_path = tmp_path / "agent_runtime_registry.md"
    registry_module.write_markdown(registry, md_path)
    markdown = md_path.read_text(encoding="utf-8")
    assert "lab=Remote fallback starter evidence" in markdown
