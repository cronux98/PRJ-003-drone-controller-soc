# 06_verification_stage — Validation Report
**Project:** IP-010 v4 | **Audit:** Claude Opus 4.8 | **Generated:** 2026-07-19

## Quick Summary
- **18/18 modules verified** (17 leaf + 1 SoC top)
- **368 tests total**, 0 failures
- **Gate:** verify_test_artifacts.sh — 39/39 checks PASS
- **Tiers:** A(9) B(5) C(4), all minimum test counts met

## Module Results
| Module | Tier | Tests | Result |
|--------|------|-------|--------|
| clk_rst_mgr | A | 8 | PASS |
| irq_ctrl | A | 8 | PASS |
| caravel_wrapper | A | 9 | PASS |
| sram_8kb | A | 8 | PASS |
| wishbone_interconnect | A | 15 | PASS |
| spi_flash_ctrl | B | 15 | PASS |
| dshot_pwm | B | 40 | PASS |
| custom_timer | B | 15 | PASS |
| timer | B | 15 | PASS |
| watchdog | B | 15 | PASS |
| uart_0 | B | 15 | PASS |
| uart_1 | B | 15 | PASS |
| uart_2 | B | 15 | PASS |
| gpio | B | 15 | PASS |
| spi_0 | C | 40 | PASS |
| i2c_0 | C | 40 | PASS |
| ibex_core | C | 40 | PASS |
| drone_soc | C | 40 | PASS |

## Gate Verdict
verify_test_artifacts.sh: **PASS** — 39/39 checks, exit 0

## Coverage Tier Assignment
- Tier A (≤500 toggle bins): 9 modules, ≥90% toggle target
- Tier B (501-2000): 5 modules, ≥70% toggle target  
- Tier C (>2000): 4 modules, ≥40% toggle target

## Cluster Analysis
0 failures clustered. 0 RTL bugs detected.

## GLS Status
NOT RUN — defer to post-PD GLS stage (compensating for frontend waivers W04-001 through W04-006).
