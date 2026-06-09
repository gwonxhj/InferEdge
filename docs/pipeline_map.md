# InferEdge Pipeline Map

Language: English | [한국어](pipeline_map.ko.md)

InferEdge is a multi-repository, local-first Edge AI inference validation and
runtime-evidence pipeline. This entrypoint repository exists to make the split
repository structure easy to clone, inspect, and smoke test.

## Three Questions

```text
Can we deploy this model?
-> Forge -> Runtime -> Lab (+ optional AIGuard)

Can this benchmark evidence be trusted and compared?
-> InferEdgeEnv

Can deployed workloads stay stable under load?
-> InferEdgeOrchestrator
```

## Evidence Snapshot

| Signal | Evidence |
|---|---|
| Core validation path | Forge -> Runtime -> Lab (+ optional AIGuard) |
| TensorRT Jetson FP16 | 10.066 ms mean, 15.548 ms p99, 99.34 FPS |
| ONNX Runtime CPU baseline | 45.430 ms mean, 49.213 ms p99, 22.01 FPS |
| Jetson device-local replay | 96 frames, 155.86 ms mean, max 45.5 C / 1000 MB RAM |
| Jetson 5-minute-class replay | 3600 frames, Vision mean 152.77 ms, max 50.375 C / 1038 MB RAM |

Jetson evidence is split between `representative snapshot` reports for
submission-facing metrics and the `latest registry` for local reviewer
navigation. `quick-scan navigation` exposes duration and
queue/deadline/fallback pressure metadata; it is not production runtime
operation proof.

## Pipeline

```text
ONNX Model
-> InferEdgeForge
-> InferEdge-Runtime
-> InferEdgeLab
-> optional InferEdgeAIGuard
-> Deployment Decision Report
-> Local Studio
```

## Repository Responsibilities

| Repository | Owns | Does not own |
|---|---|---|
| InferEdgeForge | build/provenance/handoff, `metadata.json`, `manifest.json`, source/artifact identity | Runtime execution, scheduling, deployment decision |
| InferEdge-Runtime | inference execution, Lab-compatible `result.json`, latency/FPS/backend/device evidence, runtime health snapshot | build provenance, registry, anomaly detection, scheduling, deployment decision |
| InferEdgeLab | compare/evaluate/report/API/Local Studio, Lab-owned deployment decision | build artifact creation, deterministic diagnosis ownership, scheduler behavior |
| InferEdgeAIGuard | optional `guard_analysis`, deterministic warning/diagnosis evidence items | final deployment decision, LLM root-cause inference, production monitoring |
| InferEdgeEnv | registry, replay, comparability judgement, runtime regression evidence | production DB/cloud registry, Lab decision, general monitoring SaaS |
| InferEdgeOrchestrator | worker selection, queue/deadline/fallback, runtime operation context, worker health evidence | Kubernetes replacement, cloud orchestration platform, deployability decision, completed production scheduler |

## Runtime Operation Starter Evidence Chain

Runtime Operation Platform v2 adds operation evidence without changing the Core
4 validation contracts. The current remote-dispatch and device-local starter
paths follow this bounded chain:

```text
Orchestrator remote dispatch / device-local starter
-> EdgeEnv local evidence preservation
-> optional AIGuard deterministic warning/review evidence
-> Lab operation-risk report
-> Lab-owned deployment decision
```

Responsibility split:

- **Orchestrator** owns worker selection evidence, starter execution status,
  fallback status, queue/deadline/fallback markers, worker health evidence, and
  runtime event summaries.
- **InferEdgeEnv** owns registry, replay, comparability, and handoff context
  preservation. It does not verify production remote execution and does not
  control workers.
- **InferEdgeAIGuard** owns optional deterministic warning evidence such as
  remote dispatch failure, fallback recovery, queue pressure, or runtime
  reliability warnings. It does not make the final deployment decision.
- **InferEdgeLab** owns the operation-risk report and final deployment decision
  context.

This chain should be described as remote dispatch starter evidence,
device-local operation evidence, or a remote worker selection contract. It
should not be described as production SSH/HTTP execution, long-lived worker
operation, secure tunnel operation, production retry/failover, cloud
orchestration, or a production observability platform.

The submission-ready diagram is in
[Ecosystem 1-Page Summary](ecosystem_1page.md)
([한국어: 생태계 1페이지 요약](ecosystem_1page.ko.md)).

## Contract Boundaries

Do not silently break:

- Forge `metadata.json`
- Forge `manifest.json`
- Runtime `result.json`
- Lab compare output
- Lab deployment decision output
- AIGuard `guard_analysis`

Contract changes should be backward-compatible or explicitly documented and
validated with cross-repo smoke checks.

## Recommended Smoke Order

From this entrypoint repo:

```bash
bash scripts/clone_all.sh --locked
bash scripts/smoke_all.sh
```

For local development where the repos already exist elsewhere:

```bash
INFEREDGE_REPOS_DIR=/Users/GwonHyeokJun/Documents/GitHub bash scripts/smoke_all.sh
```

## Scope Boundary

InferEdge is not presented as a production SaaS platform, production
observability platform, Kubernetes-style orchestration system, general
monitoring SaaS, or cloud control plane. DB/queue/auth/billing, file upload,
cloud dashboard deployment, production remote execution, and production worker
daemons are outside the completed scope.
