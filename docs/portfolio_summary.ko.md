# InferEdge 포트폴리오 요약

언어: [English](portfolio_summary.md) | 한국어

이 문서는 한국어 빠른 안내서입니다. 대표/canonical 문서는
[InferEdge Portfolio Summary](portfolio_summary.md)입니다.

InferEdge는 ONNX 모델을 traceable build artifact, real runtime evidence,
structured evaluation, optional diagnosis, Lab-owned deployment decision으로
연결하는 local-first Edge AI inference validation pipeline입니다.

## 30초 구조

```text
이 모델을 배포해도 되는가?
-> Forge -> Runtime -> Lab (+ optional AIGuard)

이 benchmark evidence를 믿고 비교할 수 있는가?
-> InferEdgeEnv comparability layer

배포된 workload가 부하 상황에서도 안정적인가?
-> InferEdgeOrchestrator operation layer
```

## 역할 분리

| Repository | 역할 | 경계 |
|---|---|---|
| InferEdge | multi-repo entrypoint와 clone/smoke map | 각 repo contract를 대체하지 않음 |
| InferEdgeForge | build provenance / artifact handoff | inference 실행이나 deployment decision을 소유하지 않음 |
| InferEdge-Runtime | C++ execution / result export | comparison policy를 소유하지 않음 |
| InferEdgeLab | validation / report / deployment decision | final decision owner |
| InferEdgeAIGuard | optional deterministic diagnosis evidence | final decision owner가 아님 |
| InferEdgeEnv | local evidence registry / comparability checker | deployability validation owner가 아님 |
| InferEdgeOrchestrator | post-deployment operation context | deployment decision owner가 아님 |

## 현재 강조할 수 있는 것

- Core 4 validation pipeline은 build provenance, Runtime evidence, Lab decision,
  optional AIGuard evidence로 연결되어 있습니다.
- Runtime Intelligence artifact gate는 Orchestrator -> EdgeEnv -> AIGuard ->
  Lab evidence chain의 marker와 ownership boundary를 검증합니다.
- Jetson/device-local evidence는 device-local starter smoke와 telemetry handoff를
  보여주지만, decoded YOLO accuracy나 thermal endurance validation은 아닙니다.
- Remote dispatch/fallback은 file-based starter evidence이며 production remote
  execution이 아닙니다.

## Runtime Operation Starter Chain

```text
Orchestrator worker selection / fallback starter
-> EdgeEnv local registry and replay context
-> AIGuard deterministic warning evidence
-> Lab Runtime Intelligence / operation-risk report
-> Lab-owned deployment decision
```

이 chain의 가치는 production remote operation 주장이 아니라 repo별 책임 분리입니다.

## 주장하지 말아야 할 것

- production SSH/HTTP remote execution
- long-lived remote worker daemon
- Cloudflare / secure tunnel operation 완료
- production retry/failover infrastructure
- Kubernetes-style or cloud orchestration
- production observability platform
- GitLab control plane

세부 implementation status와 evidence 수치는
[InferEdge Portfolio Summary](portfolio_summary.md)를 기준으로 확인하세요.
