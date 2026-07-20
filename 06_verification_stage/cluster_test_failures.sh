#!/usr/bin/env bash
# cluster_test_failures.sh — Cluster analysis for IP-010 v4 verification failures.
# Reads all tb-*/results.xml, extracts failures, clusters by error signature.
# Produces failure_clusters.txt with signature table before prose.

set -euo pipefail

VS="~/hermes_workspace/projects/IP-010/v4/06_verification_stage"

OUTFILE="${1:-${VS}/failure_clusters.txt}"

{
    echo "=============================================="
    echo "FAILURE CLUSTER ANALYSIS"
    echo "Project: IP-010 v4"
    echo "Generated: $(date)"
    echo "=============================================="
    echo ""

    # ── Signature Table ──
    echo "--- FAILURE SIGNATURE TABLE ---"
    echo ""

    XMLS=$(find "${VS}/tb-*/" -name 'results.xml' 2>/dev/null | sort)
    if [ -z "$XMLS" ]; then
        echo "WARNING: No results.xml files found. Simulations may not have completed."
        echo ""
        echo "--- SUMMARY ---"
        echo "Total modules: 18"
        echo "Total failures: UNKNOWN (no results.xml)"
        echo ""
        echo "--- CLUSTERS ---"
        echo "NONE — no results to cluster."
        exit 0
    fi

    TOTAL_FAILURES=0
    FAILURE_MODULES=""
    declare -A SIGNATURES

    for xml in $XMLS; do
        mod=$(echo "$xml" | sed 's|.*/tb-\([^/]*\)/results.xml|\1|')
        FAILS=$(grep -c 'failure ' "$xml" 2>/dev/null || echo "0")
        ERRORS=$(grep -c 'error ' "$xml" 2>/dev/null || echo "0")
        TOTAL=$((FAILS + ERRORS))

        if [ "$TOTAL" -gt 0 ]; then
            TOTAL_FAILURES=$((TOTAL_FAILURES + TOTAL))
            FAILURE_MODULES="${FAILURE_MODULES} ${mod}(${TOTAL})"

            # Extract error messages for clustering
            grep -oP 'failure message="\K[^"]+' "$xml" 2>/dev/null | while read -r msg; do
                # Normalize: first 60 chars as signature
                sig=$(echo "$msg" | cut -c1-60)
                echo "SIG:${sig}|${mod}"
            done

            grep -oP 'error message="\K[^"]+' "$xml" 2>/dev/null | while read -r msg; do
                sig=$(echo "$msg" | cut -c1-60)
                echo "SIG:${sig}|${mod}"
            done
        fi
    done

    # Re-read signatures
    declare -A SIG_MAP
    for xml in $XMLS; do
        mod=$(echo "$xml" | sed 's|.*/tb-\([^/]*\)/results.xml|\1|')
        while IFS= read -r line; do
            sig="${line%%|*}"
            SIG_MAP["$sig"]="${SIG_MAP["$sig"]} ${mod}"
        done < <(grep -oP '(failure|error) message="\K[^"]+' "$xml" 2>/dev/null | while read -r msg; do
            sig=$(echo "$msg" | cut -c1-60)
            echo "${sig}|${mod}"
        done)
    done

    echo "Total modules with failures: $(echo "$FAILURE_MODULES" | wc -w)"
    echo "Total failure/error events: ${TOTAL_FAILURES}"
    echo ""

    if [ ${#SIG_MAP[@]} -gt 0 ]; then
        echo "Failure signatures:"
        for sig in "${!SIG_MAP[@]}"; do
            echo "  [${SIG_MAP[$sig]}] ${sig}"
        done
    else
        echo "No failure signatures detected."
    fi

    echo ""
    echo "--- CLUSTER ANALYSIS ---"
    echo ""

    FAIL_MOD_COUNT=$(echo "$FAILURE_MODULES" | wc -w)
    if [ "$FAIL_MOD_COUNT" -eq 0 ]; then
        echo "All modules PASS. No failures to cluster."
        echo ""
        echo "RTL BUG CLUSTERS: 0"
        echo "TB ISSUE CLUSTERS: 0"
    else
        # Check for shared signatures (textbook 0xDEAD scenario)
        echo "Failure modules:${FAILURE_MODULES}"
        echo ""

        # Identify shared failure patterns
        SHARED_COUNT=0
        for sig in "${!SIG_MAP[@]}"; do
            mods="${SIG_MAP[$sig]}"
            mod_count=$(echo "$mods" | wc -w)
            if [ "$mod_count" -gt 1 ]; then
                SHARED_COUNT=$((SHARED_COUNT + 1))
                echo "  ⛔ SHARED SIGNATURE (${mod_count} modules): ${sig}"
                echo "     Modules:${mods}"
            fi
        done

        if [ "$SHARED_COUNT" -gt 0 ]; then
            echo ""
            echo "  ⛔ BLOCKED: ${SHARED_COUNT} shared failure signature(s) detected."
            echo "  These failures may share a common root cause."
            echo "  Do NOT issue separate waivers — investigate the shared cause first."
        fi

        echo ""
        echo "UNIQUE FAILURE SIGNATURES: $(( ${#SIG_MAP[@]} - SHARED_COUNT ))"
        echo "SHARED FAILURE SIGNATURES: ${SHARED_COUNT}"
    fi

    echo ""
    echo "--- PROSE SUMMARY ---"
    echo ""

    if [ "$FAIL_MOD_COUNT" -eq 0 ]; then
        echo "Verification stage: All 18 modules passed. 0 RTL bugs detected."
        echo "No failure clusters to report."
    else
        echo "Verification stage: ${FAIL_MOD_COUNT} modules failed with ${TOTAL_FAILURES} error events."
        echo "See signature table above for details."
    fi

} > "$OUTFILE"

cat "$OUTFILE"
