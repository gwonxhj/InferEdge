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
```

This reproduces the file-based chain from `agent_manifest` to Runtime
`result.agent`, Orchestrator scheduling evidence, AIGuard runtime reliability
analysis, and the Lab-owned Agent Runtime Reliability report.

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
2. `docs/final_submission_rehearsal.md`
3. This README
4. `docs/pipeline_map.md`
5. `repos/InferEdgeLab/README.md`
6. `repos/InferEdgeLab/docs/portfolio/inferedge_portfolio_submission.md`
7. `repos/InferEdge-Runtime/docs/reports/jetson_evidence_summary.md`
8. `repos/InferEdgeAIGuard/docs/detector_validation_matrix.md`
