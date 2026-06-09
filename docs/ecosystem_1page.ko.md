# InferEdge 생태계 1페이지 요약

언어: [English](ecosystem_1page.md) | 한국어

이 문서는 한국어 빠른 안내서입니다. 대표/canonical 문서는
[InferEdge Ecosystem 1-Page Summary](ecosystem_1page.md)입니다.

InferEdge는 Edge AI inference 프로젝트에서 자주 섞이는 세 질문을 분리합니다.

```text
이 모델을 배포해도 되는가?
이 benchmark evidence를 믿고 비교할 수 있는가?
배포된 workload가 부하 상황에서도 안정적인가?
```

## Evidence 스냅샷

| 항목 | 현재 evidence |
|---|---|
| Core validation path | Forge -> Runtime -> Lab (+ optional AIGuard) |
| Comparability layer | InferEdgeEnv local registry / comparability / runtime regression evidence |
| Operation layer | InferEdgeOrchestrator queue/deadline/fallback, worker-health evidence |
| TensorRT Jetson FP16 | 10.066 ms mean, 15.548 ms p99, 99.34 FPS |
| ONNX Runtime CPU baseline | 45.430 ms mean, 49.213 ms p99, 22.01 FPS |
| Jetson device-local replay | 96 frames, 155.86 ms mean, max 45.5 C / 1000 MB RAM |
| Jetson 5-minute-class replay | 3600 frames, Vision mean 152.77 ms, max 50.375 C / 1038 MB RAM |

Jetson evidence는 compact reviewer terms를 사용합니다. `representative snapshot`은
submission-facing metric report, `latest registry`는 최신 local navigation
record, `quick-scan navigation`은 duration과 queue/deadline/fallback pressure를
보는 metadata입니다. production runtime operation proof가 아닙니다.

## Layer 역할

| Layer | Project | 책임 |
|---|---|---|
| Validation | InferEdgeForge | build provenance, metadata, manifest, artifact handoff |
| Validation | InferEdge-Runtime | 실제 inference 실행과 Lab-compatible `result.json` export |
| Validation | InferEdgeLab | compare, evaluate, report, Lab-owned deployment decision |
| Validation | InferEdgeAIGuard | optional deterministic risk diagnosis evidence |
| Comparability | InferEdgeEnv | local run evidence registry와 comparability judgement |
| Operation | InferEdgeOrchestrator | queue, overload, fallback, runtime telemetry 기반 operation context |

## Canonical Ownership Matrix

이 표는 entrypoint README와 개별 레포 README에서 같은 ownership 용어를 쓰기
위한 compact 기준입니다.

| Project | 소유하는 것 | 소유하지 않는 것 |
|---|---|---|
| InferEdgeForge | build provenance / handoff evidence | Runtime execution, scheduling, deployment decision |
| InferEdge-Runtime | execution, Lab-compatible result, runtime health and telemetry seed evidence | build provenance, registry, anomaly detection, scheduling, deployment decision |
| InferEdgeLab | validation report와 Lab-owned deployment decision | build execution, registry/comparability ownership, deterministic diagnosis ownership, scheduler behavior |
| InferEdgeAIGuard | optional deterministic diagnosis and warning evidence | final deployment decision, LLM root-cause inference, production monitoring |
| InferEdgeEnv | local evidence registry, comparability judgement, runtime regression report | production database, cloud telemetry store, deployment decision, general monitoring SaaS |
| InferEdgeOrchestrator | runtime operation context, queue/deadline/fallback evidence, worker health evidence | Kubernetes replacement, cloud orchestration platform, deployability decision, completed production scheduler |

## 핵심 흐름

```text
ONNX Model
-> InferEdgeForge
-> InferEdge-Runtime
-> InferEdgeLab
-> optional InferEdgeAIGuard
-> Deployment Decision Report
-> Local Studio
```

Runtime Operation / Runtime Intelligence 확장은 기존 Core validation을
대체하지 않습니다.

```text
InferEdgeOrchestrator
-> InferEdgeEnv
-> optional InferEdgeAIGuard
-> InferEdgeLab
```

- Orchestrator는 worker selection, fallback, queue/deadline/runtime event
  context를 제공합니다.
- EdgeEnv는 registry, replay, comparability, regression evidence를 보존합니다.
- AIGuard는 deterministic warning/review evidence를 제공합니다.
- Lab은 Runtime Intelligence / operation-risk report와 최종 deployment
  decision을 소유합니다.

## 경계

이 ecosystem은 다음을 완료 기능처럼 주장하지 않습니다.

- production remote execution
- cloud control plane
- secure multi-device orchestration
- production SaaS dashboard
- production observability platform
- general monitoring SaaS
- AIGuard 또는 Orchestrator의 final deployment decision ownership

## Reviewer Path

1. [포트폴리오 요약](portfolio_summary.ko.md)을 읽고 30초 narrative를 확인합니다.
2. [파이프라인 맵](pipeline_map.ko.md)에서 repo별 책임과 contract boundary를 확인합니다.
3. [인터뷰 내러티브](interview_narrative.ko.md)에서 면접/리뷰어 설명 흐름을 확인합니다.
4. 필요하면 영어 canonical 문서인
   [InferEdge Ecosystem 1-Page Summary](ecosystem_1page.md)를 기준으로 세부 내용을 확인합니다.

## Cross-Repo Quick Guide Path

한국어로 각 repo의 역할을 빠르게 확인할 때는 아래 순서로 봅니다. 이 경로는
Validation -> Evidence -> Operation Control 경계를 유지하기 위한 reviewer
navigation입니다.

| 단계 | owner boundary | quick guide |
|---|---|---|
| 1 | Forge build provenance / handoff | [Forge agent manifest contract](https://github.com/gwonxhj/InferEdgeForge/blob/main/docs/agent_manifest_contract.ko.md) |
| 2 | Runtime execution / result evidence | [Runtime agent result contract](https://github.com/gwonxhj/InferEdge-Runtime/blob/main/docs/agent_runtime_result_contract.ko.md) |
| 3 | Lab-owned deployment decision | [Lab Korean README](https://github.com/gwonxhj/InferEdgeLab/blob/main/README.ko.md) |
| 4 | AIGuard deterministic diagnosis evidence | [AIGuard detector validation matrix](https://github.com/gwonxhj/InferEdgeAIGuard/blob/main/docs/detector_validation_matrix.ko.md) |
| 5 | EdgeEnv comparability / runtime regression evidence | [EdgeEnv runtime regression monitor](https://github.com/gwonxhj/InferEdgeEnv/blob/main/docs/ko/runtime-regression-monitor.md) |
| 6 | Orchestrator runtime operation context | [Orchestrator operation control guide](https://github.com/gwonxhj/InferEdgeOrchestrator/blob/main/docs/operation_control.ko.md) |

이 경로는 새 product layer가 아닙니다. InferEdge를 production SaaS, production
observability, general monitoring, Kubernetes-style orchestration, cloud control
plane으로 바꾸지 않습니다.
