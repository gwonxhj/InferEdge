# InferEdge

Multi-repository entrypoint for the InferEdge local-first Edge AI inference validation pipeline.

InferEdge is not a benchmark-only script and not a production SaaS dashboard.
It is a contract/preset based validation workflow that connects build
provenance, real Runtime execution, validation evidence, optional deterministic
diagnosis evidence, and Lab-owned deployment decisions.

The ecosystem is organized by lifecycle questions:

```text
Can we deploy this model?                         -> InferEdge validation layer
Can this benchmark evidence be trusted and compared? -> InferEdgeEnv comparability layer
Can deployed workloads stay stable under load?   -> InferEdgeOrchestrator operation layer
```

![InferEdge ecosystem lifecycle diagram](docs/assets/inferedge_ecosystem_diagram.svg)

```text
ONNX Model
-> InferEdgeForge
-> InferEdge-Runtime
-> InferEdgeLab
-> optional InferEdgeAIGuard
-> Deployment Decision Report
-> Local Studio
```

## Repositories

| Repository | Role | URL |
|---|---|---|
| InferEdgeForge | Build provenance, metadata, manifest, artifact handoff | https://github.com/gwonxhj/InferEdgeForge |
| InferEdge-Runtime | C++ execution, Lab-compatible result JSON, Jetson evidence reports | https://github.com/gwonxhj/InferEdge-Runtime |
| InferEdgeLab | Compare/evaluate/report/API/Local Studio/deployment decision owner | https://github.com/gwonxhj/InferEdgeLab |
| InferEdgeAIGuard | Optional deterministic diagnosis evidence provider | https://github.com/gwonxhj/InferEdgeAIGuard |

## Ecosystem Extension Layers

These repositories extend the lifecycle beyond the pinned Core 4 validation
message without replacing Forge, Runtime, Lab, or AIGuard.

| Repository | Role | URL |
|---|---|---|
| InferEdgeEnv | v0.1.5 v1-complete comparability layer: local run evidence registry and benchmark evidence trust/comparison judgement | https://github.com/gwonxhj/InferEdgeEnv |
| InferEdgeOrchestrator | Operation layer after deployment validation: scheduling, overload control, and runtime telemetry | https://github.com/gwonxhj/InferEdgeOrchestrator |

## Real-Device Evidence

[Jetson Orin Nano Internal Lab](https://github.com/gwonxhj/jetson-orin-nano-internal-lab)
provides hardware-level runtime evidence, including TensorRT, ONNX Runtime,
YOLO, Whisper, FastAPI serving, telemetry logs, sustained multi-workload
interaction evidence, and InferEdge-compatible handoff artifacts.

For the submission-ready diagram and layer split, start with
[InferEdge Ecosystem 1-Page Summary](docs/ecosystem_1page.md).

## Quick Start

Clone this entrypoint repo first:

```bash
git clone https://github.com/gwonxhj/InferEdge.git
cd InferEdge
```

Clone all pipeline repositories:

```bash
bash scripts/clone_all.sh --locked
```

This creates:

```text
repos/
├─ InferEdgeForge
├─ InferEdge-Runtime
├─ InferEdgeLab
└─ InferEdgeAIGuard
```

Run the portfolio smoke checks:

```bash
bash scripts/smoke_all.sh
```

Run the Reliable Edge Agent Runtime extension smoke when the supporting
Orchestrator repo is available in the same workspace:

```bash
bash scripts/demo_agent_runtime_e2e.sh

# Optional: run the explicit device_local starter path.
bash scripts/demo_agent_runtime_e2e.sh --device-local

# Optional: replace the device-local starter fixtures with local inputs.
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --vision-input ../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm \
  --voice-ingress-payload ../InferEdgeOrchestrator/examples/inputs/voice_ingress_requests.json \
  --capture-process-resource-snapshot

# Optional: add a lightweight ONNX Runtime probe to the Vision producer.
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --vision-input ../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm \
  --vision-onnx-model /path/to/vision_model.onnx

# Optional: generate a tiny detector-like ONNX probe model locally.
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --vision-input ../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm \
  --generate-vision-detector-probe

# Optional: route a captured Jetson tegrastats log through the same timeline.
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --tegrastats-log /path/to/tegrastats.log

# Optional: capture Jetson tegrastats during the Orchestrator sustained run.
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --vision-input ../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm \
  --vision-onnx-model /path/to/vision_model.onnx \
  --capture-tegrastats

# Optional: also replay the file-based remote worker selection starter.
bash scripts/demo_agent_runtime_e2e.sh --remote-dispatch
```

This reproduces the file-based chain from `agent_manifest` to Runtime
`result.agent`, Orchestrator scheduling evidence, AIGuard runtime reliability
analysis, and the Lab-owned Agent Runtime Reliability report.
The entrypoint smoke now also verifies that Lab preserves Orchestrator operation
context, including queue state, worker health, runtime event summary, and
timeline samples in JSON/Markdown reports.
With `--remote-dispatch`, the same script also writes Orchestrator's
file-based remote worker selection result. This is a remote dispatch starter
contract with worker selection, retry/fallback planning, and plan-only
execution metadata, not production SSH/HTTP remote execution.
The current extension smoke uses the latest Orchestrator producer-backed
sustained path: Vision reads a local image fixture, Voice-Command replays a
FastAPI-style request burst fixture, and Safety-Monitor reads resource snapshot
telemetry. It checks queue-depth, policy decision reason,
`multi_workload_sustained_summary`, producer source markers, optional
`tegrastats_timeline`, AIGuard `profiled_workload_pressure` /
`thermal_resource_pressure`, and Lab `sustained_overload_review` evidence
before live device-local sustained validation is added. Use `--device-local` to
replay the committed local image, request, and resource snapshot producers in
Orchestrator `scenario_mode=device_local`.
For local device experiments, keep `--device-local` and pass
`--vision-input`, optional `--vision-onnx-model`, `--voice-ingress-payload`, and
either `--resource-snapshot` or `--capture-process-resource-snapshot` to reuse
the same entrypoint script with runtime input overrides. The ONNX option records
provider, input/output shapes, and probe latency as lightweight Vision producer
evidence; `--tegrastats-log` can carry a captured Jetson/resource log through
the Orchestrator `tegrastats_timeline`; `--capture-tegrastats` captures Jetson
telemetry during the Orchestrator run when the `tegrastats` command is
available. These options do not claim a full live YOLO/Whisper/FastAPI
sustained service. See
[`docs/agent_runtime_e2e_demo.md`](docs/agent_runtime_e2e_demo.md) for the
minimum committed sample paths and a resource-snapshot variant.
Use `--generate-vision-detector-probe` when you want a reproducible detector-like
ONNX probe without committing a model artifact.

Recent Jetson starter validation:

| Evidence | Value |
|---|---:|
| Device mode | Jetson Orin Nano 25W |
| Scenario | `device_local` starter with live `tegrastats` log |
| Frames | 64 |
| Max queue depth | 6 |
| Dropped / fallback count | 61 / 61 |
| Deadline misses | 0 |
| Parsed `tegrastats` samples | 4 |
| Max temperature | 39.625 C |
| Max RAM used | 1783 MB |
| Lab decision | `blocked` from runtime reliability review rules |

This record proves the starter path can carry live Jetson resource telemetry
through Orchestrator, AIGuard, and Lab reports. It is still a device-local
starter smoke, not a claim of full live YOLO/Whisper/FastAPI sustained
validation.

Recent Jetson ONNX probe validation:

| Evidence | Value |
|---|---:|
| Device mode | Jetson Orin Nano 25W |
| Scenario | `device_local` starter with Vision ONNX Runtime probe |
| Frames | 16 |
| Vision probe backend | `onnxruntime` / `CPUExecutionProvider` |
| Vision probe output shape | `[1, 2]` |
| Vision probe latency | 1.255 ms |
| Max queue depth | 6 |
| Dropped / fallback count | 13 / 13 |
| Deadline misses | 1 |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` from runtime reliability review rules |

This second record validates that the entrypoint can pass a local ONNX model
into the Jetson device-local Vision producer and preserve ONNX Runtime probe
evidence through Orchestrator, AIGuard, and Lab reports. The probe used a tiny
identity ONNX model, so it should be described as device-local ONNX probe
evidence rather than full live YOLO validation.

Recent captured tegrastats handoff validation:

| Evidence | Value |
|---|---:|
| Device mode | Jetson Orin Nano 25W |
| Scenario | `device_local` starter with `--tegrastats-log` |
| Captured log duration | ~12 seconds |
| Parsed `tegrastats` samples | 11 |
| Frames | 16 |
| Vision probe backend | `onnxruntime` / `CPUExecutionProvider` |
| Max queue depth | 6 |
| Dropped / fallback count | 13 / 13 |
| Deadline misses | 1 |
| Max temperature | 41.5 C |
| Max RAM used | 830 MB |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` from runtime reliability review rules |

This record validates the new `--tegrastats-log` entrypoint option with a
captured Jetson log. It is telemetry handoff evidence, not a full thermal
endurance or live workload validation.

Recent generated detector probe validation:

| Evidence | Value |
|---|---:|
| Scenario | local `device_local` starter with generated detector-like ONNX probe |
| Generated model | `generated_models/detector_tiny.onnx` |
| Vision probe backend | `onnxruntime` / `CPUExecutionProvider` |
| Vision input shape | `[1, 3, 16, 16]` |
| Vision output shape | `[1, 6]` |
| Frames | 8 |
| Max queue depth | 6 |
| Dropped / fallback count | 5 / 5 |
| Lab decision | `blocked` from runtime reliability review rules |

This record validates a reproducible detector-like ONNX probe generated at run
time. It is closer to image-shaped perception work than the identity probe, but
it is still not full live YOLO validation.

Recent Jetson generated detector probe smoke:

| Evidence | Value |
|---|---:|
| Device | Jetson Orin Nano |
| Scenario | `device_local` starter with generated detector-like ONNX probe |
| Vision probe backend | `onnxruntime` / `CPUExecutionProvider` |
| Vision input shape | `[1, 3, 16, 16]` |
| Vision output shape | `[1, 6]` |
| Frames | 16 |
| Max queue depth | 6 |
| Dropped / fallback count | 13 / 13 |
| Deadline missed count | 1 |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` from runtime reliability review rules |

This record validates the same entrypoint chain on Jetson using a generated
detector-like probe. It is device-local smoke evidence, not full live YOLO or
thermal endurance validation.

Recent Jetson YOLOv8n ONNX probe smoke:

| Evidence | Value |
|---|---:|
| Device | Jetson Orin Nano |
| Model | user-provided `yolov8n.onnx` |
| Scenario | `device_local` starter with real ONNX model probe |
| Vision probe backend | `onnxruntime` / `CPUExecutionProvider` |
| Vision input shape | `[1, 3, 640, 640]` |
| Vision output shape | `[1, 84, 8400]` |
| Frames | 16 |
| Max queue depth | 6 |
| Dropped / fallback count | 13 / 13 |
| Deadline missed count | 10 |
| Vision probe elapsed range | `120.147-146.878 ms` |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` from runtime reliability review rules |

This record validates the entrypoint chain with a real YOLOv8n ONNX model on
Jetson. It is still an ONNX Runtime probe inside the device-local orchestration
smoke, not a full live camera or decoded detection validation.

Recent Jetson YOLOv8n ONNX probe with live tegrastats capture:

| Evidence | Value |
|---|---:|
| Device | Jetson Orin Nano |
| Model | user-provided `yolov8n.onnx` |
| Scenario | `device_local` starter with `--capture-tegrastats` |
| Vision probe backend | `onnxruntime` / `CPUExecutionProvider` |
| Vision input/output shape | `[1, 3, 640, 640]` -> `[1, 84, 8400]` |
| Frames | 32 |
| Max queue depth | 6 |
| Dropped / fallback count | 29 / 29 |
| Deadline missed count | 18 |
| Parsed `tegrastats` samples | 4 |
| Max temperature / RAM | 43.937 C / 966 MB |
| Vision probe elapsed range | `119.912-137.729 ms` |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` from runtime reliability review rules |

This record ties a real YOLOv8n ONNX probe and live Jetson telemetry capture
into the same entrypoint evidence chain. It remains a device-local smoke, not
thermal endurance or live camera validation.

Latest Jetson device-local replay:

| Evidence | Value |
|---|---:|
| Device | Jetson Orin Nano 25W |
| Model | user-provided `yolov8n.onnx` |
| Scenario | `device_local` starter with real ONNX model + live `tegrastats` |
| Frames | 24 |
| Max queue depth | 6 |
| Dropped / fallback count | 21 / 21 |
| Deadline missed count | 14 |
| Parsed `tegrastats` samples | 3 |
| Max temperature / RAM | 38.687 C / 999 MB |
| Vision mean / p95 latency | 170.174 ms / 402.416 ms |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` from runtime reliability review rules |

This replay was run from the entrypoint script with `--device-local`,
`--vision-onnx-model`, `--capture-process-resource-snapshot`, and
`--capture-tegrastats`. It confirms the latest main branch still carries real
Jetson ONNX probe and live telemetry evidence through Orchestrator, AIGuard,
and Lab. The Lab report also preserves Runtime operation guard evidence
(`runtime_latency_budget_overrun`, `runtime_error_classification`). It is not a
decoded YOLO accuracy validation or sustained thermal endurance claim.

Open the Local Studio demo:

```bash
cd repos/InferEdgeLab
poetry run inferedgelab serve --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000/studio
```

Click `Load Demo Evidence` to replay the bundled ONNX Runtime CPU vs TensorRT
Jetson evidence, compare view, deployment decision context, and optional
AIGuard diagnosis cases.

## Reproducible Clone Modes

Use the verified lock file:

```bash
bash scripts/clone_all.sh --locked
```

Use the latest `main` branch from each repo:

```bash
bash scripts/clone_all.sh --latest
```

Update existing clones:

```bash
bash scripts/update_all.sh --latest
```

or return to the locked portfolio snapshot:

```bash
bash scripts/update_all.sh --locked
```

## Entrypoint Files

| File | Purpose |
|---|---|
| `repos.yaml` | Human-readable repository map |
| `repos.lock` | Verified commit snapshot used by `--locked` |
| `scripts/clone_all.sh` | Clone all InferEdge Core repositories |
| `scripts/update_all.sh` | Update existing clones to latest or locked state |
| `scripts/smoke_all.sh` | Run cross-repo portfolio smoke checks |
| `scripts/demo_agent_runtime_e2e.sh` | Replay the Reliable Edge Agent Runtime extension smoke |
| `docs/ecosystem_1page.md` | Submission-ready ecosystem diagram and three-question layer map |
| `docs/assets/inferedge_ecosystem_diagram.svg` | Reusable ecosystem diagram asset for README, portfolio pages, and slides |
| `docs/agent_runtime_e2e_demo.md` | Agent runtime contract-chain demo guide |
| `docs/portfolio_summary.md` | 30-second portfolio summary and one-line repository role map |
| `docs/interview_narrative.md` | Interview-ready narrative for explaining the ecosystem and Jetson evidence role |
| `docs/final_submission_rehearsal.md` | Clean-clone submission gate rehearsal and results |
| `docs/pipeline_map.md` | Pipeline map and repository responsibility guide |

## Current Demo Evidence

The canonical Local Studio demo evidence is maintained in InferEdgeLab and
InferEdge-Runtime:

| Evidence | Value |
|---|---:|
| TensorRT Jetson FP16 25W mean | 10.066401 ms |
| TensorRT Jetson FP16 25W p99 | 15.548438 ms |
| TensorRT Jetson FP16 25W FPS | 99.340373 |
| ONNX Runtime CPU mean | 45.4299 ms |
| ONNX Runtime CPU p99 | 49.2128 ms |
| ONNX Runtime CPU FPS | 22.0119 |
| Local Studio speedup | about 4.51x |
| YOLOv8 subset | 10 images / 89 ground-truth boxes |
| simplified mAP@50 | 0.1410 |
| precision / recall | 0.2941 / 0.1685 |

## Scope Boundary

Included:

- local-first validation workflow
- repository clone/update entrypoint
- Core 4 contract smoke orchestration
- Local Studio demo entrypoint
- README and documentation map

Not included:

- production SaaS infrastructure
- DB/Redis queue persistence
- auth/billing/upload flow
- cloud dashboard deployment
- automatic evaluation for arbitrary model families

## Primary Review Path

For a reviewer or interviewer, start here:

1. `docs/portfolio_summary.md`
2. `docs/interview_narrative.md`
3. `docs/final_submission_rehearsal.md`
4. This README
5. `docs/pipeline_map.md`
6. `repos/InferEdgeLab/README.md`
7. `repos/InferEdgeLab/docs/portfolio/inferedge_portfolio_submission.md`
8. `repos/InferEdge-Runtime/docs/reports/jetson_evidence_summary.md`
9. `repos/InferEdgeAIGuard/docs/detector_validation_matrix.md`
