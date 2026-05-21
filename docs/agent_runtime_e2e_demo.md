# Reliable Edge Agent Runtime E2E Demo

This document describes the local extension smoke that connects the Reliable
Edge Agent Runtime contracts across the InferEdge ecosystem.

The demo is intentionally local-first and file-based. It is not a production
orchestration service, cloud dashboard, or general AI OS.

The current smoke uses the latest Orchestrator producer-backed sustained
path: Vision reads a local image fixture, Voice-Command replays a FastAPI-style
request burst fixture, and Safety-Monitor reads resource snapshot telemetry.
It verifies that queue-depth timeline evidence, policy decision reasons,
`multi_workload_sustained_summary`, producer source markers, optional
`tegrastats_timeline`, AIGuard `profiled_workload_pressure` /
`thermal_resource_pressure`, and Lab `sustained_overload_review` are preserved
across the chain before live device-local sustained validation is added. It also
checks that Lab preserves Orchestrator operation context, including queue state,
worker health, runtime event summary, and timeline samples in report output. The
optional `--device-local` mode uses committed local image, request, and resource
snapshot producers in Orchestrator `scenario_mode=device_local`.

## Status Boundary

| Path | Status | Meaning |
|---|---|---|
| Default e2e chain | Implemented | `agent_manifest -> Runtime result.agent -> Orchestrator -> AIGuard -> Lab` contract is reproducible |
| Producer-backed sustained workload path | Smoke/Starter | Queue/drop/fallback/deadline evidence is generated from committed fixtures |
| Device-local override path | Smoke/Starter | Local image, optional ONNX model, request payload, resource snapshot, and `tegrastats` input can be routed through the same chain |
| Jetson ONNX + live `tegrastats` replay | Smoke/Starter | Real device telemetry handoff is validated through the report path |
| Live camera, Whisper/FastAPI service, thermal endurance, production remote execution | Future Work | Not completed and should not be described as current functionality |

## Contract Chain

```text
Forge agent_manifest
-> Runtime result.agent
-> Orchestrator orchestration_summary
-> AIGuard guard_analysis
-> Lab agent-runtime-report
```

## Run

From the InferEdge entrypoint repository:

```bash
bash scripts/demo_agent_runtime_e2e.sh
```

Run the explicit device-local starter path when you want the Orchestrator
`scenario_mode=device_local` config:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local
```

Replace the committed device-local fixtures with local inputs from the
entrypoint script:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --vision-input /path/to/frame.ppm \
  --voice-ingress-payload /path/to/requests.json \
  --capture-process-resource-snapshot
```

If optional ONNX Runtime dependencies are installed in the Orchestrator
environment, add a lightweight Vision producer probe:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --vision-input /path/to/frame.ppm \
  --vision-onnx-model /path/to/vision_model.onnx
```

This verifies that the entrypoint can pass an ONNX model path into the
Orchestrator device-local Vision producer and preserve
`vision_inference_backend`, input/output shapes, and probe latency through the
e2e smoke outputs. It is not a full live YOLO service.

Add the remote dispatch starter when you want the entrypoint smoke to include
remote worker selection evidence:

```bash
bash scripts/demo_agent_runtime_e2e.sh --remote-dispatch
```

By default this uses Orchestrator's committed remote worker registry and task
request examples. It writes `06_remote_dispatch_result.json`, including
`selected_worker_id`, `decision_reason`, worker health snapshot,
`worker_selection`, `retry_fallback_plan`, `remote_execution_plan`, and
`remote_execution_result`. It also writes
`07_remote_dispatch_guard_analysis.json` so AIGuard can explain whether the
remote dispatch starter stayed selection-only, skipped execution, failed, or
completed the explicit starter path.

Explicit HTTP/SSH starter execution is opt-in:

```bash
bash scripts/demo_agent_runtime_e2e.sh --remote-dispatch --remote-execute-plan
```

The committed file-contract worker examples are selection-only, so the
execution result is recorded as skipped starter evidence. A registry entry with
an `http_request` or `ssh_command` endpoint can use the same option to record
starter execution status, transport, and error category. This is remote dispatch
starter evidence, not production SSH/HTTP execution.

To reproduce bounded remote fallback recovery, run only the fallback HTTP
starter worker and leave the primary endpoint unavailable:

```bash
# Terminal A
python3 ../InferEdgeOrchestrator/scripts/remote_http_worker.py \
  --host 127.0.0.1 \
  --port 8765 \
  --worker-id fallback-http-worker

# Terminal B
bash scripts/demo_agent_runtime_e2e.sh \
  --output-dir /tmp/inferedge_agent_runtime_fallback_e2e \
  --frames 8 \
  --remote-dispatch \
  --remote-execute-plan \
  --remote-timeout-sec 1 \
  --remote-worker-registry examples/remote_fallback/remote_worker_registry_fallback.json \
  --remote-task-request examples/remote_fallback/remote_task_request_fallback.json
```

The fallback fixture selects `primary-http-worker` first, where
`http://127.0.0.1:9876/execute` is intentionally unavailable. The retry policy
allows one fallback attempt on `connection_error`, and the local
`fallback-http-worker` listens on `http://127.0.0.1:8765/execute`. A successful
starter replay should include:

- `06_remote_dispatch_result.json` with `fallback_execution_result.final_status`
  set to `succeeded`
- `07_remote_dispatch_guard_analysis.json` with
  `remote_execution_recovered_by_fallback`
- `05_lab_agent_runtime_report.md` with `Remote fallback starter evidence`

This is a bounded starter recovery smoke. It does not provide production retry
control, auth, heartbeat, or a long-lived remote worker.

When you do not have a local ONNX file but want a detector-like probe instead
of the tiny identity model, generate one under the output directory:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --vision-input /path/to/frame.ppm \
  --generate-vision-detector-probe
```

This calls the Orchestrator synthetic detector ONNX generator and uses the
generated `detector_tiny.onnx` as the Vision probe. The generated model is a
local artifact and is not committed. It is closer to image-shaped perception
work than the identity probe, but it still should not be described as full live
YOLO validation.

If you already captured a Jetson `tegrastats` log, pass it through the same
entrypoint smoke:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --tegrastats-log /path/to/tegrastats.log
```

The script copies the provided log into the generated evidence directory and
routes it through the Orchestrator `tegrastats_timeline`, AIGuard reliability
analysis, and Lab report. This is telemetry handoff evidence, not a full
thermal endurance validation.

On Jetson, use `--capture-tegrastats` when you want the entrypoint smoke to
capture `tegrastats` during the Orchestrator sustained run:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --vision-input /path/to/frame.ppm \
  --vision-onnx-model /path/to/model.onnx \
  --capture-tegrastats
```

This starts `tegrastats` for the duration of the Orchestrator run and routes the
captured log through the same `tegrastats_timeline`. It is still a device-local
smoke path, not thermal endurance validation.

Use `--resource-snapshot /path/to/resources.json` instead of
`--capture-process-resource-snapshot` when you already have a resource snapshot
fixture. These overrides intentionally require `--device-local` so the default
producer-backed smoke remains stable and dependency-light.

## Minimum Sample Inputs

If `InferEdgeOrchestrator` is cloned next to this entrypoint repo, the smallest
committed input set is:

| Workload | Path | Source marker |
|---|---|---|
| Vision | `../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm` | `image_file` |
| Voice / Command | `../InferEdgeOrchestrator/examples/inputs/voice_ingress_requests.json` | `fastapi_request_fixture` |
| Safety / Monitor | `../InferEdgeOrchestrator/examples/inputs/safety_resource_snapshots.json` | `resource_snapshot_fixture` |

Concrete replay command:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --output-dir /tmp/inferedge_agent_runtime_device_local_inputs \
  --frames 8 \
  --vision-input ../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm \
  --voice-ingress-payload ../InferEdgeOrchestrator/examples/inputs/voice_ingress_requests.json \
  --resource-snapshot ../InferEdgeOrchestrator/examples/inputs/safety_resource_snapshots.json
```

Concrete process-snapshot variant:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --output-dir /tmp/inferedge_agent_runtime_device_local_process \
  --frames 8 \
  --vision-input ../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm \
  --voice-ingress-payload ../InferEdgeOrchestrator/examples/inputs/voice_ingress_requests.json \
  --capture-process-resource-snapshot
```

This remains a device-local starter path. It validates that local producer
inputs flow through Orchestrator, AIGuard, and Lab report contracts. It does not
claim full live YOLO/Whisper/FastAPI/Jetson sustained validation.

## Jetson Starter Validation Record

The same device-local starter path was replayed on a Jetson Orin Nano with a
live `tegrastats` capture. This validates the telemetry handoff path without
claiming full live workload validation.

| Field | Observed value |
|---|---:|
| Power mode | 25W |
| Scenario mode | `device_local` |
| Frames | 64 |
| Max queue depth | 6 |
| Dropped count | 61 |
| Fallback count | 61 |
| Deadline missed count | 0 |
| Parsed `tegrastats` samples | 4 |
| Max temperature | 39.625 C |
| Max RAM used | 1783 MB |
| Max GPU percent | 0 |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` |

The generated Orchestrator summary preserved `image_file`,
`fastapi_request_fixture`, and `process_resource_snapshot` producer sources.
The Lab report preserved `queue_state_summary`, `worker_health_snapshot`,
`runtime_event_summary`, and `runtime_event_timeline_sample` under
`agent_runtime_summary.operation_context`.

## Jetson ONNX Probe Validation Record

The device-local entrypoint path was also replayed on the same Jetson Orin Nano
with `--vision-onnx-model`. This validates that a local ONNX model can be passed
into the Orchestrator Vision producer and preserved as lightweight inference
probe evidence across Orchestrator, AIGuard, and Lab reports.

| Field | Observed value |
|---|---:|
| Power mode | 25W |
| Scenario mode | `device_local` |
| Frames | 16 |
| Vision inference backend | `onnxruntime` |
| Vision provider | `CPUExecutionProvider` |
| Vision output shape | `[1, 2]` |
| Vision probe latency | 1.255 ms |
| Max queue depth | 6 |
| Dropped count | 13 |
| Fallback count | 13 |
| Deadline missed count | 1 |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` |

The ONNX model used for this validation was a tiny identity probe model. This
record should be described as device-local ONNX Runtime probe evidence, not as
full live YOLO/Whisper/FastAPI sustained validation.

## Captured Tegrastats Log Option Validation

The entrypoint `--tegrastats-log` option was validated with a separately
captured Jetson Orin Nano `tegrastats` log. The log was captured for about
12 seconds and then passed into the local entrypoint smoke, which copied it into
the evidence bundle and routed it through Orchestrator, AIGuard, and Lab.

| Field | Observed value |
|---|---:|
| Power mode | 25W |
| Scenario mode | `device_local` |
| Captured log duration | ~12 seconds |
| Parsed `tegrastats` samples | 11 |
| Frames | 16 |
| Vision inference backend | `onnxruntime` |
| Vision provider | `CPUExecutionProvider` |
| Max queue depth | 6 |
| Dropped count | 13 |
| Fallback count | 13 |
| Deadline missed count | 1 |
| Max temperature | 41.5 C |
| Max RAM used | 830 MB |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` |

This validates the captured-log telemetry handoff path. It should not be
described as thermal endurance validation or full live YOLO/Whisper/FastAPI
sustained validation.

## Generated Detector Probe Validation

The entrypoint `--generate-vision-detector-probe` option was validated with the
Orchestrator synthetic detector ONNX generator. The generated model stayed under
the temporary output directory and was used only as local probe evidence. The
Lab report step uses `poetry run inferedgelab` when Poetry is available, and
falls back to an installed `inferedgelab` CLI when running on a device image
without Poetry.

| Field | Observed value |
|---|---:|
| Scenario mode | `device_local` |
| Generated model | `generated_models/detector_tiny.onnx` |
| Vision inference backend | `onnxruntime` |
| Vision provider | `CPUExecutionProvider` |
| Vision input shape | `[1, 3, 16, 16]` |
| Vision output shape | `[1, 6]` |
| Frames | 8 |
| Max queue depth | 6 |
| Dropped count | 5 |
| Fallback count | 5 |
| Lab decision | `blocked` |

This validates the generated detector-like ONNX probe path. It should be
described as a reproducible lightweight vision probe, not as full live YOLO
validation.

The same path was also replayed on Jetson Orin Nano with the generated detector
probe and process resource snapshot enabled.

| Field | Jetson observed value |
|---|---:|
| Scenario mode | `device_local` |
| Vision inference backend | `onnxruntime` |
| Vision provider | `CPUExecutionProvider` |
| Vision input shape | `[1, 3, 16, 16]` |
| Vision output shape | `[1, 6]` |
| Frames | 16 |
| Max queue depth | 6 |
| Dropped count | 13 |
| Fallback count | 13 |
| Deadline missed count | 1 |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` |

This is Jetson device-local smoke evidence for the entrypoint contract chain.
It should not be described as full live YOLO/Whisper/FastAPI sustained
validation or thermal endurance validation.

The same device-local entrypoint path was also replayed with a user-provided
YOLOv8n ONNX model copied to the Jetson temporary directory and passed through
`--vision-onnx-model`.

| Field | Jetson YOLOv8n observed value |
|---|---:|
| Scenario mode | `device_local` |
| Model | `yolov8n.onnx` |
| Vision inference backend | `onnxruntime` |
| Vision provider | `CPUExecutionProvider` |
| Vision input shape | `[1, 3, 640, 640]` |
| Vision output shape | `[1, 84, 8400]` |
| Frames | 16 |
| Max queue depth | 6 |
| Dropped count | 13 |
| Fallback count | 13 |
| Deadline missed count | 10 |
| Vision probe elapsed range | `120.147-146.878 ms` |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` |

This validates a real ONNX model probe through the entrypoint contract chain on
Jetson. It should not be described as decoded YOLO accuracy validation, live
camera operation, or full thermal endurance validation.

The real YOLOv8n ONNX probe was then replayed with `--capture-tegrastats` so
that live Jetson telemetry was captured during the Orchestrator sustained run
and routed through AIGuard and the Lab report.

| Field | Jetson YOLOv8n + live tegrastats value |
|---|---:|
| Scenario mode | `device_local` |
| Model | `yolov8n.onnx` |
| Vision inference backend | `onnxruntime` |
| Vision provider | `CPUExecutionProvider` |
| Vision input shape | `[1, 3, 640, 640]` |
| Vision output shape | `[1, 84, 8400]` |
| Frames | 32 |
| Max queue depth | 6 |
| Dropped count | 29 |
| Fallback count | 29 |
| Deadline missed count | 18 |
| Parsed `tegrastats` samples | 4 |
| Max temperature | `43.937 C` |
| Max RAM used | `966 MB` |
| Vision probe elapsed range | `119.912-137.729 ms` |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` |

This validates the live Jetson telemetry capture path and a real ONNX model
probe in one evidence bundle. It is still not decoded YOLO accuracy validation,
live camera operation, or thermal endurance validation.

The latest main-branch replay was run again on Jetson Orin Nano 25W with the
same entrypoint path, a user-provided `yolov8n.onnx`, local image input,
process resource snapshot capture, and live `tegrastats` capture.

| Field | Latest Jetson device-local replay |
|---|---:|
| Scenario mode | `device_local` |
| Model | `yolov8n.onnx` |
| Vision inference backend | `onnxruntime` |
| Vision provider | `CPUExecutionProvider` |
| Frames | 96 |
| Max queue depth | 6 |
| Dropped count | 93 |
| Fallback count | 93 |
| Deadline missed count | 50 |
| Parsed `tegrastats` samples | 9 |
| Max temperature | `39.0 C` |
| Max RAM used | `979 MB` |
| Vision mean / p95 latency | `156.43 ms / 159.629 ms` |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` |

This latest replay confirms that the current main branches still carry real
Jetson ONNX probe and live telemetry evidence through Orchestrator, AIGuard,
and Lab over a longer 96-frame starter replay. It also confirms the Lab report
preserves Runtime operation guard evidence (`runtime_latency_budget_overrun`,
`runtime_error_classification`).
It remains a device-local smoke record, not decoded YOLO accuracy, live camera,
Whisper/FastAPI, or sustained thermal endurance validation.
A submission-facing snapshot of the generated Lab evidence is captured in
[`Jetson Device-Local Agent Runtime Evidence Report`](evidence/jetson_device_local_agent_runtime_report.md).

The longer 5-minute-class Jetson replay used the same path with `--frames 3600`
and a 420-second guard timeout.

| Field | 5-minute-class Jetson sustained smoke |
|---|---:|
| Runtime window | about 297 seconds |
| Scenario mode | `device_local` |
| Model | `yolov8n.onnx` |
| Vision inference backend | `onnxruntime` |
| Vision provider | `CPUExecutionProvider` |
| Frames | 3600 |
| Max queue depth | 6 |
| Dropped count | 3597 |
| Fallback count | 3597 |
| Deadline missed count | 1802 |
| Parsed `tegrastats` samples | 282 |
| Max temperature | `43.125 C` |
| Max RAM used | `1028 MB` |
| Vision mean / p95 latency | `153.231 ms / 157.2 ms` |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` |

This replay is captured as
[`Jetson Device-Local 5-Minute Sustained Smoke Report`](evidence/jetson_device_local_5min_sustained_report.md)
and
[`HTML report`](evidence/jetson_device_local_5min_sustained_report.html).
It is still runtime-operation smoke evidence, not decoded YOLO accuracy
validation, live camera operation, Whisper/FastAPI service execution, production
remote execution, or sustained thermal endurance validation.

For repeat runs on Jetson, use the convenience wrapper:

```bash
bash scripts/demo_jetson_5min_sustained.sh
```

The wrapper calls `scripts/demo_agent_runtime_e2e.sh` with the documented
`device_local`, ONNX Runtime probe, process resource snapshot, and live
`tegrastats` capture options. Use `--help` to override output directory,
frame count, timeout, ONNX model, or clean Forge repo path.

The script writes generated evidence under:

```text
reports/agent_runtime_e2e/
```

Use a temporary output directory for clean validation:

```bash
bash scripts/demo_agent_runtime_e2e.sh --output-dir /tmp/inferedge_agent_runtime_e2e
bash scripts/demo_agent_runtime_e2e.sh --device-local --output-dir /tmp/inferedge_agent_runtime_e2e_device_local
```

## Clean Jetson Replay Runbook

Use this runbook when the Jetson has local Forge or Runtime worktrees with
experimental builds, untracked artifacts, or branch-specific changes. Do not
delete or reset those worktrees just to reproduce the entrypoint smoke. Instead,
use a temporary clean Forge clone for the fixture contract and keep the evidence
bundle under `/tmp`.

Prepare a clean Forge fixture source:

```bash
rm -rf /tmp/inferedge_clean_repos
mkdir -p /tmp/inferedge_clean_repos
git clone --depth 1 https://github.com/gwonxhj/InferEdgeForge.git \
  /tmp/inferedge_clean_repos/InferEdgeForge
test -f /tmp/inferedge_clean_repos/InferEdgeForge/tests/fixtures/agent_manifest_vision.json
```

Replay the 96-frame Jetson device-local path from the entrypoint repo:

```bash
cd ~/InferEdge
PATH=$HOME/miniconda3/envs/yolo_env/bin:$PATH \
INFEREDGE_FORGE_REPO=/tmp/inferedge_clean_repos/InferEdgeForge \
bash scripts/demo_agent_runtime_e2e.sh \
  --device-local \
  --output-dir /tmp/inferedge_agent_runtime_jetson_sustained_96_main \
  --frames 96 \
  --vision-input ../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm \
  --vision-onnx-model ~/InferEdge_device_local_inputs/models/yolov8n.onnx \
  --capture-process-resource-snapshot \
  --capture-tegrastats
```

Expected output files:

- `/tmp/inferedge_agent_runtime_jetson_sustained_96_main/00_evidence_index.md`
- `/tmp/inferedge_agent_runtime_jetson_sustained_96_main/00_evidence_index.json`
- `/tmp/inferedge_agent_runtime_jetson_sustained_96_main/03_orchestration_summary.json`
- `/tmp/inferedge_agent_runtime_jetson_sustained_96_main/04_aiguard_guard_analysis.json`
- `/tmp/inferedge_agent_runtime_jetson_sustained_96_main/05_lab_agent_runtime_report.json`
- `/tmp/inferedge_agent_runtime_jetson_sustained_96_main/05_lab_agent_runtime_report.md`

The `00_evidence_index.*` files are generated after the Lab report and provide
a compact navigation layer over the bundle. They summarize scenario mode, queue
pressure, deadline/drop/fallback counts, AIGuard verdict, Lab decision, and
optional remote-dispatch status without replacing the source JSON contracts.

Expected evidence markers:

- `multi_workload_sustained_summary`
- `tegrastats_timeline`
- `profiled_workload_pressure`
- `thermal_resource_pressure`
- `runtime_latency_budget_overrun`
- `runtime_error_classification`
- `agent_deployment_decision`

The observed timing and resource values can vary slightly by Jetson mode,
current load, and thermal state. This runbook validates a clean replay of the
device-local ONNX probe and live telemetry handoff path. It is not decoded YOLO
accuracy validation, live camera operation, Whisper/FastAPI service execution,
or sustained thermal endurance validation.

## Inputs

The script resolves repositories from `./repos`, sibling directories, or
`/Users/GwonHyeokJun/Documents/GitHub`.

Override paths when needed:

```bash
INFEREDGE_FORGE_REPO=/path/to/InferEdgeForge \
INFEREDGE_RUNTIME_REPO=/path/to/InferEdge-Runtime \
INFEREDGE_ORCHESTRATOR_REPO=/path/to/InferEdgeOrchestrator \
INFEREDGE_AIGUARD_REPO=/path/to/InferEdgeAIGuard \
INFEREDGE_LAB_REPO=/path/to/InferEdgeLab \
bash scripts/demo_agent_runtime_e2e.sh
```

## Outputs

| Output | Purpose |
|---|---|
| `00_evidence_index.json` | Compact machine-readable navigation index for generated evidence files |
| `00_evidence_index.md` | Human-readable evidence bundle index and decision summary |
| `01_forge_agent_manifest_vision.json` | Agent workload handoff contract example |
| `02_runtime_result_agent.json` | Runtime result with backward-compatible `agent` block |
| `03_orchestration_summary.json` | Profiled multi-workload scheduler policy decision evidence |
| `03_tegrastats_sample.log` | Local tegrastats-style sample, copied captured log, or live captured Jetson log for thermal/resource evidence |
| `generated_models/detector_tiny.onnx` | Optional local artifact written only when `--generate-vision-detector-probe` is used |
| `04_aiguard_guard_analysis.json` | Deterministic runtime reliability diagnosis evidence |
| `04_aiguard_guard_analysis.md` | Human-readable AIGuard report |
| `05_lab_agent_runtime_report.json` | Lab-owned agent runtime reliability report |
| `05_lab_agent_runtime_report.md` | Human-readable Lab deployment decision context |
| `06_remote_dispatch_result.json` | Optional file-based remote worker selection evidence when `--remote-dispatch` is used |

Expected sustained evidence markers:

- `sustained_high_load` in Orchestrator output
- `multi_workload_sustained_summary` and `tegrastats_timeline` in Orchestrator output
- `image_file`, `fastapi_request_fixture`, `resource_snapshot_fixture`, and `resource_degradation_score` in Orchestrator output
- `producer_sources` and `device_local_producer_count` in Orchestrator output when `--device-local` is used
- `sustained_overload_risk` in AIGuard output
- `profiled_workload_pressure` and `thermal_resource_pressure` in AIGuard output
- `max_total_queue_depth` in Lab report metrics
- `profiled_workload_pressure` and `thermal_resource_pressure` preserved in Lab report evidence
- `operation_context`, `queue_state_summary`, `worker_health_snapshot`,
  `runtime_event_summary`, and `runtime_event_timeline_sample` preserved in
  the Lab report
- `Orchestrator Operation Context`, `Worker Health`, and
  `Runtime Event Summary` visible in the Lab Markdown report
- `sustained_overload_review` in Lab decision rules
- `inferedge-remote-dispatch-result-v1`, `file_contract_starter`, and
  `selected_worker_id` in `06_remote_dispatch_result.json` when
  `--remote-dispatch` is used
- `remote_execution_plan`, `worker_selection`, and `retry_fallback_plan` in
  `06_remote_dispatch_result.json` when `--remote-dispatch` is used
- `remote_execution_result` in `06_remote_dispatch_result.json` and
  `Remote execution starter evidence` in the Lab Markdown report when
  `--remote-dispatch` is used
- `07_remote_dispatch_guard_analysis.json` with deterministic AIGuard evidence
  for the remote dispatch starter when `--remote-dispatch` is used

## Scope Boundary

Included:

- Vision / Voice-Command / Safety-Monitor workload contracts
- priority/deadline scheduling evidence
- drop/fallback/deadline signal propagation
- lightweight producer-backed sustained workload summary
- Vision local image fixture, Voice FastAPI-style request fixture, and Safety resource snapshot fixture propagation
- optional `--device-local` replay for the explicit Orchestrator device-local starter config
- optional device-local input overrides through `--vision-input`,
  `--voice-ingress-payload`, `--resource-snapshot`, or
  `--capture-process-resource-snapshot`
- optional generated detector-like ONNX probe through
  `--generate-vision-detector-probe`
- local tegrastats-style thermal/resource sample propagation
- optional captured `tegrastats` log propagation through `--tegrastats-log`
- optional live Jetson `tegrastats` capture through `--capture-tegrastats`
- optional file-based remote worker selection evidence through
  `--remote-dispatch`
- AIGuard runtime reliability interpretation
- Lab-owned report and deployment decision context

Not included:

- production SaaS infrastructure
- DB/queue persistence
- cloud orchestration
- production remote worker execution, SSH/HTTP dispatch, or secure tunnel
  operation
- LLM agent framework implementation
- universal AI OS claims
