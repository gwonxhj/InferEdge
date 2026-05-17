# Reliable Edge Agent Runtime E2E Demo

This document describes the local extension smoke that connects the Reliable
Edge Agent Runtime contracts across the InferEdge ecosystem.

The demo is intentionally local-first and file-based. It is not a production
orchestration service, cloud dashboard, or general AI OS.

## Contract Chain

```text
Forge agent_manifest
-> Runtime result.agent
-> Orchestrator orchestration_summary
-> AIGuard guard_analysis
-> Lab agent-runtime-report
```

## Run

From the InferEdge entrypoint repository:

```bash
bash scripts/demo_agent_runtime_e2e.sh
```

The script writes generated evidence under:

```text
reports/agent_runtime_e2e/
```

Use a temporary output directory for clean validation:

```bash
bash scripts/demo_agent_runtime_e2e.sh --output-dir /tmp/inferedge_agent_runtime_e2e
```

## Inputs

The script resolves repositories from `./repos`, sibling directories, or
`/Users/GwonHyeokJun/Documents/GitHub`.

Override paths when needed:

```bash
INFEREDGE_FORGE_REPO=/path/to/InferEdgeForge \
INFEREDGE_RUNTIME_REPO=/path/to/InferEdge-Runtime \
INFEREDGE_ORCHESTRATOR_REPO=/path/to/InferEdgeOrchestrator \
INFEREDGE_AIGUARD_REPO=/path/to/InferEdgeAIGuard \
INFEREDGE_LAB_REPO=/path/to/InferEdgeLab \
bash scripts/demo_agent_runtime_e2e.sh
```

## Outputs

| Output | Purpose |
|---|---|
| `01_forge_agent_manifest_vision.json` | Agent workload handoff contract example |
| `02_runtime_result_agent.json` | Runtime result with backward-compatible `agent` block |
| `03_orchestration_summary.json` | 3-agent scheduler policy decision evidence |
| `04_aiguard_guard_analysis.json` | Deterministic runtime reliability diagnosis evidence |
| `04_aiguard_guard_analysis.md` | Human-readable AIGuard report |
| `05_lab_agent_runtime_report.json` | Lab-owned agent runtime reliability report |
| `05_lab_agent_runtime_report.md` | Human-readable Lab deployment decision context |

## Scope Boundary

Included:

- Vision / Voice-Command / Safety-Monitor workload contracts
- priority/deadline scheduling evidence
- drop/fallback/deadline signal propagation
- AIGuard runtime reliability interpretation
- Lab-owned report and deployment decision context

Not included:

- production SaaS infrastructure
- DB/queue persistence
- cloud orchestration
- LLM agent framework implementation
- universal AI OS claims
