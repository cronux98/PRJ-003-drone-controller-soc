/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* custom_timer — Polled-mode driver
 * Base address: from memory_map.json custom_timer_BASE
 */
#include "custom_timer_driver.h"

void custom_timer_init(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(custom_timer_BASE);
    (void)regs;
}

int custom_timer_selftest(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(custom_timer_BASE);
    (void)regs;
    return 0;
}
