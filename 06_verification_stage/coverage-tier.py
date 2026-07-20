#!/usr/bin/env python3
"""
coverage-tier.py — Assign coverage tiers based on estimated toggle bin counts.
IP-010 v4: For modules without coverage data, use synthesis cell count as proxy.
"""
import json, os, sys, re
from pathlib import Path

VS = "~/hermes_workspace/projects/IP-010/v4/06_verification_stage"
FS = "~/hermes_workspace/projects/IP-010/v4/04_frontend_stage"

# Cell counts from synthesis (proxy for toggle bins when coverage data unavailable)
# Source: 04_frontend_stage/00_frontend_index.md
CELL_COUNTS = {
    "ibex_core": 3534, "wishbone_interconnect": 699, "sram_8kb": 0,
    "uart_0": 252, "uart_1": 252, "uart_2": 252,
    "spi_0": 1116, "i2c_0": 2141, "dshot_pwm": 2254,
    "gpio": 593, "spi_flash_ctrl": 377, "irq_ctrl": 396,
    "timer": 1766, "watchdog": 364, "caravel_wrapper": 199,
    "clk_rst_mgr": 44, "custom_timer": 1875,
    "drone_soc": 19305,
}

# Tier assignment based on estimated toggle bins (cell count as proxy)
def assign_tier(name, cells):
    if cells <= 500:
        return "A"
    elif cells <= 2000:
        return "B"
    else:
        return "C"

def count_tests_in_results_xml(xml_path):
    """Parse results.xml and count tests."""
    try:
        with open(xml_path) as f:
            content = f.read()
        # Count tests=
        tests_match = re.search(r'tests="(\d+)"', content)
        if tests_match:
            return int(tests_match.group(1))
        # Count number of testcase elements as fallback
        return len(re.findall(r'<testcase\s', content))
    except Exception:
        return 0

def main():
    assignments = {}
    findings = []

    for name, cells in sorted(CELL_COUNTS.items()):
        tier = assign_tier(name, cells)
        xml_path = os.path.join(VS, f"tb-{name}/results.xml")
        tests_found = count_tests_in_results_xml(xml_path)

        min_tests = {"A": 8, "B": 15, "C": 40}[tier]
        met = tests_found >= min_tests

        entry = {
            "module": name,
            "tier": tier,
            "estimated_toggle_bins": cells,
            "tests_found": tests_found,
            "tests_required": min_tests,
            "test_count_met": met,
            "coverage_target_toggle": {"A": 90, "B": 70, "C": 40}[tier],
            "coverage_target_line": 90,
        }

        if not met:
            entry["warning"] = f"Insufficient tests: {tests_found}/{min_tests}"
            findings.append(f"{name}: {tests_found}/{min_tests} tests (Tier {tier})")

        # Special: drone_soc has waiver for coverage (SoC top)
        if name == "drone_soc":
            entry["waiver"] = "SoC top-level — coverage threshold waived per CLAUDE.md §4.6e"

        assignments[name] = entry

    result = {
        "generated_by": "coverage-tier.py",
        "project": "IP-010",
        "version": "v4",
        "method": "Synthesis cell count used as toggle-bin estimate proxy",
        "modules": len(assignments),
        "tier_summary": {
            "A": sum(1 for v in assignments.values() if v["tier"] == "A"),
            "B": sum(1 for v in assignments.values() if v["tier"] == "B"),
            "C": sum(1 for v in assignments.values() if v["tier"] == "C"),
        },
        "assignments": assignments,
        "findings": findings,
    }

    out_path = os.path.join(VS, "tier_assignment.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Tier assignment written to {out_path}")
    print(f"  A: {result['tier_summary']['A']} modules (≥8 tests, ≥90% toggle)")
    print(f"  B: {result['tier_summary']['B']} modules (≥15 tests, ≥70% toggle)")
    print(f"  C: {result['tier_summary']['C']} modules (≥40 tests, ≥40% toggle)")
    if findings:
        print(f"\nFindings ({len(findings)}):")
        for f in findings:
            print(f"  - {f}")

if __name__ == "__main__":
    main()
