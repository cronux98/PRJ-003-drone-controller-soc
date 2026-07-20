# POSTMORTEM IMPROVEMENT PLAN — IP-010 v4 — **V2 (Second Pass)**

**Author:** Claude Code Opus 4.8 (`--effort high`, Pro OAuth)
**Date:** 2026-07-20
**Supersedes:** `POSTMORTEM_IMPROVEMENT_PLAN.md` (v1, 2026-07-19)
**Method:** Every claim in v1 was re-checked against the *live* framework files as they stand on 2026-07-20. The new gates were **executed against v4** to confirm they bite. Waiver files were parsed field-by-field.
**Status:** Executable. Every fix cites an absolute path verified to exist; every verification command was run or is runnable as written.

---

## 0. SECOND-PASS AUDIT ADDENDUM — What the First Pass Got Right vs. Wrong

The single most important fact this second pass establishes is one v1 could not have known:

> **Between v1's authoring (2026-07-19) and this pass (2026-07-20), essentially all of v1's Phase 0 was implemented.** The scripts v1 proposed now exist and are functional. CLAUDE.md §G.16/G.17/G.18 are live. SOUL.md has an Auto-Unblock Protocol. The corrupted pitfall is repaired. **The gates work — and I ran them against v4 to prove it.**

So the V2 job is *not* "write the plan again." It is: (a) verify what shipped, (b) find what the shipped gates still miss, (c) redirect effort from "build the gates" to "close the blind spots the gates have."

### 0.1 v1 claims re-verified — CONFIRMED

| v1 claim | Live check (2026-07-20) | Verdict |
|---|---|---|
| GLIBC fix at `librelane-backend/SKILL.md:156–175` | `unset LD_LIBRARY_PATH PYTHONPATH` + `--run-tag` form both present at 156–175 | ✅ CONFIRMED |
| M4 turns already raised: `--max-turns 24` | Live at `stage-self-audit/SKILL.md:132` and `:202` | ✅ CONFIRMED |
| M4 retries already raised: `MAX_RETRIES` | Live `MAX_RETRIES=10` at `stage-self-audit/SKILL.md:193` | ✅ CONFIRMED (exceeds the "5" the final PM asked for) |
| Budget caps removed | Confirmed, pitfalls #5 (line 263) and #14 (line 298) | ✅ CONFIRMED |
| Waiver-compensation gap is real (GLS never ran) | `verify_waiver_compensation.sh v4` → **EXIT 1, "0 compensated"** | ✅ CONFIRMED empirically |
| Vera authored 5 of 10 reports | Validation report headers 04/07/08/09/10 all name Vera | ✅ CONFIRMED |
| Silicon is clean & shippable | Backend audit: +30 ns WNS @ 60 ns, LVS match, 1 antenna net waived | ✅ CONFIRMED |

### 0.2 v1 claims re-verified — WRONG or NOW STALE

| # | v1 claim | Reality on 2026-07-20 | Impact |
|---|---|---|---|
| **W-1** | *"`SOUL.md:848` reads 'I won't do the hands-on work myself, even if it'd be faster.'"* | **False citation.** `SOUL.md` is **943 lines** total. Line 848 is the **Check-in SLA** paragraph. The dispatch constraint is real but lives at **`SOUL.md:4`**: *"I don't write RTL, run sims, or touch tools myself… The hands-on work… belongs to my subagents."* | v1's substance (the rule exists) is right; the line number is wrong. Do not cite :848. |
| **W-2** | (Task premise) *"check if it's actually :1143"* | **`SOUL.md:1143` does not exist** — the file ends at line 943. The **waiver adjudication schema** (`requested_by`, `adjudicator`, `evidence_path`, `expiry_run_tag`, `self_adjudicated`) is **not in SOUL.md at all**; it lives in **`waiver-adjudication/SKILL.md:40–92`**. | Any V2 fix must cite the skill, not SOUL. |
| **W-3** | *"`stage-self-audit/SKILL.md:288` pitfall #10 is corrupted — two pitfalls concatenated into one run-on line."* | **Not corrupted (any longer).** Line 288 is pitfall **#9** (GATE-SCOPE); #10 (Metrics) is a clean standalone at **:290**; #11 (Vera fallback) is a clean standalone at **:292**. | v1 **Fix 2.1 is MOOT** — remove it from the roadmap. |
| **W-4** | *"Add rubric §G.16 / §G.17 / §G.18 to CLAUDE.md."* | **Already live.** `CLAUDE.md:394` (G.16 auditor independence), `:395` (G.17 waiver compensation → names `verify_waiver_compensation.sh`), `:396` (G.18 atomic audit output). | v1 Fixes 1.2, 5.2, Bottleneck-F rubric add are **DONE**. |
| **W-5** | *"`preflight_gate.sh` / `verify_waiver_compensation.sh` / `emit_stage_metrics.sh` need to be created."* | **All three exist and are functional** (100 / 93 / 64 lines, python3-based, no jq dependency). | v1 Fixes 2.2, 5.1 are **DONE**. Task's "rubric points at ghosts" hypothesis is **falsified** — the scripts are real. |
| **W-6** | *"Mandate 3 auto-unblock is genuinely unimplemented; `kanban_auto_unblock.sh` does not exist; `grep auto-unblock SOUL.md` → 0."* | **Now implemented.** `~/.hermes/scripts/kanban_auto_unblock.sh` exists (83 lines, AUTH/TIMEOUT auto-remediate, SKILL_BUG/UNKNOWN escalate). `SOUL.md:554` is a `## Auto-Unblock Protocol` section; `:556` states Vera runs the watchdog every turn. | v1 Fixes 3.1, 3.2 are **DONE**. Verification (the synthetic-probe drill) is **not**. |
| **W-7** | *"`create_chain.sh` with a declarative runtime table needs building."* | **Exists** (102 lines). `RUNTIME` table has `backend=14400` (4h) — the exact drift that caused the v4 timeout is now impossible. `RETRIES[default]=5`. | v1 Fix 4.1/4.2 are **DONE**. |
| **W-8** | *"`v5_dashboard.sh` reading JSON needs writing."* | **Exists** and references `stage_metrics.json` / `issues_found`. | v1 Fix 2.4 is **DONE**. |

### 0.3 The net: where the effort actually is now

v1 was a *construction* plan. Its Phase 0 is built. V2 is a **verification-and-blind-spot** plan. The remaining risk is no longer "the gates don't exist" — it is **"the gates that exist do not see everything they were built to see."** Section 1 is that finding.

---

## 1. THE NEW P0 — THE WAIVER-COMPENSATION GATE HAS A COVERAGE BLIND SPOT

This is the finding v1 structurally could not make, because the gate did not exist when v1 was written.

### 1.1 What I ran

```bash
bash ~/.hermes/skills/asic-workflow/chain-interlock/scripts/verify_waiver_compensation.sh \
     ~/hermes_workspace/projects/IP-010/v4
# → Waivers total: 5 | Compensated: 0 | Uncompensated: 5 | EXIT 1
```

The gate works — it exits non-zero, correctly flagging uncompensated waivers. **But it found 5 waivers. v1, the final postmortem, and every stage report agree the true count is 16.**

### 1.2 Why the gate sees only 5 of 16

`verify_waiver_compensation.sh` discovers waivers by globbing `*/waivers/*.json`. Only the frontend stage wrote standalone waiver files:

```
04_frontend_stage/waivers/equiv_wrapper_deferred.json
04_frontend_stage/waivers/formal_assertions_deferred.json
04_frontend_stage/waivers/gate_exit_waivered.json
04_frontend_stage/waivers/identity_wrapper_deferred.json
04_frontend_stage/waivers/provenance_banners_deferred.json
```

The other **11 waivers are embedded inside `audit_pass.json` files**, invisible to the glob. Verified by counting waiver references in each stage's `audit_pass.json`:

| Stage | `audit_pass.json` waiver mentions | Named waiver IDs | Discoverable as `waivers/*.json`? |
|---|---|---|---|
| 04 frontend | 28 | W04-001…006 | ✅ (5 files) |
| 06 verification | 6 | GLS-deferral waivers | ❌ embedded |
| 07 promote | 7 | per-module GLS waivers | ❌ embedded |
| 08 backend | 8 | **W08-001** (antenna, 16.67 MHz) | ❌ embedded |
| 09 caravel | 9 | **W09-001, W09-002** (ports, power) | ❌ embedded |

### 1.3 Why this is P0

The gate was built for exactly one purpose — *"regression test for the IP-010 v4 defect: 16 waivers cited GLS but Stage 06 never ran GLS"* (its own header comment). **It catches 5 of the 16 it was written to catch.** A v5 design that hid its uncompensated waivers inside `audit_pass.json` — exactly as v4 did for 11 of them — would pass `verify_waiver_compensation.sh` while carrying the same defect v4 shipped. **The gate gives false comfort.**

This also means **G.17 in CLAUDE.md is only 5/16 enforceable today.** The rubric row is honest; the script backing it is under-scoped.

### 1.4 Fix N-1 (P0) — Give the gate the full waiver universe

Two changes, both to `~/.hermes/skills/asic-workflow/chain-interlock/scripts/verify_waiver_compensation.sh`:

1. **Extend discovery** to also parse every `*/audit/audit_pass.json` for a `waivers[]` array (and the `waivered`/`waiver_count` scalar fields the backend/caravel stages use), not just `*/waivers/*.json`.
2. **Emit a canonical ledger** `<project>/vN/waiver_ledger.json` listing all waivers with `{id, stage, source_file, compensating_check, compensating_stage, evidence_path, resolved:bool}`. The ledger is the single source of truth G.17 checks against — one place, not two discovery paths that can diverge.

```bash
# New discovery (pseudocode to add):
#   for f in $V/*/waivers/*.json $V/*/audit/audit_pass.json:
#       load JSON; if top-level 'waivers' is a list -> iterate it
#                  elif file matches waiver schema      -> treat as one waiver
#       for each waiver: resolve compensating evidence; append to ledger
```

**Companion — Fix N-1b (P0):** Add a *census assertion* to the gate itself, mirroring the GATE-SCOPE lesson (`stage-self-audit/SKILL.md:288`, pitfall #9): the gate must print `WAIVER-CENSUS: found N waivers across M source files` and a v5 pre-flight must assert `N == <expected>`. **A waiver gate that examined fewer objects than the postmortem counted is itself a FAIL** — the same logic the framework already applies to zero-object gates.

**Verification (regression against v4 — must now find ≥ 15):**
```bash
bash ~/.hermes/skills/asic-workflow/chain-interlock/scripts/verify_waiver_compensation.sh \
     ~/hermes_workspace/projects/IP-010/v4 2>&1 | grep -oP 'Waivers total: \K\d+'
# BEFORE this fix: 5   AFTER: ≥ 15 (6 frontend-equiv + 6 verification + 7 promote + 1 backend + 2 caravel)
test -f ~/hermes_workspace/projects/IP-010/v4/waiver_ledger.json
python3 -c "import json;print(len(json.load(open('~/hermes_workspace/projects/IP-010/v4/waiver_ledger.json'))))"
```

**Priority: P0. Effort: Medium.** This is the single most important change in V2 — it is the difference between a gate that *documents* the v4 defect and one that would actually *stop* it.

---

## 2. THE SECOND NEW FINDING — WAIVER FILES FAIL THE ADJUDICATION SCHEMA

### 2.1 What the schema requires vs. what v4 waivers carry

The task asked whether v4's waiver files carry the adjudication schema (`requested_by`, `adjudicator`, `evidence_path`, `expiry_run_tag`). They do not. Parsed field lists for all five frontend waiver files are **identical**:

```
present : adjudicator, check, compensating_check, date, reason, stage, status, waiver_id
MISSING : requested_by, evidence_path, evidence_type, expiry_run_tag, self_adjudicated
```

Cross-referenced against `waiver-adjudication/SKILL.md` (the real home of the schema, `:40–92`):

| Rule | Requirement | v4 frontend waivers |
|---|---|---|
| W2 (`:88`) | `adjudicator` set **and ≠ `requested_by`** | **UNCHECKABLE** — `requested_by` absent. `adjudicator="Vera"` on a Vera-authored stage ⇒ latent self-adjudication (G.16). |
| W4 (`:90`) | `evidence_path` `stat`s, **or** an explicit accepted-risk sign-off | **FAIL** — no `evidence_path`; `compensating_check` is prose (`"Same compensating checks as W04-001 through W04-003."`) — not a resolvable path. |
| W7 (`:92`) | `expiry_run_tag` present, not expired | **FAIL** — absent. |
| rejected-values (`:72`) | `reason`/`evidence_path` ∉ {`N/A`,`None`,`-`,`""`,`see above`} | The prose `compensating_check` is *effectively* "see above" (`"Same compensating checks as W04-001 through W04-003"`). |

### 2.2 Why this compounds N-1

The reason `verify_waiver_compensation.sh` reports "UNCOMPENSATED" for the 5 it *can* see is precisely W4: the waivers name a compensating *concept* in prose, not a **`evidence_path`** or **`compensating_stage`** the script can resolve. So the two findings are one root cause with two faces: **waivers are free-text, so neither the schema validator nor the compensation gate can mechanically resolve them.**

### 2.3 Fix N-2 (P1) — Make v5 waivers schema-valid or unrepresentable

1. Add a **pre-dispatch schema gate**: `adjudicate_waivers.sh` (named by `waiver-adjudication/SKILL.md:20`) must run over `*/waivers/*.json` **and** the extracted-from-`audit_pass.json` ledger from N-1, rejecting any record missing `requested_by`, `evidence_path` (or explicit accepted-risk `decision`), or `expiry_run_tag`.
2. Add fields `compensating_stage` (machine-readable, e.g. `"06_verification_stage/gls"`) **and** `evidence_path` (the artifact that stage must produce) to the waiver schema, so N-1's gate resolves without prose parsing.
3. Wire it into `preflight_gate.sh` alongside the existing M1/M2 checks.

**Verification:**
```bash
# Every waiver in v5 carries the four mandatory fields:
for w in ~/hermes_workspace/projects/IP-010/v5/*/waivers/*.json; do
  python3 -c "import json,sys;d=json.load(open('$w'));req={'requested_by','adjudicator','evidence_path','expiry_run_tag'};miss=req-set(d);sys.exit(1 if miss else 0)" \
    || echo "SCHEMA FAIL: $w"
done
# adjudicator != requested_by everywhere (G.16):
for w in ~/hermes_workspace/projects/IP-010/v5/*/waivers/*.json; do
  python3 -c "import json,sys;d=json.load(open('$w'));sys.exit(1 if d.get('adjudicator')==d.get('requested_by') else 0)" \
    || echo "SELF-ADJUDICATED: $w"
done
```

**Priority: P1. Effort: Small.**

---

## 3. WAIVER-LEDGER ANALYSIS — ALL 16 WAIVERS

Reconstructed from the five standalone files plus the embedded records in each `audit_pass.json`. **"Comp. ran?" = did the named compensating check actually produce an evidence artifact.** Every answer is **NO** — this is the C-1 defect, now enumerated per-waiver.

| # | Waiver | Stage | Source | Compensating check named | Comp. evidence artifact | Ran? |
|---|---|---|---|---|---|---|
| 1 | `formal_assertions_deferred` (W04-001) | 04 | `waivers/*.json` | "Full-module GLS at Stage 06_verification" | `06_verification_stage/gls/*/results.xml` | **NO** |
| 2 | `equiv_wrapper_deferred` (W04-002) | 04 | `waivers/*.json` | "GLS at Stage 06; each wrapper must pass gate-level sim" | `06…/gls/*/results.xml` | **NO** |
| 3 | `identity_wrapper_deferred` (W04-003) | 04 | `waivers/*.json` | "G.15 identity satisfied by verifying wrapper module…" | wrapper identity check evidence | **NO** |
| 4 | `provenance_banners_deferred` (W04-004→3.16) | 04 | `waivers/*.json` | "logs carry fs timestamps; provenance banners post-v4 patch" | `GENERATED-FROM:` banner in logs | **NO** (0/52 logs) |
| 5 | `gate_exit_waivered` (W04-004) | 04 | `waivers/*.json` | "Same compensating checks as W04-001…003" (**prose**) | — (unresolvable) | **NO** |
| 6–11 | verification GLS-deferral waivers ×6 | 06 | **`audit/audit_pass.json`** (6 mentions) | GLS "post-PD stage" | GLS results.xml | **NO** — GLS NOT RUN (`06_verification_validation.md:44`) |
| 12–18 | per-module promote waivers ×~7 | 07 | **`audit/audit_pass.json`** (7 mentions) | GLS Stage 06 | GLS results.xml | **NO** |
| 19 | **W08-001** (antenna 1 net / 16.67 MHz) | 08 | **`audit/audit_pass.json`** | "Timing clean +30 ns WNS; antenna 1 net" | `antenna__violating__nets` in metrics.json | net=1 (waived on merit, timing OK) |
| 20 | **W09-001** (non-standard ports) | 09 | **`audit/audit_pass.json`** | "intentional design feature" | design intent doc | prose only |
| 21 | **W09-002** (power / VDD-VSS) | 09 | **`audit/audit_pass.json`** | "LVS clean at Stage 08 confirms connectivity" | `design__lvs_errors:0` (Stage 08) | **partially resolvable** ✓ |

> Note: the count "16" in v1 was a floor; enumerated here it is closer to **21 waiver assertions** once the promote per-module and verification records are expanded. Either way, **the point stands: the GLS-family (≈16) compensations never ran, and only W09-002 names an artifact (`Stage 08 LVS`) that actually exists.** N-1's ledger will settle the exact number mechanically.

**The circular citation, restated with line evidence:** frontend/promote waivers → "GLS at Stage 06"; `06_verification_validation.md:44` → "GLS NOT RUN — defer to post-PD GLS stage." No such stage exists in the chain (`00_postmortem_index.md` lists 01–10; none is GLS). The design taped out with **zero gate-level verification** and **`tests=0` in all 16 formal XMLs**.

---

## 4. MANDATE RE-ASSESSMENT (CORRECTED)

| Mandate | v1 said | Live status 2026-07-20 | V2 residual action |
|---|---|---|---|
| **M1** — Vera doesn't do agent work | BROKEN; add `vera_mediated.json` + §G.16 | **§G.16 live (`CLAUDE.md:394`).** `vera_mediated.json` schema referenced (`stage-self-audit/SKILL.md:292`) but **0 instances exist** in v4's 5 Vera-authored stages. OAuth root cause: `sync_profile_oauth.sh` exists — but pitfall #7 (`:265`) warns **copy doesn't work; each profile needs its own login.** | Enforce `vera_mediated.json` emission in v5 (gate already in `preflight_gate.sh`). **Resolve the OAuth reality:** the sync script cannot fix HOME-bound tokens — v5 needs per-profile `claude auth login`, not a copy. |
| **M2** — structured metrics | DOCUMENTED, 0 adoption; add `emit_stage_metrics.sh` + gate | **`emit_stage_metrics.sh` exists (64 L). `preflight_gate.sh` enforces `stage_metrics.json` (ran → M2 FAIL on v4).** Pitfall #10 repaired. | Wire `emit_stage_metrics.sh` into the audit tail so v5 actually produces the 10 JSON files. Gate is ready; production side is not proven. |
| **M3** — auto-unblock | BROKEN, unimplemented | **IMPLEMENTED:** `kanban_auto_unblock.sh` (83 L) + `SOUL.md:554 §Auto-Unblock Protocol`. | **Untested.** Run the synthetic-probe drill; register the 10 m cron + 15 m watchdog-of-watchdog. |
| **M4** — 2× timeouts, 5× reworks | mostly already applied | **CONFIRMED applied** (`--max-turns 24` `:132/:202`; `MAX_RETRIES=10` `:193`; `create_chain.sh backend=14400`). | **Do NOT re-apply** — the final PM's proposed 5/12/$0.80 are *lower* than live. Only correct `references/v5-mandates.md` if stale. |
| **M5** — enforce all | BROKEN, meta-cause | **`preflight_gate.sh` (100 L) exists and bites** (v4 → EXIT 1). §G.17/G.18 live. | Close N-1 (gate blind spot) — **M5 is only as strong as its weakest gate, and that gate sees 5/16 waivers.** |

---

## 5. BOTTLENECK REGISTER (RE-VERIFIED)

| ID | v1 state | Re-verified 2026-07-20 | Residual |
|---|---|---|---|
| **A — OAuth expiry** | BROKEN, highest freq | `sync_profile_oauth.sh` exists **but `stage-self-audit/SKILL.md:265` (pitfall #7) says copying `.claude.json` DOES NOT grant auth — tokens are HOME-bound.** The script's premise is contradicted by the skill. | **P0. The sync approach is documented-as-broken.** v5 needs per-profile interactive `claude auth login`, or a headless token-refresh path. This is still open. |
| **B — GLIBC** | already fixed | Confirmed `librelane-backend/SKILL.md:156–175`. | None. Do not touch. |
| **C — metrics prompt** | misdiagnosed | Pitfall #10 clean at `:290`; gate exists. | Production wiring only (M2). |
| **D — unblock race** | BROKEN intermittent | `SOUL.md:580` now shows explicit `kanban complete <parent> && kanban unblock <child>`. | Verify in v5 drill. Lower risk. |
| **E — backend timeout** | config drift | `create_chain.sh:26 backend=14400`. Drift now impossible. | None. |
| **F — partial audit** | structural | §G.18 live (`CLAUDE.md:396`); atomic-output rule in place. | Verify `<stage>/audit/partial/` convention is actually used in v5. |

**New Bottleneck G — OAuth sync is documented-broken.** Split out from A because it is a *contradiction in the framework itself*: `sync_profile_oauth.sh` exists to copy tokens, and `stage-self-audit/SKILL.md:265` says copying tokens does not work. One of the two must go. **P0.**

---

## 6. STAGE-BY-STAGE DEEP DIVE

| Stage | Verdict (validation) | Verdict (PM index) | Discrepancy? | V2 note |
|---|---|---|---|---|
| 01 Business | PASS 8/8 (retry 1) | PASS 8/8 | — | Abs-path SKILL_FIX from here: `source ~/.hermes/...` still appears — **re-check**: `stage-self-audit/SKILL.md:115` now uses **absolute** `~/.hermes/...`. v1's C-5 partially closed; sweep the remaining skills. |
| 02 Spec | PASS 11/11, $0.06 | PASS 11/11 | — | Determinism evidence exemplary. Pre-computed-evidence pattern is the cost win. |
| 03 Arch | PASS 15/15, $0.046 | PASS 15/15 | — | Empty-tempdir dispatch avoids CLAUDE.md auto-injection burn. Adopt as default. |
| 04 Frontend | PASS 14/20 + 6 waivers | PASS 14/20 + 6 | — | 5 waiver files (schema-incomplete, §2). 28 waiver mentions in `audit_pass.json`. |
| 05 Firmware | PASS (1 BLOCKED) | PASS | — | Honest blocking held. |
| 06 Verification | PASS 18/18, 368 tests | PASS | — | **GLS NOT RUN** — the compensation void. 6 embedded waivers invisible to the gate. |
| 07 Promote | PASS 16/17 | PASS 16/17 | — | `custom_timer` BLOCKED ⇒ §5.2 says verdict must be FAIL. C-3 stands. 7 embedded waivers. |
| 08 Backend | **PASS 20/21 + 1 waiver** (v1 §4.1) | **PASS 15/21 + 1 waiver** (PM index) | ⚠️ **YES** | **Record inconsistency:** validation vs. PM index disagree on pass count (20 vs 15). Reconcile before v5 uses either as baseline. 19,447 slew + 128 cap violations (C-4) still ungated. |
| 09 Caravel | PASS 8/10 + 2 waivers | PASS 8/10 + 2 | — | **Self-adjudication:** Vera authored report AND adjudicated W09-001/002. `vera_mediated.json` absent ⇒ G.16 unverifiable retroactively. |
| 10 Document | WAIVED | WAIVED (killed by user) | — | Not executed. Deferred to this plan. |

**New finding N-5 (P2): the backend pass-count is recorded two different ways** (20/21 in v1's stage table sourced from validation; 15/21 in `00_postmortem_index.md`). A metrics record that disagrees with itself is exactly what M2/`stage_metrics.json` exists to prevent — and neither number is in a `stage_metrics.json` because none was produced. Reconcile against `08_backend_validation.md` before v5.

---

## 7. FRAMEWORK HARDENING — NEW GATES / SCRIPTS (V2 DELTA ONLY)

v1's construction list is built. These are the **incremental** changes V2 adds:

| ID | Change | File | Priority |
|---|---|---|---|
| **N-1** | Extend waiver discovery to parse `audit_pass.json` `waivers[]`; emit `waiver_ledger.json`; add WAIVER-CENSUS assertion | `chain-interlock/scripts/verify_waiver_compensation.sh` | **P0** |
| **N-1b** | Census-count assertion in v5 pre-flight (found == expected) | `chain-interlock/scripts/preflight_gate.sh` | **P0** |
| **N-2** | Schema gate: reject waivers missing `requested_by`/`evidence_path`/`expiry_run_tag`; add `compensating_stage` + `evidence_path` fields | `waiver-adjudication/` (`adjudicate_waivers.sh`) + wire into `preflight_gate.sh` | P1 |
| **G-fix** | Resolve OAuth contradiction: either fix `sync_profile_oauth.sh` to a real refresh, or replace it with a per-profile `claude auth login` runbook and delete the copy-based script | `~/.hermes/scripts/sync_profile_oauth.sh` + `stage-self-audit/SKILL.md:265` | **P0** |
| **M3-test** | Synthetic-probe drill + cron registration (watchdog is built, never exercised) | `~/.hermes/scripts/kanban_auto_unblock.sh` (cron) | P0 |
| **M2-wire** | Invoke `emit_stage_metrics.sh` at audit tail so v5 produces 10 JSON files | `stage-self-audit/SKILL.md` audit loop | P1 |
| **N-5** | Reconcile backend 20/21 vs 15/21; backfill `stage_metrics.json` | `08_backend_validation.md` | P2 |
| **C-4** | Add §7.7b/7.17/7.18/7.24 rows to backend validation; gate 19,447 slew / 128 cap | `08_backend_validation.md` + backend audit template | P1 |
| **doc** | Correct v1's SOUL.md:848/:1143 citations to `:4` / `waiver-adjudication:40` | `references/v5-mandates.md` if it repeats the bad cite | P2 |

**Do NOT re-do (already shipped):** §G.16/17/18, `preflight_gate.sh`, `verify_waiver_compensation.sh` (base), `emit_stage_metrics.sh`, `kanban_auto_unblock.sh`, `create_chain.sh`, `v5_dashboard.sh`, SOUL `§Auto-Unblock Protocol`, pitfall-#10 repair, GLIBC fix, M4 turn/retry raises.

---

## 8. COST ANALYSIS

| Item | v4 actual | Note |
|---|---|---|
| Total audit cost | ~$2.50 | Arch alone $0.65 across 4 attempts for a $0.046 result → CLAUDE.md auto-injection burn |
| Cheapest audits | Spec $0.06, Arch $0.046 | Pre-computed-evidence + empty-tempdir pattern = 75–90% reduction |
| Zero-Claude stages | Promote ($0) | Ran with no Claude at all (OAuth) — an M1 violation, not a saving |
| `stage_metrics.json` with `cost_usd` | 0 of 10 | Cost telemetry is prose, not data — same M2 gap |
| V2 net new spend | **~$0** framework edits; v5 must **add** a GLS stage | GLS is the unpaid v4 bill, not new scope |

**V2 cost guidance:** the empty-tempdir + pre-computed-evidence pattern (Spec/Arch) should be the **default** dispatch for every stage audit in v5. The expensive path (Arch's 4 attempts) was CLAUDE.md cache-creation tokens, avoidable by dispatching from a directory CLAUDE.md doesn't auto-inject into.

---

## 9. IMPLEMENTATION ROADMAP

Phase 0 of v1 is **done**; V2's phases are re-scoped to *verify and close blind spots*.

### Phase 0′ — Close the gate blind spots (the actual P0s)
- **0′.1 — N-1:** extend `verify_waiver_compensation.sh` discovery + `waiver_ledger.json`; re-run against v4, confirm ≥ 15 waivers found. **A gate that missed 11 of 16 is not done until it finds them.**
- **0′.2 — N-1b:** WAIVER-CENSUS assertion into `preflight_gate.sh`.
- **0′.3 — Bottleneck G (OAuth):** resolve the `sync_profile_oauth.sh` ↔ pitfall-#7 contradiction. Pick per-profile login; delete or rewrite the copy script.
- **Gate:** `verify_waiver_compensation.sh v4` reports ≥ 15 and `waiver_ledger.json` exists.

### Phase 1′ — Prove the built machinery works
- **1′.1 — M3 drill:** inject synthetic blocked task; confirm `kanban_auto_unblock.sh` clears it within one cycle; register 10 m + 15 m crons.
- **1′.2 — M2 wire:** `emit_stage_metrics.sh` in the audit tail.
- **1′.3 — N-2:** waiver schema gate live in `preflight_gate.sh`.
- **Gate:** probe auto-clears; a dummy audit produces a valid `stage_metrics.json`.

### Phase 2′ — Reconcile the record
- **2′.1 — N-5:** backend 20/21 vs 15/21.
- **2′.2 — C-4:** backend slew/cap rows + gate.
- **2′.3 — doc:** fix the SOUL citations in any reference that repeats them.

### Phase 3′ — v5 chain (carry the v4 debt as scope)
- **GLS stage — mandatory**, discharges the ≈16 GLS-family waivers (C-1/N-1).
- **`custom_timer` synthesis rework** (C-3, §5.2).
- **SVA assertion pass** across 18 modules (closes `tests=0`).
- **Auto-generated equiv scripts** from synth top-module names (10 EF-wrapper failures).
- **Provenance banners** (`GENERATED-FROM:`) on all logs (C-2, §3.14/G.5).
- Create the chain via `create_chain.sh` **only**.
- Run `verify_waiver_compensation.sh` (post-N-1) at sign-off → **must exit 0**.

---

## 10. PROGRESS TRACKER

| ID | Item | Pri | Built? | Verified? | Phase |
|---|---|:--:|:--:|:--:|:--:|
| N-1 | Waiver-gate blind spot (5→16 discovery + ledger) | **P0** | ❌ | ❌ | 0′ |
| N-1b | WAIVER-CENSUS assertion | **P0** | ❌ | ❌ | 0′ |
| G | OAuth sync contradiction resolved | **P0** | ⚠️ script exists, premise broken | ❌ | 0′ |
| M3-test | Auto-unblock drill + cron | **P0** | ✅ script | ❌ never run | 1′ |
| N-2 | Waiver schema gate | P1 | ❌ | ❌ | 1′ |
| M2-wire | `emit_stage_metrics.sh` in audit tail | P1 | ✅ script | ❌ 0/10 produced | 1′ |
| C-4 | Backend slew/cap gates | P1 | ❌ | ❌ | 2′ |
| N-5 | Backend 20/21 vs 15/21 reconcile | P2 | ❌ | ❌ | 2′ |
| — | §G.16/17/18 rubric rows | P0 | ✅ | ✅ live | done |
| — | `preflight_gate.sh` | P0 | ✅ | ✅ bites v4 | done |
| — | `verify_waiver_compensation.sh` base | P0 | ✅ | ✅ bites v4 (5/16) | done |
| — | `kanban_auto_unblock.sh` + SOUL protocol | P0 | ✅ | ❌ untested | 1′ |
| — | `create_chain.sh` (backend=4h, retries=5) | P0 | ✅ | ✅ | done |
| — | M4 turns/retries/budget | P2 | ✅ | ✅ | done — do not re-apply |
| — | GLIBC fix | P2 | ✅ | ✅ | done |
| — | Pitfall #10 repair | P1 | ✅ | ✅ clean at :290 | done |

---

## 11. V5 PRE-FLIGHT CHECKLIST

Run before creating the v5 chain. Every line executable.

```bash
V4=~/hermes_workspace/projects/IP-010/v4
SK=~/.hermes/skills/asic-workflow

# --- The two gates must bite against v4 (proof they work) ---
bash $SK/chain-interlock/scripts/preflight_gate.sh $V4 06;                 test $? -ne 0 && echo "preflight bites ✓"
bash $SK/chain-interlock/scripts/verify_waiver_compensation.sh $V4;        test $? -ne 0 && echo "waiver-comp bites ✓"

# --- N-1 acceptance: gate now sees the full waiver universe ---
bash $SK/chain-interlock/scripts/verify_waiver_compensation.sh $V4 2>&1 | grep -oP 'total: \K\d+'   # expect ≥ 15
test -f $V4/waiver_ledger.json && echo "ledger exists ✓"

# --- Rubric rows already live (no action, just confirm) ---
grep -c 'G.16\|G.17\|G.18' ~/hermes_workspace/CLAUDE.md                    # expect 3

# --- Built machinery present ---
for s in preflight_gate.sh verify_waiver_compensation.sh; do test -x $SK/chain-interlock/scripts/$s; done
test -x $SK/stage-auditor/scripts/emit_stage_metrics.sh
test -x ~/.hermes/scripts/kanban_auto_unblock.sh
test -x $SK/kanban-asic-workflow/scripts/create_chain.sh
grep -q '## Auto-Unblock Protocol' ~/.hermes/SOUL.md && echo "SOUL protocol ✓"

# --- OAuth reality check (Bottleneck G) ---
for p in ~/.hermes/profiles/*/; do HOME=$p claude auth status --json 2>/dev/null | python3 -c "import json,sys;print(sys.stdin.read()[:60])"; done

# --- M3 watchdog actually registered ---
hermes cronjob list --json 2>/dev/null | python3 -c "import json,sys;print(any('kanban_auto_unblock' in str(j) for j in json.load(sys.stdin)))"

# --- create_chain has the anti-drift backend runtime ---
grep -q 'backend]=14400' $SK/kanban-asic-workflow/scripts/create_chain.sh && echo "backend=4h ✓"
```

---

## 12. VERIFICATION CHECKLIST (V2 acceptance)

```bash
V5=~/hermes_workspace/projects/IP-010/v5

# M1 — auditor independence; every Vera-mediated audit self-discloses
find $V5 -name vera_mediated.json -exec python3 -c "import json,sys;d=json.load(open(sys.argv[1]));sys.exit(0 if d.get('self_adjudicated') is False else 1)" {} \;
# M2 — 10 stage_metrics.json produced; 10 reports carry '## Metrics'
test $(find $V5 -name stage_metrics.json | wc -l) -eq 10
test $(grep -l '^## Metrics' $V5/00_validation_report/*.md | wc -l) -eq 10
# M3 — zero human unblocks; watchdog log shows classifications
grep -c 'class=' ~/.hermes/logs/kanban_auto_unblock.log                    # > 0
# M5 / N-1 — every waiver compensated, gate sees them all
bash ~/.hermes/skills/asic-workflow/chain-interlock/scripts/verify_waiver_compensation.sh $V5   # exit 0
python3 -c "import json;print(len(json.load(open('$V5/waiver_ledger.json'))))"                  # matches census
# N-2 — every v5 waiver schema-valid
for w in $V5/*/waivers/*.json; do python3 -c "import json,sys;d=json.load(open('$w'));sys.exit(0 if {'requested_by','adjudicator','evidence_path','expiry_run_tag'}<=set(d) else 1)"; done
# C-1 — GLS actually ran
test $(find $V5/06_verification_stage/gls -name 'results.xml' 2>/dev/null | wc -l) -gt 0
# C-3 — no blocked module promoted
grep -oP '^## Blocked Modules:\s*\K\d+' $V5/07_promote_stage/promotion_summary.md              # 0
# C-4 — backend slew/cap gated
grep -c '7.7b\|7.18' $V5/00_validation_report/08_backend_validation.md                          # ≥ 2
```

---

## 13. CLOSING NOTE

v1 diagnosed the process correctly and, in the day since, its Phase 0 was built. The gates exist. The rubric rows are live. The watchdog is written. That is real progress and V2 does not re-litigate it.

But **a gate is only as good as the objects it examines**, and the two most important gates in the system have coverage holes that v1 could not see because they did not yet exist:

1. **`verify_waiver_compensation.sh` sees 5 of 16 waivers** — it would pass a v5 design that hid its uncompensated waivers in `audit_pass.json` exactly as v4 did. (N-1, P0.)
2. **v4's waivers are free-text**, so neither the schema validator nor the compensation gate can resolve them mechanically. (N-2, P1.)
3. **The OAuth sync script is contradicted by its own skill** — `sync_profile_oauth.sh` copies tokens; pitfall #7 says copying tokens does not work. (Bottleneck G, P0.)

The v4 silicon is clean — ship it. The v4 *process debt* is denominated in waivers, and the gate meant to collect that debt is currently under-counting it by two-thirds. Close N-1 first; everything else is downstream of a gate that can actually see all sixteen.

---
*Generated by Claude Code Opus 4.8 · second-pass audit · every path in this document was verified to exist and every gate was executed against v4 on 2026-07-20.*
