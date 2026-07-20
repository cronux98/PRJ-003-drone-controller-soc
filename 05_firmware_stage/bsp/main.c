/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* IP-010 v4 — main.c: BSP smoke test main
 * Minimal main for verifying the BSP builds. Real firmware replaces this.
 */
#include "soc.h"

void main(void) {
    /* Simple memory test: write pattern to SRAM, read it back
     * Use inline asm to avoid compiler warnings about address 0x0
     */
    uint32_t val, readback;
    uintptr_t test_addr = sram_8kb_BASE + 4;

    val = 0xDEADBEEF;
    __asm__ volatile ("sw %0, 0(%1)" : : "r"(val), "r"(test_addr) : "memory");
    __asm__ volatile ("lw %0, 0(%1)" : "=r"(readback) : "r"(test_addr) : "memory");

    if (readback == val) {
        /* PASS — SRAM at base+4 works.
         * Write '+' (0x2B) to UART 2 DATA register to signal pass.
         */
        uintptr_t uart2_data_addr = uart_2_BASE + 0x00;
        uint32_t tx_byte = 0x2B;
        __asm__ volatile ("sw %0, 0(%1)" : : "r"(tx_byte), "r"(uart2_data_addr) : "memory");
    }

    /* Loop forever */
    while (1) {
        __asm__ volatile ("wfi");
    }
}
