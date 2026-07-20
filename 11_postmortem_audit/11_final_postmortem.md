# 11_final_postmortem.md — IP-010 v4 Framework Audit

**Status:** PENDING REVIEW — Claude Fable 5 cross-project synthesis
**Date:** 2026-07-19
**Scope:** All 9 v4 stages + framework systemic issues

---

## Mandate 1: Vera Dispatches Kanban, Doesn't Do Agent Work

### Current State (BROKEN)

In v4, Vera directly executed agent work on three separate occasions:

| Incident | What Vera Did | What Should Have Happened |
|----------|--------------|--------------------------|
| Frontend run #24 | Vera pre-computed evidence, wrote `audit_pass.json`, validation, postmortem | Vera should have unblocked kanban task after fixing CLAUDE.md path in skill |
| Frontend run #25 | Vera ran Frontend Claude audit from own terminal | Vera should have bumped retry count on kanban task and re-dispatched |
| Backend run | Vera launched LibreLane manually (`proc_ee3b7344b6c5`), applied 5 admin fixes, wrote audit_pass.json | Vera should have increased kanban timeout to 7200s, unblocked, and let physical-design-agent retry |

**Root cause:** Vera's SOUL.md and dispatch pattern has no explicit `Vera-does-NOT-execute` constraint. When a kanban task blocks, Vera's default behavior is to fix it herself rather than fix the kanban/system and re-dispatch.

### Required Fix

Add to Vera's SOUL.md `## What I Won't Do` section:

```
- I won't run a stage agent's task myself. If a kanban task blocks, I diagnose the block reason, fix the skill/tool/config that caused it, unblock the task, and let the profile agent retry.
- I won't write audit_pass.json. That's the profile agent's job via stage-self-audit → Claude Opus.
- I won't execute tool flows (LibreLane, Yosys, Magic) directly. I fix the environment/config so the agent can run them.
- Exception: If ALL retries are exhausted AND the block is a skill/config defect I already fixed, I may force-complete the task with a Vera-adjudicated waiver record.
```

**Verification:** In v5, count Vera terminal sessions that produce stage artifacts. Target: 0.

---

## Mandate 2: Validation Reports Need Structured Metrics

### Current State (BROKEN)

Each validation report has a different format. The dashboard (`v4_dashboard.sh`) relies on crude regex:

```bash
# Line 115 — counts EVERY "FAIL" substring including "0 FAIL"
ISSUES=$(grep -rci 'FAIL\|BLOCKED\|violation' *_postmortem*.md)

# Line 116 — matches emoji and English words with no structure
FIXES=$(grep -rci '✅\|Fixed\|applied\|fix.*verified' *_postmortem*.md)

# Line 117 — counts "retry" mentions including "retry 0" (not a rework)
ITERS=$(grep -rci 'retry\|iteration\|rework' *_postmortem*.md)
```

This produces approximate numbers (24 issues, 14 fixes, 13 iterations) that do not reconcile with actual stage-level data. For example, "FAIL" matches "0 FAIL" in the backend report, and "PASS" appearing near "FAIL" in context like "14/20 PASS, 6 FAIL" double-counts.

### Required Fix

Every validation report SHALL include a structured `## Metrics` section:

```markdown
## Metrics
| Metric | Value |
|--------|-------|
| Checks passed | 20 |
| Checks failed | 0 |
| Checks waivered | 1 |
| Issues found (total) | 6 |
| Fixes applied | 5 |
| Rework iterations | 2 |
| Wall clock (stage) | 67 min |
| Claude cost | $1.10 |
| Token usage (est.) | 45K |
| Agent runs | 3 |
| Waivers granted | 1 |
```

And a corresponding `stage_metrics.json` at `<stage>/audit/stage_metrics.json`:

```json
{
  "stage": "08_backend_stage",
  "verdict": "PASS",
  "checks_passed": 20, "checks_failed": 0, "checks_waivered": 1,
  "issues_found": 6, "fixes_applied": 5, "rework_iterations": 2,
  "wall_clock_s": 4021, "cost_usd": 1.10, "token_usage_est": 45000,
  "agent_runs": 3, "waivers_granted": 1,
  "auditor": "claude-opus-4-8", "retry": 1
}
```

Dashboard script reads `stage_metrics.json` per stage and sums fields. No regex. No postmortem grepping.

**Action:** Patch `stage-self-audit/SKILL.md` §Step 1 audit prompt to mandate `## Metrics` section in validation report AND `stage_metrics.json` output. Patch `v4_dashboard.sh` to read from JSON.

---

## Mandate 3: Vera Must Auto-Unblock the Chain

### Current State (BROKEN)

The v4 chain blocked 4 times. Every time, the user had to explicitly tell Vera "it's blocked" before Vera diagnosed and acted:

| Block # | Stage | Reason | User Intervention Required? |
|---------|-------|--------|:---:|
| 1 | 04_frontend | CLAUDE.md path resolution (~/ bug) | YES — "It's blocked again" |
| 2 | 04_frontend | Claude OAuth expired | YES — "It's blocked again" |
| 3 | 04_frontend | Claude OAuth again | YES — "It's blocked again" |
| 4 | 08_backend | Agent timeout 3600s | YES — "It's blocked" |

**The chain-interlock skill (P0) blocks chain advance on FAIL — but Vera has no monitor that detects blocked tasks and auto-responds.**

### Required Fix

**Phase 1 — Vera's kanban watchdog (cron-based):**

Create a watchdog cron script (`~/.hermes/scripts/kanban_auto_unblock.sh`) that runs every 10 minutes:

```bash
#!/usr/bin/env bash
# Poll kanban for blocked tasks. For each blocked task:
# 1. Read block reason from kanban task diagnostics
# 2. Classify: AUTH | TIMEOUT | SKILL_BUG | EXHAUSTED | UNKNOWN
# 3. Auto-fix where possible:
#    AUTH → run claude auth login recovery, then unblock
#    TIMEOUT → bump task timeout 2×, unblock, let daemon retry
#    SKILL_BUG → patch skill, unblock
#    EXHAUSTED → check if fix is trivial; if so, force-complete with waiver; else escalate
#    UNKNOWN → escalate to Vera for diagnosis
# 4. Log action to kanban_auto_unblock.log
```

**Phase 2 — Vera's SOUL.md amendment:**

```
## Auto-Unblock Protocol (MANDATORY — fires on every turn)

At the START of every Vera turn (before responding to user), I check:
1. `hermes kanban list | grep '⊘'` — any blocked tasks?
2. For each blocked task: `hermes kanban show <id>` — read diagnostics
3. If block reason matches known auto-fix pattern → apply fix, unblock, note in response
4. If block reason requires human → tell user what's blocked and why
5. I do NOT wait for the user to say "it's blocked" — I check proactively.
```

**Phase 3 — Vera's cron-based poller:**

Create a recurring cron (`every 10m`, `no_agent=true`, script=`kanban_auto_unblock.sh`) that polls kanban, detects blocked tasks, and applies Phase 1 classification. This runs independently of user turns — the chain self-heals between conversations.

**Verification:** In v5, no user message should say "it's blocked" or "unblock it."

---

## Mandate 4: 2× All Timeouts, 5× Reworks

### Current State (MEASURED)

| Parameter | Current Value | Source | Breakage |
|-----------|:---:|--------|----------|
| Kanban task timeout | 3600s (1h) | `--max-runtime 60m` in chain create | Backend timed out 2× at 3604s |
| Retry limit (agent give_up) | 2 | `failure_threshold=2` in kanban diagnostics | Frontend gave_up after 2 OAuth failures |
| Claude audit timeout | 600s | `stage-auditor/SKILL.md` pitfall #20 | Audit killed before validation+postmortem |
| Claude max-turns | 12 | `stage-self-audit` step 1 | Audit hit turn limit on frontend (18-module) |
| Claude budget | $0.80 | `stage-self-audit` step 1 | Backend audit hit $0.50 cap, incomplete |
| Self-audit retries | 3 | `MAX_RETRIES=3` in stage-self-audit | User wants 5 |

### Required Fix (2× baseline, 5 retries)

| Parameter | Old | New | Where to Change |
|-----------|:---:|:---:|---|
| Kanban task timeout | 3600s | **7200s** | `kanban-asic-workflow` chain create `--max-runtime` |
| Agent failure threshold | 2 | **5** | Kanban task `--max-retries 5` (was `max-retries: 2 (default)`) |
| Claude audit timeout | 600s | **1200s** | `stage-auditor/SKILL.md` pitfall #20 |
| Claude max-turns | 12 | **24** | `stage-self-audit/SKILL.md` step 1 `--max-turns` |
| Claude budget (BA/Spec/Arch) | $0.80 | **$1.60** | `stage-self-audit` per-stage `--max-budget-usd` |
| Claude budget (Frontend/Backend) | $0.80 | **$2.00** | Per pitfall #23 already documented, never enforced |
| Claude budget (Verify/Caravel/Doc) | $0.80 | **$2.50** | Document stage hit $1.50 cap in v1 |
| Self-audit MAX_RETRIES | 3 | **5** | `stage-self-audit/SKILL.md` line 56 + retry loop |

**Per-stage budget caps (from v3 pitfall #23, now enforced):**

| Stage Type | Budget Cap |
|-----------|:---:|
| Business, Spec, Arch, Promote | $1.60 |
| Frontend, Firmware, Verification | $2.00 |
| Backend, Caravel, Document | $2.50 |

---

## Mandate 5: Enforce All of the Above

### Enforcement Mechanism

1. **`stage-self-audit/SKILL.md`** — bump version to 2.0.0, update all timeout/budget/retry values, add `## Metrics` section mandate
2. **`kanban-asic-workflow/SKILL.md`** — update chain create examples with `--max-runtime 120m --max-retries 5`
3. **Vera SOUL.md** — add auto-unblock protocol, Vera-does-NOT-execute constraints, pre-turn kanban poll
4. **`v4_dashboard.sh` / `v5_dashboard.sh`** — read from `stage_metrics.json`, remove regex grepping
5. **`kanban_auto_unblock.sh`** — new watchdog cron script (Phase 1 classification + auto-fix)
6. **Cron watchdog** — `every 10m`, monitors kanban for blocked tasks, auto-unblocks AUTH/TIMEOUT/SKILL_BUG cases
7. **`chain-interlock`** — already structurally sound (P0), but needs integration with Vera's auto-unblock to avoid user ping-pong

---

## Additional Bottlenecks Identified (Beyond the 5 Mandates)

### Bottleneck A: Claude OAuth Expiry (Recurring)

**Evidence:** Hit on frontend runs #24 (CLAUDE.md path) and #25 (OAuth expired). Documented in `stage-auditor/SKILL.md` pitfall #16 as "Headless OAuth expiration blocks the entire audit chain."

**Root cause:** Profile agents run with `HOME=~/.hermes/profiles/<name>/`. Claude OAuth tokens are at `~/.claude.json`. The `stage-self-audit` skill forces `HOME=~` for Claude invocation, but tokens still expire and the interactive `claude auth login` flow requires a browser.

**Fix already documented but not automated:**
```bash
# Capture URL from non-interactive attempt, user authorizes, paste code
timeout 8 claude auth login 2>&1 | grep 'http' # gives URL
# User pastes code → echo "$CODE" | claude auth login
```

**Auto-fix for Phase 1 watchdog:** When block reason contains "OAuth" or "authenticate," run `claude auth status`. If loggedIn=false, attempt non-interactive re-auth with stored refresh token. If that fails, escalate to user with the auth URL.

### Bottleneck B: GLIBC Clash with oss-cad-suite

**Evidence:** LibreLane AppImage failed with `GLIBC_2.38 not found` when `LD_LIBRARY_PATH` included oss-cad-suite. Fix: `unset LD_LIBRARY_PATH PYTHONPATH` before AppImage invocation.

**Fix:** Add to `librelane-backend/SKILL.md` preconditions:
```bash
unset LD_LIBRARY_PATH PYTHONPATH
export PATH="/usr/local/bin:/usr/bin:/bin:~/.local/bin"
```

### Bottleneck C: Stage-Self-Audit Prompt Doesn't Mandate Metrics

**Evidence:** All 8 validation reports use different formats. Business (01) has a Run Summary table. Frontend (04) has retry count in header. Backend (08) has no metrics section at all.

**Fix:** Update the audit prompt template in `stage-self-audit/SKILL.md` §Step 1 to include:
```
## Metrics (REQUIRED — include in every validation report)
| Metric | Value |
|--------|-------|
| Checks passed | N |
| Checks failed | N |
| Issues found | N |
| Fixes applied | N |
| Rework iterations | N |
| Wall clock (min) | N |
| Claude cost | $N |
```

### Bottleneck D: Kanban Daemon Unblock Timing

**Evidence:** Arch→Frontend auto-unblock failed (user had to manually unblock). Frontend→Firmware worked. Inconsistent daemon behavior.

**Root cause:** Kanban gateway daemon polls on an interval. If a parent completes and the daemon poll happens before the child's blocked status is processed, the child stays blocked. The gateway's unblock propagation is not atomic with task completion.

**Fix:** After `kanban complete <parent>`, explicitly run `kanban unblock <child>` to force propagation. Or add a post-completion hook to the kanban gateway.

### Bottleneck E: Backend Task Timeout vs Actual LibreLane Duration

**Evidence:** LibreLane v4-complete took 4021s (67 min) for a 69K-cell design. Kanban timeout was 3600s. Two consecutive timeouts triggered `give_up`.

**Fix already in Mandate 4 (7200s).** Additionally, the `librelane-backend` skill should include a warning: "This design size (19K post-synth cells → 69K placed cells) requires ~70 minutes on sky130A. Ensure kanban timeout ≥ 90 minutes."

### Bottleneck F: Condorcet Failure — Two Audit Attempts, Neither Complete

**Evidence:** Frontend audit retry 0 (Claude 12 turns → fix_instructions.json produced but no validation/postmortem). Retry 1 (Claude 8 turns → budget cap). Neither attempt was sufficient alone.

**Fix:** The first audit should use enough turns/budget to complete (24 turns, $2.00 for frontend). A partial audit that produces fix_instructions.json but no validation/postmortem is worse than no audit — it leaves the stage in an undocumented state.

---

## Summary: What v5 Must Change

| # | Change | Type | Owner |
|---|--------|------|-------|
| 1 | Vera auto-unblocks — pre-turn kanban poll + watchdog cron | SOUL + Script | Vera |
| 2 | Vera doesn't do agent work — dispatch constraint | SOUL | Vera |
| 3 | 2× all timeouts (7200s tasks, 1200s audit, 24 turns) | Skills + Kanban | Vera |
| 4 | 5× reworks max (was 2) | Kanban config | Vera |
| 5 | Validation reports get `## Metrics` + `stage_metrics.json` | Skill patch | Vera |
| 6 | Dashboard reads JSON, not regex | Script rewrite | Vera |
| 7 | Claude budget caps 2× + per-stage tiers enforced | Skill patch | Vera |
| 8 | GLIBC/oss-cad-suite fix in librelane-backend precondition | Skill patch | Vera |
| 9 | Post-completion unblock propagation hook | Kanban/Script | Vera |
| 10 | Framework improvement proposals (FIPs) from all 8 stage postmortems consolidated | This document | Claude Fable 5 |
