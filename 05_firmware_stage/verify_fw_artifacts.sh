#!/bin/bash
# verify_fw_artifacts.sh — Stage 05 exit gate
# Enforces §3.15: every firmware artifact must have provenance, build log, and budget check.
# Exit 0 = PASS, non-zero = FAIL.

set -euo pipefail

STAGE_DIR="$(cd "$(dirname "$0")" && pwd)"
FAILURES=0
PASSES=0

red()   { echo -e "\033[31mFAIL:\033[0m $*"; }
green() { echo -e "\033[32mPASS:\033[0m $*"; }
warn()  { echo -e "\033[33mWARN:\033[0m $*"; }

check() {
    local desc="$1"; shift
    if "$@"; then
        green "$desc"
        ((PASSES++)) || true
        return 0
    else
        red "$desc"
        ((FAILURES++)) || true
        return 1
    fi
}

echo "=== verify_fw_artifacts.sh — Stage 05 Exit Gate ==="
echo "Stage dir: $STAGE_DIR"
echo ""

# ── 1. fw_build.log exists with compiler version ──
echo "── Check 1: fw_build.log with compiler --version"
check "fw_build.log exists" \
    test -f "$STAGE_DIR/fw_build.log"
check "fw_build.log contains compiler --version output" \
    grep -q 'riscv32-unknown-elf-gcc.*14\.2\.1' "$STAGE_DIR/fw_build.log" 2>/dev/null
check "fw_build.log is non-empty (>500 bytes)" \
    test "$(stat --format=%s "$STAGE_DIR/fw_build.log" 2>/dev/null || echo 0)" -gt 500
# Anti-fabrication: reject unexpanded $(...) strings
if grep -q '\$(date\b\|\$(cat\b\|\$(echo\b\|\$(' "$STAGE_DIR/fw_build.log" 2>/dev/null; then
    red "fw_build.log contains unexpanded command substitutions — build was not actually run"
    ((FAILURES++)) || true
fi

# ── 2. bsp_manifest.json with per-file provenance ──
echo ""
echo "── Check 2: bsp_manifest.json provenance"
check "bsp_manifest.json exists" \
    test -f "$STAGE_DIR/bsp/bsp_manifest.json"

# Check that bsp_manifest.json references actual files
BSP_MANIFEST="$STAGE_DIR/bsp/bsp_manifest.json"
if [ -f "$BSP_MANIFEST" ]; then
    check "bsp_manifest.json has .files key" \
        python3 -c "import json; d=json.load(open('$BSP_MANIFEST')); assert 'files' in d" 2>/dev/null

    # Verify each file in manifest exists on disk
    while IFS= read -r fpath; do
        abs_path="$STAGE_DIR/$fpath"
        if [ -f "$abs_path" ] || [ -d "$abs_path" ]; then
            green "  manifest file exists: $fpath"
        else
            red "  manifest file MISSING: $fpath"
            ((FAILURES++)) || true
        fi
    done < <(python3 -c "
import json
d=json.load(open('$BSP_MANIFEST'))
for k in d.get('files',{}): print(k)
" 2>/dev/null)
fi

# ── 3. bootrom_report.json — budget not exceeded ──
echo ""
echo "── Check 3: bootrom_report.json budget gate"
check "bootrom_report.json exists" \
    test -f "$STAGE_DIR/bootrom/bootrom_report.json"
if [ -f "$STAGE_DIR/bootrom/bootrom_report.json" ]; then
    VERDICT=$(python3 -c "import json; print(json.load(open('$STAGE_DIR/bootrom/bootrom_report.json')).get('verdict','UNKNOWN'))" 2>/dev/null || echo "ERROR")
    if [ "$VERDICT" = "PASS" ]; then
        green "bootrom budget verdict: PASS"
        ((PASSES++)) || true
    else
        red "bootrom budget verdict: $VERDICT (expected PASS)"
        ((FAILURES++)) || true
    fi
    BOOT_SIZE=$(python3 -c "import json; print(json.load(open('$STAGE_DIR/bootrom/bootrom_report.json')).get('bootrom_size_bytes',0))" 2>/dev/null || echo "0")
    BUDGET=$(python3 -c "import json; print(json.load(open('$STAGE_DIR/bootrom/bootrom_report.json')).get('max_budget_bytes',4096))" 2>/dev/null || echo "4096")
    echo "  bootrom: $BOOT_SIZE / $BUDGET bytes"
fi
check "bootrom.hex exists" \
    test -f "$STAGE_DIR/bootrom/bootrom.hex"
check "bootrom.hex is non-empty" \
    test "$(stat --format=%s "$STAGE_DIR/bootrom/bootrom.hex" 2>/dev/null || echo 0)" -gt 10

# ── 4. Every driver has results.xml with >= 1 testcase ──
echo ""
echo "── Check 4: Per-peripheral driver results.xml"
MMAP="$STAGE_DIR/../03_architecture_stage/memory_map.json"
if [ -f "$MMAP" ]; then
    PERIPH_NAMES=$(python3 -c "
import json
d=json.load(open('$MMAP'))
periphs = d.get('peripherals', d.get('regions', []))
for p in periphs:
    t = p.get('type','')
    if t == 'Peripheral' or ('base_address' in p and int(p.get('base_address','0x80000000',16) or 0, 16 if isinstance(p.get('base_address',''),str) else 0) >= 0x80000000):
        print(p['name'])
" 2>/dev/null)
    for pname in $PERIPH_NAMES; do
        results_xml="$STAGE_DIR/fw/drivers/$pname/results.xml"
        if [ -f "$results_xml" ]; then
            TESTCASE_COUNT=$(grep -c '<testcase' "$results_xml" 2>/dev/null || echo "0")
            FAIL_COUNT=$(grep -o 'failures="[0-9]*"' "$results_xml" 2>/dev/null | head -1 | grep -o '[0-9]*' || echo "0")
            if [ "$TESTCASE_COUNT" -ge 1 ] && [ "$FAIL_COUNT" = "0" ]; then
                green "  $pname: $TESTCASE_COUNT testcase(s), failures=$FAIL_COUNT"
                ((PASSES++)) || true
            else
                red "  $pname: testcases=$TESTCASE_COUNT failures=$FAIL_COUNT — FAIL"
                ((FAILURES++)) || true
            fi
        else
            red "  $pname: results.xml MISSING"
            ((FAILURES++)) || true
        fi
    done
else
    warn "memory_map.json not found at $MMAP — skipping driver check"
fi

# ── 5. tb-fw-bringup/results.xml with failures=0 ──
echo ""
echo "── Check 5: Bring-up cosimulation results"
check "tb-fw-bringup/results.xml exists" \
    test -f "$STAGE_DIR/tb-fw-bringup/results.xml"
if [ -f "$STAGE_DIR/tb-fw-bringup/results.xml" ]; then
    FAIL_COUNT=$(grep -o 'failures="[0-9]*"' "$STAGE_DIR/tb-fw-bringup/results.xml" 2>/dev/null | head -1 | grep -o '[0-9]*' || echo "1")
    if [ "$FAIL_COUNT" = "0" ]; then
        green "  bring-up: failures=0"
        ((PASSES++)) || true
    else
        red "  bring-up: failures=$FAIL_COUNT (expected 0)"
        ((FAILURES++)) || true
    fi
    # Check if BLOCKED (honest skip is acceptable)
    if grep -qi 'BLOCKED' "$STAGE_DIR/tb-fw-bringup/results.xml" 2>/dev/null; then
        warn "  bring-up: BLOCKED (no SoC top-level) — tests skipped but results.xml is honest"
    fi
fi

# ── 6. Caravel management firmware ──
echo ""
echo "── Check 6: Caravel management firmware"
check "caravel_fw/mgmt_fw.hex exists" \
    test -f "$STAGE_DIR/caravel_fw/mgmt_fw.hex"
check "caravel_fw/mgmt_fw.hex is non-empty" \
    test "$(stat --format=%s "$STAGE_DIR/caravel_fw/mgmt_fw.hex" 2>/dev/null || echo 0)" -gt 10
check "caravel_fw/mgmt_fw.c exists" \
    test -f "$STAGE_DIR/caravel_fw/mgmt_fw.c"

# ── 7. BSP artifacts present ──
echo ""
echo "── Check 7: BSP core artifacts"
check "bsp/include/soc.h exists" \
    test -f "$STAGE_DIR/bsp/include/soc.h"
check "bsp/crt0.S exists" \
    test -f "$STAGE_DIR/bsp/crt0.S"
check "bsp/link.ld exists" \
    test -f "$STAGE_DIR/bsp/link.ld"
check "bsp/Makefile exists" \
    test -f "$STAGE_DIR/bsp/Makefile"

# ── SUMMARY ──
echo ""
echo "============================================"
if [ "$FAILURES" -eq 0 ]; then
    green "VERDICT: PASS — $PASSES checks passed, $FAILURES failed"
    echo "PASS" > "$STAGE_DIR/.fw_artifacts_verified"
    exit 0
else
    red "VERDICT: FAIL — $PASSES checks passed, $FAILURES failed"
    rm -f "$STAGE_DIR/.fw_artifacts_verified"
    exit 1
fi
