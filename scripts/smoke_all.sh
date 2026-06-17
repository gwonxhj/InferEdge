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

require_artifact() {
  local file="$1"
  if [[ ! -f "$file" ]]; then
    echo "missing required artifact: $file" >&2
    exit 1
  fi
}

require_artifacts() {
  local file
  for file in "$@"; do
    require_artifact "$file"
  done
}

require_markers() {
  local file="$1"
  shift
  local marker
  for marker in "$@"; do
    require_marker "$file" "$marker"
  done
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
  local runtime_intelligence_required_artifacts=(
    "$bundle_summary"
    "$RUNTIME_INTELLIGENCE_SMOKE_OUT/edgeenv_runtime_regression.md"
    "$RUNTIME_INTELLIGENCE_SMOKE_OUT/edgeenv_runtime_regression.html"
    "$summary_md"
    "$summary_html"
    "$gate_summary"
    "$ci_summary"
    "$RUNTIME_INTELLIGENCE_SMOKE_OUT/aiguard_edgeenv_handoff_alignment.json"
    "$RUNTIME_INTELLIGENCE_SMOKE_OUT/aiguard_edgeenv_handoff_alignment.md"
  )
  local runtime_report_gate_markers=(
    "Validated Duration Traceability"
    "duration_handoff_alignment: EdgeEnv/AIGuard report context preserved"
    "duration_source: source=entrypoint_requested_frames"
    "duration_scope_label: scope_label=source=entrypoint_requested_frames"
    "duration_label: short 96-frame-class replay (96 frames)"
    "Validated Reviewer Focus"
    "reviewer_focus_operation_quick_scan: Reviewer Focus / Operation quick scan marker validated"
    "reviewer_focus_operation_quick_scan_raw_marker: raw marker preserved in Lab report"
    "Validated Review Path"
    "review_path_section: short Review Path section rendered"
    "review_path_fast_path: readable Review Path fast path rendered"
    "review_path: Reviewer Focus -> Detailed Evidence Rows guidance validated"
    "review_path_scope: comparable regression / telemetry replay / operation evidence preserved"
    "review_path_artifact_gate_summary: artifact gate summary reference row validated"
  )
  local runtime_summary_common_markers=(
    "Jetson/device-local EdgeEnv preservation run"
    "Jetson/device-local EdgeEnv preservation details"
    "identity=jetson_device_local_preservation"
    "path=device_local_starter"
    "sources=device_local_cli_override"
    "Runtime replay duration scope"
    "short 96-frame-class replay (96 frames)"
    "source=entrypoint_requested_frames"
    "scope_label=source=entrypoint_requested_frames"
    "Orchestrator queue/deadline/fallback markers"
    "Operation quick scan"
    "Reviewer operation quick scan"
    "raw_marker=reviewer_focus_operation_quick_scan"
    "queue_pressure_reason=queue_backlog_threshold_exceeded"
    "max_total_queue_depth=7"
    "deadline_missed_count=2"
    "fallback_count=1"
    "preservation=identity=jetson_device_local_preservation"
    "Remote fallback starter evidence"
    "lab=Remote fallback starter evidence; evidence=remote_execution_recovered_by_fallback"
  )

  require_artifacts "${runtime_intelligence_required_artifacts[@]}"
  require_marker "$bundle_summary" "expected_report_markers: remote fallback Lab context row declared"
  require_marker "$bundle_summary" "aiguard_raw_context: max_total_queue_depth traceability preserved"
  require_marker "$bundle_summary" "reviewer_path_gate: README/ecosystem reviewer path gate context declared"
  require_marker "$bundle_summary" "reviewer_path_local_links: local reviewer path link gate context preserved"
  require_marker "$bundle_summary" "reviewer_path_anchor_fragments: reviewer path anchor gate context preserved"
  require_markers "$gate_summary" "${runtime_report_gate_markers[@]}"
  require_markers "$ci_summary" "${runtime_report_gate_markers[@]}"
  require_markers "$summary_md" "${runtime_summary_common_markers[@]}"
  require_marker "$summary_md" "class=short_96_frame_class, frames=96"
  require_marker "$summary_md" "remote_execution_recovered_by_fallback"
  require_markers "$summary_html" "${runtime_summary_common_markers[@]}"
}

require_agent_runtime_edgeenv_markers() {
  local lab_md="$AGENT_RUNTIME_EDGEENV_SMOKE_OUT/05_lab_agent_runtime_report.md"
  local index_json="$AGENT_RUNTIME_EDGEENV_SMOKE_OUT/00_evidence_index.json"
  local index_md="$AGENT_RUNTIME_EDGEENV_SMOKE_OUT/00_evidence_index.md"
  local agent_edgeenv_lab_markers=(
    "Runtime Intelligence EdgeEnv Preservation"
    "preservation_identity"
    "preservation_details"
    "identity=jetson_device_local_preservation"
    "path=device_local_starter"
    "Queue pressure reasons:"
    "queue_pressure_reason"
    "queue_backlog_threshold_exceeded"
    "fallback_count"
    "deadline_missed_count"
    "max_total_queue_depth"
  )
  local agent_edgeenv_index_common_markers=(
    "identity=jetson_device_local_preservation"
    "fallback_count"
    "deadline_missed_count"
    "max_total_queue_depth"
    "queue_pressure_reason"
    "duration_class"
    "quick_starter_smoke"
    "duration_label"
    "quick starter smoke (8 frames)"
    "duration_source"
    "entrypoint_requested_frames"
    "duration_scope_label"
    "source=entrypoint_requested_frames"
    "lab_report_operation_quick_scan_focus_marker"
    "Operation quick scan"
    "lab_report_operation_quick_scan_marker"
    "Reviewer operation quick scan"
    "lab_report_operation_quick_scan_raw_marker"
    "lab_report_operation_quick_scan_raw_marker_label"
    "raw_marker=reviewer_focus_operation_quick_scan"
    "lab_report_operation_quick_scan_label"
    "edgeenv_runtime_operation_summary_label"
    "operation_summary: mode=timeout_threshold_exceeded"
    "operation_summary_label"
    "lab_report_operation_summary_label"
    "operation_summary: mode=device_local_starter"
    "lab_expected_report_markers"
    "lab_report_contract_context"
    "aiguard_validates_expected_report_markers"
  )
  local agent_edgeenv_index_json_markers=(
    "preservation_identity_label"
    "preservation_details_label"
    "queue_backlog_threshold_exceeded"
  )
  local agent_edgeenv_index_md_markers=(
    "preservation_identity"
    "preservation_details"
    "Runtime operation summary"
    "queue=queue_backlog_threshold_exceeded"
    "Reviewer Duration Label"
    "Duration label"
    "Duration class"
    "Duration source"
    "Duration scope label"
  )

  require_markers "$lab_md" "${agent_edgeenv_lab_markers[@]}"
  require_markers "$index_json" "${agent_edgeenv_index_common_markers[@]}"
  require_markers "$index_json" "${agent_edgeenv_index_json_markers[@]}"
  require_markers "$index_md" "${agent_edgeenv_index_common_markers[@]}"
  require_markers "$index_md" "${agent_edgeenv_index_md_markers[@]}"
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
