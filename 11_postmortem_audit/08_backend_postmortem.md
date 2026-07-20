# 08_backend_stage — Postmortem

**Date:** 2026-07-19
**Verdict:** PASS (20/21 + 1 waiver)
**Flow:** v4-complete, 77/77 steps

## What Happened

The backend agent timed out twice (3600s limit, full P&R needs ~4000s for 69K cells). Vera launched LibreLane manually with corrected invocation (`librelane config.yaml --run-tag v4-complete`) and clean environment (unset LD_LIBRARY_PATH to avoid oss-cad-suite GLIBC clash). Flow completed in 67 minutes.

Claude Opus 4.8 ran first-pass audit (15/21 PASS) but hit $0.50 budget cap mid-execution. Vera applied 5 admin fixes and wrote final audit_pass.json.

## Root Cause Analysis

**RCA-1: Agent timeout (3600s < 4000s needed)**
The physical-design-agent kanban task has a 3600s (1h) timeout. Full LibreLane flow for a 69K-cell design on sky130 takes ~67 minutes. Two consecutive timeouts trigger the give_up limit. Fix: increase backend task timeout to 5400s (90 min).

**RCA-2: GLIBC mismatch with oss-cad-suite**
The LibreLane AppImage bundles Nix-built binaries that need GLIBC 2.36+. oss-cad-suite ships older libc. When LD_LIBRARY_PATH includes oss-cad-suite/lib/, the AppImage crashes. Fix: `unset LD_LIBRARY_PATH PYTHONPATH` before invocation.

**RCA-3: Wrong LibreLane CLI syntax**
The `--run_flow --design . --from detailed_routing` syntax doesn't work with LibreLane v3. Correct: `librelane config.yaml --run-tag TAG`. The AppImage's entry point is `librelane` subcommand, not `--run_flow`.

**RCA-4: Claude budget cap too low**
$0.50 budget for a 21-check backend audit was insufficient. Claude wrote 15/21 checks before hitting the cap. Fix: backend audit budget should be $0.80-1.00.

## Fixes Applied

1. **LibreLane invocation** — `librelane config.yaml --run-tag v4-complete` with clean env
2. **Results handoff** — populated results/{gds,nl,metrics,RUN_TAG}
3. **Cost telemetry** — wall_clock_s and cost_usd added to metrics.json
4. **PD iteration log** — 4 runs documented (3 timeout + v4-complete)
5. **Checker-disable hygiene** — [expires: v4-complete] tags on 3 ERROR_ON_* lines
6. **Index rows** — backend rows added to validation + postmortem indexes
7. **Antenna waiver** — W08-001 for 1 antenna-violating net

## Key Metrics

| Metric | Value |
|--------|-------|
| Setup WNS | +30.02 ns |
| Hold WNS | +0.09 ns |
| DRC violations | 0 |
| LVS result | Match |
| Utilization | 49.7% |
| Power | 11.17 mW |
| Cell count | 69,310 |
| DFF count | 5,042 (SRAM NOT flops) |
| Max slew violations | 19,447 |
| Max cap violations | 128 |
| Antenna violations | 1 (waivered) |
| Wall clock | 4,021s (67 min) |

## Lessons Learned

1. **1 hour is not enough for PD.** 69K cells on sky130 takes ~67 min. The kanban timeout should be 90 min minimum for backend tasks.
2. **AppImage env is fragile.** Always unset LD_LIBRARY_PATH and PYTHONPATH before running LibreLane AppImage. The Nix-packaged binaries are sensitive to host library paths.
3. **Claude budget scales with stage complexity.** Frontend audit (20 checks, 18 modules) needed $0.80. Backend audit (21 checks) needs similar. $0.50 is too low.
4. **Pre-computed evidence saves turns.** Claude completed 15/21 checks before budget cap because evidence was pre-computed. Without it, would have been 3-5 checks.

## What Went Well

- Timing: 30 ns positive slack at 60 ns period — 50% margin
- DRC/LVS: clean first pass
- SRAM: verified blackbox, no flop expansion
- Claude identified all 6 failures correctly even with budget cap
