/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */

/* IP-010 v4 — rv32imc ilp32 */

MEMORY
{
    sram_8kb (rwx)  : ORIGIN = 0x00000000, LENGTH = 8192
    uart_0 (rwx)  : ORIGIN = 0x80000000, LENGTH = 4096
    uart_1 (rwx)  : ORIGIN = 0x80001000, LENGTH = 4096
    uart_2 (rwx)  : ORIGIN = 0x80002000, LENGTH = 4096
    spi_0 (rwx)  : ORIGIN = 0x80003000, LENGTH = 4096
    i2c_0 (rwx)  : ORIGIN = 0x80004000, LENGTH = 4096
    dshot_pwm (rwx)  : ORIGIN = 0x80005000, LENGTH = 4096
    gpio (rwx)  : ORIGIN = 0x80006000, LENGTH = 4096
    spi_flash_ctrl (rwx)  : ORIGIN = 0x80007000, LENGTH = 4096
    irq_ctrl (rwx)  : ORIGIN = 0x80008000, LENGTH = 4096
    timer (rwx)  : ORIGIN = 0x80009000, LENGTH = 4096
    watchdog (rwx)  : ORIGIN = 0x8000A000, LENGTH = 4096
    caravel_wrapper (rwx)  : ORIGIN = 0x8000B000, LENGTH = 4096
    clk_rst_mgr (rwx)  : ORIGIN = 0x8000C000, LENGTH = 4096
    custom_timer (rwx)  : ORIGIN = 0x8000D000, LENGTH = 4096
}

ENTRY(_start)

SECTIONS
{
    . = 0x00000000;

    .text : {
        *(.text._start)
        *(.text*)
    } > sram_8kb

    .rodata : {
        *(.rodata*)
    } > sram_8kb

    .data : {
        *(.data*)
    } > sram_8kb

    .bss : {
        _bss_start = .;
        *(.bss*)
        *(COMMON)
        _bss_end = .;
    } > sram_8kb

    _stack_top = ORIGIN(sram_8kb) + LENGTH(sram_8kb);
}
