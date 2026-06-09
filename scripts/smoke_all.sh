#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPOS_ROOT="${INFEREDGE_REPOS_DIR:-$ROOT_DIR/repos}"
FULL=0

usage() {
  cat <<'USAGE'
Usage: bash scripts/smoke_all.sh [--full]

Run InferEdge cross-repo portfolio smoke checks.

Default checks:
  - Forge pytest + manifest validation
  - Runtime smoke + manifest identity test
  - Lab portfolio demo check + Core 4 conformance check
  - Agent Runtime EdgeEnv preservation identity/details smoke
  - EdgeEnv regression replay fixture matrix gate
  - Lab Runtime Intelligence artifact smoke
  - AIGuard pytest + portfolio demo

Options:
  --full  Also run the full InferEdgeLab pytest suite.

Environment:
  INFEREDGE_REPOS_DIR  Override repository directory root.
  INFEREDGE_RUNTIME_INTELLIGENCE_SMOKE_OUT
                       Override Runtime Intelligence smoke output directory.
  INFEREDGE_REMOTE_FALLBACK_REGISTRY_SMOKE_OUT
                       Override fixture-only remote fallback registry smoke output directory.
  INFEREDGE_QUICK_SCAN_REGISTRY_SMOKE_OUT
                       Override fixture-only operation quick-scan registry smoke output directory.
  INFEREDGE_AGENT_RUNTIME_EDGEENV_SMOKE_OUT
                       Override Agent Runtime EdgeEnv preservation smoke output directory.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --full) FULL=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage; exit 2 ;;
  esac
  shift
done

require_repo() {
  local name="$1"
  local path="$REPOS_ROOT/$name"
  if [[ ! -d "$path/.git" ]]; then
    echo "missing repo: $path" >&2
    echo "run: bash scripts/clone_all.sh --locked" >&2
    exit 1
  fi
  printf '%s\n' "$path"
}

run_step() {
  local label="$1"
  shift
  echo
  echo "==> $label"
  "$@"
}

require_marker() {
  local file="$1"
  local marker="$2"
  if [[ ! -f "$file" ]]; then
    echo "missing required artifact: $file" >&2
    exit 1
  fi
  if ! grep -qF "$marker" "$file"; then
    echo "missing required marker in $file: $marker" >&2
    exit 1
  fi
}

require_edgeenv_regression_fixture_matrix() {
  local matrix="$ENV_REPO/examples/regression/fixture_matrix.json"
  if [[ ! -f "$matrix" ]]; then
    echo "missing EdgeEnv regression fixture matrix: $matrix" >&2
    exit 1
  fi
  python3 - "$matrix" <<'PY'
import json
import sys
from pathlib import Path

matrix_path = Path(sys.argv[1])
matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
root = matrix_path.parent


def fail(message: str) -> None:
    raise SystemExit(f"EdgeEnv regression fixture matrix gate failed: {message}")


required_boundaries = {
    "not_a_deployment_decision": True,
    "not_a_guard_analysis": True,
    "not_production_monitoring": True,
    "comparability_first": True,
}
required_roles = {
    "same_condition_regression",
    "runtime_comparison_blocked",
    "target_comparison_blocked",
    "protocol_mismatch_blocked",
    "telemetry_gap_same_condition",
    "replay_sequence_context",
}
delta_keys = {
    "mean_delta_pct",
    "p95_delta_pct",
    "p99_delta_pct",
    "fps_delta_pct",
    "memory_peak_delta_pct",
}

if matrix.get("schema_version") != "edgeenv-regression-replay-fixture-matrix-v1":
    fail("unexpected schema_version")
if matrix.get("owner") != "edgeenv":
    fail("owner must be edgeenv")
if matrix.get("boundaries") != required_boundaries:
    fail("boundary flags changed")
if set(matrix.get("required_roles", [])) != required_roles:
    fail("required_roles coverage changed")

fixtures = matrix.get("fixtures")
if not isinstance(fixtures, list):
    fail("fixtures must be a list")
if {entry.get("role") for entry in fixtures} != required_roles:
    fail("fixture roles do not cover required roles exactly")

seen_modes = set()
for entry in fixtures:
    path = root / entry["path"]
    if not path.is_file():
        fail(f"missing fixture report: {entry['path']}")
    report = json.loads(path.read_text(encoding="utf-8"))
    seen_modes.add(entry["mode"])
    if "guard_analysis" in report or "deployment_decision" in report:
        fail(f"{entry['path']} must stay EdgeEnv-owned")
    if report.get("mode") != entry["mode"]:
        fail(f"{entry['path']} mode mismatch")
    if report.get("comparable") is not entry["comparable"]:
        fail(f"{entry['path']} comparable mismatch")
    if report.get("regression_detected") is not entry["expected_regression_detected"]:
        fail(f"{entry['path']} regression_detected mismatch")
    if report.get("recommendation") != entry["expected_recommendation"]:
        fail(f"{entry['path']} recommendation mismatch")

    evidence = report.get("evidence", {})
    if entry["regression_delta_allowed"]:
        if not delta_keys <= set(evidence):
            fail(f"{entry['path']} must preserve same-condition deltas")
    elif delta_keys & set(evidence):
        fail(f"{entry['path']} must suppress regression deltas")

    context = report.get("runtime_telemetry_context")
    if entry["requires_runtime_telemetry_context"]:
        if not isinstance(context, dict):
            fail(f"{entry['path']} missing runtime telemetry context")
        notes = context.get("notes", [])
        if not any("not a comparability gate" in note for note in notes):
            fail(f"{entry['path']} missing comparability boundary note")
    elif context is not None:
        fail(f"{entry['path']} should not require telemetry context")

    if entry["requires_history_seed_run_config"]:
        summary = context["history"]["summary"]
        if summary.get("history_seed_run_config_runs") != 2:
            fail(f"{entry['path']} missing history seed run_config coverage")

    if entry["telemetry_gap_expected"]:
        observed = {gap["reason"] for gap in context.get("evidence_gaps", [])}
        expected = set(entry.get("expected_evidence_gaps", []))
        if not expected <= observed:
            fail(f"{entry['path']} telemetry gap mismatch")

    if entry.get("sequence_context") == "inverted":
        baseline_sequence = context["baseline"]["execution_sequence_id"]
        candidate_sequence = context["candidate"]["execution_sequence_id"]
        if baseline_sequence <= candidate_sequence:
            fail(f"{entry['path']} sequence context is not inverted")

if not {"same-condition", "runtime-comparison", "target-comparison", "protocol_mismatch"} <= seen_modes:
    fail("mode coverage is incomplete")

print("EdgeEnv regression fixture matrix gate passed")
PY
}

require_runtime_intelligence_report_markers() {
  local bundle_summary="$RUNTIME_INTELLIGENCE_SMOKE_OUT/runtime_intelligence_bundle_manifest_gate_summary.md"
  local gate_summary="$RUNTIME_INTELLIGENCE_SMOKE_OUT/runtime_anomaly_gate_summary.md"
  local ci_summary="$RUNTIME_INTELLIGENCE_SMOKE_OUT/runtime_intelligence_ci_artifact_gate_summary.md"
  local summary_md="$RUNTIME_INTELLIGENCE_SMOKE_OUT/runtime_anomaly_summary.md"
  local summary_html="$RUNTIME_INTELLIGENCE_SMOKE_OUT/runtime_anomaly_summary.html"

  require_marker "$bundle_summary" "expected_report_markers: remote fallback Lab context row declared"
  require_marker "$bundle_summary" "aiguard_raw_context: max_total_queue_depth traceability preserved"
  require_marker "$gate_summary" "Validated Duration Traceability"
  require_marker "$gate_summary" "duration_handoff_alignment: EdgeEnv/AIGuard report context preserved"
  require_marker "$gate_summary" "duration_source: source=entrypoint_requested_frames"
  require_marker "$gate_summary" "duration_scope_label: scope_label=source=entrypoint_requested_frames"
  require_marker "$gate_summary" "duration_label: short 96-frame-class replay (96 frames)"
  require_marker "$gate_summary" "Validated Reviewer Focus"
  require_marker "$gate_summary" "reviewer_focus_operation_quick_scan: Reviewer Focus / Operation quick scan marker validated"
  require_marker "$gate_summary" "reviewer_focus_operation_quick_scan_raw_marker: raw marker preserved in Lab report"
  require_marker "$gate_summary" "Validated Review Path"
  require_marker "$gate_summary" "review_path_section: short Review Path section rendered"
  require_marker "$gate_summary" "review_path_fast_path: readable Review Path fast path rendered"
  require_marker "$gate_summary" "review_path: Reviewer Focus -> Detailed Evidence Rows guidance validated"
  require_marker "$gate_summary" "review_path_scope: comparable regression / telemetry replay / operation evidence preserved"
  require_marker "$ci_summary" "Validated Duration Traceability"
  require_marker "$ci_summary" "duration_handoff_alignment: EdgeEnv/AIGuard report context preserved"
  require_marker "$ci_summary" "duration_source: source=entrypoint_requested_frames"
  require_marker "$ci_summary" "duration_scope_label: scope_label=source=entrypoint_requested_frames"
  require_marker "$ci_summary" "duration_label: short 96-frame-class replay (96 frames)"
  require_marker "$ci_summary" "Validated Reviewer Focus"
  require_marker "$ci_summary" "reviewer_focus_operation_quick_scan: Reviewer Focus / Operation quick scan marker validated"
  require_marker "$ci_summary" "reviewer_focus_operation_quick_scan_raw_marker: raw marker preserved in Lab report"
  require_marker "$ci_summary" "Validated Review Path"
  require_marker "$ci_summary" "review_path_section: short Review Path section rendered"
  require_marker "$ci_summary" "review_path_fast_path: readable Review Path fast path rendered"
  require_marker "$ci_summary" "review_path: Reviewer Focus -> Detailed Evidence Rows guidance validated"
  require_marker "$ci_summary" "review_path_scope: comparable regression / telemetry replay / operation evidence preserved"
  require_marker "$summary_md" "Jetson/device-local EdgeEnv preservation run"
  require_marker "$summary_md" "Jetson/device-local EdgeEnv preservation details"
  require_marker "$summary_md" "identity=jetson_device_local_preservation"
  require_marker "$summary_md" "path=device_local_starter"
  require_marker "$summary_md" "sources=device_local_cli_override"
  require_marker "$summary_md" "Runtime replay duration scope"
  require_marker "$summary_md" "short 96-frame-class replay (96 frames)"
  require_marker "$summary_md" "class=short_96_frame_class, frames=96"
  require_marker "$summary_md" "source=entrypoint_requested_frames"
  require_marker "$summary_md" "scope_label=source=entrypoint_requested_frames"
  require_marker "$summary_md" "Orchestrator queue/deadline/fallback markers"
  require_marker "$summary_md" "Operation quick scan"
  require_marker "$summary_md" "Reviewer operation quick scan"
  require_marker "$summary_md" "raw_marker=reviewer_focus_operation_quick_scan"
  require_marker "$summary_md" "queue_pressure_reason=queue_backlog_threshold_exceeded"
  require_marker "$summary_md" "max_total_queue_depth=7"
  require_marker "$summary_md" "deadline_missed_count=2"
  require_marker "$summary_md" "fallback_count=1"
  require_marker "$summary_md" "preservation=identity=jetson_device_local_preservation"
  require_marker "$summary_md" "Remote fallback starter evidence"
  require_marker "$summary_md" "lab=Remote fallback starter evidence; evidence=remote_execution_recovered_by_fallback"
  require_marker "$summary_md" "remote_execution_recovered_by_fallback"
  require_marker "$summary_html" "Jetson/device-local EdgeEnv preservation run"
  require_marker "$summary_html" "Jetson/device-local EdgeEnv preservation details"
  require_marker "$summary_html" "identity=jetson_device_local_preservation"
  require_marker "$summary_html" "path=device_local_starter"
  require_marker "$summary_html" "sources=device_local_cli_override"
  require_marker "$summary_html" "Runtime replay duration scope"
  require_marker "$summary_html" "short 96-frame-class replay (96 frames)"
  require_marker "$summary_html" "source=entrypoint_requested_frames"
  require_marker "$summary_html" "scope_label=source=entrypoint_requested_frames"
  require_marker "$summary_html" "Orchestrator queue/deadline/fallback markers"
  require_marker "$summary_html" "Operation quick scan"
  require_marker "$summary_html" "Reviewer operation quick scan"
  require_marker "$summary_html" "raw_marker=reviewer_focus_operation_quick_scan"
  require_marker "$summary_html" "queue_pressure_reason=queue_backlog_threshold_exceeded"
  require_marker "$summary_html" "max_total_queue_depth=7"
  require_marker "$summary_html" "deadline_missed_count=2"
  require_marker "$summary_html" "fallback_count=1"
  require_marker "$summary_html" "preservation=identity=jetson_device_local_preservation"
  require_marker "$summary_html" "Remote fallback starter evidence"
  require_marker "$summary_html" "lab=Remote fallback starter evidence; evidence=remote_execution_recovered_by_fallback"
}

require_agent_runtime_edgeenv_markers() {
  local lab_md="$AGENT_RUNTIME_EDGEENV_SMOKE_OUT/05_lab_agent_runtime_report.md"
  local index_json="$AGENT_RUNTIME_EDGEENV_SMOKE_OUT/00_evidence_index.json"
  local index_md="$AGENT_RUNTIME_EDGEENV_SMOKE_OUT/00_evidence_index.md"

  require_marker "$lab_md" "Runtime Intelligence EdgeEnv Preservation"
  require_marker "$lab_md" "preservation_identity"
  require_marker "$lab_md" "preservation_details"
  require_marker "$lab_md" "identity=jetson_device_local_preservation"
  require_marker "$lab_md" "path=device_local_starter"
  require_marker "$lab_md" "Queue pressure reasons:"
  require_marker "$lab_md" "queue_pressure_reason"
  require_marker "$lab_md" "queue_backlog_threshold_exceeded"
  require_marker "$lab_md" "fallback_count"
  require_marker "$lab_md" "deadline_missed_count"
  require_marker "$lab_md" "max_total_queue_depth"
  require_marker "$index_json" "preservation_identity_label"
  require_marker "$index_json" "preservation_details_label"
  require_marker "$index_json" "identity=jetson_device_local_preservation"
  require_marker "$index_json" "fallback_count"
  require_marker "$index_json" "deadline_missed_count"
  require_marker "$index_json" "max_total_queue_depth"
  require_marker "$index_json" "queue_pressure_reason"
  require_marker "$index_json" "queue_backlog_threshold_exceeded"
  require_marker "$index_json" "duration_class"
  require_marker "$index_json" "quick_starter_smoke"
  require_marker "$index_json" "duration_label"
  require_marker "$index_json" "quick starter smoke (8 frames)"
  require_marker "$index_json" "duration_source"
  require_marker "$index_json" "entrypoint_requested_frames"
  require_marker "$index_json" "duration_scope_label"
  require_marker "$index_json" "source=entrypoint_requested_frames"
  require_marker "$index_json" "lab_report_operation_quick_scan_focus_marker"
  require_marker "$index_json" "Operation quick scan"
  require_marker "$index_json" "lab_report_operation_quick_scan_marker"
  require_marker "$index_json" "Reviewer operation quick scan"
  require_marker "$index_json" "lab_report_operation_quick_scan_raw_marker"
  require_marker "$index_json" "raw_marker=reviewer_focus_operation_quick_scan"
  require_marker "$index_json" "lab_report_operation_quick_scan_label"
  require_marker "$index_json" "lab_expected_report_markers"
  require_marker "$index_json" "lab_report_contract_context"
  require_marker "$index_json" "aiguard_validates_expected_report_markers"
  require_marker "$index_md" "preservation_identity"
  require_marker "$index_md" "preservation_details"
  require_marker "$index_md" "Runtime operation summary"
  require_marker "$index_md" "fallback_count"
  require_marker "$index_md" "deadline_missed_count"
  require_marker "$index_md" "max_total_queue_depth"
  require_marker "$index_md" "queue_pressure_reason"
  require_marker "$index_md" "queue=queue_backlog_threshold_exceeded"
  require_marker "$index_md" "Reviewer Duration Label"
  require_marker "$index_md" "Duration label"
  require_marker "$index_md" "Duration class"
  require_marker "$index_md" "Duration source"
  require_marker "$index_md" "Duration scope label"
  require_marker "$index_md" "duration_class"
  require_marker "$index_md" "quick_starter_smoke"
  require_marker "$index_md" "duration_label"
  require_marker "$index_md" "quick starter smoke (8 frames)"
  require_marker "$index_md" "duration_source"
  require_marker "$index_md" "entrypoint_requested_frames"
  require_marker "$index_md" "duration_scope_label"
  require_marker "$index_md" "source=entrypoint_requested_frames"
  require_marker "$index_md" "lab_report_operation_quick_scan_focus_marker"
  require_marker "$index_md" "Operation quick scan"
  require_marker "$index_md" "lab_report_operation_quick_scan_marker"
  require_marker "$index_md" "Reviewer operation quick scan"
  require_marker "$index_md" "lab_report_operation_quick_scan_raw_marker"
  require_marker "$index_md" "raw_marker=reviewer_focus_operation_quick_scan"
  require_marker "$index_md" "lab_report_operation_quick_scan_label"
  require_marker "$index_md" "lab_expected_report_markers"
  require_marker "$index_md" "lab_report_contract_context"
  require_marker "$index_md" "aiguard_validates_expected_report_markers"
}

FORGE="$(require_repo InferEdgeForge)"
RUNTIME="$(require_repo InferEdge-Runtime)"
LAB="$(require_repo InferEdgeLab)"
AIGUARD="$(require_repo InferEdgeAIGuard)"
ORCHESTRATOR="$(require_repo InferEdgeOrchestrator)"
ENV_REPO="$(require_repo InferEdgeEnv)"
RUNTIME_INTELLIGENCE_SMOKE_OUT="${INFEREDGE_RUNTIME_INTELLIGENCE_SMOKE_OUT:-/tmp/inferedge_runtime_intelligence_chain_smoke}"
REMOTE_FALLBACK_REGISTRY_SMOKE_OUT="${INFEREDGE_REMOTE_FALLBACK_REGISTRY_SMOKE_OUT:-/tmp/inferedge_remote_fallback_registry_marker_smoke}"
QUICK_SCAN_REGISTRY_SMOKE_OUT="${INFEREDGE_QUICK_SCAN_REGISTRY_SMOKE_OUT:-/tmp/inferedge_quick_scan_registry_summary_smoke}"
AGENT_RUNTIME_EDGEENV_SMOKE_OUT="${INFEREDGE_AGENT_RUNTIME_EDGEENV_SMOKE_OUT:-/tmp/inferedge_agent_runtime_edgeenv_preservation_smoke}"

run_step "Remote fallback registry marker smoke" bash "$ROOT_DIR/scripts/smoke_remote_fallback_registry_marker.sh" --output-dir "$REMOTE_FALLBACK_REGISTRY_SMOKE_OUT"
run_step "Operation quick-scan registry summary smoke" bash "$ROOT_DIR/scripts/smoke_quick_scan_registry_summary.sh" --output-dir "$QUICK_SCAN_REGISTRY_SMOKE_OUT"

run_step "Forge tests" bash -lc "cd '$FORGE' && poetry run pytest -q"
run_step "Forge manifest validation" bash -lc "cd '$FORGE' && poetry run python -m inferedgeforge.cli validate-manifest --manifest tests/fixtures/runtime_handoff_manifest.json"

run_step "Runtime smoke" bash -lc "cd '$RUNTIME' && bash scripts/smoke_default.sh"
run_step "Runtime manifest identity" bash -lc "cd '$RUNTIME' && python3 tests/test_manifest_compare_identity.py"

run_step "Lab install" bash -lc "cd '$LAB' && poetry install --no-interaction"
run_step "Lab portfolio demo check" bash -lc "cd '$LAB' && poetry run inferedgelab portfolio-demo-check"
run_step "Lab Core 4 conformance check" bash -lc "cd '$LAB' && poetry run inferedgelab core4-conformance-check"
run_step "Agent Runtime EdgeEnv preservation identity/details smoke" bash "$ROOT_DIR/scripts/demo_agent_runtime_e2e.sh" --device-local --edgeenv-run-evidence --output-dir "$AGENT_RUNTIME_EDGEENV_SMOKE_OUT"
run_step "Agent Runtime EdgeEnv preservation marker gate" require_agent_runtime_edgeenv_markers
run_step "EdgeEnv regression replay fixture matrix gate" require_edgeenv_regression_fixture_matrix
run_step "Lab Runtime Intelligence artifact smoke" bash -lc "cd '$LAB' && bash scripts/smoke_runtime_intelligence_chain.sh --output-dir '$RUNTIME_INTELLIGENCE_SMOKE_OUT'"
run_step "Lab Runtime Intelligence report marker gate" require_runtime_intelligence_report_markers
if [[ "$FULL" -eq 1 ]]; then
  run_step "Lab full pytest" bash -lc "cd '$LAB' && poetry run python3 -m pytest -q"
fi

run_step "AIGuard tests" bash -lc "cd '$AIGUARD' && python -m pytest -q -p no:cacheprovider"
run_step "AIGuard portfolio demo" bash -lc "cd '$AIGUARD' && python -m inferedge_aiguard.cli portfolio-demo --save-json /tmp/aiguard_portfolio_demo.json --save-md /tmp/aiguard_portfolio_demo.md"

echo
echo "InferEdge cross-repo smoke: pass"
