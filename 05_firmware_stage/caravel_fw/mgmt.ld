/* Caravel mgmt core linker script — IP-010 v4 */
MEMORY
{
    mgmt_ram (rwx) : ORIGIN = 0x00000000, LENGTH = 32K
}
ENTRY(main)
SECTIONS {
    . = 0x00000000;
    .text : { *(.text*) } > mgmt_ram
    .rodata : { *(.rodata*) } > mgmt_ram
    .data : { *(.data*) } > mgmt_ram
    .bss : { _bss_start = .; *(.bss*) *(COMMON); _bss_end = .; } > mgmt_ram
    _stack_top = ORIGIN(mgmt_ram) + LENGTH(mgmt_ram);
}
