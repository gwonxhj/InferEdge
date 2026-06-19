# InferEdge 파이프라인 맵

언어: [English](pipeline_map.md) | 한국어

이 문서는 한국어 빠른 안내서입니다. 대표/canonical 문서는
[InferEdge Pipeline Map](pipeline_map.md)입니다.

InferEdge entrypoint repo는 split repository 구조를 clone, inspect, smoke test할
수 있게 만드는 local-first coordination layer입니다.

## 세 가지 질문

| 질문 | 담당 흐름 |
|---|---|
| 이 모델을 배포해도 되는가? | Forge -> Runtime -> Lab (+ optional AIGuard) |
| 이 benchmark evidence를 믿고 비교할 수 있는가? | InferEdgeEnv |
| 배포된 workload가 부하 상황에서도 안정적인가? | InferEdgeOrchestrator |

## Evidence 스냅샷

| 항목 | 현재 evidence |
|---|---|
| Core 4 validation contract | Forge -> Runtime -> Lab (+ optional AIGuard) |
| TensorRT Jetson FP16 | 10.066 ms mean, 15.548 ms p99, 99.34 FPS |
| ONNX Runtime CPU baseline | 45.430 ms mean, 49.213 ms p99, 22.01 FPS |
| Jetson device-local replay | 96 frames, 155.86 ms mean, 156.877 ms p95, max 45.5 C / 1000 MB RAM |
| Jetson 5-minute-class replay | 3600 frames, Vision mean 152.77 ms, p95 156.948 ms, max 50.375 C / 1038 MB RAM |
| Jetson quick-scan registry | 연결된 metric snapshot 값과 `Duration Comparison Summary`, `Operation Quick Scan Summary` local reviewer navigation |

Jetson evidence는 submission-facing metric을 보여주는 `representative snapshot`
report와 local reviewer navigation을 위한 `latest registry`를 분리합니다.
registry는 연결된 metric snapshot 값을 참조하지만 metric record owner가
되지는 않습니다. `quick-scan navigation`은 duration과 queue/deadline/fallback
pressure metadata를 노출하지만 production runtime operation proof가 아닙니다.

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

| Repository | 책임 | 소유하지 않는 것 |
|---|---|---|
| InferEdgeForge | build/provenance/handoff, `metadata.json`, `manifest.json` | Runtime execution, Lab deployment decision |
| InferEdge-Runtime | inference execution, latency/FPS/backend/device evidence, Lab-compatible `result.json` | deployment decision, scheduler, registry |
| InferEdgeLab | compare/evaluate/report/API/Local Studio, Lab-owned deployment decision | build artifact 생성, scheduler behavior |
| InferEdgeAIGuard | optional AIGuard `guard_analysis`, deterministic evidence items | final deployment decision, LLM guessing |
| InferEdgeEnv | registry, replay, comparability, runtime regression evidence | production DB/cloud registry, Lab decision |
| InferEdgeOrchestrator | worker selection, queue/deadline/fallback, runtime operation context | production cloud orchestration, deployability decision |

## Runtime Operation Starter Evidence Chain

```text
Orchestrator remote dispatch / device-local starter
-> EdgeEnv local evidence preservation
-> optional AIGuard deterministic warning/review evidence
-> Lab operation-risk report
-> Lab-owned deployment decision
```

이 chain은 Core 4 validation contract를 바꾸지 않고 operation evidence를 추가합니다.

책임 분리:

- Orchestrator는 worker selection, fallback, queue/deadline/runtime event context를 제공합니다.
- EdgeEnv는 registry, replay, comparability, handoff context를 보존합니다.
- AIGuard는 deterministic warning/review evidence를 제공합니다.
- Lab은 Runtime Intelligence / operation-risk report와 최종 deployment decision을 소유합니다.

이 경로는 remote dispatch starter evidence 또는 device-local operation evidence로
설명해야 합니다. production SSH/HTTP execution, long-lived worker operation,
secure tunnel operation, cloud orchestration, production observability platform으로
설명하지 않습니다.

Lab report summary와 generated `00_evidence_index.*` artifact의 공통 reviewer
marker-gate 상세 vocabulary는 [Agent Runtime E2E Demo](agent_runtime_e2e_demo.ko.md)에
둡니다. 이 pipeline map은 repo contract-boundary view이며 세부 marker
vocabulary owner가 아닙니다.
smoke-gated evidence-index boundary는 `00_evidence_index.md`를 Lab report
owner나 source contract가 아니라 reviewer navigation으로 유지합니다.
run registry도 같은 boundary를 multi-run review용 machine-readable
`evidence_index_boundary_summary` metadata로 보존합니다.
현재 handoff gate는 EdgeEnv handoff context의 policy-pressure summary run ID가
AIGuard `guard_analysis` raw context까지 보존되는지도 확인한 뒤 Lab
operation-risk report로 넘깁니다.

## Contract Boundaries

조용히 깨뜨리면 안 되는 contract:

- Forge `metadata.json`
- Forge `manifest.json`
- Runtime `result.json`
- Lab compare output
- Lab deployment decision output
- AIGuard `guard_analysis`

변경이 필요하면 backward-compatible하게 설계하거나 명시적으로 문서화하고
cross-repo smoke로 검증해야 합니다.

## Recommended Smoke Order

```bash
bash scripts/clone_all.sh --locked
bash scripts/smoke_all.sh
```

## Scope Boundary

InferEdge는 production SaaS platform, production observability platform,
Kubernetes-style orchestration, general monitoring SaaS, cloud control plane으로
제시하지 않습니다. DB/queue/auth/billing, file upload, cloud dashboard deployment,
production remote execution, production worker daemon은 현재 완료 범위가 아닙니다.
