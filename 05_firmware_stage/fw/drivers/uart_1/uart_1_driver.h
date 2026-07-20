/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* uart_1 — GPS UART driver, 115200 baud, 8N1 */
#ifndef UART_1_DRIVER_H
#define UART_1_DRIVER_H
#include "soc.h"
#include "uart_1.h"

/* UART register offsets (standard 16550-compatible subset) */
#define UART_DATA_OFFSET    0x00
#define UART_STATUS_OFFSET  0x04
#define UART_DIVISOR_OFFSET 0x08
#define UART_CTRL_OFFSET    0x0C

/* Status bits */
#define UART_TX_READY  (1 << 0)
#define UART_RX_VALID  (1 << 1)
#define UART_TX_FULL   (1 << 2)
#define UART_RX_FULL   (1 << 3)

void uart_1_init(unsigned int baud_divisor);
int  uart_1_putc(char c);
int  uart_1_getc(void);
int  uart_1_puts(const char *s);
int  uart_1_selftest(void);

#endif
