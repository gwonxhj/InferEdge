# InferEdge Final Submission Rehearsal

Date: 2026-05-14

This document records the final submission rehearsal for the InferEdge multi-repository portfolio entrypoint.

The purpose is to prove the reviewer path from a clean clone:

1. clone the entrypoint repository
2. run `clone_all --locked`
3. run the cross-repo smoke suite
4. verify the Local Studio demo evidence path
5. review the portfolio summary wording

## Scope

This is a submission readiness record, not a new feature milestone.

It validates the current local-first portfolio path:

- Forge build provenance and manifest validation
- Runtime smoke execution and Lab-compatible result evidence
- Lab portfolio demo and Core 4 conformance
- AIGuard deterministic diagnosis demo
- Local Studio demo evidence summary
- portfolio summary role boundaries

Supporting layers remain separate:

- InferEdgeEnv records run evidence and comparability.
- InferEdgeOrchestrator controls runtime operation after deployment.

## Clean Clone Setup

Temporary rehearsal root:

```text
/tmp/inferedge-final-submission.LRaM97
```

Clean clone command:

```bash
git clone https://github.com/gwonxhj/InferEdge.git /tmp/inferedge-final-submission.LRaM97/InferEdge
```

Locked repository checkout:

```bash
cd /tmp/inferedge-final-submission.LRaM97/InferEdge
bash scripts/clone_all.sh --locked
```

Locked commits checked out:

| Repository | Locked commit | Result |
|---|---|---|
| InferEdgeForge | `df7e56b97cb967f3cc740197189d453d26bc50b1` | checked out |
| InferEdge-Runtime | `59b35b5cc12ade26afdc5be801d9479c79de32b8` | checked out |
| InferEdgeLab | `e75ff9f3a1cd4a1434c007f62221caf9e5371062` | checked out |
| InferEdgeAIGuard | `b827046284a5fc36196fedde4b51d5e359a74602` | checked out |

## Rehearsal Finding And Fix

The first clean-clone smoke run found one real submission-path issue:

```text
==> Lab portfolio demo check
Creating virtualenv inferedgelab-p1hbgDW8-py3.11 ...
Command not found: inferedgelab
```

Cause:

- The clean clone created a new Poetry virtualenv for InferEdgeLab.
- `scripts/smoke_all.sh` called `poetry run inferedgelab ...` before installing the Lab package into that new environment.
- Existing sibling-repo smoke runs had passed because the local Poetry environment was already prepared.

Fix applied:

```bash
run_step "Lab install" bash -lc "cd '$LAB' && poetry install --no-interaction"
```

The install step runs before the Lab CLI checks and makes the clean-clone path reproducible.

## Final Smoke Result

Command:

```bash
cd /tmp/inferedge-final-submission.LRaM97/InferEdge
bash scripts/smoke_all.sh
```

Result:

```text
InferEdge cross-repo smoke: pass
```

Key checks:

| Step | Result |
|---|---|
| Forge tests | `87 passed` |
| Forge manifest validation | valid, 0 errors, 0 warnings |
| Runtime smoke | success |
| Runtime manifest identity | `Ran 3 tests`, OK |
| Lab install | installed current project `inferedgelab (0.1.0)` |
| Lab portfolio demo check | pass, 50 total / 0 failed |
| Lab Core 4 conformance check | pass, 133 total / 0 failed |
| AIGuard tests | `134 passed` |
| AIGuard portfolio demo | generated 4 deterministic demo cases |

## Local Studio Demo Evidence

Command:

```bash
cd /tmp/inferedge-final-submission.LRaM97/InferEdge/repos/InferEdgeLab
poetry run inferedgelab demo-evidence-summary
```

Result:

```text
InferEdge Local Studio Demo Evidence
- TensorRT Jetson FP16 25W mean_ms: 10.0664
- ONNX Runtime CPU mean_ms: 45.4299
- speedup: 4.513x faster
- TensorRT FPS: 99.3404
- ONNX Runtime FPS: 22.0119
- deployment_decision: review_required
- policy_version: inferedge-lab-decision-policy-v1
- triggered_rules: guard_warning_review
- evaluation map50: 0.141
- in_memory_note: Local Studio demo evidence is in-memory and resets when the server restarts.
```

Interpretation:

- The Local Studio demo evidence is available from the clean locked Lab checkout.
- The demo decision is review-oriented, not an unconditional deploy claim.
- The evidence path remains local-first and does not require production workers, queues, DBs, or cloud services.

## Portfolio Summary Review

Reviewed:

```text
docs/portfolio_summary.md
```

Status: pass.

The summary gives the intended 30-second structure:

- InferEdge Core 4 is the validation path.
- InferEdgeEnv is the run evidence registry / comparability checker.
- InferEdgeOrchestrator is the post-deployment runtime operation-control layer.
- Lab owns deployment decisions.
- AIGuard supplies optional deterministic diagnosis evidence.

No wording conflict was found between validation, evidence registry, and operation-control responsibilities.

## Submission Gate

Status: pass after smoke script hardening.

Accepted submission path:

```bash
git clone https://github.com/gwonxhj/InferEdge.git
cd InferEdge
bash scripts/clone_all.sh --locked
bash scripts/smoke_all.sh
```

Then review:

```text
docs/portfolio_summary.md
README.md
docs/pipeline_map.md
repos/InferEdgeLab/README.md
repos/InferEdgeLab/docs/portfolio/inferedge_portfolio_submission.md
repos/InferEdge-Runtime/docs/reports/jetson_evidence_summary.md
repos/InferEdgeAIGuard/docs/detector_validation_matrix.md
```

## Notes

- `scripts/smoke_all.sh` now installs the Lab package before calling Lab console scripts.
- No Core 4 schema, result JSON, compare output, or repository lock changed.
- This rehearsal does not claim production SaaS readiness.
- This rehearsal does not include live Jetson execution; it validates the locked local submission smoke and committed Jetson evidence path.
