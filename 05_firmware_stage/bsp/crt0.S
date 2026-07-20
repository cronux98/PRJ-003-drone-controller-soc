/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* IP-010 v4 — crt0.S: Boot startup for Ibex RV32IMC
 *
 * Boot vector: 0x00000000 (SRAM base)
 * SRAM size: 8KB, stack at top of SRAM
 * Trap handler: simple loop (unexpected trap)
 *
 * Per §3.10: all addresses trace to memory_map.json via generated headers.
 */
.section .text._start, "ax", @progbits
.globl _start
.globl _stack_top

_start:
    /* --- Initialize stack pointer ---
     * _stack_top defined in link.ld = ORIGIN(sram_8kb) + LENGTH(sram_8kb) = 0x2000
     */
    la sp, _stack_top

    /* --- Clear BSS ---
     * _bss_start / _bss_end defined in link.ld
     */
    la t0, _bss_start
    la t1, _bss_end
    bgeu t0, t1, 1f
bss_clear:
    sw zero, 0(t0)
    addi t0, t0, 4
    bltu t0, t1, bss_clear
1:

    /* --- Jump to main --- */
    call main

    /* --- main() returned — trap --- */
hang:
    wfi
    j hang

/* --- Trap vector / handler ---
 * For Ibex: mtvec.BASE = 0x0, mode = direct
 */
.section .text.trap, "ax", @progbits
.globl trap_handler
.align 4
trap_handler:
    /* Simple handler: infinite loop on any trap */
    csrr t0, mcause
    csrr t1, mepc
trap_loop:
    wfi
    j trap_loop
