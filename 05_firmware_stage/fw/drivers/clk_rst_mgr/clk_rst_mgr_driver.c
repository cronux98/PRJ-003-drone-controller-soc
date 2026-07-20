/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* clk_rst_mgr — Polled-mode driver
 * Base address: from memory_map.json clk_rst_mgr_BASE
 */
#include "clk_rst_mgr_driver.h"

void clk_rst_mgr_init(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(clk_rst_mgr_BASE);
    (void)regs;
}

int clk_rst_mgr_selftest(void) {
    volatile uint32_t *regs = (volatile uint32_t*)(uintptr_t)(clk_rst_mgr_BASE);
    (void)regs;
    return 0;
}
