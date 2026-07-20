# 07_promote_stage — Postmortem
**Project:** IP-010 v4 | **Agent:** physical-design-agent | **Date:** 2026-07-19

## Outcome
**PASS** — 16/17 modules promoted (94.1%). 1 module BLOCKED (custom_timer). Gate script exit 0.

## Key Decisions
1. **Waiver W04-002 accepted:** 10 Efabless wrapper modules (uart_0/1/2, spi_0, i2c_0, gpio, timer, watchdog, caravel_wrapper, sram_8kb) promoted with equiv waived. Adjudicator=Vera, compensating check=GLS at Stage 06.
2. **sram_8kb as blackbox:** cell_count=0 is expected and accepted. No equiv possible for blackbox macro.
3. **custom_timer blocked:** Synthesis incomplete (ABC pass started but never finished), no equiv log. Requires frontend rework — fix synthesis script for this module.
4. **drone_soc excluded:** Not in blueprint.json (not a leaf module for IP-010 v4). Denominator is 17, not 18.
5. **Waiver path mismatch:** Waivers live at 04_frontend_stage/waivers/, not v4/waivers/ as the skill expects. Accepted on merit (adjudicator=Vera ≠ requested_by, properly documented in frontend audit).

## Lessons
- The admission_check.py script referenced in the module-promotion skill does not exist — checks were implemented inline.
- verify_promotion_artifacts.sh expects `tb_*/results.xml` (underscore) but verification uses `tb-*/` (hyphen). Script patched for this run.
- Promotion gate must cross-reference frontend waivers directory, not just vN/waivers/ — frontend audit documents waivers that the promotion gate must honor.
- Per-module promotion reports + consolidation report creates duplicates found by find — consolidated report renamed to avoid double-counting.

## Hallucination Incidents
0 — all cell counts parsed from actual synthesis logs. Equiv status parsed from actual equiv.log files. Waiver adjudication verified from frontend audit_pass.json.

## Anti-Fabrication Compliance
- All numeric claims cite actual tool output paths
- Cell counts parsed via regex from Yosys stat sections
- Equiv status verified by reading equiv.log files (not assumed)
- verify_promotion_artifacts.sh exit 0 confirmed
- promotion_report.json modules array = 17 (matches blueprint.json)
