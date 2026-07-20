/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* irq_ctrl — 16-source interrupt controller driver */
#include "irq_ctrl_driver.h"

void irq_ctrl_init(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(irq_ctrl_BASE);
    regs[IRQ_ENABLE_OFFSET / 4] = 0x00000000;
    regs[IRQ_THRESHOLD_OFFSET / 4] = 0x0000000F;
}

void irq_enable(int irq_num) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(irq_ctrl_BASE);
    regs[IRQ_ENABLE_OFFSET / 4] |= (1u << irq_num);
}

void irq_disable(int irq_num) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(irq_ctrl_BASE);
    regs[IRQ_ENABLE_OFFSET / 4] &= ~(1u << irq_num);
}

void irq_set_priority(int irq_num, int priority) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(irq_ctrl_BASE);
    uint32_t shift = (irq_num % 8) * 4;
    uint32_t mask = 0xFu << shift;
    uint32_t val = (regs[IRQ_PRIORITY_OFFSET / 4] & ~mask) | ((priority & 0xF) << shift);
    regs[IRQ_PRIORITY_OFFSET / 4] = val;
}

int irq_selftest(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(irq_ctrl_BASE);
    uint32_t orig = regs[IRQ_ENABLE_OFFSET / 4];
    regs[IRQ_ENABLE_OFFSET / 4] = 0xAA;
    if (regs[IRQ_ENABLE_OFFSET / 4] != 0xAA) return -1;
    regs[IRQ_ENABLE_OFFSET / 4] = orig;
    return 0;
}
