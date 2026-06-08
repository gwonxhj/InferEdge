#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
OUTPUT_DIR="${INFEREDGE_QUICK_SCAN_REGISTRY_SMOKE_OUT:-/tmp/inferedge_quick_scan_registry_summary_smoke}"

usage() {
  cat <<'USAGE'
Usage: bash scripts/smoke_quick_scan_registry_summary.sh [--output-dir DIR]

Build a fixture-only device-local EdgeEnv preservation bundle and verify that
the generated run registry renders Operation Quick Scan Summary before the
wide run table. This is reviewer navigation evidence only; it is not a live
Jetson run, Lab report ownership transfer, or production operation proof.

Options:
  --output-dir DIR  Directory for generated smoke artifacts.

Environment:
  INFEREDGE_QUICK_SCAN_REGISTRY_SMOKE_OUT
                    Default output directory when --output-dir is omitted.
  PYTHON_BIN        Python executable. Default: python3.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir)
      OUTPUT_DIR="${2:?missing value for --output-dir}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

BUNDLE_DIR="$OUTPUT_DIR/quick_scan_device_local_bundle"
mkdir -p "$BUNDLE_DIR"

"$PYTHON_BIN" - "$BUNDLE_DIR" <<'PY'
import json
import sys
from pathlib import Path

bundle_dir = Path(sys.argv[1])


def write_json(name: str, payload: dict) -> None:
    (bundle_dir / name).write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


write_json(
    "02_runtime_result_agent.json",
    {
        "schema_version": "inferedge-runtime-result-v1",
        "runtime_operation_summary": {
            "schema_version": "inferedge-runtime-operation-summary-v1",
            "health_reason": "timeout_threshold_exceeded",
            "recommended_action": "review_latency_budget_or_degrade",
            "risk_labels": [
                "runtime_timeout_observed",
                "latency_budget_exceeded",
            ],
            "evidence_gaps": ["thermal_memory_evidence_missing"],
        },
    },
)

write_json(
    "03_orchestration_summary.json",
    {
        "multi_workload_sustained_summary": {
            "schema_version": "inferedge-agent-runtime-sustained-summary-v1",
            "scenario_label": "device_local_quick_scan_fixture",
            "scenario_category": "device_local",
            "scenario_description": "Fixture-only quick-scan registry smoke",
            "scenario_mode": "device_local",
            "observed_runtime_signals": {
                "executed_count": 99,
                "dropped_count": 93,
                "fallback_count": 93,
                "deadline_missed_count": 50,
                "max_total_queue_depth": 6,
                "producer_sources": [
                    "process_resource_snapshot",
                    "image_file",
                    "fastapi_request_fixture",
                ],
                "producer_source_count": 99,
                "device_local_producer_count": 99,
                "policy_decision_count": 99,
                "tegrastats_sample_count": 9,
            },
            "workload_profiles": [
                {
                    "agent_id": "vision_agent",
                    "producer_stage": "device_local_cli_override",
                },
                {
                    "agent_id": "voice_command_agent",
                    "producer_stage": "device_local_starter",
                },
                {
                    "agent_id": "safety_monitor_agent",
                    "producer_stage": "device_local_cli_override",
                },
            ],
        },
        "queue_state_summary": {
            "queue_pressure_reason": "queue_backlog_threshold_exceeded",
            "max_total_queue_depth": 6,
            "max_pressure_task": "vision_agent",
            "sample_count": 9,
        },
        "runtime_event_summary": {
            "device_local_event_count": 99,
            "producer_event_count": 99,
        },
        "operation_risk_summary": {
            "schema_version": "inferedge-entrypoint-operation-risk-summary-v1",
            "queue_pressure_reason": "queue_backlog_threshold_exceeded",
            "max_pressure_task": "vision_agent",
            "device_local_event_count": 99,
            "producer_event_count": 99,
            "not_a_deployment_decision": True,
        },
    },
)

write_json(
    "04_aiguard_guard_analysis.json",
    {
        "guard_verdict": "blocked",
        "severity": "high",
        "confidence": 0.91,
        "primary_reason": "runtime_queue_overload",
        "evidence": [
            {
                "type": "runtime_queue_overload",
                "status": "warning",
            }
        ],
    },
)

preservation_identity = (
    "identity=jetson_device_local_preservation, "
    "path=device_local_starter, run=run-quick-scan-registry-smoke"
)
preservation_details = (
    "sources=process_resource_snapshot+image_file+fastapi_request_fixture, "
    "stages=device_local_cli_override+device_local_starter, "
    "device_local_events=99, resource=process_resource_snapshot, "
    "queue=queue_backlog_threshold_exceeded"
)

write_json(
    "05_lab_agent_runtime_report.json",
    {
        "agent_deployment_decision": {
            "decision": "blocked",
            "reason": "sustained_overload_review",
            "triggered_rules": ["sustained_overload_review"],
        },
        "agent_runtime_summary": {
            "edgeenv_preservation_context": {
                "run_id": "run-quick-scan-registry-smoke",
                "decision_owner": "lab",
                "runtime_operation_decision_owner": "lab",
                "preservation_identity_label": preservation_identity,
                "preservation_details_label": preservation_details,
            }
        },
    },
)

(bundle_dir / "05_lab_agent_runtime_report.md").write_text(
    "# Lab Agent Runtime Reliability Report\n\n"
    "## Runtime Intelligence EdgeEnv Preservation\n\n"
    "| Field | Value |\n"
    "|---|---|\n"
    f"| preservation_identity | {preservation_identity} |\n"
    f"| preservation_details | {preservation_details} |\n"
    "| decision_owner | lab |\n",
    encoding="utf-8",
)

write_json(
    "08_edgeenv_result.json",
    {
        "schema_version": "inferedge-runtime-result-v1",
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

write_json(
    "08_edgeenv_run_show.json",
    {
        "schema_version": "inferedge-edgeenv-run-show-v1",
        "run_id": "run-quick-scan-registry-smoke",
        "result_path": str(bundle_dir / "08_edgeenv_result.json"),
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
PY

"$PYTHON_BIN" "$ROOT_DIR/scripts/build_agent_runtime_evidence_index.py" \
  --output-dir "$BUNDLE_DIR" \
  --requested-frames 96

"$PYTHON_BIN" "$ROOT_DIR/scripts/build_agent_runtime_run_registry.py" \
  --run-dir "$BUNDLE_DIR" \
  --output-json "$OUTPUT_DIR/agent_runtime_quick_scan_registry.json" \
  --output-md "$OUTPUT_DIR/agent_runtime_quick_scan_registry.md"

grep -q "Reviewer operation quick scan" "$BUNDLE_DIR/00_evidence_index.md"
grep -q "lab_expected_report_markers" "$BUNDLE_DIR/00_evidence_index.md"
grep -q "lab_report_contract_context" "$BUNDLE_DIR/00_evidence_index.md"
grep -q "aiguard_validates_expected_report_markers" "$BUNDLE_DIR/00_evidence_index.md"
grep -q "## Operation Quick Scan Summary" "$OUTPUT_DIR/agent_runtime_quick_scan_registry.md"
grep -q "Reviewer operation quick scan:" "$OUTPUT_DIR/agent_runtime_quick_scan_registry.md"
grep -q "queue_pressure_reason=queue_backlog_threshold_exceeded" "$OUTPUT_DIR/agent_runtime_quick_scan_registry.md"
grep -q "max_total_queue_depth=6" "$OUTPUT_DIR/agent_runtime_quick_scan_registry.md"
grep -q "deadline_missed_count=50" "$OUTPUT_DIR/agent_runtime_quick_scan_registry.md"
grep -q "fallback_count=93" "$OUTPUT_DIR/agent_runtime_quick_scan_registry.md"
grep -q "reviewer navigation metadata" "$OUTPUT_DIR/agent_runtime_quick_scan_registry.md"
grep -q "does not make the registry a Lab report owner" "$OUTPUT_DIR/agent_runtime_quick_scan_registry.md"

"$PYTHON_BIN" - "$OUTPUT_DIR/agent_runtime_quick_scan_registry.md" <<'PY'
import sys
from pathlib import Path

markdown = Path(sys.argv[1]).read_text(encoding="utf-8")
summary = markdown.index("## Operation Quick Scan Summary")
runs = markdown.index("## Runs")
if summary >= runs:
    raise SystemExit("Operation Quick Scan Summary must appear before ## Runs")
PY

echo "Quick-scan registry summary smoke: pass"
echo "Registry Markdown: $OUTPUT_DIR/agent_runtime_quick_scan_registry.md"
grep -m1 "Operation Quick Scan Summary" "$OUTPUT_DIR/agent_runtime_quick_scan_registry.md"
grep -m1 "Reviewer operation quick scan:" "$OUTPUT_DIR/agent_runtime_quick_scan_registry.md"
