# InferEdge Portfolio Summary

Language: English | [한국어](portfolio_summary.ko.md)

InferEdge is a local-first Edge AI inference validation portfolio. It turns an
ONNX model into traceable build artifacts, real runtime evidence, structured
evaluation, optional deterministic diagnosis, and a Lab-owned deployment
decision.

## Portfolio Snapshot

| Signal | Evidence |
|---|---|
| Core validation path | Forge -> Runtime -> Lab (+ optional AIGuard) |
| Comparability layer | InferEdgeEnv v0.1.5 local registry / comparability / runtime regression evidence |
| Operation layer | InferEdgeOrchestrator queue/deadline/fallback and worker-health evidence |
| TensorRT Jetson FP16 | 10.066 ms mean, 15.548 ms p99, 99.34 FPS |
| ONNX Runtime CPU baseline | 45.430 ms mean, 49.213 ms p99, 22.01 FPS |
| Jetson device-local replay | 96 frames, 155.86 ms mean, max 45.5 C / 1000 MB RAM |
| Jetson 5-minute-class replay | 3600 frames, Vision mean 152.77 ms, max 50.375 C / 1038 MB RAM |

For the diagram-first version, see
[InferEdge Ecosystem 1-Page Summary](ecosystem_1page.md)
([한국어: InferEdge 생태계 1페이지 요약](ecosystem_1page.md)).

Reusable visual:

```text
docs/assets/inferedge_ecosystem_diagram.svg
```

## 30-Second Structure

```text
Can we deploy this model?
-> Forge -> Runtime -> Lab (+ optional AIGuard)

Can this benchmark evidence be trusted and compared?
-> InferEdgeEnv comparability layer

Can deployed workloads stay stable under load?
-> InferEdgeOrchestrator operation layer
```

The first screen should make this clear: InferEdge validates deployability,
EdgeEnv preserves and judges benchmark evidence, and Orchestrator provides
bounded operation-control context after deployment validation.

## Repository Roles

| Repository | One-line role | Boundary |
|---|---|---|
| InferEdge | Multi-repository entrypoint and reproducible clone/smoke map | Orchestrates review flow; does not replace individual repo contracts |
| InferEdgeForge | Build provenance and artifact handoff layer | Creates metadata/manifest evidence; does not run inference or decide deployment |
| InferEdge-Runtime | C++ execution and Lab-compatible result export layer | Runs/profiles artifacts and exports result JSON; does not own comparison policy |
| InferEdgeLab | Validation, comparison, report, API, Local Studio, and deployment decision layer | Owns `deployment_decision`; consumes evidence rather than generating build artifacts |
| InferEdgeAIGuard | Optional deterministic diagnosis evidence layer | Adds `guard_analysis`; does not make the final deployment decision |
| InferEdgeEnv | Local-first run evidence registry and comparability checker | Records whether benchmark evidence can be trusted and compared; does not validate deployability |
| InferEdgeOrchestrator | Runtime operation context provider | Records queue/deadline/fallback and worker-health evidence; does not decide whether a model should deploy |

## Implementation Status

| Capability | Status | Portfolio wording |
|---|---|---|
| Core 4 validation pipeline | Implemented | Local-first validation pipeline with provenance, Runtime evidence, Lab decision, and optional AIGuard evidence |
| Local Studio | Implemented | Browser-based local workflow for demo evidence replay, compare, decision, and AIGuard cases |
| Evaluation / contract validation | Implemented | YOLOv8 COCO subset, simplified mAP50, bbox/score/model contract evidence |
| AIGuard diagnosis cases | Implemented | Deterministic evidence for bbox collapse, score saturation, temporal instability, baseline deviation, and runtime warnings |
| Runtime Intelligence artifact gate | Implemented | Cross-repo smoke protects the Orchestrator -> EdgeEnv -> AIGuard -> Lab report/bundle markers |
| Producer-backed sustained workload path | Smoke/Starter | Reproducible scheduling/drop/fallback evidence, not a production scheduler |
| Jetson ONNX + `tegrastats` replay | Smoke/Starter | Device-local smoke evidence with live telemetry handoff, not decoded YOLO accuracy or thermal endurance validation |
| Remote dispatch/fallback | Smoke/Starter | Worker-selection/fallback evidence preserved through EdgeEnv, AIGuard, and Lab; not production remote execution |
| Live camera, Whisper/FastAPI sustained services, Cloudflare hardening, dashboard | Future Work | Roadmap only |

## Runtime Operation Starter Chain

The remote-dispatch/fallback path is valuable because it shows role separation
across repositories, not because it claims production remote operation.

```text
Orchestrator worker selection / fallback starter
-> EdgeEnv local registry and replay context
-> AIGuard deterministic warning evidence
-> Lab Runtime Intelligence / operation-risk report
-> Lab-owned deployment decision
```

Portfolio emphasis:

- Orchestrator records worker eligibility, selected/rejected worker reasons,
  starter execution status, fallback final status, and compact event summary.
- EdgeEnv preserves operation evidence as local registry / handoff context
  while leaving comparability and deployment decisions to their owning layers.
- AIGuard explains observed remote-dispatch failure or fallback recovery with
  deterministic evidence, not LLM root-cause guessing.
- Lab ties the evidence back to deployment risk and remains the final decision
  owner.

The fixture-only `scripts/smoke_remote_fallback_registry_marker.sh` keeps the
remote fallback marker path reproducible without a live HTTP worker. It must
preserve `remote_execution_recovered_by_fallback` and
`lab=Remote fallback starter evidence` in the generated registry/report path.

## Runtime Intelligence Marker Contract

The marker list below is intentionally compact. It protects reviewer navigation
without making the portfolio read like a production control plane.

| Area | Protected marker vocabulary |
|---|---|
| Artifact gate | `Runtime Intelligence artifact gate`, `Cross-repo smoke`, `Orchestrator -> EdgeEnv -> AIGuard -> Lab`, `directly gated Jetson preservation and remote fallback Lab markers` |
| EdgeEnv preservation | `Lab EdgeEnv preservation context`, `lab_report_preservation_context_present=True`, `lab_preservation=present`, `identity=jetson_device_local_preservation`, `path=device_local_starter` |
| Duration traceability | `Runtime replay duration scope`, `short 96-frame-class replay (96 frames)`, `scope_label=source=entrypoint_requested_frames`, `Validated Duration Traceability`, `runtime_intelligence_ci_artifact_gate_summary.md`, `duration_handoff_alignment`, `duration_source`, `duration_scope_label` |
| Handoff alignment | `EdgeEnv/AIGuard duration handoff alignment`, `duration_handoff_alignment_20260601`, EdgeEnv `de64d50` and AIGuard `7289899` |
| Operation pressure | `compact queue/deadline/fallback operation markers`, `Orchestrator queue/deadline/fallback markers`, `Queue pressure reasons`, `queue_pressure_reason`, `queue_pressure_reason=queue_backlog_threshold_exceeded`, `max_total_queue_depth`, `max_total_queue_depth=7`, `fallback_count`, `deadline_missed_count` |
| AIGuard / Lab traceability | `aiguard_raw_context: max_total_queue_depth traceability preserved`, `lab_expected_report_markers`, `lab_report_contract_context`, `aiguard_validates_expected_report_markers=false` |
| Remote fallback | `Remote fallback starter evidence`, `lab=Remote fallback starter evidence`, `remote_execution_recovered_by_fallback` |

These are local-first review markers. They do not make CI, telemetry
artifacts, or remote dispatch a production control plane.

## Device-Local / Jetson Evidence

| Evidence | Current record | Claim boundary |
|---|---|---|
| Device-local ONNX replay | Jetson Orin Nano 25W, 96 frames, 155.86 ms mean, 156.877 ms p95, max 45.5 C / 1000 MB RAM | Real ONNX probe and telemetry handoff, not decoded YOLO accuracy |
| EdgeEnv preservation replay | EdgeEnv run evidence stores `runtime_operation_summary`; Lab preserves `Runtime Intelligence EdgeEnv Preservation` | Registry/report preservation, not a deployment decision override |
| 5-minute-class sustained replay | 3600 frames, 281 `tegrastats` samples, Vision mean 152.77 ms, max 50.375 C / 1038 MB RAM | Smoke/Starter sustained evidence, not thermal endurance validation |

Submission-facing Lab evidence snapshot:
[`Jetson Device-Local Agent Runtime Evidence Report`](evidence/jetson_device_local_agent_runtime_report.md)
([한국어: Jetson 디바이스 로컬 에이전트 런타임 증거 보고서](evidence/jetson_device_local_agent_runtime_report.md)).

For the 5-minute-class sustained record, see
[`Jetson Device-Local 5-Minute Sustained Smoke Report`](evidence/jetson_device_local_5min_sustained_report.md)
([한국어: Jetson 디바이스 로컬 5분급 지속 스모크 보고서](evidence/jetson_device_local_5min_sustained_report.md)).

## What To Show First

For an external reviewer, use this order:

1. `docs/ecosystem_1page.md`
2. This summary
3. `README.md`
4. `docs/pipeline_map.md`
5. `docs/interview_narrative.md` ([한국어: 인터뷰 내러티브](interview_narrative.ko.md))
6. InferEdgeLab Local Studio / report evidence
7. InferEdge-Runtime Jetson/runtime reports
8. InferEdgeAIGuard detector validation matrix

## What Not To Claim

- InferEdge is not a production SaaS dashboard.
- InferEdge is not a production observability platform.
- GitLab/CI artifact automation is not a production control plane.
- InferEdgeEnv is not the validation or deployment decision layer.
- InferEdgeOrchestrator is not a Kubernetes-style or cloud orchestration system.
- Remote dispatch/fallback is not production SSH/HTTP remote execution.
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

The smoke validates Core 4 contract health, remote fallback marker preservation,
Agent Runtime EdgeEnv preservation, and the Runtime Intelligence artifact gate.
For full command history and generated artifact details, use
[`docs/agent_runtime_e2e_demo.md`](agent_runtime_e2e_demo.md).
