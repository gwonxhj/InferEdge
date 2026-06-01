# InferEdge Pipeline Map

InferEdge is a multi-repository, local-first Edge AI inference validation
pipeline. This entrypoint repository exists to make the split repository
structure easy to clone, inspect, and smoke test.

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

### InferEdgeForge

Build/provenance/handoff layer.

- creates TensorRT/RKNN-style build artifacts
- writes `metadata.json`
- writes `manifest.json`
- records source model hash and artifact hash
- preserves source/artifact identity for Runtime/Lab handoff

Forge does not own Runtime execution or Lab deployment decisions.

### InferEdge-Runtime

C++ execution/result export layer.

- executes ONNX Runtime CPU and TensorRT/Jetson style runtime paths
- writes Lab-compatible Runtime result JSON
- records latency mean/p50/p95/p99 and FPS
- records run configuration, backend, device, and Jetson evidence
- generates Jetson evidence Markdown reports

Runtime does not own deployment decisions. It exports evidence for Lab.

### InferEdgeLab

Validation/evaluation/report/deployment decision owner.

- imports Runtime result JSON
- compares backend/device evidence
- evaluates YOLOv8 COCO subset and model contract evidence
- generates Markdown/HTML reports
- owns `deployment_decision`
- serves Local Studio at `/studio`
- provides `core4-conformance-check` and `portfolio-demo-check`

Lab remains the final decision owner even when AIGuard evidence is present.

### InferEdgeAIGuard

Optional deterministic diagnosis evidence provider.

- produces `guard_analysis`
- explains bbox validity, score distribution, detection count drift, baseline
  deviation, temporal consistency, and provenance mismatch evidence
- emits `guard_verdict` and evidence items

AIGuard does not make final deployment decisions and does not use LLM guessing.

## Ecosystem Extension Layers

The pinned Core 4 validation smoke stays focused on Forge, Runtime, Lab, and
AIGuard. The full ecosystem portfolio adds two separate lifecycle layers.

- **InferEdgeEnv:** `v0.1.5` v1-complete experiment hygiene /
  comparability layer for local benchmark evidence trust and comparison
  judgement.
- **InferEdgeOrchestrator:** post-deployment runtime operation control,
  scheduling, overload control, and telemetry.

Role boundary:

- InferEdge Core: deployment validation before release.
- InferEdgeEnv: benchmark run evidence registry and comparability layer.
- InferEdgeOrchestrator: runtime operation control after deployment validation.

## Runtime Operation Starter Evidence Chain

Runtime Operation Platform v2 adds operation evidence without changing the Core
4 validation contracts. The current remote-dispatch starter follows this
bounded path:

```text
Orchestrator remote dispatch starter
-> EdgeEnv local evidence preservation
-> AIGuard deterministic warning/review evidence
-> Lab operation-risk report
-> Lab-owned deployment decision
```

Responsibility split:

- **Orchestrator** owns worker selection evidence, starter execution status,
  fallback status, queue / runtime event summaries, and the
  `operation_boundary=remote dispatch starter evidence only` marker.
- **InferEdgeEnv** owns registry, replay, comparability, and handoff context
  preservation. It does not verify production remote execution and does not
  control workers.
- **InferEdgeAIGuard** owns optional deterministic warning evidence such as
  remote dispatch failure or fallback recovery. It does not make the final
  deployment decision.
- **InferEdgeLab** owns the operation-risk report and final deployment decision
  context.

This chain should be described as remote dispatch starter evidence or a remote
worker selection contract. It should not be described as production SSH/HTTP
execution, long-lived worker operation, secure tunnel operation, production
retry/failover, or cloud orchestration.

The submission-ready diagram is in
[Ecosystem 1-Page Summary](ecosystem_1page.md)
([한국어: 생태계 1페이지 요약](ecosystem_1page.md)).

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

InferEdge is not presented as a production SaaS platform. DB/queue/auth/billing,
file upload, cloud dashboard deployment, and production worker daemons are
future work.
