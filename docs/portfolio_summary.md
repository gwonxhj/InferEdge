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

Replay the same entrypoint with explicit local input overrides:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --output-dir /tmp/inferedge_agent_runtime_device_local_inputs \
  --frames 8 \
  --vision-input ../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm \
  --voice-ingress-payload ../InferEdgeOrchestrator/examples/inputs/voice_ingress_requests.json \
  --resource-snapshot ../InferEdgeOrchestrator/examples/inputs/safety_resource_snapshots.json
```

For a minimal live local resource signal, replace `--resource-snapshot` with
`--capture-process-resource-snapshot`. This records process-level resource
evidence only; it should not be described as full Jetson thermal validation.
If a Jetson `tegrastats` log was captured separately, pass
`--tegrastats-log /path/to/tegrastats.log` to the same entrypoint smoke. The
script copies that log into the evidence bundle and routes it through
Orchestrator `tegrastats_timeline`, AIGuard, and the Lab report without
claiming full thermal endurance validation.

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
