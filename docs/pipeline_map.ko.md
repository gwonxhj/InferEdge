# InferEdge 파이프라인 맵

언어: [English](pipeline_map.md) | 한국어

이 문서는 한국어 빠른 안내서입니다. 대표/canonical 문서는
[InferEdge Pipeline Map](pipeline_map.md)입니다.

InferEdge entrypoint repo는 split repository 구조를 clone, inspect, smoke test할
수 있게 만드는 local-first coordination layer입니다.

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
| InferEdge-Runtime | inference execution, latency/FPS/backend/device evidence, Lab-compatible result JSON | deployment decision |
| InferEdgeLab | compare/evaluate/report/API/Local Studio/deployment decision | build artifact 생성 |
| InferEdgeAIGuard | optional `guard_analysis`, deterministic evidence items | final deployment decision, LLM guessing |
| InferEdgeEnv | registry, replay, comparability, regression evidence | production DB/cloud registry, Lab decision |
| InferEdgeOrchestrator | worker selection, queue/deadline/fallback, runtime operation context | production cloud orchestration, deployability decision |

## Runtime Operation Starter Evidence Chain

```text
Orchestrator remote dispatch starter
-> EdgeEnv local evidence preservation
-> AIGuard deterministic warning/review evidence
-> Lab operation-risk report
-> Lab-owned deployment decision
```

이 chain은 Core 4 validation contract를 바꾸지 않고 operation evidence를 추가합니다.

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

InferEdge는 production SaaS platform으로 제시하지 않습니다. DB/queue/auth/billing,
file upload, cloud dashboard deployment, production worker daemon은 현재 완료 범위가
아닙니다.
