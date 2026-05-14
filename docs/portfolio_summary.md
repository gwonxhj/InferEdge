# InferEdge Portfolio Summary

InferEdge is a local-first Edge AI inference validation pipeline that turns an ONNX model into traceable build artifacts, real runtime evidence, structured evaluation, optional diagnosis, and a Lab-owned deployment decision.

## 30-Second Structure

```text
Validation path:
ONNX Model
-> InferEdgeForge
-> InferEdge-Runtime
-> InferEdgeLab
-> optional InferEdgeAIGuard
-> Deployment Decision Report
-> Local Studio

Supporting layers:
InferEdgeEnv -> run evidence registry / comparability checker
InferEdgeOrchestrator -> post-deployment runtime operation control
```

## Repository Roles

| Repository | One-line role | Boundary |
|---|---|---|
| InferEdge | Multi-repository entrypoint and reproducible clone/smoke map | Orchestrates review flow; does not replace individual repo contracts |
| InferEdgeForge | Build provenance and artifact handoff layer | Creates metadata/manifest evidence; does not run inference or decide deployment |
| InferEdge-Runtime | C++ execution and Lab-compatible result export layer | Runs/profiles artifacts and exports result JSON; does not own comparison policy |
| InferEdgeLab | Validation, comparison, report, API, Local Studio, and deployment decision layer | Owns `deployment_decision`; consumes evidence rather than generating build artifacts |
| InferEdgeAIGuard | Optional deterministic diagnosis evidence layer | Adds `guard_analysis`; does not make the final deployment decision |
| InferEdgeEnv | Local-first run evidence registry and comparability checker | Records whether benchmark evidence can be trusted and compared; does not validate deployability |
| InferEdgeOrchestrator | Post-deployment runtime operation-control layer | Schedules and sheds load after deployment; does not decide whether a model should deploy |

## Core Message

The Core 4 validation path is:

- Forge preserves build identity.
- Runtime records real execution evidence.
- Lab compares, evaluates, reports, and decides.
- AIGuard optionally explains suspicious evidence.

The supporting layers stay separate:

- Env records benchmark evidence and comparability.
- Orchestrator controls runtime behavior after deployment.

## What To Show First

For an external reviewer, use this order:

1. This summary.
2. `README.md`.
3. `docs/pipeline_map.md`.
4. `repos/InferEdgeLab/README.md`.
5. `repos/InferEdgeLab/docs/portfolio/inferedge_portfolio_submission.md`.
6. `repos/InferEdge-Runtime/docs/reports/jetson_evidence_summary.md`.
7. `repos/InferEdgeAIGuard/docs/detector_validation_matrix.md`.

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
