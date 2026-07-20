/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* timer — 32-bit timer driver */
#include "timer_driver.h"

void timer_init(uint32_t prescale, uint32_t reload) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(timer_BASE);
    regs[TIMER_PRESCALE_OFFSET / 4] = prescale;
    regs[TIMER_COMPARE_OFFSET / 4] = reload;
    regs[TIMER_COUNT_OFFSET / 4] = 0;
}

void timer_start(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(timer_BASE);
    regs[TIMER_CTRL_OFFSET / 4] = 0x01;
}

void timer_stop(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(timer_BASE);
    regs[TIMER_CTRL_OFFSET / 4] = 0x00;
}

uint32_t timer_read(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(timer_BASE);
    return regs[TIMER_COUNT_OFFSET / 4];
}

int timer_selftest(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(timer_BASE);
    uint32_t orig = regs[TIMER_PRESCALE_OFFSET / 4];
    regs[TIMER_PRESCALE_OFFSET / 4] = 0xDEAD;
    if (regs[TIMER_PRESCALE_OFFSET / 4] != 0xDEAD) return -1;
    regs[TIMER_PRESCALE_OFFSET / 4] = orig;
    return 0;
}
