/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* caravel_wrapper — Polled-mode driver
 * Base address: from memory_map.json caravel_wrapper_BASE
 */
#include "caravel_wrapper_driver.h"

void caravel_wrapper_init(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(caravel_wrapper_BASE);
    (void)regs;
}

int caravel_wrapper_selftest(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(caravel_wrapper_BASE);
    (void)regs;
    return 0;
}
