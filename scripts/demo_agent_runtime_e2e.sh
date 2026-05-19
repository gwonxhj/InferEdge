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
REMOTE_WORKER_REGISTRY=""
REMOTE_TASK_REQUEST=""
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
                                             [--remote-worker-registry PATH]
                                             [--remote-task-request PATH]

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
  --remote-worker-registry PATH
                    Override the remote worker registry JSON.
                    Implies --remote-dispatch.
  --remote-task-request PATH
                    Override the remote task request JSON.
                    Implies --remote-dispatch.
  -h, --help        Show this help.

Environment:
  INFEREDGE_REPOS_DIR          Override ./repos lookup root.
  INFEREDGE_FORGE_REPO         Override InferEdgeForge path.
  INFEREDGE_RUNTIME_REPO       Override InferEdge-Runtime path.
  INFEREDGE_ORCHESTRATOR_REPO  Override InferEdgeOrchestrator path.
  INFEREDGE_AIGUARD_REPO       Override InferEdgeAIGuard path.
  INFEREDGE_LAB_REPO           Override InferEdgeLab path.
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

  cd "$LAB_REPO"
  if command -v poetry >/dev/null 2>&1; then
    poetry run inferedgelab agent-runtime-report \
      --orchestration-summary "$ORCHESTRATION_OUT" \
      --guard-analysis "$AIGUARD_JSON_OUT" \
      --format "$format" \
      --output "$output"
  elif command -v inferedgelab >/dev/null 2>&1; then
    inferedgelab agent-runtime-report \
      --orchestration-summary "$ORCHESTRATION_OUT" \
      --guard-analysis "$AIGUARD_JSON_OUT" \
      --format "$format" \
      --output "$output"
  else
    echo "missing Lab CLI: install poetry or ensure inferedgelab is on PATH" >&2
    exit 1
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

ORCH_PYTHON="$(choose_python "$ORCHESTRATOR_REPO")"
AIGUARD_PYTHON="$(choose_python "$AIGUARD_REPO")"

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

run_step "Record Forge agent_manifest contract input" cp "$FORGE_AGENT_MANIFEST" "$FORGE_OUT"
run_step "Record Runtime result.agent contract input" cp "$RUNTIME_AGENT_RESULT" "$RUNTIME_OUT"

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

run_step "Generate Orchestrator $SUSTAINED_MODE multi-workload sustained summary" \
  run_orchestrator_sustained

run_step "Generate AIGuard runtime reliability guard_analysis" \
  bash -lc "cd '$AIGUARD_REPO' && PYTHONDONTWRITEBYTECODE=1 '$AIGUARD_PYTHON' -m inferedge_aiguard.cli reason-orchestration --input '$ORCHESTRATION_OUT' --save-json '$AIGUARD_JSON_OUT' --save-md '$AIGUARD_MD_OUT'"

run_step "Generate Lab Agent Runtime Reliability report JSON" \
  run_lab_agent_runtime_report json "$LAB_JSON_OUT"

run_step "Generate Lab Agent Runtime Reliability report Markdown" \
  run_lab_agent_runtime_report markdown "$LAB_MD_OUT"

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
    bash -lc "cd '$ORCHESTRATOR_REPO' && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src '$ORCH_PYTHON' -m inferedge_orchestrator remote-dispatch --registry '$REMOTE_WORKER_REGISTRY' --request '$REMOTE_TASK_REQUEST' --output '$REMOTE_DISPATCH_OUT'"
fi

run_step "Validate schema markers" grep -q "inferedge-agent-manifest-v1" "$FORGE_OUT"
grep -q "inferedge-runtime-agent-task-v1" "$RUNTIME_OUT"
grep -q "inferedge-orchestration-summary-v1" "$ORCHESTRATION_OUT"
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
grep -q "max_total_queue_depth" "$LAB_JSON_OUT"
grep -q "operation_context" "$LAB_JSON_OUT"
grep -q "queue_state_summary" "$LAB_JSON_OUT"
grep -q "worker_health_snapshot" "$LAB_JSON_OUT"
grep -q "runtime_event_summary" "$LAB_JSON_OUT"
grep -q "runtime_event_timeline_sample" "$LAB_JSON_OUT"
grep -q "profiled_workload_pressure" "$LAB_JSON_OUT"
grep -q "thermal_resource_pressure" "$LAB_JSON_OUT"
grep -q "sustained_overload_review" "$LAB_JSON_OUT"
grep -q "Orchestrator Operation Context" "$LAB_MD_OUT"
grep -q "Worker Health" "$LAB_MD_OUT"
grep -q "Runtime Event Summary" "$LAB_MD_OUT"
if [[ "$RUN_REMOTE_DISPATCH" -eq 1 ]]; then
  grep -q "inferedge-remote-dispatch-result-v1" "$REMOTE_DISPATCH_OUT"
  grep -q "file_contract_starter" "$REMOTE_DISPATCH_OUT"
  grep -q "production_remote_execution" "$REMOTE_DISPATCH_OUT"
  grep -q "selected_worker_id" "$REMOTE_DISPATCH_OUT"
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
if [[ "$RUN_REMOTE_DISPATCH" -eq 1 ]]; then
  echo "  Remote dispatch result:     $REMOTE_DISPATCH_OUT"
fi
