# InferEdge Portfolio Summary

InferEdge is a local-first Edge AI inference validation pipeline that turns an ONNX model into traceable build artifacts, real runtime evidence, structured evaluation, optional diagnosis, and a Lab-owned deployment decision.

## 30-Second Structure

```text
Can we deploy this model?
-> Forge -> Runtime -> Lab (+ optional AIGuard)

Can this benchmark evidence be trusted and compared?
-> InferEdgeEnv v0.1.5 comparability layer

Can deployed workloads stay stable under load?
-> InferEdgeOrchestrator operation layer
```

For a diagram-first version of this same structure, see
[InferEdge Ecosystem 1-Page Summary](ecosystem_1page.md).

Reusable first-slide / README visual:

```text
docs/assets/inferedge_ecosystem_diagram.svg
```

## Repository Roles

| Repository | One-line role | Boundary |
|---|---|---|
| InferEdge | Multi-repository entrypoint and reproducible clone/smoke map | Orchestrates review flow; does not replace individual repo contracts |
| InferEdgeForge | Build provenance and artifact handoff layer | Creates metadata/manifest evidence; does not run inference or decide deployment |
| InferEdge-Runtime | C++ execution and Lab-compatible result export layer | Runs/profiles artifacts and exports result JSON; does not own comparison policy |
| InferEdgeLab | Validation, comparison, report, API, Local Studio, and deployment decision layer | Owns `deployment_decision`; consumes evidence rather than generating build artifacts |
| InferEdgeAIGuard | Optional deterministic diagnosis evidence layer | Adds `guard_analysis`; does not make the final deployment decision |
| InferEdgeEnv | v1-complete local-first run evidence registry and comparability checker | Records whether benchmark evidence can be trusted and compared; does not validate deployability |
| InferEdgeOrchestrator | Post-deployment runtime operation-control layer | Schedules and sheds load after deployment; does not decide whether a model should deploy |

## Core Message

The Core 4 validation path is:

- Forge preserves build identity.
- Runtime records real execution evidence.
- Lab compares, evaluates, reports, and decides.
- AIGuard optionally explains suspicious evidence.

The ecosystem extension layers stay separate:

- Env records benchmark evidence and comparability. Its `v0.1.5` release freezes this role as the v1-complete baseline.
- Orchestrator controls runtime behavior after deployment.

## Implementation Status

This status table prevents roadmap language from being read as completed
production capability.

| Capability | Status | Portfolio wording |
|---|---|---|
| Core 4 validation pipeline | Implemented | Local-first validation pipeline with provenance, Runtime evidence, Lab decision, and optional AIGuard evidence |
| Local Studio | Implemented | Browser-based local workflow for demo evidence replay, compare, decision, and AIGuard cases |
| Evaluation / contract validation | Implemented | YOLOv8 COCO subset, simplified mAP50, bbox/score/model contract evidence |
| AIGuard diagnosis cases | Implemented | Deterministic evidence for bbox collapse, score saturation, temporal instability, and baseline deviation |
| Runtime operation e2e chain | Implemented | Entrypoint smoke connects agent manifest, Runtime result, Orchestrator summary, AIGuard analysis, and Lab report |
| Orchestrator operation evidence in Lab report | Implemented | Lab surfaces AIGuard `worker_health_degradation` and `scheduler_delay_pattern` context from Orchestrator telemetry |
| Producer-backed sustained workload path | Smoke/Starter | Reproducible scheduling/drop/fallback evidence, not a production scheduler |
| Jetson ONNX + `tegrastats` replay | Smoke/Starter | Device-local smoke evidence with live telemetry handoff, not decoded YOLO accuracy or thermal endurance validation |
| Remote dispatch/fallback | Smoke/Starter | Worker selection/fallback starter evidence, not production remote execution |
| Live camera, Whisper/FastAPI sustained services, Cloudflare hardening, dashboard | Future Work | Roadmap only |

## Device-Local Sustained Validation Starter

The current runtime-operation extension is a local-first starter, not a full
production remote execution system. It lets a reviewer replay the same
contract chain with committed Orchestrator input fixtures, then replace those
fixtures with local device inputs when available.

Assuming `InferEdgeOrchestrator` is cloned next to this entrypoint repo, the
minimum committed sample inputs are:

| Workload | Sample input path | Purpose |
|---|---|---|
| Vision | `../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm` | Local image producer input |
| Voice / Command | `../InferEdgeOrchestrator/examples/inputs/voice_ingress_requests.json` | FastAPI-style request burst fixture |
| Safety / Monitor | `../InferEdgeOrchestrator/examples/inputs/safety_resource_snapshots.json` | Resource snapshot fixture |

Replay the committed device-local starter:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --output-dir /tmp/inferedge_agent_runtime_device_local \
  --frames 8
```

Replay the same chain with the remote dispatch starter:

```bash
bash scripts/demo_agent_runtime_e2e.sh --remote-dispatch \
  --output-dir /tmp/inferedge_agent_runtime_remote_dispatch \
  --frames 8
```

This adds `06_remote_dispatch_result.json` with remote worker selection
evidence, worker selection reasons, retry/fallback planning,
`remote_execution_plan`, and `remote_execution_result`. It also adds
`07_remote_dispatch_guard_analysis.json` so AIGuard can explain the remote
dispatch starter evidence. Use `--remote-execute-plan` to explicitly request
the HTTP/SSH starter execution path when a worker registry entry supports it;
the committed file-contract fixture records skipped starter evidence. This
proves the worker registry/task request/remote execution starter contract, not
production remote worker execution.

Remote fallback recovery can also be replayed with the committed
`examples/remote_fallback` fixtures. Start only the local fallback HTTP starter
worker on port `8765`, then run the entrypoint smoke with `--remote-execute-plan`
and the fallback registry/request overrides. The resulting evidence chain is:

```text
primary-http-worker connection_error
-> fallback-http-worker starter succeeds
-> AIGuard remote_execution_recovered_by_fallback
-> Lab Remote fallback starter evidence
```

This shows bounded recovery evidence propagation. It is still a starter smoke,
not production-grade remote retry control.

The generated `00_evidence_index.json` files can be combined into a local
entrypoint navigation registry so the device-local probe/process path and
remote fallback path are reviewed side by side. This registry is only a
navigation and comparison layer; it preserves links back to the source
Orchestrator, AIGuard, Lab, and remote dispatch artifacts instead of replacing
those contracts or InferEdgeEnv's run evidence registry / comparability checker.

The current Lab report also has a dedicated `AIGuard Orchestrator Operation
Evidence` section. It preserves `worker_health_degradation` and
`scheduler_delay_pattern` when AIGuard explains Orchestrator worker health or
scheduler-delay telemetry, including worker reason summaries and policy/drop
reason counts. This is deployment context for Lab-owned decisions, not a change
in final decision ownership.

Replay the same entrypoint with explicit local input overrides:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --output-dir /tmp/inferedge_agent_runtime_device_local_inputs \
  --frames 8 \
  --vision-input ../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm \
  --voice-ingress-payload ../InferEdgeOrchestrator/examples/inputs/voice_ingress_requests.json \
  --resource-snapshot ../InferEdgeOrchestrator/examples/inputs/safety_resource_snapshots.json
```

If no local ONNX model should be committed but a vision-shaped probe is needed,
add `--generate-vision-detector-probe`. This creates a small detector-like ONNX
artifact inside the output directory and routes it through the same Vision
producer probe path. It is stronger than the identity probe for workflow
evidence, but it is still not full live YOLO validation.
The local validation run generated `detector_tiny.onnx`, preserved
`CPUExecutionProvider`, input shape `[1, 3, 16, 16]`, output shape `[1, 6]`,
and carried the resulting runtime reliability evidence into a Lab `blocked`
decision.
The same entrypoint path was replayed on Jetson Orin Nano with 16 frames,
max queue depth 6, dropped/fallback count 13/13, one deadline miss, and a Lab
`blocked` decision. This is device-local smoke evidence, not full live YOLO or
thermal endurance validation.
Using a real user-provided `yolov8n.onnx` probe on Jetson preserved
`CPUExecutionProvider`, input shape `[1, 3, 640, 640]`, output shape
`[1, 84, 8400]`, 16 frames, max queue depth 6, dropped/fallback count 13/13,
10 deadline misses, and a Lab `blocked` decision. This is a real ONNX model
probe through the orchestration contract chain, not decoded YOLO accuracy or
live camera validation.
The same real model probe was then replayed with live `--capture-tegrastats`:
32 frames, max queue depth 6, dropped/fallback count 29/29, 18 deadline misses,
4 parsed `tegrastats` samples, max temperature 43.937 C, max RAM 966 MB, and a
Lab `blocked` decision. This ties real ONNX model execution evidence and live
Jetson telemetry into one device-local smoke bundle, not a thermal endurance
claim.
A latest main-branch replay used the same Jetson Orin Nano 25W path with a
user-provided `yolov8n.onnx`, local image input, process resource snapshot
capture, and live `tegrastats` capture. It ran 96 frames, reached max queue
depth 6, recorded dropped/fallback count 93/93, 50 deadline misses, parsed 9
`tegrastats` samples, and preserved max temperature 39.0 C / max RAM 979 MB.
The Vision ONNX probe reported mean/p95 latency 156.43 ms / 159.629 ms, while
AIGuard reported `blocked` / `high` and Lab produced a `blocked` decision. The
Lab report also preserved Runtime operation guard evidence
(`runtime_latency_budget_overrun`, `runtime_error_classification`). This is
current-main device-local ONNX probe and telemetry handoff evidence from a
longer 96-frame starter replay, not decoded YOLO accuracy, live camera, or
thermal endurance validation.
The submission-facing Lab evidence snapshot is stored in
[`Jetson Device-Local Agent Runtime Evidence Report`](evidence/jetson_device_local_agent_runtime_report.md).
The clean Jetson replay runbook uses a temporary Forge clone under `/tmp` so
dirty local Jetson Forge/Runtime worktrees do not need to be deleted or reset
for reproduction.

For a minimal live local resource signal, replace `--resource-snapshot` with
`--capture-process-resource-snapshot`. This records process-level resource
evidence only; it should not be described as full Jetson thermal validation.
If a Jetson `tegrastats` log was captured separately, pass
`--tegrastats-log /path/to/tegrastats.log` to the same entrypoint smoke. The
script copies that log into the evidence bundle and routes it through
Orchestrator `tegrastats_timeline`, AIGuard, and the Lab report without
claiming full thermal endurance validation.
On Jetson, `--capture-tegrastats` can capture telemetry during the Orchestrator
sustained run and route the live captured log through the same evidence path.
This remains device-local smoke evidence, not a thermal endurance claim.

Jetson starter validation has also been checked on a Jetson Orin Nano in 25W
mode using the same `device_local` starter flow with live `tegrastats` capture.
The observed starter run used 64 frames, reached max queue depth 6, recorded
61 dropped tasks and 61 fallback events, had 0 deadline misses, parsed 4
`tegrastats` samples, and reported max temperature 39.625 C / max RAM 1783 MB.
This is useful as a portfolio evidence bridge because it shows live Jetson
resource telemetry flowing through Orchestrator -> AIGuard -> Lab, while still
remaining below the claim level of full live YOLO/Whisper/FastAPI sustained
validation.

A follow-up Jetson ONNX probe run used the same entrypoint `device_local` path
with `--vision-onnx-model`. It ran 16 frames on Jetson Orin Nano 25W,
preserved `vision_inference_backend=onnxruntime`, `CPUExecutionProvider`,
output shape `[1, 2]`, and 1.255 ms probe latency in the Orchestrator summary,
then carried `blocked` / `high` AIGuard evidence into a Lab `blocked` decision.
This is device-local ONNX Runtime probe evidence using a tiny identity model,
not full live YOLO validation.

The new `--tegrastats-log` option was then validated with a separately captured
~12 second Jetson log. The entrypoint parsed 11 `tegrastats` samples, preserved
max temperature 41.5 C and max RAM 830 MB, and carried the same device-local
ONNX probe path into AIGuard `blocked` / `high` evidence and a Lab `blocked`
decision. This is captured telemetry handoff evidence, not full thermal
endurance validation.

## What To Show First

For an external reviewer, use this order:

1. `docs/ecosystem_1page.md`.
2. This summary.
3. `docs/interview_narrative.md`.
4. `README.md`.
5. `docs/pipeline_map.md`.
6. `repos/InferEdgeLab/README.md`.
7. `repos/InferEdgeLab/docs/portfolio/inferedge_portfolio_submission.md`.
8. `repos/InferEdge-Runtime/docs/reports/jetson_evidence_summary.md`.
9. `repos/InferEdgeAIGuard/docs/detector_validation_matrix.md`.

## What Not To Claim

- InferEdge is not a production SaaS dashboard.
- InferEdgeEnv is not the validation or deployment decision layer.
- InferEdgeOrchestrator is not the benchmark or validation layer.
- Runtime evidence is not a public leaderboard or single-score ranking.
- AIGuard is deterministic diagnosis evidence, not LLM guessing.

## Validation Entry

From this entrypoint repo:

```bash
bash scripts/clone_all.sh --locked
bash scripts/smoke_all.sh
```

For a workspace where the repositories already exist as siblings:

```bash
INFEREDGE_REPOS_DIR=/Users/GwonHyeokJun/Documents/GitHub bash scripts/smoke_all.sh
```
