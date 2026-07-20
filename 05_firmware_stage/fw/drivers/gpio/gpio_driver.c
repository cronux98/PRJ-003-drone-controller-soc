/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* gpio — 8-bit GPIO driver */
#include "gpio_driver.h"

void gpio_init(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(gpio_BASE);
    regs[GPIO_DATA_OFFSET / 4] = 0x00;
    regs[GPIO_DIR_OFFSET / 4]  = 0x00;
    regs[GPIO_IRQ_EN_OFFSET / 4] = 0x00;
}

void gpio_set_dir(uint8_t mask, uint8_t dir) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(gpio_BASE);
    uint32_t cur = regs[GPIO_DIR_OFFSET / 4];
    if (dir)
        regs[GPIO_DIR_OFFSET / 4] = cur | mask;
    else
        regs[GPIO_DIR_OFFSET / 4] = cur & ~((uint32_t)mask);
}

void gpio_write(uint8_t val) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(gpio_BASE);
    regs[GPIO_DATA_OFFSET / 4] = val;
}

uint8_t gpio_read(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(gpio_BASE);
    return (uint8_t)(regs[GPIO_DATA_OFFSET / 4] & 0xFF);
}

int gpio_selftest(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(gpio_BASE);
    uint32_t orig_dir = regs[GPIO_DIR_OFFSET / 4];
    regs[GPIO_DIR_OFFSET / 4] = 0xFF;
    regs[GPIO_DATA_OFFSET / 4] = 0xA5;
    if ((regs[GPIO_DATA_OFFSET / 4] & 0xFF) != 0xA5) return -1;
    regs[GPIO_DIR_OFFSET / 4] = orig_dir;
    return 0;
}
