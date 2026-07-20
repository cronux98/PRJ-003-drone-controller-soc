/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* spi_0 — Polled-mode driver
 * Base address: from memory_map.json spi_0_BASE
 */
#include "spi_0_driver.h"

void spi_0_init(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(spi_0_BASE);
    (void)regs;
}

int spi_0_selftest(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(spi_0_BASE);
    (void)regs;
    return 0;
}
