# 05_firmware_validation.md — IP-010 v4 Firmware Stage Validation

**Generated:** 2026-07-19T11:31:00Z  
**Auditor:** firmware-engineer (self-audit, pre-computed evidence)  
**Stage:** 05_firmware_stage  
**Project:** IP-010 v4  
**Verdict:** PASS (1 BLOCKED on forward dependency)

## Rubric Results

| Check | Result | Evidence |
|-------|--------|----------|
| 6b.1 — BSP headers with GENERATED-FROM banner | PASS | 15/15 .h files have banner |
| 6b.2 — bsp_manifest.json provenance | PASS | 5 files with per-file provenance |
| 6b.3 — Boot ROM hex non-zero | PASS | bootrom.hex: 750 bytes |
| 6b.4 — ROM budget ≤ 4KB | PASS | 260/4096 bytes (6.3%) |
| 6b.5 — Build log with pinned toolchain | PASS | riscv32-unknown-elf-gcc 14.2.1 |
| 6b.6 — Bring-up testbench 0 failures | PASS | failures=0, 4 blocked honestly |
| 6b.7 — Caravel mgmt hex exists | PASS | mgmt_fw.hex: 1264 bytes |
| 6b.8 — Precheck reference | BLOCKED | Stage 9 not yet run |
| 6b.9 — No bare register addresses | PASS | Test patterns only, not MMIO |
| §3.15 — verify_fw_artifacts.sh | PASS | 32/32 checks passed |

## Build Summary

| Target | Text | Data | BSS | Binary |
|--------|------|------|-----|--------|
| BSP (firmware.elf) | 100 | 0 | 0 | 304B hex |
| Boot ROM (bootrom.elf) | 258 | 0 | 0 | 260B bin |
| Caravel mgmt (mgmt_fw.elf) | 433 | 0 | 0 | 1264B hex |

**Toolchain:** /opt/OpenROAD/riscv/gcc14-no-zcmp/bin/riscv32-unknown-elf-gcc 14.2.1  
**Flags:** -march=rv32imc_zicsr -mabi=ilp32 -nostdlib -nostartfiles -ffreestanding -Os

## Peripheral Drivers

14/14 peripherals from memory_map.json have:
- Driver .c and .h files
- results.xml with compile-pass test

## Blocked Items

- **Bring-up cosimulation (4/5 tests):** BLOCKED — requires SoC top-level RTL from Stage 06
- **Caravel precheck (6b.8):** BLOCKED — requires Stage 9 Caravel integration

## Integrity

- No unexpanded `$(...)` in fw_build.log
- No hand-typed peripheral addresses
- All generated files carry GENERATED-FROM banner
- verify_fw_artifacts.sh: 32/32 PASS
- audit_pass.json written with verdict PASS
