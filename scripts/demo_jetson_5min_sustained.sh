#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="/tmp/inferedge_agent_runtime_jetson_sustained_5min_3600"
FRAMES=3600
TIMEOUT_SEC=420
VISION_INPUT="../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm"
VISION_ONNX_MODEL="$HOME/InferEdge_device_local_inputs/models/yolov8n.onnx"
FORGE_REPO="${INFEREDGE_FORGE_REPO:-/tmp/inferedge_clean_repos/InferEdgeForge}"

usage() {
  cat <<'USAGE'
Usage: bash scripts/demo_jetson_5min_sustained.sh [options]

Run the Jetson device-local 5-minute-class sustained smoke path:

  device_local ONNX Runtime probe
  + live tegrastats capture
  + Orchestrator queue/drop/fallback evidence
  + AIGuard runtime reliability analysis
  + Lab-owned deployment decision report

This is runtime-operation smoke evidence. It is not decoded YOLO accuracy
validation, live camera operation, Whisper/FastAPI service execution,
production remote execution, or thermal endurance validation.

Options:
  --output-dir DIR       Output bundle directory.
                         Default: /tmp/inferedge_agent_runtime_jetson_sustained_5min_3600
  --frames N            Frame cycles for the sustained run.
                         Default: 3600
  --timeout-sec SEC     Guard timeout around the full e2e command.
                         Default: 420
  --vision-input PATH   Vision producer local image input.
                         Default: ../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm
  --vision-onnx-model PATH
                         ONNX model for the Vision producer probe.
                         Default: ~/InferEdge_device_local_inputs/models/yolov8n.onnx
  --forge-repo PATH     Clean Forge repo for agent manifest fixture input.
                         Default: /tmp/inferedge_clean_repos/InferEdgeForge
  -h, --help            Show this help.

Environment:
  INFEREDGE_FORGE_REPO  Overrides the default clean Forge repo path.
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
    --timeout-sec)
      TIMEOUT_SEC="${2:?missing value for --timeout-sec}"
      shift 2
      ;;
    --vision-input)
      VISION_INPUT="${2:?missing value for --vision-input}"
      shift 2
      ;;
    --vision-onnx-model)
      VISION_ONNX_MODEL="${2:?missing value for --vision-onnx-model}"
      shift 2
      ;;
    --forge-repo)
      FORGE_REPO="${2:?missing value for --forge-repo}"
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

if [[ ! -d "$FORGE_REPO/.git" ]]; then
  cat >&2 <<EOF
missing clean Forge repo: $FORGE_REPO

Prepare it on the Jetson with:

  rm -rf /tmp/inferedge_clean_repos
  mkdir -p /tmp/inferedge_clean_repos
  git clone --depth 1 https://github.com/gwonxhj/InferEdgeForge.git \\
    /tmp/inferedge_clean_repos/InferEdgeForge
EOF
  exit 1
fi

if [[ ! -f "$VISION_ONNX_MODEL" ]]; then
  echo "missing ONNX model: $VISION_ONNX_MODEL" >&2
  exit 1
fi

if ! command -v tegrastats >/dev/null 2>&1; then
  echo "tegrastats command not found; this runner is intended for Jetson validation." >&2
  exit 1
fi

echo "InferEdge Jetson 5-minute-class sustained smoke"
echo "  output_dir: $OUTPUT_DIR"
echo "  frames: $FRAMES"
echo "  timeout_sec: $TIMEOUT_SEC"
echo "  forge_repo: $FORGE_REPO"
echo "  vision_input: $VISION_INPUT"
echo "  vision_onnx_model: $VISION_ONNX_MODEL"
echo

cd "$ROOT_DIR"
PATH="$HOME/miniconda3/envs/yolo_env/bin:$PATH" \
INFEREDGE_FORGE_REPO="$FORGE_REPO" \
timeout "$TIMEOUT_SEC" bash scripts/demo_agent_runtime_e2e.sh \
  --device-local \
  --output-dir "$OUTPUT_DIR" \
  --frames "$FRAMES" \
  --vision-input "$VISION_INPUT" \
  --vision-onnx-model "$VISION_ONNX_MODEL" \
  --capture-process-resource-snapshot \
  --capture-tegrastats

cat <<EOF

Jetson sustained smoke complete.

Key outputs:
  $OUTPUT_DIR/00_evidence_index.md
  $OUTPUT_DIR/03_orchestration_summary.json
  $OUTPUT_DIR/04_aiguard_guard_analysis.json
  $OUTPUT_DIR/05_lab_agent_runtime_report.json
  $OUTPUT_DIR/05_lab_agent_runtime_report.md
EOF
