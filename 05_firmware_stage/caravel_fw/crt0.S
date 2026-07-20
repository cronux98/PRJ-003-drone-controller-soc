/* Caravel mgmt core crt0 — minimal startup */
.section .text, "ax", @progbits
.globl _start
_start:
    la sp, _stack_top
    la t0, _bss_start
    la t1, _bss_end
    bgeu t0, t1, 1f
bss_clear:
    sw zero, 0(t0)
    addi t0, t0, 4
    bltu t0, t1, bss_clear
1:
    call main
hang:
    wfi
    j hang
