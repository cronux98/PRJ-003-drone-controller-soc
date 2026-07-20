/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* IP-010 v4 — Bring-up test firmware
 *
 * Tests boot sequence, SRAM integrity, UART loopback, and
 * per-peripheral register R/W on the assembled SoC top-level.
 *
 * Requires: SoC top-level from 06_integration stage.
 * Status: BLOCKED — 06_verification_stage exists but is empty (no SoC top-level).
 * When SoC top-level is available, this firmware + cocotb bench exercises it.
 */
#include "soc.h"
#include "uart_0_driver.h"

#define TEST_PASS 0
#define TEST_FAIL 1

/* Prototypes */
void run_sram_test(void);
void run_uart_test(void);
void run_register_rw_test(void);

void main(void) {
    /* --- Boot banner on UART 2 --- */
    volatile uint32_t *uart2_data = (volatile uint32_t*)(uintptr_t)(uart_2_BASE + 0x00);
    volatile uint32_t *uart2_status = (volatile uint32_t*)(uintptr_t)(uart_2_BASE + 0x04);

    /* Signal boot complete to testbench */
    *(volatile uint32_t*)(uintptr_t)(sram_8kb_BASE + 0x10) = 0xB0070BAD;

    /* --- SRAM Test --- */
    run_sram_test();

    /* --- UART Loopback Test --- */
    run_uart_test();

    /* --- Register R/W Test --- */
    run_register_rw_test();

    /* --- DONE signal --- */
    *(volatile uint32_t*)(uintptr_t)(sram_8kb_BASE + 0x10) = 0xD0NE0000;

    while (1) { __asm__ volatile ("wfi"); }
}

void run_sram_test(void) {
    volatile uint32_t *sram = (volatile uint32_t*)(uintptr_t)(sram_8kb_BASE);
    uint32_t *magic = (uint32_t*)(uintptr_t)(sram_8kb_BASE + 0x10);

    /* Walking 1s test on SRAM[16..31] (above boot area) */
    for (int i = 16; i < 32; i++) {
        for (int bit = 0; bit < 32; bit++) {
            uint32_t pattern = 1u << bit;
            sram[i] = pattern;
            if (sram[i] != pattern) {
                *magic = 0xDEAD0000 | i;
                return;
            }
        }
    }
    *magic = 0x5RAM0K00;
}

void run_uart_test(void) {
    volatile uint32_t *magic = (volatile uint32_t*)(uintptr_t)(sram_8kb_BASE + 0x14);
    /* Initialize UART 2 at 115200 baud. At 16.67 MHz, divisor = 16670000 / (16 * 115200) = 9 */
    uart_2_init(9);

    /* Write a test byte */
    uart_2_putc('T');

    /* Read status register to verify peripheral responds */
    volatile uint32_t *status_reg = (volatile uint32_t*)(uintptr_t)(uart_2_BASE + 0x04);
    uint32_t status_val = *status_reg;

    /* TX ready bit should be set after the byte is transmitted */
    if (status_val & 0x01) {
        *magic = 0xUART0K00;
    } else {
        *magic = 0xDEAD0002;
    }
}

void run_register_rw_test(void) {
    volatile uint32_t *magic = (volatile uint32_t*)(uintptr_t)(sram_8kb_BASE + 0x18);
    int failures = 0;

    /* Test each peripheral's first register for R/W */
    struct { const char *name; uintptr_t base; } periphs[] = {
        {"uart_0", uart_0_BASE},
        {"uart_1", uart_1_BASE},
        {"uart_2", uart_2_BASE},
        {"gpio",   gpio_BASE},
        {"timer",  timer_BASE},
        {"irq_ctrl", irq_ctrl_BASE},
        {NULL, 0}
    };

    for (int i = 0; periphs[i].name; i++) {
        volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(periphs[i].base);
        uint32_t orig = regs[0];
        regs[0] = 0x5A5A0000 | i;
        if (regs[0] != (0x5A5A0000 | i)) {
            failures++;
            /* Mark which peripheral failed */
            *magic = 0xDEAD0000 | (i + 10);
        }
        regs[0] = orig;
    }

    if (failures == 0) {
        *magic = 0xREG5OK00;
    }
}
