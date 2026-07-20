/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* IP-010 v4 — bootrom/boot_main.c: Stage-0 boot loader
 *
 * Boot ROM budget: < 4KB (text + rodata + data + bss)
 */

#include "soc.h"

extern void app_main(void);

#define UART_DATA   0x00
#define UART_STATUS 0x04
#define UART_TX_READY 0x01

static void uart_putc(char c) {
    volatile uint32_t *status = (volatile uint32_t*)(uintptr_t)(uart_2_BASE + UART_STATUS);
    volatile uint32_t *data   = (volatile uint32_t*)(uintptr_t)(uart_2_BASE + UART_DATA);
    while (!(REG_READ(status) & UART_TX_READY)) {
        __asm__ volatile ("");
    }
    REG_WRITE(data, (uint32_t)(unsigned char)c);
}

static void uart_puts(const char *s) {
    while (*s) uart_putc(*s++);
}

/* SRAM integrity check using inline asm to avoid null-address warnings */
static int sram_check(void) {
    uint32_t pattern = 0xAA55AA55;
    uint32_t r1, r2;
    uintptr_t addr2 = sram_8kb_BASE + 8;
    uintptr_t addr3 = sram_8kb_BASE + 12;

    __asm__ volatile ("sw %0, 0(%1)" : : "r"(pattern), "r"(addr2) : "memory");
    __asm__ volatile ("sw %0, 0(%1)" : : "r"(~pattern), "r"(addr3) : "memory");
    __asm__ volatile ("lw %0, 0(%1)" : "=r"(r1) : "r"(addr2) : "memory");
    __asm__ volatile ("lw %0, 0(%1)" : "=r"(r2) : "r"(addr3) : "memory");

    if (r1 != pattern) return -1;
    if (r2 != ~pattern) return -1;
    return 0;
}

void boot_main(void) {
    uart_puts("\r\nIP-010 v4 BOOT\r\n");

    if (sram_check() != 0) {
        uart_puts("SRAM FAIL\r\n");
        while (1) { __asm__ volatile ("wfi"); }
    }

    uart_puts("SRAM OK\r\n");
    uart_puts("JUMP APP\r\n");

    app_main();

    while (1) { __asm__ volatile ("wfi"); }
}

__attribute__((weak)) void app_main(void) {
    uart_puts("NO APP\r\n");
    while (1) { __asm__ volatile ("wfi"); }
}
