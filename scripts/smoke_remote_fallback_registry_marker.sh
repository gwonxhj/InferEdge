#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
OUTPUT_DIR="${INFEREDGE_REMOTE_FALLBACK_REGISTRY_SMOKE_OUT:-/tmp/inferedge_remote_fallback_registry_marker_smoke}"

usage() {
  cat <<'USAGE'
Usage: bash scripts/smoke_remote_fallback_registry_marker.sh [--output-dir DIR]

Build a fixture-only remote fallback evidence bundle and verify that the
entrypoint evidence index plus run registry preserve the Lab-facing remote
fallback context without requiring a live HTTP worker.

Options:
  --output-dir DIR  Directory for generated smoke artifacts.

Environment:
  INFEREDGE_REMOTE_FALLBACK_REGISTRY_SMOKE_OUT
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

mkdir -p "$OUTPUT_DIR"

"$PYTHON_BIN" - "$OUTPUT_DIR" <<'PY'
import json
import sys
from pathlib import Path

output_dir = Path(sys.argv[1])

def write_json(name: str, payload: dict) -> None:
    (output_dir / name).write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )

write_json(
    "06_remote_dispatch_result.json",
    {
        "schema_version": "inferedge-remote-dispatch-result-v1",
        "dispatch_summary": {
            "dispatch_status": "accepted",
            "selected_worker_id": "primary-http-worker",
            "decision_reason": "selected online worker matching backend/device requirements",
        },
        "remote_execution_result": {
            "schema_version": "inferedge-remote-execution-result-v1",
            "execution_requested": True,
            "execution_performed": True,
            "production_remote_execution": False,
            "status": "failed",
            "error_category": "connection_error",
            "selected_worker_id": "primary-http-worker",
        },
        "fallback_execution_result": {
            "schema_version": "inferedge-remote-fallback-execution-v1",
            "fallback_requested": True,
            "fallback_reason": "connection_error",
            "primary_worker_id": "primary-http-worker",
            "attempted_worker_ids": ["fallback-http-worker"],
            "final_status": "succeeded",
            "production_remote_execution": False,
        },
        "remote_runtime_event_summary": {
            "schema_version": "inferedge-remote-runtime-event-summary-v1",
            "event_count": 4,
            "runtime_event_count": 4,
            "final_status": "succeeded",
            "fallback_recovered": True,
            "production_remote_execution": False,
            "evidence_role": "remote_dispatch_runtime_event_compact_summary",
            "operation_boundary": "remote dispatch starter evidence only",
        },
    },
)

write_json(
    "07_remote_dispatch_guard_analysis.json",
    {
        "guard_verdict": "review_required",
        "severity": "medium",
        "confidence": 0.88,
        "evidence": [
            {"type": "remote_execution_failed", "status": "failed"},
            {
                "type": "remote_execution_recovered_by_fallback",
                "status": "warning",
            },
        ],
    },
)

(output_dir / "05_lab_agent_runtime_report.md").write_text(
    "# Lab Agent Runtime Reliability Report\n\n"
    "Remote fallback starter evidence:\n\n"
    "| Field | Value |\n"
    "|---|---|\n"
    "| final_status | succeeded |\n"
    "| production_remote_execution | False |\n",
    encoding="utf-8",
)
PY

"$PYTHON_BIN" "$ROOT_DIR/scripts/build_agent_runtime_evidence_index.py" \
  --output-dir "$OUTPUT_DIR" \
  --requested-frames 8

"$PYTHON_BIN" "$ROOT_DIR/scripts/build_agent_runtime_run_registry.py" \
  --run-dir "$OUTPUT_DIR" \
  --output-json "$OUTPUT_DIR/agent_runtime_registry.json" \
  --output-md "$OUTPUT_DIR/agent_runtime_registry.md"

grep -q '"evidence_index_boundary"' "$OUTPUT_DIR/00_evidence_index.json"
grep -q '"role": "reviewer_navigation_metadata"' "$OUTPUT_DIR/00_evidence_index.json"
grep -q '"lab_report_owner": false' "$OUTPUT_DIR/00_evidence_index.json"
grep -q '"source_contract": false' "$OUTPUT_DIR/00_evidence_index.json"
grep -q '"deployment_decision_owner": false' "$OUTPUT_DIR/00_evidence_index.json"
grep -q '"evidence_index_boundary_summary"' "$OUTPUT_DIR/agent_runtime_registry.json"
grep -q '"all_runs_match": true' "$OUTPUT_DIR/agent_runtime_registry.json"
grep -q '"evidence_index_boundary"' "$OUTPUT_DIR/agent_runtime_registry.json"
grep -q "remote_execution_recovered_by_fallback" "$OUTPUT_DIR/00_evidence_index.md"
grep -q "Remote fallback starter evidence" "$OUTPUT_DIR/00_evidence_index.md"
grep -q "Duration source" "$OUTPUT_DIR/00_evidence_index.md"
grep -q "Duration scope label" "$OUTPUT_DIR/00_evidence_index.md"
grep -q "source=entrypoint_requested_frames" "$OUTPUT_DIR/00_evidence_index.md"
grep -q "reviewer navigation context" "$OUTPUT_DIR/00_evidence_index.md"
grep -q "do not make the index a Lab report owner" "$OUTPUT_DIR/00_evidence_index.md"
grep -q "not a Lab report owner or source contract" "$OUTPUT_DIR/00_evidence_index.md"
grep -q "not as a new source contract" "$OUTPUT_DIR/00_evidence_index.md"
grep -q "Duration Sources" "$OUTPUT_DIR/agent_runtime_registry.md"
grep -q "Evidence index boundary: role=reviewer_navigation_metadata" "$OUTPUT_DIR/agent_runtime_registry.md"
grep -q "lab_report_owner=False" "$OUTPUT_DIR/agent_runtime_registry.md"
grep -q "source_contract=False" "$OUTPUT_DIR/agent_runtime_registry.md"
grep -q "entrypoint_requested_frames" "$OUTPUT_DIR/agent_runtime_registry.md"
grep -q "aiguard=remote_execution_recovered_by_fallback" "$OUTPUT_DIR/agent_runtime_registry.md"
grep -q "lab=Remote fallback starter evidence" "$OUTPUT_DIR/agent_runtime_registry.md"
grep -q "boundary=remote dispatch starter evidence only" "$OUTPUT_DIR/agent_runtime_registry.md"
grep -q "production_remote_execution=False" "$OUTPUT_DIR/agent_runtime_registry.md"

echo "Remote fallback registry marker smoke: pass"
echo "Output: $OUTPUT_DIR"
