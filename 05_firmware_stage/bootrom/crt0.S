/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* IP-010 v4 — bootrom/crt0.S: Stage-0 boot ROM startup
 * Placed at 0x00000000 (SRAM base, loaded by Caravel).
 * Budget: < 4KB (must fit in one SRAM block of the SRAM 8KB region).
 */
.section .text._start, "ax", @progbits
.globl _start
.globl _stack_top

_start:
    /* Initialize stack pointer to top of SRAM (0x2000) */
    la sp, _stack_top

    /* Clear BSS */
    la t0, _bss_start
    la t1, _bss_end
    bgeu t0, t1, 1f
bss_clear:
    sw zero, 0(t0)
    addi t0, t0, 4
    bltu t0, t1, bss_clear
1:

    /* Jump to boot_main */
    call boot_main

hang:
    wfi
    j hang

/* Trap handler — direct mode */
.section .text.trap, "ax", @progbits
.globl trap_handler
.align 4
trap_handler:
    csrr t0, mcause
    csrr t1, mepc
trap_loop:
    wfi
    j trap_loop
