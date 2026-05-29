#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPOS_ROOT="${INFEREDGE_REPOS_DIR:-$ROOT_DIR/repos}"
OUTPUT_DIR="$ROOT_DIR/reports/agent_runtime_e2e"
FRAMES=8
SUSTAINED_MODE="producer-backed"
VISION_INPUT=""
VISION_ONNX_MODEL=""
VOICE_INGRESS_PAYLOAD=""
RESOURCE_SNAPSHOT=""
TEGRASTATS_LOG=""
GENERATE_VISION_DETECTOR_PROBE=0
CAPTURE_TEGRASTATS=0
CAPTURE_PROCESS_RESOURCE_SNAPSHOT=0
RUN_REMOTE_DISPATCH=0
RUN_REMOTE_EXECUTE_PLAN=0
REMOTE_EXECUTE_TIMEOUT_SEC=10.0
REMOTE_WORKER_REGISTRY=""
REMOTE_TASK_REQUEST=""
RUN_EDGEENV_EVIDENCE=0
VISION_PRODUCER_MARKER="image_file"
SAFETY_PRODUCER_MARKER="resource_snapshot_fixture"

usage() {
  cat <<'USAGE'
Usage: bash scripts/demo_agent_runtime_e2e.sh [--output-dir DIR] [--frames N] [--device-local]
                                             [--vision-input PATH]
                                             [--vision-onnx-model PATH]
                                             [--generate-vision-detector-probe]
                                             [--voice-ingress-payload PATH]
                                             [--resource-snapshot PATH]
                                             [--tegrastats-log PATH]
                                             [--capture-tegrastats]
                                             [--capture-process-resource-snapshot]
                                             [--remote-dispatch]
                                             [--remote-execute-plan]
                                             [--remote-timeout-sec SEC]
                                             [--remote-worker-registry PATH]
                                             [--remote-task-request PATH]
                                             [--edgeenv-run-evidence]

Replay the Reliable Edge Agent Runtime contract chain:

  agent_manifest
  -> runtime result.agent
  -> orchestration_summary
  -> AIGuard guard_analysis
  -> Lab agent-runtime-report

This script is an extension smoke for local developer workspaces. It does not
replace the Core 4 portfolio smoke in scripts/smoke_all.sh.

Options:
  --output-dir DIR  Directory for generated evidence.
                    Default: ./reports/agent_runtime_e2e
  --frames N        Number of frame cycles for the Orchestrator sustained demo.
                    Default: 8
  --device-local   Use the Orchestrator device_local starter config.
                    Default uses the producer-backed sustained smoke config.
  --vision-input PATH
                    Device-local override for the Vision producer input.
                    Requires --device-local.
  --vision-onnx-model PATH
                    Optional local ONNX model for the Vision producer probe.
                    Requires --device-local and Orchestrator ONNX dependencies.
  --generate-vision-detector-probe
                    Generate a tiny detector-like ONNX model under the output
                    directory and use it as the Vision producer probe.
                    Requires --device-local and Orchestrator ONNX dependencies.
                    Mutually exclusive with --vision-onnx-model.
  --voice-ingress-payload PATH
                    Device-local override for the Voice/FastAPI request payload.
                    Requires --device-local.
  --resource-snapshot PATH
                    Device-local override for the Safety resource snapshot.
                    Requires --device-local.
  --tegrastats-log PATH
                    Optional captured tegrastats log to route through the
                    Orchestrator sustained timeline. If omitted, the script
                    writes a small local tegrastats-style sample.
  --capture-tegrastats
                    Capture tegrastats during the Orchestrator sustained run
                    and route the captured log through the same evidence
                    bundle. Intended for Jetson device-local validation.
                    Mutually exclusive with --tegrastats-log.
  --capture-process-resource-snapshot
                    Capture a small local process resource snapshot for Safety.
                    Requires --device-local. Mutually exclusive with
                    --resource-snapshot.
  --remote-dispatch
                    Also run the Orchestrator file-based remote dispatch
                    starter and write 06_remote_dispatch_result.json.
  --remote-execute-plan
                    Explicitly ask Orchestrator to execute the selected
                    HTTP/SSH remote starter endpoint. Implies
                    --remote-dispatch. File-contract workers are recorded as
                    skipped starter evidence, not production remote execution.
  --remote-timeout-sec SEC
                    Timeout for explicit HTTP/SSH remote starter execution.
                    Default: 10.0. Implies --remote-dispatch.
  --remote-worker-registry PATH
                    Override the remote worker registry JSON.
                    Implies --remote-dispatch.
  --remote-task-request PATH
                    Override the remote task request JSON.
                    Implies --remote-dispatch.
  --edgeenv-run-evidence
                    Also preserve the Runtime operation summary through
                    InferEdgeEnv's local run registry contract. This writes
                    08_edgeenv_run_show.json and a local .edgeenv directory
                    under the output bundle.
  -h, --help        Show this help.

Environment:
  INFEREDGE_REPOS_DIR          Override ./repos lookup root.
  INFEREDGE_FORGE_REPO         Override InferEdgeForge path.
  INFEREDGE_RUNTIME_REPO       Override InferEdge-Runtime path.
  INFEREDGE_ORCHESTRATOR_REPO  Override InferEdgeOrchestrator path.
  INFEREDGE_AIGUARD_REPO       Override InferEdgeAIGuard path.
  INFEREDGE_LAB_REPO           Override InferEdgeLab path.
  INFEREDGE_ENV_REPO           Override InferEdgeEnv path.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir)
      OUTPUT_DIR="${2:?missing value for --output-dir}"
      shift 2
      ;;
    --frames)
      FRAMES="${2:?missing value for --frames}"
      shift 2
      ;;
    --device-local)
      SUSTAINED_MODE="device-local"
      shift
      ;;
    --vision-input)
      VISION_INPUT="${2:?missing value for --vision-input}"
      shift 2
      ;;
    --vision-onnx-model)
      VISION_ONNX_MODEL="${2:?missing value for --vision-onnx-model}"
      shift 2
      ;;
    --generate-vision-detector-probe)
      GENERATE_VISION_DETECTOR_PROBE=1
      shift
      ;;
    --voice-ingress-payload)
      VOICE_INGRESS_PAYLOAD="${2:?missing value for --voice-ingress-payload}"
      shift 2
      ;;
    --resource-snapshot)
      RESOURCE_SNAPSHOT="${2:?missing value for --resource-snapshot}"
      shift 2
      ;;
    --tegrastats-log)
      TEGRASTATS_LOG="${2:?missing value for --tegrastats-log}"
      shift 2
      ;;
    --capture-tegrastats)
      CAPTURE_TEGRASTATS=1
      shift
      ;;
    --capture-process-resource-snapshot)
      CAPTURE_PROCESS_RESOURCE_SNAPSHOT=1
      shift
      ;;
    --remote-dispatch)
      RUN_REMOTE_DISPATCH=1
      shift
      ;;
    --remote-execute-plan)
      RUN_REMOTE_DISPATCH=1
      RUN_REMOTE_EXECUTE_PLAN=1
      shift
      ;;
    --remote-timeout-sec)
      REMOTE_EXECUTE_TIMEOUT_SEC="${2:?missing value for --remote-timeout-sec}"
      RUN_REMOTE_DISPATCH=1
      shift 2
      ;;
    --remote-worker-registry)
      REMOTE_WORKER_REGISTRY="${2:?missing value for --remote-worker-registry}"
      RUN_REMOTE_DISPATCH=1
      shift 2
      ;;
    --remote-task-request)
      REMOTE_TASK_REQUEST="${2:?missing value for --remote-task-request}"
      RUN_REMOTE_DISPATCH=1
      shift 2
      ;;
    --edgeenv-run-evidence)
      RUN_EDGEENV_EVIDENCE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
done

resolve_repo() {
  local env_value="$1"
  local repo_name="$2"
  local label="$3"
  local candidate

  if [[ -n "$env_value" ]]; then
    if [[ -d "$env_value/.git" ]]; then
      printf '%s\n' "$env_value"
      return 0
    fi
    echo "$label repo is not a git repository: $env_value" >&2
    exit 1
  fi

  for candidate in \
    "$REPOS_ROOT/$repo_name" \
    "$ROOT_DIR/../$repo_name" \
    "/Users/GwonHyeokJun/Documents/GitHub/$repo_name"
  do
    if [[ -d "$candidate/.git" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  echo "missing $label repo: $repo_name" >&2
  echo "set the matching INFEREDGE_*_REPO environment variable or clone it next to this repo." >&2
  exit 1
}

choose_python() {
  local repo="$1"
  if [[ -x "$repo/.venv/bin/python" ]]; then
    printf '%s\n' "$repo/.venv/bin/python"
  elif [[ -x "/opt/anaconda3/bin/python" ]]; then
    printf '%s\n' "/opt/anaconda3/bin/python"
  elif command -v python3 >/dev/null 2>&1; then
    command -v python3
  elif command -v python >/dev/null 2>&1; then
    command -v python
  else
    echo "python interpreter not found" >&2
    exit 1
  fi
}

run_lab_agent_runtime_report() {
  local format="$1"
  local output="$2"
  local report_args=(
    agent-runtime-report
    --orchestration-summary "$ORCHESTRATION_OUT"
    --guard-analysis "$AIGUARD_JSON_OUT"
    --runtime-result "$RUNTIME_OUT"
    --format "$format"
    --output "$output"
  )

  if [[ "$RUN_REMOTE_DISPATCH" -eq 1 && -f "$REMOTE_DISPATCH_OUT" ]]; then
    report_args+=(--remote-dispatch "$REMOTE_DISPATCH_OUT")
  fi
  if [[ "$RUN_EDGEENV_EVIDENCE" -eq 1 && -f "$EDGEENV_RUN_SHOW_OUT" ]]; then
    report_args+=(--edgeenv-run-show "$EDGEENV_RUN_SHOW_OUT")
  fi

  cd "$LAB_REPO"
  if command -v poetry >/dev/null 2>&1; then
    poetry run inferedgelab "${report_args[@]}"
  elif command -v inferedgelab >/dev/null 2>&1; then
    inferedgelab "${report_args[@]}"
  else
    local lab_python
    lab_python="$(choose_python "$LAB_REPO")"
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$LAB_REPO${PYTHONPATH:+:$PYTHONPATH}" \
      "$lab_python" -m inferedgelab.cli "${report_args[@]}"
  fi
}

require_file() {
  local path="$1"
  local label="$2"
  if [[ ! -f "$path" ]]; then
    echo "missing $label: $path" >&2
    exit 1
  fi
}

absolute_file_path() {
  local path="$1"
  local dir
  local base
  dir="$(cd "$(dirname "$path")" && pwd)"
  base="$(basename "$path")"
  printf '%s/%s\n' "$dir" "$base"
}

run_step() {
  local label="$1"
  shift
  echo
  echo "==> $label"
  "$@"
}

if [[ -n "$VISION_INPUT$VISION_ONNX_MODEL$VOICE_INGRESS_PAYLOAD$RESOURCE_SNAPSHOT" || "$CAPTURE_PROCESS_RESOURCE_SNAPSHOT" -eq 1 || "$GENERATE_VISION_DETECTOR_PROBE" -eq 1 ]]; then
  if [[ "$SUSTAINED_MODE" != "device-local" ]]; then
    echo "device-local input overrides require --device-local" >&2
    exit 2
  fi
fi

if [[ -n "$VISION_ONNX_MODEL" && "$GENERATE_VISION_DETECTOR_PROBE" -eq 1 ]]; then
  echo "use either --vision-onnx-model or --generate-vision-detector-probe" >&2
  exit 2
fi

if [[ -n "$RESOURCE_SNAPSHOT" && "$CAPTURE_PROCESS_RESOURCE_SNAPSHOT" -eq 1 ]]; then
  echo "use either --resource-snapshot or --capture-process-resource-snapshot" >&2
  exit 2
fi

if [[ -n "$TEGRASTATS_LOG" && "$CAPTURE_TEGRASTATS" -eq 1 ]]; then
  echo "use either --tegrastats-log or --capture-tegrastats" >&2
  exit 2
fi

FORGE_REPO="$(resolve_repo "${INFEREDGE_FORGE_REPO:-}" InferEdgeForge "Forge")"
RUNTIME_REPO="$(resolve_repo "${INFEREDGE_RUNTIME_REPO:-}" InferEdge-Runtime "Runtime")"
ORCHESTRATOR_REPO="$(resolve_repo "${INFEREDGE_ORCHESTRATOR_REPO:-}" InferEdgeOrchestrator "Orchestrator")"
AIGUARD_REPO="$(resolve_repo "${INFEREDGE_AIGUARD_REPO:-}" InferEdgeAIGuard "AIGuard")"
LAB_REPO="$(resolve_repo "${INFEREDGE_LAB_REPO:-}" InferEdgeLab "Lab")"
EDGEENV_REPO=""
if [[ "$RUN_EDGEENV_EVIDENCE" -eq 1 ]]; then
  EDGEENV_REPO="$(resolve_repo "${INFEREDGE_ENV_REPO:-}" InferEdgeEnv "EdgeEnv")"
fi

ORCH_PYTHON="$(choose_python "$ORCHESTRATOR_REPO")"
AIGUARD_PYTHON="$(choose_python "$AIGUARD_REPO")"
EDGEENV_PYTHON=""
if [[ "$RUN_EDGEENV_EVIDENCE" -eq 1 ]]; then
  EDGEENV_PYTHON="$(choose_python "$EDGEENV_REPO")"
fi

FORGE_AGENT_MANIFEST="$FORGE_REPO/tests/fixtures/agent_manifest_vision.json"
RUNTIME_AGENT_RESULT="$ORCHESTRATOR_REPO/examples/agent_runtime/vision_runtime_result.json"

if [[ "$SUSTAINED_MODE" == "device-local" ]]; then
  ORCHESTRATOR_CONFIG="$ORCHESTRATOR_REPO/configs/agent_multi_workload_sustained_device_local.json"
  ORCHESTRATOR_CONFIG_LABEL="Orchestrator device_local sustained config"
  ORCHESTRATOR_MODE_MARKER="device_local"
  EXTRA_ORCHESTRATOR_MARKERS=("producer_sources" "device_local_producer_count")
else
  ORCHESTRATOR_CONFIG="$ORCHESTRATOR_REPO/configs/agent_multi_workload_sustained_safety_resource.json"
  ORCHESTRATOR_CONFIG_LABEL="Orchestrator producer-backed sustained config"
  ORCHESTRATOR_MODE_MARKER="sustained_high_load"
  EXTRA_ORCHESTRATOR_MARKERS=()
fi

require_file "$FORGE_AGENT_MANIFEST" "Forge agent_manifest fixture"
require_file "$RUNTIME_AGENT_RESULT" "Runtime result.agent fixture"
require_file "$ORCHESTRATOR_CONFIG" "$ORCHESTRATOR_CONFIG_LABEL"

if [[ -n "$REMOTE_WORKER_REGISTRY" ]]; then
  require_file "$REMOTE_WORKER_REGISTRY" "remote worker registry"
  REMOTE_WORKER_REGISTRY="$(absolute_file_path "$REMOTE_WORKER_REGISTRY")"
fi
if [[ -n "$REMOTE_TASK_REQUEST" ]]; then
  require_file "$REMOTE_TASK_REQUEST" "remote task request"
  REMOTE_TASK_REQUEST="$(absolute_file_path "$REMOTE_TASK_REQUEST")"
fi

mkdir -p "$OUTPUT_DIR"

if [[ "$GENERATE_VISION_DETECTOR_PROBE" -eq 1 ]]; then
  GENERATED_MODEL_DIR="$OUTPUT_DIR/generated_models"
  run_step "Generate tiny detector ONNX probe model" \
    "$ORCH_PYTHON" "$ORCHESTRATOR_REPO/scripts/create_tensorrt_diverse_onnx.py" \
    --output-dir "$GENERATED_MODEL_DIR" \
    --model detector
  VISION_ONNX_MODEL="$GENERATED_MODEL_DIR/detector_tiny.onnx"
  require_file "$VISION_ONNX_MODEL" "generated Vision detector ONNX probe model"
fi

ORCHESTRATOR_EXTRA_ARGS=()
if [[ -n "$VISION_INPUT" ]]; then
  require_file "$VISION_INPUT" "Vision producer override input"
  case "${VISION_INPUT##*.}" in
    mp4|MP4|mov|MOV|mkv|MKV|avi|AVI|webm|WEBM)
      VISION_PRODUCER_MARKER="video_file"
      ;;
    *)
      VISION_PRODUCER_MARKER="image_file"
      ;;
  esac
  VISION_INPUT="$(absolute_file_path "$VISION_INPUT")"
  ORCHESTRATOR_EXTRA_ARGS+=(--vision-input "$VISION_INPUT")
  EXTRA_ORCHESTRATOR_MARKERS+=("device_local_cli_override")
fi
if [[ -n "$VISION_ONNX_MODEL" ]]; then
  require_file "$VISION_ONNX_MODEL" "Vision ONNX producer probe model"
  VISION_ONNX_MODEL="$(absolute_file_path "$VISION_ONNX_MODEL")"
  ORCHESTRATOR_EXTRA_ARGS+=(--vision-onnx-model "$VISION_ONNX_MODEL")
  EXTRA_ORCHESTRATOR_MARKERS+=(
    "device_local_cli_override"
    "vision_inference_backend"
    "onnxruntime"
    "vision_probe_elapsed_ms"
  )
fi
if [[ -n "$VOICE_INGRESS_PAYLOAD" ]]; then
  require_file "$VOICE_INGRESS_PAYLOAD" "Voice ingress override payload"
  VOICE_INGRESS_PAYLOAD="$(absolute_file_path "$VOICE_INGRESS_PAYLOAD")"
  ORCHESTRATOR_EXTRA_ARGS+=(--voice-ingress-payload "$VOICE_INGRESS_PAYLOAD")
  EXTRA_ORCHESTRATOR_MARKERS+=("device_local_cli_override")
fi
if [[ -n "$RESOURCE_SNAPSHOT" ]]; then
  require_file "$RESOURCE_SNAPSHOT" "Safety resource snapshot override"
  RESOURCE_SNAPSHOT="$(absolute_file_path "$RESOURCE_SNAPSHOT")"
  ORCHESTRATOR_EXTRA_ARGS+=(--resource-snapshot "$RESOURCE_SNAPSHOT")
  EXTRA_ORCHESTRATOR_MARKERS+=("device_local_cli_override")
fi
if [[ "$CAPTURE_PROCESS_RESOURCE_SNAPSHOT" -eq 1 ]]; then
  ORCHESTRATOR_EXTRA_ARGS+=(--capture-process-resource-snapshot)
  SAFETY_PRODUCER_MARKER="process_resource_snapshot"
  EXTRA_ORCHESTRATOR_MARKERS+=("device_local_cli_override" "process_resource_snapshot")
fi
if [[ -n "$TEGRASTATS_LOG" ]]; then
  require_file "$TEGRASTATS_LOG" "tegrastats log"
  TEGRASTATS_LOG="$(absolute_file_path "$TEGRASTATS_LOG")"
fi

FORGE_OUT="$OUTPUT_DIR/01_forge_agent_manifest_vision.json"
RUNTIME_OUT="$OUTPUT_DIR/02_runtime_result_agent.json"
ORCHESTRATION_OUT="$OUTPUT_DIR/03_orchestration_summary.json"
TEGRSTATS_SAMPLE_OUT="$OUTPUT_DIR/03_tegrastats_sample.log"
AIGUARD_JSON_OUT="$OUTPUT_DIR/04_aiguard_guard_analysis.json"
AIGUARD_MD_OUT="$OUTPUT_DIR/04_aiguard_guard_analysis.md"
LAB_JSON_OUT="$OUTPUT_DIR/05_lab_agent_runtime_report.json"
LAB_MD_OUT="$OUTPUT_DIR/05_lab_agent_runtime_report.md"
REMOTE_DISPATCH_OUT="$OUTPUT_DIR/06_remote_dispatch_result.json"
REMOTE_AIGUARD_JSON_OUT="$OUTPUT_DIR/07_remote_dispatch_guard_analysis.json"
REMOTE_AIGUARD_MD_OUT="$OUTPUT_DIR/07_remote_dispatch_guard_analysis.md"
EDGEENV_DIR="$OUTPUT_DIR/08_edgeenv"
EDGEENV_BENCH_CONFIG="$EDGEENV_DIR/runtime_operation_bench.yaml"
EDGEENV_TARGET_PROFILE="$EDGEENV_DIR/local_target.yaml"
EDGEENV_ADAPTER="$EDGEENV_DIR/emit_runtime_operation_summary.py"
EDGEENV_ROOT="$EDGEENV_DIR/.edgeenv"
EDGEENV_RUN_STDOUT="$OUTPUT_DIR/08_edgeenv_run_stdout.txt"
EDGEENV_RUN_SHOW_OUT="$OUTPUT_DIR/08_edgeenv_run_show.json"
EVIDENCE_INDEX_JSON_OUT="$OUTPUT_DIR/00_evidence_index.json"
EVIDENCE_INDEX_MD_OUT="$OUTPUT_DIR/00_evidence_index.md"

run_step "Record Forge agent_manifest contract input" cp "$FORGE_AGENT_MANIFEST" "$FORGE_OUT"
run_step "Record Runtime result.agent contract input" cp "$RUNTIME_AGENT_RESULT" "$RUNTIME_OUT"

run_step "Attach Runtime operation evidence to local smoke result" \
  "$ORCH_PYTHON" - "$RUNTIME_OUT" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
agent = data.get("agent") or {}
telemetry = agent.get("telemetry_snapshot") or {}
mean_ms = float(telemetry.get("latency_mean_ms") or 28.0)
p99_ms = float(telemetry.get("latency_p99_ms") or 36.0)
fps = float(telemetry.get("fps") or 30.0)
timeout_budget_ms = 20
runtime_exceeded = mean_ms > timeout_budget_ms
health_reason = "timeout_threshold_exceeded" if runtime_exceeded else "benchmark_completed"
risk_labels = (
    ["runtime_timeout_observed", "latency_budget_exceeded"]
    if runtime_exceeded
    else []
)
evidence_gaps = ["thermal_memory_evidence_missing"]

data["runtime_health_snapshot"] = {
    "schema_version": "inferedge-runtime-health-v1",
    "status": "degraded" if runtime_exceeded else "ok",
    "engine_backend": data.get("backend_key", "onnxruntime__cpu").split("__")[0],
    "device": (data.get("backend_key", "onnxruntime__cpu").split("__")[-1] or "cpu"),
    "engine_available": True,
    "run_count": 5,
    "health_reason": health_reason,
    "mean_ms": mean_ms,
    "p99_ms": p99_ms,
    "fps": fps,
    "latency_budget_ms": timeout_budget_ms,
    "latency_budget_exceeded": runtime_exceeded,
    "deadline_missed": bool(agent.get("deadline_missed", False)),
    "timeout_policy": "latency_threshold",
    "timeout_budget_ms": timeout_budget_ms,
    "timeout_observed": runtime_exceeded,
    "thermal_memory_evidence_available": False,
}
data["runtime_error_classification"] = {
    "category": "runtime_timeout_observed" if runtime_exceeded else "none",
    "severity": "medium" if runtime_exceeded else "none",
    "retryable": runtime_exceeded,
    "retry_hint": (
        "reduce_input_rate_or_relax_latency_budget"
        if runtime_exceeded
        else "none"
    ),
    "observed_mean_ms": mean_ms,
    "timeout_budget_ms": timeout_budget_ms,
    "timeout_observed": runtime_exceeded,
}
data["runtime_operation_summary"] = {
    "schema_version": "inferedge-runtime-operation-summary-v1",
    "observation_scope": "single_runtime_result",
    "decision_owner": "lab",
    "scheduler_owner": "orchestrator",
    "production_cancellation": False,
    "health_status": data["runtime_health_snapshot"]["status"],
    "health_reason": health_reason,
    "error_category": data["runtime_error_classification"]["category"],
    "retryable": data["runtime_error_classification"]["retryable"],
    "recommended_action": (
        "review_latency_budget_or_degrade" if runtime_exceeded else "none"
    ),
    "risk_labels": risk_labels,
    "evidence_gaps": evidence_gaps,
    "timeout_observed": runtime_exceeded,
    "latency_budget_exceeded": runtime_exceeded,
    "deadline_missed": data["runtime_health_snapshot"]["deadline_missed"],
    "thermal_memory_evidence_available": False,
}
data["runtime_events"] = [
    {
        "event_index": 0,
        "event_type": "runtime_health_snapshot",
        "status": data["runtime_health_snapshot"]["status"],
        "health_reason": health_reason,
        "engine_backend": data["runtime_health_snapshot"]["engine_backend"],
        "detail": "entrypoint smoke attached Runtime operation context",
    },
    {
        "event_index": 1,
        "event_type": "runtime_error_classified",
        "status": data["runtime_error_classification"]["severity"],
        "category": data["runtime_error_classification"]["category"],
        "retryable": data["runtime_error_classification"]["retryable"],
        "retry_hint": data["runtime_error_classification"]["retry_hint"],
        "timeout_budget_ms": timeout_budget_ms,
    },
    {
        "event_index": 2,
        "event_type": "runtime_operation_summary_recorded",
        "type": "runtime_operation_summary_recorded",
        "status": data["runtime_operation_summary"]["health_status"],
        "health_reason": health_reason,
        "recommended_action": data["runtime_operation_summary"]["recommended_action"],
        "risk_labels": risk_labels,
        "evidence_gaps": evidence_gaps,
    },
]
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

if [[ -n "$TEGRASTATS_LOG" ]]; then
  run_step "Record provided tegrastats log" cp "$TEGRASTATS_LOG" "$TEGRSTATS_SAMPLE_OUT"
elif [[ "$CAPTURE_TEGRASTATS" -eq 1 ]]; then
  : > "$TEGRSTATS_SAMPLE_OUT"
else
  cat > "$TEGRSTATS_SAMPLE_OUT" <<'EOF'
RAM 2048/7771MB SWAP 0/3885MB CPU [12%@1510] GR3D_FREQ 42% cpu@45.5C gpu@44.0C
EOF
fi

run_orchestrator_sustained() {
  cd "$ORCHESTRATOR_REPO"
  local tegrastats_pid=""
  if [[ "$CAPTURE_TEGRASTATS" -eq 1 ]]; then
    if ! command -v tegrastats >/dev/null 2>&1; then
      echo "tegrastats command not found; use --tegrastats-log with a captured log instead" >&2
      return 1
    fi
    tegrastats --interval 1000 --logfile "$TEGRSTATS_SAMPLE_OUT" >/dev/null 2>&1 &
    tegrastats_pid=$!
    sleep 1
  fi

  local status=0
  if ((${#ORCHESTRATOR_EXTRA_ARGS[@]} > 0)); then
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src "$ORCH_PYTHON" -m inferedge_orchestrator run-multi-workload-sustained \
      --config "$ORCHESTRATOR_CONFIG" \
      --output "$ORCHESTRATION_OUT" \
      --frames "$FRAMES" \
      --tegrastats-log "$TEGRSTATS_SAMPLE_OUT" \
      "${ORCHESTRATOR_EXTRA_ARGS[@]}" || status=$?
  else
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src "$ORCH_PYTHON" -m inferedge_orchestrator run-multi-workload-sustained \
      --config "$ORCHESTRATOR_CONFIG" \
      --output "$ORCHESTRATION_OUT" \
      --frames "$FRAMES" \
      --tegrastats-log "$TEGRSTATS_SAMPLE_OUT" || status=$?
  fi

  if [[ -n "$tegrastats_pid" ]]; then
    sleep 1
    kill "$tegrastats_pid" >/dev/null 2>&1 || true
    wait "$tegrastats_pid" >/dev/null 2>&1 || true
  fi
  return "$status"
}

run_remote_dispatch_starter() {
  cd "$ORCHESTRATOR_REPO"
  local dispatch_args=(
    remote-dispatch
    --registry "$REMOTE_WORKER_REGISTRY"
    --request "$REMOTE_TASK_REQUEST"
    --output "$REMOTE_DISPATCH_OUT"
  )
  if [[ "$RUN_REMOTE_EXECUTE_PLAN" -eq 1 ]]; then
    dispatch_args+=(--execute-plan --timeout-sec "$REMOTE_EXECUTE_TIMEOUT_SEC")
  fi
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src "$ORCH_PYTHON" -m inferedge_orchestrator "${dispatch_args[@]}"
}

run_remote_dispatch_aiguard() {
  cd "$AIGUARD_REPO"
  PYTHONDONTWRITEBYTECODE=1 "$AIGUARD_PYTHON" -m inferedge_aiguard.cli reason-remote-dispatch \
    --input "$REMOTE_DISPATCH_OUT" \
    --save-json "$REMOTE_AIGUARD_JSON_OUT" \
    --save-md "$REMOTE_AIGUARD_MD_OUT"
}

run_edgeenv_runtime_operation_evidence() {
  mkdir -p "$EDGEENV_DIR"
  "$EDGEENV_PYTHON" - "$EDGEENV_BENCH_CONFIG" "$EDGEENV_TARGET_PROFILE" "$EDGEENV_ADAPTER" "$EDGEENV_PYTHON" "$RUNTIME_OUT" <<'PY'
import shlex
import sys
from pathlib import Path

bench_path = Path(sys.argv[1])
target_path = Path(sys.argv[2])
adapter_path = Path(sys.argv[3])
python_path = sys.argv[4]
runtime_path = Path(sys.argv[5])

adapter_path.write_text(
    """#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-result", required=True)
    args = parser.parse_args()

    data = json.loads(Path(args.runtime_result).read_text(encoding="utf-8"))
    summary = data.get("runtime_operation_summary") or {}
    health = data.get("runtime_health_snapshot") or {}
    telemetry = (data.get("agent") or {}).get("telemetry_snapshot") or {}

    mean = float(health.get("mean_ms") or telemetry.get("latency_mean_ms") or 0.0)
    p99 = float(health.get("p99_ms") or telemetry.get("latency_p99_ms") or mean)
    fps = float(health.get("fps") or telemetry.get("fps") or 0.0)
    metrics = {
        "latency_mean_ms": mean,
        "latency_p50_ms": mean,
        "latency_p95_ms": p99,
        "latency_p99_ms": p99,
        "throughput_fps": fps,
    }
    print("EDGEENV_RUNTIME_OPERATION_SUMMARY_JSON=" + json.dumps(summary, sort_keys=True))
    print("EDGEENV_METRICS_JSON=" + json.dumps(metrics, sort_keys=True))


if __name__ == "__main__":
    main()
""",
    encoding="utf-8",
)

command = (
    f"{shlex.quote(python_path)} {shlex.quote(str(adapter_path))} "
    f"--runtime-result {shlex.quote(str(runtime_path))}"
)
bench_path.write_text(
    "\n".join(
        [
            "name: entrypoint-runtime-operation-evidence",
            f"command: {command}",
            "model_name: entrypoint-runtime-operation-result",
            "model_version: v1",
            "model_format: runtime-result-json",
            f"model_path: {runtime_path}",
            "task: runtime-operation-evidence",
            "input_shape: [1]",
            "input_dtype: json",
            "runtime: entrypoint-smoke",
            "execution_provider: local-python",
            "precision: evidence",
            "batch_size: 1",
            "warmup_runs: 0",
            "repeat_runs: 1",
            "include_preprocess: false",
            "include_postprocess: false",
            "",
        ]
    ),
    encoding="utf-8",
)
target_path.write_text(
    "\n".join(
        [
            "target_name: entrypoint-local",
            "target_type: local",
            "board_name: local-dev-machine",
            "os: local",
            "runtime_tags: [entrypoint, runtime-operation-evidence]",
            "",
        ]
    ),
    encoding="utf-8",
)
PY

  cd "$EDGEENV_REPO"
  PYTHONDONTWRITEBYTECODE=1 "$EDGEENV_PYTHON" -m inferedge_env.cli bench run \
    --target "$EDGEENV_TARGET_PROFILE" \
    --config "$EDGEENV_BENCH_CONFIG" \
    --edgeenv-root "$EDGEENV_ROOT" | tee "$EDGEENV_RUN_STDOUT"

  local edgeenv_run_id
  edgeenv_run_id="$(awk -F': ' '/^Run ID:/ {print $2; exit}' "$EDGEENV_RUN_STDOUT")"
  if [[ -z "$edgeenv_run_id" ]]; then
    echo "failed to parse EdgeEnv run id from $EDGEENV_RUN_STDOUT" >&2
    return 1
  fi
  PYTHONDONTWRITEBYTECODE=1 "$EDGEENV_PYTHON" -m inferedge_env.cli runs show \
    "$edgeenv_run_id" \
    --edgeenv-root "$EDGEENV_ROOT" > "$EDGEENV_RUN_SHOW_OUT"
}

run_step "Generate Orchestrator $SUSTAINED_MODE multi-workload sustained summary" \
  run_orchestrator_sustained

run_step "Attach Runtime result to local orchestration bundle" \
  "$ORCH_PYTHON" - "$ORCHESTRATION_OUT" "$RUNTIME_OUT" <<'PY'
import json
import sys
from pathlib import Path

summary_path = Path(sys.argv[1])
runtime_path = Path(sys.argv[2])
summary = json.loads(summary_path.read_text(encoding="utf-8"))
runtime_result = json.loads(runtime_path.read_text(encoding="utf-8"))
summary["runtime_results"] = [runtime_result]
summary.setdefault("source_contracts", {})["runtime_result"] = runtime_result.get(
    "schema_version"
)
summary_path.write_text(
    json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
PY

run_step "Derive Orchestrator operation risk summary markers" \
  "$ORCH_PYTHON" - "$ORCHESTRATION_OUT" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
multi = data.get("multi_workload_sustained_summary") or {}
observed = multi.get("observed_runtime_signals") or {}
queue = data.setdefault("queue_state_summary", {})
runtime_events = data.setdefault("runtime_event_summary", {})
workers = (data.get("worker_health_snapshot") or {}).get("workers") or {}

policy_reasons = observed.get("policy_decision_reasons") or []
if isinstance(policy_reasons, str):
    policy_reasons = [policy_reasons]
queue_pressure_reason = (
    policy_reasons[0]
    if policy_reasons
    else queue.get("queue_pressure_reason")
    or queue.get("queue_pressure_state")
    or "unknown"
)

max_by_task = queue.get("max_queue_depth_by_task") or {}
max_pressure_task = queue.get("max_pressure_task") or "unknown"
if isinstance(max_by_task, dict) and max_by_task:
    max_pressure_task = max(max_by_task.items(), key=lambda item: item[1])[0]

degraded_workers = []
if isinstance(workers, dict):
    for worker_id, worker in workers.items():
        if isinstance(worker, dict) and worker.get("health_state") != "healthy":
            degraded_workers.append(str(worker_id))
primary_health_reason = (
    "worker_health_degraded"
    if degraded_workers
    else str(queue.get("queue_pressure_state") or "healthy")
)

device_local_event_count = (
    observed.get("device_local_producer_count")
    or runtime_events.get("device_local_event_count")
    or runtime_events.get("event_count")
    or "unknown"
)
producer_event_count = (
    observed.get("producer_source_count")
    or runtime_events.get("producer_event_count")
    or "unknown"
)

queue["queue_pressure_reason"] = queue_pressure_reason
queue["max_pressure_task"] = max_pressure_task
data.setdefault("worker_health_snapshot", {})[
    "primary_health_reason"
] = primary_health_reason
runtime_events["device_local_event_count"] = device_local_event_count
runtime_events["producer_event_count"] = producer_event_count
data["operation_risk_summary"] = {
    "schema_version": "inferedge-entrypoint-operation-risk-summary-v1",
    "evidence_role": "derived_navigation_context",
    "decision_owner": "lab",
    "scheduler_owner": "orchestrator",
    "queue_pressure_reason": queue_pressure_reason,
    "max_pressure_task": max_pressure_task,
    "primary_health_reason": primary_health_reason,
    "degraded_worker_ids": degraded_workers,
    "device_local_event_count": device_local_event_count,
    "producer_event_count": producer_event_count,
    "not_a_deployment_decision": True,
}

path.write_text(
    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
PY

run_step "Generate AIGuard runtime reliability guard_analysis" \
  bash -lc "cd '$AIGUARD_REPO' && PYTHONDONTWRITEBYTECODE=1 '$AIGUARD_PYTHON' -m inferedge_aiguard.cli reason-orchestration --input '$ORCHESTRATION_OUT' --save-json '$AIGUARD_JSON_OUT' --save-md '$AIGUARD_MD_OUT'"

if [[ "$RUN_REMOTE_DISPATCH" -eq 1 ]]; then
  if [[ -z "$REMOTE_WORKER_REGISTRY" ]]; then
    REMOTE_WORKER_REGISTRY="$ORCHESTRATOR_REPO/examples/remote_worker_registry.json"
  fi
  if [[ -z "$REMOTE_TASK_REQUEST" ]]; then
    REMOTE_TASK_REQUEST="$ORCHESTRATOR_REPO/examples/remote_task_request.json"
  fi
  require_file "$REMOTE_WORKER_REGISTRY" "remote worker registry"
  require_file "$REMOTE_TASK_REQUEST" "remote task request"
  REMOTE_WORKER_REGISTRY="$(absolute_file_path "$REMOTE_WORKER_REGISTRY")"
  REMOTE_TASK_REQUEST="$(absolute_file_path "$REMOTE_TASK_REQUEST")"
  run_step "Generate Orchestrator remote dispatch starter result" \
    run_remote_dispatch_starter

  run_step "Generate AIGuard remote dispatch starter guard_analysis" \
    run_remote_dispatch_aiguard
fi

if [[ "$RUN_EDGEENV_EVIDENCE" -eq 1 ]]; then
  run_step "Preserve Runtime operation summary in EdgeEnv run registry" \
    run_edgeenv_runtime_operation_evidence
fi

run_step "Generate Lab Agent Runtime Reliability report JSON" \
  run_lab_agent_runtime_report json "$LAB_JSON_OUT"

run_step "Generate Lab Agent Runtime Reliability report Markdown" \
  run_lab_agent_runtime_report markdown "$LAB_MD_OUT"

run_step "Generate Agent Runtime evidence index" \
  "$ORCH_PYTHON" "$ROOT_DIR/scripts/build_agent_runtime_evidence_index.py" \
    --output-dir "$OUTPUT_DIR" \
    --requested-frames "$FRAMES"

run_step "Validate schema markers" grep -q "inferedge-agent-manifest-v1" "$FORGE_OUT"
grep -q "inferedge-runtime-agent-task-v1" "$RUNTIME_OUT"
grep -q "runtime_health_snapshot" "$RUNTIME_OUT"
grep -q "runtime_operation_summary" "$RUNTIME_OUT"
grep -q "runtime_operation_summary_recorded" "$RUNTIME_OUT"
grep -q "inferedge-orchestration-summary-v1" "$ORCHESTRATION_OUT"
grep -q "runtime_results" "$ORCHESTRATION_OUT"
grep -q "runtime_operation_summary" "$ORCHESTRATION_OUT"
grep -q "inferedge-aiguard-diagnosis-v1" "$AIGUARD_JSON_OUT"
grep -q "inferedgelab-agent-runtime-reliability-report-v1" "$LAB_JSON_OUT"
grep -q "$ORCHESTRATOR_MODE_MARKER" "$ORCHESTRATION_OUT"
grep -q "multi_workload_sustained_summary" "$ORCHESTRATION_OUT"
if ((${#EXTRA_ORCHESTRATOR_MARKERS[@]} > 0)); then
  for marker in "${EXTRA_ORCHESTRATOR_MARKERS[@]}"; do
    grep -q "$marker" "$ORCHESTRATION_OUT"
  done
fi
grep -q "$VISION_PRODUCER_MARKER" "$ORCHESTRATION_OUT"
grep -q "fastapi_request_fixture" "$ORCHESTRATION_OUT"
grep -q "$SAFETY_PRODUCER_MARKER" "$ORCHESTRATION_OUT"
grep -q "resource_degradation_score" "$ORCHESTRATION_OUT"
grep -q "tegrastats_timeline" "$ORCHESTRATION_OUT"
grep -q "sustained_overload_risk" "$AIGUARD_JSON_OUT"
grep -q "profiled_workload_pressure" "$AIGUARD_JSON_OUT"
grep -q "thermal_resource_pressure" "$AIGUARD_JSON_OUT"
grep -q "runtime_latency_budget_overrun" "$AIGUARD_JSON_OUT"
grep -q "runtime_error_retryable" "$AIGUARD_JSON_OUT"
grep -q "runtime_retryable_error" "$AIGUARD_JSON_OUT"
grep -q "runtime_operation_health" "$AIGUARD_JSON_OUT"
grep -q "runtime_operation_summary_risk_count" "$AIGUARD_JSON_OUT"
grep -q "review_latency_budget_or_degrade" "$AIGUARD_JSON_OUT"
grep -q "max_total_queue_depth" "$LAB_JSON_OUT"
grep -q "operation_context" "$LAB_JSON_OUT"
grep -q "runtime_result_context" "$LAB_JSON_OUT"
grep -q "runtime_operation_summary" "$LAB_JSON_OUT"
grep -q "runtime_operation_guard_summary" "$LAB_JSON_OUT"
grep -q "runtime_retryable_error_review" "$LAB_JSON_OUT"
grep -q "runtime_operation_summary_review" "$LAB_JSON_OUT"
grep -q "queue_state_summary" "$LAB_JSON_OUT"
grep -q "worker_health_snapshot" "$LAB_JSON_OUT"
grep -q "runtime_event_summary" "$LAB_JSON_OUT"
grep -q "runtime_event_timeline_sample" "$LAB_JSON_OUT"
grep -q "queue_pressure_reason" "$ORCHESTRATION_OUT"
grep -q "max_pressure_task" "$ORCHESTRATION_OUT"
grep -q "primary_health_reason" "$ORCHESTRATION_OUT"
grep -q "operation_risk_summary" "$ORCHESTRATION_OUT"
grep -q "queue_pressure_context" "$AIGUARD_JSON_OUT"
grep -q "worker_operation_risk_summary" "$AIGUARD_JSON_OUT"
grep -q "queue_pressure_reason" "$LAB_JSON_OUT"
grep -q "max_pressure_task" "$LAB_JSON_OUT"
grep -q "operation_risk_summary" "$LAB_JSON_OUT"
grep -q "Worker operation risk summary" "$LAB_MD_OUT"
grep -q "Worker producer context" "$LAB_MD_OUT"
grep -q "Queue pressure reasons" "$LAB_MD_OUT"
grep -q "profiled_workload_pressure" "$LAB_JSON_OUT"
grep -q "thermal_resource_pressure" "$LAB_JSON_OUT"
grep -q "sustained_overload_review" "$LAB_JSON_OUT"
grep -q "Orchestrator Operation Context" "$LAB_MD_OUT"
grep -q "Worker Health" "$LAB_MD_OUT"
grep -q "Runtime Event Summary" "$LAB_MD_OUT"
grep -q "Runtime Result Operation Evidence" "$LAB_MD_OUT"
grep -q "runtime_error_retryable" "$LAB_MD_OUT"
grep -q "runtime_error_retry_hint" "$LAB_MD_OUT"
grep -q "operation_summary_recommended_action" "$LAB_MD_OUT"
grep -q "runtime_operation_summary_review" "$LAB_MD_OUT"
grep -q "AIGuard Runtime Operation Evidence" "$LAB_MD_OUT"
grep -q "inferedge-agent-runtime-evidence-index-v1" "$EVIDENCE_INDEX_JSON_OUT"
grep -q "Agent Runtime Evidence Index" "$EVIDENCE_INDEX_MD_OUT"
grep -q "Lab decision" "$EVIDENCE_INDEX_MD_OUT"
grep -q "queue_pressure_reason" "$EVIDENCE_INDEX_MD_OUT"
grep -q "max_pressure_task" "$EVIDENCE_INDEX_MD_OUT"
grep -q "device_local_event_count" "$EVIDENCE_INDEX_MD_OUT"
grep -q "runtime_operation_recommended_action" "$EVIDENCE_INDEX_MD_OUT"
grep -q "runtime_operation_risk_labels" "$EVIDENCE_INDEX_MD_OUT"
if [[ "$RUN_EDGEENV_EVIDENCE" -eq 1 ]]; then
  grep -q "runtime_operation_summary" "$EDGEENV_RUN_SHOW_OUT"
  grep -q "inferedge-runtime-operation-summary-v1" "$EDGEENV_RUN_SHOW_OUT"
  grep -q "edgeenv_preservation_context" "$LAB_JSON_OUT"
  grep -q "Runtime Intelligence EdgeEnv Preservation" "$LAB_MD_OUT"
  grep -q "edgeenv_run_id" "$LAB_MD_OUT"
  grep -q "edgeenv_summary" "$EVIDENCE_INDEX_JSON_OUT"
  grep -q "lab_report_preservation_section_present" "$EVIDENCE_INDEX_JSON_OUT"
  grep -q "Runtime Intelligence EdgeEnv Preservation" "$EVIDENCE_INDEX_JSON_OUT"
  grep -q "EdgeEnv Runtime Operation Evidence" "$EVIDENCE_INDEX_MD_OUT"
  grep -q "lab_report_preservation_section_present" "$EVIDENCE_INDEX_MD_OUT"
  grep -q "Runtime Intelligence EdgeEnv Preservation" "$EVIDENCE_INDEX_MD_OUT"
fi
if [[ "$SUSTAINED_MODE" == "device-local" ]]; then
  grep -q "device_local_operation_context" "$AIGUARD_JSON_OUT"
  grep -q "device_local_operation_context" "$LAB_JSON_OUT"
  grep -q "device_local_producer_sources" "$LAB_JSON_OUT"
  grep -q "producer_sources_by_task" "$LAB_JSON_OUT"
fi
if [[ "$RUN_REMOTE_DISPATCH" -eq 1 ]]; then
  grep -q "inferedge-remote-dispatch-result-v1" "$REMOTE_DISPATCH_OUT"
  grep -q "file_contract_starter" "$REMOTE_DISPATCH_OUT"
  grep -q "production_remote_execution" "$REMOTE_DISPATCH_OUT"
  grep -q "remote_dispatch_runtime_event_compact_summary" "$REMOTE_DISPATCH_OUT"
  grep -q "remote dispatch starter evidence only" "$REMOTE_DISPATCH_OUT"
  grep -q "selected_worker_id" "$REMOTE_DISPATCH_OUT"
  grep -q "remote_execution_plan" "$REMOTE_DISPATCH_OUT"
  grep -q "inferedge-remote-execution-plan-v1" "$REMOTE_DISPATCH_OUT"
  grep -q "network_execution_performed" "$REMOTE_DISPATCH_OUT"
  grep -q "remote_execution_result" "$REMOTE_DISPATCH_OUT"
  grep -q "execution_requested" "$REMOTE_DISPATCH_OUT"
  grep -q "execution_performed" "$REMOTE_DISPATCH_OUT"
  grep -q "inferedge-aiguard-diagnosis-v1" "$REMOTE_AIGUARD_JSON_OUT"
  grep -q "remote_execution" "$REMOTE_AIGUARD_JSON_OUT"
  grep -q "remote_runtime_event_summary" "$REMOTE_AIGUARD_JSON_OUT"
  grep -q "remote_dispatch_runtime_event_compact_summary" "$REMOTE_AIGUARD_JSON_OUT"
  grep -q "remote dispatch starter evidence only" "$REMOTE_AIGUARD_JSON_OUT"
  grep -q "production_remote_execution" "$REMOTE_AIGUARD_JSON_OUT"
  grep -Eq "remote_dispatch_health|remote_execution_(plan_only|skipped|failed|starter_success|recovered_by_fallback)" "$REMOTE_AIGUARD_JSON_OUT"
  grep -q "worker_selection" "$REMOTE_DISPATCH_OUT"
  grep -q "inferedge-remote-worker-selection-v1" "$REMOTE_DISPATCH_OUT"
  grep -q "retry_fallback_plan" "$REMOTE_DISPATCH_OUT"
  grep -q "inferedge-remote-retry-fallback-plan-v1" "$REMOTE_DISPATCH_OUT"
  grep -q "remote_dispatch_context" "$LAB_JSON_OUT"
  grep -q "remote_execution_plan" "$LAB_JSON_OUT"
  grep -q "remote_execution_result" "$LAB_JSON_OUT"
  grep -q "remote_runtime_event_summary" "$LAB_JSON_OUT"
  grep -q "remote_dispatch_runtime_event_compact_summary" "$LAB_JSON_OUT"
  grep -q "remote dispatch starter evidence only" "$LAB_JSON_OUT"
  grep -q "production_remote_execution" "$LAB_JSON_OUT"
  grep -q "Remote execution starter evidence" "$LAB_MD_OUT"
  grep -q "Remote Dispatch Context" "$LAB_MD_OUT"
  grep -q "remote_runtime_evidence_role" "$LAB_MD_OUT"
  grep -q "remote_dispatch_runtime_event_compact_summary" "$LAB_MD_OUT"
  grep -q "remote_runtime_summary_boundary" "$LAB_MD_OUT"
  grep -q "remote dispatch starter evidence only" "$LAB_MD_OUT"
  grep -q "remote_event_summary_role" "$EVIDENCE_INDEX_JSON_OUT"
  grep -q "remote_dispatch_runtime_event_compact_summary" "$EVIDENCE_INDEX_JSON_OUT"
  grep -q "operation_boundary" "$EVIDENCE_INDEX_JSON_OUT"
  grep -q "remote dispatch starter evidence only" "$EVIDENCE_INDEX_JSON_OUT"
  grep -q "remote_event_summary_role" "$EVIDENCE_INDEX_MD_OUT"
  grep -q "remote_dispatch_runtime_event_compact_summary" "$EVIDENCE_INDEX_MD_OUT"
  grep -q "operation_boundary" "$EVIDENCE_INDEX_MD_OUT"
  grep -q "remote dispatch starter evidence only" "$EVIDENCE_INDEX_MD_OUT"
  if grep -q "fallback_execution_result" "$REMOTE_DISPATCH_OUT"; then
    grep -q "fallback_execution_result" "$LAB_JSON_OUT"
    grep -q "Remote fallback starter evidence" "$LAB_MD_OUT"
  fi
fi

echo
echo "Reliable Edge Agent Runtime e2e smoke ($SUSTAINED_MODE): pass"
echo
echo "Outputs:"
echo "  Forge agent manifest:       $FORGE_OUT"
echo "  Runtime result.agent:       $RUNTIME_OUT"
echo "  Orchestration summary:      $ORCHESTRATION_OUT"
echo "  Tegrastats log:             $TEGRSTATS_SAMPLE_OUT"
echo "  AIGuard guard analysis:     $AIGUARD_JSON_OUT"
echo "  AIGuard Markdown report:    $AIGUARD_MD_OUT"
echo "  Lab report JSON:            $LAB_JSON_OUT"
echo "  Lab report Markdown:        $LAB_MD_OUT"
echo "  Evidence index JSON:        $EVIDENCE_INDEX_JSON_OUT"
echo "  Evidence index Markdown:    $EVIDENCE_INDEX_MD_OUT"
if [[ "$RUN_REMOTE_DISPATCH" -eq 1 ]]; then
  echo "  Remote dispatch result:     $REMOTE_DISPATCH_OUT"
  echo "  Remote dispatch AIGuard:    $REMOTE_AIGUARD_JSON_OUT"
  echo "  Remote dispatch AIGuard MD: $REMOTE_AIGUARD_MD_OUT"
fi
if [[ "$RUN_EDGEENV_EVIDENCE" -eq 1 ]]; then
  echo "  EdgeEnv run show:           $EDGEENV_RUN_SHOW_OUT"
  echo "  EdgeEnv registry root:      $EDGEENV_ROOT"
fi
