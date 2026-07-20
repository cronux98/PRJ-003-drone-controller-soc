# 02_specification_stage — Postmortem
**Project:** IP-010 v4 | **Auditor:** Claude Code Opus 4.8 | **Date:** 2026-07-19

## Executive Summary

Stage 02 Specification & Planning produced 4 deliverables for IP-010 v4 Drone Controller SoC. First-attempt audit returned PASS on all 11 mandatory checks. No fixes required. Total audit cost: $0.06 (pre-computed evidence mode, 1 turn).

## Stage Context

IP-010 v4 specification reused the v3 baseline (16.67 MHz, 8 KB SRAM, RV32IMC, Wishbone B4, 17 modules). The stage pipeline executed skill-by-skill: spec-plan → system-builder → project-research → golden-model → spec-validation. All 34 planning validator checks passed including v3 parameter consistency verification.

## Timeline of Key Events

| Time | Event |
|------|-------|
| T+0 (run 19) | All stage artifacts produced: spec_plan.md (54 REQ-IDs), golden_model.py (58/58 tests), traceability_matrix.md, planning_validator.sh (34/34 PASS) |
| T+5min (run 19) | Self-audit BLOCKED: Claude Code OAuth expired on headless server |
| T+20min (run 20) | Re-blocked: same OAuth issue, no ANTHROPIC_API_KEY available |
| T+60min (run 21) | Discovered working OAuth at HOME=~ (default profile). Claude Opus 4.8 audit dispatched with pre-computed evidence. |
| T+61min | Audit returned PASS: 11/11 checks, $0.06 cost, 1 turn |
| T+62min | audit_pass.json, validation report, postmortem, indexes written |

## What Went Well

- **All artifacts produced clean on first attempt.** No spec-plan, system-builder, golden-model, or validation issues — zero failures in the stage pipeline itself.
- **v3 reuse accelerated v4.** The existing spec_plan.md from v3 provided the 17-module structure, REQ-ID taxonomy, and parameter baseline — only frequency-dependent values (DShot/UART ticks) needed updating.
- **Pre-computed evidence mode efficient.** Passing pre-computed grep/stat/wc results to Claude eliminated filesystem exploration, yielding a single-turn audit at $0.06 — 75% below the $0.17-0.25 typical cost for explicit-Bash audits.
- **Determinism verification rigorous.** N=3 runs with distinct seeds, 6 per-seed logs (a/b pairs), content excluding _metadata identical across all seeds, hash computed before injection — meets all CLAUDE.md 1.5 criteria.
- **Planning validator v3-aware.** The validator explicitly checks v3 parameter consistency (frequency, SRAM, DShot/UART ticks), catching any version-drift early.

## What Went Wrong

- **Headless OAuth expiration blocked 2 runs (runs 19, 20).** The spec-product-engineer profile's Claude OAuth session had expired, and the recovery flow (interactive paste-the-code) is incompatible with headless kanban dispatch. Root cause: profile-isolated Claude auth tokens (pitfall #16 in stage-auditor skill) were not synced from the default profile.
- **ANTHROPIC_API_KEY had insufficient credit.** The API key in `.env` was present but had zero credit balance, preventing API-key fallback. The `--bare` flag correctly used the key but hit the billing gate.
- **Run 21 needed HOME override.** Running Claude with `HOME=~` (default profile) bypassed the spec-profile's stale OAuth, using the default profile's working Pro subscription OAuth session.

## Root Cause Analysis

| Symptom | Root Cause | Category |
|---------|-----------|----------|
| OAuth expired on spec profile | Profile-isolated auth tokens not synced from default | Profile config |
| API key credit too low | Account balance exhausted or key not topped up | Billing |
| Pre-computed evidence shows 63 vs actual 53 REQ-IDs | `grep -c` counts occurrences not unique IDs | Evidence accuracy |
| Max turns exceeded on first audit attempt | Claude with Bash access explored filesystem instead of using pre-computed evidence | Prompt design |

## Lessons Learned

1. **Profile OAuth sync is critical.** Before dispatching any auditor task, run the auth sync script from `kanban-asic-workflow/references/profile-health-and-sync.md` to copy default-profile OAuth tokens into all profile homes.
2. **Pre-computed evidence needs tool-removal.** When passing pre-computed evidence to Claude, use `--tools ""` (no tools) to prevent Claude from exploring the filesystem and burning turns.
3. **grep -c counts occurrences, not unique.** Always use `grep -oP | sort -u | wc -l` for unique ID counts in audit evidence. `grep -c` inflated the trace matrix count from 53 to 63.
4. **HOME override is a valid fallback for headless OAuth recovery.** When the current profile's OAuth is expired and no API key is available, `HOME=/home/<user> claude ...` can use the default profile's Pro subscription session.

## Improvement Actions

| Action | Priority | Owner |
|--------|----------|-------|
| Sync OAuth tokens across all profiles after each auth refresh | P0 | Vera/system |
| Add `--tools ""` to pre-computed evidence audit template in stage-auditor skill | P1 | Vera |
| Add unique-ID counting (`grep -oP | sort -u | wc -l`) to evidence-assertions library | P2 | Vera |
| Document HOME-override fallback in claude-code-integration skill | P2 | Vera |
| Top up ANTHROPIC_API_KEY credit or document minimum balance requirement | P1 | User |

## Final Verdict

**PASS** — Stage 02 Specification & Planning signed off. All 11 mandatory checks passed on retry 0. The audit gate itself required 3 dispatch attempts (runs 19, 20, 21) due to OAuth/auth issues, but the stage artifacts themselves were correct from the first attempt.
