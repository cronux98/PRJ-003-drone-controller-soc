/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* i2c_0 — Polled-mode driver
 * Base address: from memory_map.json i2c_0_BASE
 */
#include "i2c_0_driver.h"

void i2c_0_init(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(i2c_0_BASE);
    (void)regs;
}

int i2c_0_selftest(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(i2c_0_BASE);
    (void)regs;
    return 0;
}
