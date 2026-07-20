/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* uart_0 — GPS UART driver, 115200 baud, 8N1 */
#include "uart_0_driver.h"

void uart_0_init(unsigned int baud_divisor) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(uart_0_BASE);
    /* Set baud rate divisor */
    regs[UART_DIVISOR_OFFSET / 4] = baud_divisor;
    /* Enable TX */
    regs[UART_CTRL_OFFSET / 4] = 0x01;
}

int uart_0_putc(char c) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(uart_0_BASE);
    /* Wait for TX ready */
    while (!(regs[UART_STATUS_OFFSET / 4] & UART_TX_READY)) {
        __asm__ volatile ("");
    }
    regs[UART_DATA_OFFSET / 4] = (unsigned char)c;
    return 0;
}

int uart_0_getc(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(uart_0_BASE);
    while (!(regs[UART_STATUS_OFFSET / 4] & UART_RX_VALID)) {
        __asm__ volatile ("");
    }
    return (int)(regs[UART_DATA_OFFSET / 4] & 0xFF);
}

int uart_0_puts(const char *s) {
    while (*s) {
        if (uart_0_putc(*s++) < 0) return -1;
    }
    return 0;
}

int uart_0_selftest(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(uart_0_BASE);
    uint32_t orig_div = regs[UART_DIVISOR_OFFSET / 4];
    /* Write/read divisor register to verify peripheral responds */
    regs[UART_DIVISOR_OFFSET / 4] = 0x55;
    if (regs[UART_DIVISOR_OFFSET / 4] != 0x55) return -1;
    regs[UART_DIVISOR_OFFSET / 4] = 0xAA;
    if (regs[UART_DIVISOR_OFFSET / 4] != 0xAA) return -2;
    /* Restore */
    regs[UART_DIVISOR_OFFSET / 4] = orig_div;
    return 0;
}
