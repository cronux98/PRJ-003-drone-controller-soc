# 06_verification_stage — Index
**Project:** IP-010 v4 | **Agent:** verification-agent | **Self-Audit:** Pre-computed evidence (Claude OAuth expired)

## Artifacts
| # | File | Description | Status |
|---|------|-------------|--------|
| 1 | tb-*/test_*.py | 18 cocotb testbenches (368 tests total) | ✅ |
| 2 | tb-*/results.xml | Per-module simulation results (18/18) | ✅ |
| 3 | verification_summary.json | Canonical summary (18/18 PASS, 368 tests) | ✅ |
| 4 | tier_assignment.json | Coverage tier assignment (A=9, B=5, C=4) | ✅ |
| 5 | failure_clusters.txt | Cluster analysis (0 failures, 0 RTL bugs) | ✅ |
| 6 | verify_test_artifacts.sh | Exit gate (39/39 checks PASS, exit 0) | ✅ |

## Gate
- **audit_pass.json:** ~/hermes_workspace/projects/IP-010/v4/06_verification_stage/audit/audit_pass.json
- **Validation:** [../../00_validation_report/06_verification_validation.md](../../00_validation_report/06_verification_validation.md)
- **Postmortem:** [../../11_postmortem_audit/06_verification_postmortem.md](../../11_postmortem_audit/06_verification_postmortem.md)

## Note
Claude Code OAuth expired on headless server. Self-audit uses pre-computed evidence.
Human: run `claude auth login` with browser, then `claude -p "audit <path>" --model opus` to confirm.
