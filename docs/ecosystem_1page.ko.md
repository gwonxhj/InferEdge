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

## Layer 역할

| Layer | Project | 책임 |
|---|---|---|
| Validation | InferEdgeForge | build provenance, metadata, manifest, artifact handoff |
| Validation | InferEdge-Runtime | 실제 inference 실행과 Lab-compatible `result.json` export |
| Validation | InferEdgeLab | compare, evaluate, report, Lab-owned deployment decision |
| Validation | InferEdgeAIGuard | optional deterministic risk diagnosis evidence |
| Comparability | InferEdgeEnv | local run evidence registry와 comparability judgement |
| Operation | InferEdgeOrchestrator | queue, overload, fallback, runtime telemetry 기반 operation context |

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
-> InferEdgeAIGuard
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
- AIGuard 또는 Orchestrator의 final deployment decision ownership

## Reviewer Path

1. [포트폴리오 요약](portfolio_summary.ko.md)을 읽고 30초 narrative를 확인합니다.
2. [파이프라인 맵](pipeline_map.ko.md)에서 repo별 책임과 contract boundary를 확인합니다.
3. 필요하면 영어 canonical 문서인
   [InferEdge Ecosystem 1-Page Summary](ecosystem_1page.md)를 기준으로 세부 내용을 확인합니다.
