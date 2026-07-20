# 09_caravel_stage — Index
**Project:** IP-010 v4 | **Agent:** physical-design-agent (Hermes run_id 33) | **Self-Audit:** Claude Opus 4.8

## Artifacts
| # | File | Description | Status |
|---|------|-------------|--------|
| 1 | precheck_input/gds/user_project_wrapper.gds | GDS (67MB, top cell renamed drone_soc→user_project_wrapper via KLayout) | DONE |
| 2 | precheck_input/user_project_wrapper.lef | LEF (118KB, MACRO renamed to user_project_wrapper) | DONE |
| 3 | precheck_input/verilog/gl/user_project_wrapper.v | Gate-level netlist (318K lines, post-P&R structural) | DONE |
| 4 | precheck_input/verilog/rtl/user_project_wrapper.v | RTL wrapper (drone_soc instantiation) | DONE |
| 5 | precheck_input/verilog/rtl/user_defines.v | GPIO configuration (33 GPIOs, 0x0403 bidirectional) | DONE |
| 6 | precheck_input/Makefile | Caravel Makefile (all required targets) | DONE |
| 7 | precheck_input/lvs/user_project_wrapper/lvs_config.json | LVS config | DONE |
| 8 | precheck_input/README.md | Project README | DONE |
| 9 | precheck_input/LICENSE | MIT License | DONE |
| 10 | mpw-precheck-v4-final.log | Precheck log (9533 bytes, 15/15 PASS) | DONE |
| 11 | PRECHECK_REPORT.md | Precheck report (this document references tool output) | DONE |

## Precheck Summary
- 15/15 evaluable checks PASS (DRC=0 Magic + KLayout, GPIO valid, structural checks clean)
- 4/19 checks SKIPPED (consistency, XOR, OEB, LVS — require full Caravel wrapper synthesis)
- GDS is DRC-clean for sky130A

## Gate
- **audit_pass.json:** ~/hermes_workspace/projects/IP-010/v4/09_caravel_stage/audit/ (or 99_audit/)
- **Validation:** [../../00_validation_report/09_caravel_validation.md](../../00_validation_report/09_caravel_validation.md)
- **Postmortem:** [../../11_postmortem_audit/09_caravel_postmortem.md](../../11_postmortem_audit/09_caravel_postmortem.md)
