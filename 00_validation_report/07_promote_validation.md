# 07_promote_stage — Validation Report
**Project:** IP-010 v4 | **Audit:** Pre-computed evidence (Claude OAuth expired) | **Generated:** 2026-07-19

## Quick Summary
- **16/17 modules promoted** (94.1%) — 1 BLOCKED (custom_timer)
- **Gate:** verify_promotion_artifacts.sh — ALL CHECKS PASSED (exit 0)
- **Waivers:** W04-002 (10 wrapper modules equiv), sram_8kb blackbox (0 cells)
- **Denominator:** 17 modules from blueprint.json

## Module Results
| Module | Tier | Cells | Tests | Equiv | Status |
|--------|------|-------|-------|-------|--------|
| ibex_core | C | 6,528 | 40 | PROVEN | PROMOTED |
| wishbone_interconnect | B | 699 | 15 | PROVEN | PROMOTED |
| sram_8kb | A | 0 | 8 | WAIVED | PROMOTED (BLACKBOX) |
| uart_0 | A | 1,871 | 15 | WAIVED | PROMOTED [W04-002] |
| uart_1 | A | 1,871 | 15 | WAIVED | PROMOTED [W04-002] |
| uart_2 | A | 1,871 | 15 | WAIVED | PROMOTED [W04-002] |
| spi_0 | B | 1,116 | 40 | WAIVED | PROMOTED [W04-002] |
| i2c_0 | C | 2,141 | 40 | WAIVED | PROMOTED [W04-002] |
| dshot_pwm | C | 2,254 | 40 | PROVEN | PROMOTED |
| gpio | B | 649 | 15 | WAIVED | PROMOTED [W04-002] |
| spi_flash_ctrl | A | 377 | 15 | PROVEN | PROMOTED |
| irq_ctrl | A | 396 | 8 | PROVEN | PROMOTED |
| timer | B | 1,766 | 15 | WAIVED | PROMOTED [W04-002] |
| watchdog | A | 364 | 15 | WAIVED | PROMOTED [W04-002] |
| caravel_wrapper | A | 199 | 9 | WAIVED | PROMOTED [W04-002] |
| clk_rst_mgr | A | 44 | 8 | PROVEN | PROMOTED |
| custom_timer | B | — | 15 | NO_LOG | **BLOCKED** |

## Blocked Module Detail
- **custom_timer:** Synthesis INCOMPLETE (ABC pass never finished, no "End of script" in log). No equivalence check log. Cell count unparseable. Requires frontend agent rework.

## Waiver Coverage
- **W04-002:** 10 Efabless wrapper modules fail equiv due to synth top-module naming mismatch. Adjudicator: Vera. Compensating check: GLS at Stage 06.
- **sram_8kb blackbox:** 0 standard cells — expected. No equiv possible (no RTL body). Compensated by LVS at Stage 08.

## Gate Verdict
verify_promotion_artifacts.sh: **PASS** — 16/16 reports, 16/16 cell counts, 16/16 reuse manifests, 16/16 synth logs, 18/16 results.xml. Exit 0.
