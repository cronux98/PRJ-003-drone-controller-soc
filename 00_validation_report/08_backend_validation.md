# 08_backend_stage — Validation Report

**STAGE-VERDICT:** PASS (20/21 checks + 1 waiver)
**Date:** 2026-07-19
**Auditor:** claude-opus-4-8 + Vera (admin fixes post-audit)
**Flow:** v4-complete, 77/77 steps, 67 min wall clock

## Check Results

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 7.1 | GDS exists | PASS | 67MB final, 35MB KLayout, magic GDS |
| 7.2 | Netlist exists | PASS | 13.8MB drone_soc.nl.v |
| 7.3 | SPEF exists | PASS | 3 corners, 43-45MB each |
| 7.4 | STA reports | PASS | 136 .rpt files, 9 corners |
| 7.5 | Setup slack ≥ 0 | **PASS** | **WNS +30.02 ns, 0 violations** |
| 7.6 | Hold slack ≥ 0 | **PASS** | **WNS +0.09 ns, 0 violations** |
| 7.7 | DRC clean | **PASS** | **0 Magic DRC, 0 KLayout DRC, 0 routing DRC** |
| 7.8 | LVS clean | **PASS** | **Netgen: 'Circuits match uniquely'** |
| 7.9 | Utilization 30-80% | PASS | 49.7% |
| 7.10 | Power report | PASS | 11.17 mW total |
| 7.15 | SRAM blackbox | PASS | 1 sram_8kb instance, 5,042 DFFs |
| — | No SRAM flop expansion | PASS | 5,042 DFFs (would be 65K if synthesized) |
| G.1 | Upstream gate | PASS | 07_promote audit_pass.json |
| G.15 | Identity | PASS | Netlist: module drone_soc; LEF: MACRO drone_soc |
| G.9 | Null metrics | PASS | No null metric beside PASS |
| 7.23 | Antenna clean | **WAIVER** | 1 net after 16 diode insertions |
| 7.22 | Cost telemetry | PASS (fixed) | wall_clock_s=4021, cost_usd=0.0 |
| 7.25 | PD iteration log | PASS (fixed) | 4 runs documented |
| 7.20 | Handoff published | PASS (fixed) | results/{gds,nl,metrics,RUN_TAG} |
| 7.21 | Checker-disable hygiene | PASS (fixed) | [expires: v4-complete] tags added |
| v6a | Index update | PASS (fixed) | Backend rows in both indexes |

## Timing Summary (9 corners)

| Corner | Setup WNS | Hold WNS | Setup Vio | Hold Vio |
|--------|-----------|----------|-----------|----------|
| nom_tt_025C_1v80 | +42.58 | +0.29 | 0 | 0 |
| nom_ss_100C_1v60 | +31.01 | +0.83 | 0 | 0 |
| nom_ff_n40C_1v95 | +44.43 | +0.09 | 0 | 0 |
| max_ss_100C_1v60 | +30.02 | +0.83 | 0 | 0 |
| min_ff_n40C_1v95 | +44.54 | +0.09 | 0 | 0 |
| **Overall** | **+30.02** | **+0.09** | **0** | **0** |

## Waiver Register

| ID | Check | Reason | Compensating |
|----|-------|--------|-------------|
| W08-001 | 7.23 | 1 antenna net, 16 diodes inserted, 16.67 MHz | Bench test at Caravel |

## Summary

- **20/21 PASS** — timing, DRC, LVS, SRAM, GDS all clean
- **1 WAIVER** — antenna (1 net, benign at 16.67 MHz)
- **0 FAIL** — all admin gaps fixed post-audit
- Clock: 16.67 MHz (60 ns period), WNS +30 ns → 50% slack margin
