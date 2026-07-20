#!/bin/bash
# verify_frontend_artifacts.sh — IP-010 v4 frontend artifact verification
# Checks that all required artifacts exist for each module
# Exit 0 = all present, non-zero = missing artifacts

set -e
V4="$(dirname "$0")"
FAILS=0
CHECKS=0

modules=(
    ibex_core wishbone_interconnect sram_8kb
    uart_0 uart_1 uart_2 spi_0 i2c_0
    dshot_pwm gpio spi_flash_ctrl irq_ctrl
    timer watchdog caravel_wrapper clk_rst_mgr
    custom_timer drone_soc
)

echo "=== IP-010 v4 Frontend Artifact Verification ==="
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)  host=$(hostname)"
echo ""

for mod in "${modules[@]}"; do
    rtl_file="$V4/rtl-$mod/rtl/${mod}.v"
    # Some modules have different main RTL file names
    case "$mod" in
        gpio)      rtl_file="$V4/rtl-$mod/rtl/gpio.v" ;;
        spi_0)     rtl_file="$V4/rtl-$mod/rtl/spi_0.v" ;;
        timer)     rtl_file="$V4/rtl-$mod/rtl/timer.v" ;;
        uart_0|uart_1|uart_2) rtl_file="$V4/rtl-$mod/rtl/EF_UART_WB.v" ;;
        watchdog)  rtl_file="$V4/rtl-$mod/rtl/watchdog.v" ;;
        i2c_0)     rtl_file="$V4/rtl-$mod/rtl/i2c_0.v" ;;
        sram_8kb)  rtl_file="$V4/rtl-$mod/rtl/sram_8kb_blackbox.v" ;;
    esac
    
    lint_log="$V4/rtl-$mod/logs/lint/${mod}_iverilog.log"
    formal_sby="$V4/rtl-$mod/formal/${mod}.sby"
    formal_xml=$(find "$V4/rtl-$mod/formal/" -name "${mod}*_bmc.xml" 2>/dev/null | head -1)
    synth_netlist="$V4/rtl-$mod/synth/${mod}.v"
    synth_log="$V4/rtl-$mod/logs/synth/${mod}_synth.log"
    equiv_log="$V4/rtl-$mod/equiv_check/equiv.log"
    
    # 1. RTL
    CHECKS=$((CHECKS + 1))
    if [ -f "$rtl_file" ]; then
        echo "  [PASS] $mod: RTL exists"
    else
        echo "  [FAIL] $mod: RTL missing ($rtl_file)"
        FAILS=$((FAILS + 1))
    fi
    
    # 2. Lint
    CHECKS=$((CHECKS + 1))
    if [ -f "$lint_log" ]; then
        echo "  [PASS] $mod: lint log exists"
    else
        echo "  [FAIL] $mod: lint log missing"
        FAILS=$((FAILS + 1))
    fi
    
    # 3. Formal (.sby exists → but XML must have tests>=1)
    CHECKS=$((CHECKS + 1))
    if [ -f "$formal_sby" ]; then
        if [ -n "$formal_xml" ] && [ -f "$formal_xml" ]; then
            tests=$(grep -oP 'tests="\K[0-9]+' "$formal_xml" 2>/dev/null || echo "0")
            if [ "$tests" -gt 0 ] 2>/dev/null; then
                echo "  [PASS] $mod: formal BMC (tests=$tests)"
            else
                echo "  [FAIL] $mod: formal BMC tests=0 (no assertions executed)"
                FAILS=$((FAILS + 1))
            fi
        else
            echo "  [FAIL] $mod: formal .sby exists but no BMC XML"
            FAILS=$((FAILS + 1))
        fi
    else
        echo "  [FAIL] $mod: formal .sby missing"
        FAILS=$((FAILS + 1))
    fi
    
    # 4. Synthesis (netlist exists AND contains module declaration)
    CHECKS=$((CHECKS + 1))
    if [ -f "$synth_netlist" ]; then
        if grep -q "module $mod" "$synth_netlist" 2>/dev/null || [ "$mod" = "sram_8kb" ]; then
            echo "  [PASS] $mod: synth netlist exists"
        else
            echo "  [FAIL] $mod: synth netlist exists but doesn't declare module $mod (G.15 identity check)"
            FAILS=$((FAILS + 1))
        fi
    else
        echo "  [FAIL] $mod: synth netlist missing"
        FAILS=$((FAILS + 1))
    fi
    
    # 5. Equivalence
    CHECKS=$((CHECKS + 1))
    if [ -f "$equiv_log" ]; then
        if grep -q 'Equivalence successfully proven' "$equiv_log" 2>/dev/null; then
            echo "  [PASS] $mod: equiv check PASS"
        else
            echo "  [FAIL] $mod: equiv check FAIL (see $equiv_log)"
            FAILS=$((FAILS + 1))
        fi
    else
        echo "  [FAIL] $mod: equiv log missing"
        FAILS=$((FAILS + 1))
    fi
done

echo ""
echo "=== Summary ==="
echo "Total checks: $CHECKS"
echo "Failures: $FAILS"
if [ $FAILS -eq 0 ]; then
    echo "VERDICT: PASS"
    exit 0
else
    echo "VERDICT: FAIL"
    exit 1
fi
