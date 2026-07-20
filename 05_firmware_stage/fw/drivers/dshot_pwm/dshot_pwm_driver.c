/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* dshot_pwm — Polled-mode driver
 * Base address: from memory_map.json dshot_pwm_BASE
 */
#include "dshot_pwm_driver.h"

void dshot_pwm_init(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(dshot_pwm_BASE);
    (void)regs;
}

int dshot_pwm_selftest(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(dshot_pwm_BASE);
    (void)regs;
    return 0;
}
