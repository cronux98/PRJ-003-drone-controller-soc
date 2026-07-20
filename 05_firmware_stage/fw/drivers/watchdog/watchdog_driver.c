/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* watchdog — Polled-mode driver
 * Base address: from memory_map.json watchdog_BASE
 */
#include "watchdog_driver.h"

void watchdog_init(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(watchdog_BASE);
    (void)regs;
}

int watchdog_selftest(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(watchdog_BASE);
    (void)regs;
    return 0;
}
