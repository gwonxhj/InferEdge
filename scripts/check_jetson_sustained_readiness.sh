#!/usr/bin/env bash
set -euo pipefail

SSH_TARGET="${JETSON_SSH_TARGET:-risenano01@nano01.local}"
CONNECT_TIMEOUT_SEC="${JETSON_CONNECT_TIMEOUT_SEC:-8}"
INFEREDGE_DIR="${JETSON_INFEREDGE_DIR:-~/InferEdge}"
FORGE_REPO="${JETSON_FORGE_REPO:-/tmp/inferedge_clean_repos/InferEdgeForge}"
VISION_INPUT="${JETSON_VISION_INPUT:-../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm}"
VISION_ONNX_MODEL="${JETSON_VISION_ONNX_MODEL:-~/InferEdge_device_local_inputs/models/yolov8n.onnx}"
EDGEENV_REPO="${JETSON_EDGEENV_REPO:-~/InferEdgeEnv}"
CHECK_EDGEENV=0

usage() {
  cat <<'USAGE'
Usage: bash scripts/check_jetson_sustained_readiness.sh [options]

Check whether a Jetson target is ready for the device-local sustained smoke.
This is a preflight helper only. It does not run inference, capture telemetry,
or claim new Jetson evidence.

Options:
  --ssh-target TARGET        SSH target. Default: $JETSON_SSH_TARGET or risenano01@nano01.local
  --connect-timeout SEC      SSH connect timeout. Default: $JETSON_CONNECT_TIMEOUT_SEC or 8
  --inferedge-dir PATH       InferEdge entrypoint directory on Jetson. Default: ~/InferEdge
  --forge-repo PATH          Clean Forge fixture repo on Jetson. Default: /tmp/inferedge_clean_repos/InferEdgeForge
  --vision-input PATH        Vision input path from InferEdge dir. Default: ../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm
  --vision-onnx-model PATH   Vision ONNX model path. Default: ~/InferEdge_device_local_inputs/models/yolov8n.onnx
  --edgeenv-run-evidence     Also check InferEdgeEnv repo/CLI readiness for the
                              optional EdgeEnv registry preservation path.
  --edgeenv-repo PATH        InferEdgeEnv repo on Jetson. Default: $JETSON_EDGEENV_REPO or ~/InferEdgeEnv
  -h, --help                 Show this help.

Environment:
  JETSON_SSH_TARGET
  JETSON_CONNECT_TIMEOUT_SEC
  JETSON_INFEREDGE_DIR
  JETSON_FORGE_REPO
  JETSON_VISION_INPUT
  JETSON_VISION_ONNX_MODEL
  JETSON_EDGEENV_REPO
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ssh-target)
      SSH_TARGET="${2:?missing value for --ssh-target}"
      shift 2
      ;;
    --connect-timeout)
      CONNECT_TIMEOUT_SEC="${2:?missing value for --connect-timeout}"
      shift 2
      ;;
    --inferedge-dir)
      INFEREDGE_DIR="${2:?missing value for --inferedge-dir}"
      shift 2
      ;;
    --forge-repo)
      FORGE_REPO="${2:?missing value for --forge-repo}"
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
    --edgeenv-run-evidence)
      CHECK_EDGEENV=1
      shift
      ;;
    --edgeenv-repo)
      EDGEENV_REPO="${2:?missing value for --edgeenv-repo}"
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

echo "InferEdge Jetson sustained readiness preflight"
echo "  ssh_target: $SSH_TARGET"
echo "  connect_timeout_sec: $CONNECT_TIMEOUT_SEC"
echo "  inferedge_dir: $INFEREDGE_DIR"
echo "  forge_repo: $FORGE_REPO"
if [[ "$CHECK_EDGEENV" -eq 1 ]]; then
  echo "  edgeenv_repo: $EDGEENV_REPO"
fi
echo "  vision_input: $VISION_INPUT"
echo "  vision_onnx_model: $VISION_ONNX_MODEL"
echo

ssh \
  -o BatchMode=yes \
  -o ConnectTimeout="$CONNECT_TIMEOUT_SEC" \
  "$SSH_TARGET" \
  "set -e
   cd $INFEREDGE_DIR
   echo host=\$(hostname)
   echo inferedge_commit=\$(git rev-parse --short HEAD)
   git status --short --branch
   command -v tegrastats >/dev/null
   echo tegrastats=available
   test -d $FORGE_REPO/.git
   echo clean_forge_repo=available
   test -f $VISION_INPUT
   echo vision_input=available
   test -f $VISION_ONNX_MODEL
   echo vision_onnx_model=available
   if [ $CHECK_EDGEENV -eq 1 ]; then
     test -d $EDGEENV_REPO/.git
     echo edgeenv_repo=available
     cd $EDGEENV_REPO
     edgeenv_python=python3
     if [ -x \"\$HOME/miniconda3/envs/yolo_env/bin/python\" ]; then
       edgeenv_python=\"\$HOME/miniconda3/envs/yolo_env/bin/python\"
     fi
     \"\$edgeenv_python\" -m inferedge_env.cli --help >/dev/null
     echo edgeenv_cli=available
     cd $INFEREDGE_DIR
   fi
   test -x scripts/demo_jetson_5min_sustained.sh
   echo sustained_runner=available"

cat <<'EOF'

Jetson readiness preflight passed.

Next command on the Jetson:

  bash scripts/demo_jetson_5min_sustained.sh

For the EdgeEnv preservation path:

  bash scripts/demo_jetson_5min_sustained.sh --edgeenv-run-evidence

This preflight does not create evidence. Use it only to check the target before
running the device-local sustained smoke.
EOF
