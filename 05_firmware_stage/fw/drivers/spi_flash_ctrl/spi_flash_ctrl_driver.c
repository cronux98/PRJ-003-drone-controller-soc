/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* spi_flash_ctrl — Polled-mode driver
 * Base address: from memory_map.json spi_flash_ctrl_BASE
 */
#include "spi_flash_ctrl_driver.h"

void spi_flash_ctrl_init(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(spi_flash_ctrl_BASE);
    (void)regs;
}

int spi_flash_ctrl_selftest(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(spi_flash_ctrl_BASE);
    (void)regs;
    return 0;
}
