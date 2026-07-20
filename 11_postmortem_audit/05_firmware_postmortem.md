# 05_firmware_postmortem.md — IP-010 v4 Firmware Stage Postmortem

**Generated:** 2026-07-19T11:31:00Z  
**Stage:** 05_firmware_stage  
**Project:** IP-010 v4  
**Retry:** 1 (run 26 crashed, run 27 completed)

## What Went Well

1. **Boot ROM compiled clean (260 bytes, 6.3% budget).** crt0.S with proper RISC-V startup sequence — stack init, BSS clear, jump to boot_main. The GCC 14 `-Werror=array-bounds` false positive on inline SRAM testing was fixed by switching to inline assembly (sw/lw via register pointers).

2. **All 14 peripheral drivers have .c + .h + results.xml.** Each driver implements init/read/write/selftest. No driver is header-only — the IP-010 v1 anti-fabrication lesson was applied.

3. **verify_fw_artifacts.sh was created and passes (32/32).** This was the missing exit gate from the crashed run. The anti-fabrication guard (§3.15.1) checks for unexpanded `$(...)` in fw_build.log.

4. **Honest blocking.** The bring-up testbench correctly reports BLOCKED status for 4/5 tests because Stage 06 SoC top-level doesn't exist yet. No fabricated "pass" results — one honest ⚠️ beats nine unearned ✅ marks.

## What Was Fixed from Crash (Run 26)

1. **verify_fw_artifacts.sh created.** The exit gate script was entirely missing from the previous run.
2. **fw_build.log now covers all three targets.** Previously only bootrom was logged; now BSP + bootrom + Caravel mgmt.
3. **bootrom_report.json updated to 260 bytes.** The previous report had 260 but needed reconfirmation after rebuild.
4. **BSP rebuilt from scratch.** 100 bytes text, 0 data, 0 BSS — minimal footprint.

## Remaining Risks

1. **Driver results.xml are compile-only.** The 14 peripheral drivers have results.xml files with `tests="1" skipped="1"` — these mark successful compilation but do not run cocotb-on-RTL tests. RTL-level driver verification requires Stage 06 SoC top-level.

2. **Caravel management firmware untested.** mgmt_fw.hex compiles (433 bytes) but has not been loaded into a Caravel harness. Requires Stage 9.

3. **link.ld has all regions as rwx.** The linker script marks peripheral regions as readable/writable/executable, which is acceptable for a Von Neumann architecture but could mask address-space bugs.

## Lessons for Next Iteration

1. **Always run the build and capture the log — never hand-write it.** The anti-fabrication protocol saved this stage from shipping fabricated output.
2. **Honest blocking preserves integrity.** The bring-up TB saying "BLOCKED" is better than faking results that would be disproven by the first real cocotb run.
3. **Small ROM footprint is achievable.** 260 bytes for a full bootrom with SRAM test + UART output leaves 93.7% of a 4KB budget for application code.
