#!/usr/bin/env bash
# verify_test_artifacts.sh — IP-010 v4 Verification Stage exit gate
# Checks: results.xml per module, test counts per tier, no fabrication, full scope
set -euo pipefail

VS="~/hermes_workspace/projects/IP-010/v4/06_verification_stage"

GATE_PASS=0
GATE_FAIL=0
gate_pass() { echo "  ✅ $*"; GATE_PASS=$((GATE_PASS+1)); }
gate_fail() { echo "  ❌ $*"; GATE_FAIL=$((GATE_FAIL+1)); }

echo "=== verify_test_artifacts.sh — IP-010 v4 Stage 06 ==="
echo ""

# ── 1. results.xml for every module ──
MODULES=(
    clk_rst_mgr irq_ctrl caravel_wrapper sram_8kb wishbone_interconnect
    spi_flash_ctrl dshot_pwm custom_timer
    timer watchdog
    uart_0 uart_1 uart_2 gpio
    spi_0 i2c_0
    ibex_core drone_soc
)

echo "--- Check 1: results.xml per module (GATE-SCOPE: ${#MODULES[@]}) ---"
RESULTS_FOUND=0
for mod in "${MODULES[@]}"; do
    if [ -f "${VS}/tb-${mod}/results.xml" ] && [ -s "${VS}/tb-${mod}/results.xml" ]; then
        gate_pass "tb-${mod}/results.xml ($(stat -c%s ${VS}/tb-${mod}/results.xml)B)"
        RESULTS_FOUND=$((RESULTS_FOUND+1))
    else
        gate_fail "tb-${mod}/results.xml MISSING or EMPTY"
    fi
done
echo "  Found: ${RESULTS_FOUND}/${#MODULES[@]}"
echo ""

# ── 2. Test counts per tier (from results.xml) ──
echo "--- Check 2: Minimum test counts per tier ---"
TIER_A=("clk_rst_mgr" "irq_ctrl" "caravel_wrapper" "sram_8kb" "wishbone_interconnect")
TIER_B=("spi_flash_ctrl" "dshot_pwm" "custom_timer" "timer" "watchdog" "uart_0" "uart_1" "uart_2" "gpio")
TIER_C=("spi_0" "i2c_0" "ibex_core" "drone_soc")

check_tier() {
    local tier_name="$1"; shift
    local min_tests="$1"; shift
    local modules=("$@")
    for mod in "${modules[@]}"; do
        local xml="${VS}/tb-${mod}/results.xml"
        if [ -f "$xml" ]; then
            local count=$(grep -c '<testcase ' "$xml" 2>/dev/null || echo "0")
            if [ "$count" -ge "$min_tests" ]; then
                gate_pass "${mod} (Tier ${tier_name}): ${count}/${min_tests} tests"
            else
                gate_fail "${mod} (Tier ${tier_name}): ${count}/${min_tests} tests — INSUFFICIENT"
            fi
        fi
    done
}

check_tier "A" 8 "${TIER_A[@]}"
check_tier "B" 15 "${TIER_B[@]}"
check_tier "C" 40 "${TIER_C[@]}"
echo ""

# ── 3. No empty glob fallthrough ──
echo "--- Check 3: Anti-fabrication (empty glob = FAIL) ---"
XML_COUNT=$(find "${VS}" -maxdepth 2 -name 'results.xml' 2>/dev/null | wc -l)
if [ "$XML_COUNT" -ge "${#MODULES[@]}" ]; then
    gate_pass "results.xml count=${XML_COUNT} >= expected=${#MODULES[@]}"
else
    gate_fail "results.xml count=${XML_COUNT} < expected=${#MODULES[@]}"
fi
echo ""

# ── 4. Verification summary exists ──
echo "--- Check 4: verification_summary.json ---"
if [ -f "${VS}/verification_summary.json" ] && [ -s "${VS}/verification_summary.json" ]; then
    gate_pass "verification_summary.json exists ($(stat -c%s ${VS}/verification_summary.json)B)"
else
    gate_fail "verification_summary.json MISSING or EMPTY"
fi
echo ""

# ── 5. failure_clusters.txt ──
echo "--- Check 5: failure_clusters.txt ---"
if [ -f "${VS}/failure_clusters.txt" ]; then
    gate_pass "failure_clusters.txt exists"
else
    gate_fail "failure_clusters.txt MISSING"
fi
echo ""

# ── VERDICT ──
echo "==========================================="
echo "GATE CHECKS: $((GATE_PASS+GATE_FAIL)) total, ${GATE_PASS} PASS, ${GATE_FAIL} FAIL"
if [ "$GATE_FAIL" -eq 0 ] && [ "$RESULTS_FOUND" -eq "${#MODULES[@]}" ]; then
    echo "VERDICT: PASS — all gates clear"
    exit 0
else
    echo "VERDICT: FAIL — ${GATE_FAIL} gate(s) failed"
    exit 1
fi
