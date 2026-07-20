/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */

/* IP-010 v4 — Peripheral Register Map */
#ifndef SOC_H
#define SOC_H

#include <stdint.h>

/* ── Core ─────────────────────────────── */
#define CPU_ISA           "rv32imc"
#define CPU_ABI           "ilp32"
#define CLOCK_HZ           16670000

/* ── Memory Regions ───────────────────── */
#define sram_8kb_BASE       0x0000
#define sram_8kb_SIZE_BYTES 8192

#define uart_0_BASE       0x80000000
#define uart_0_SIZE_BYTES 4096

#define uart_1_BASE       0x80001000
#define uart_1_SIZE_BYTES 4096

#define uart_2_BASE       0x80002000
#define uart_2_SIZE_BYTES 4096

#define spi_0_BASE       0x80003000
#define spi_0_SIZE_BYTES 4096

#define i2c_0_BASE       0x80004000
#define i2c_0_SIZE_BYTES 4096

#define dshot_pwm_BASE       0x80005000
#define dshot_pwm_SIZE_BYTES 4096

#define gpio_BASE       0x80006000
#define gpio_SIZE_BYTES 4096

#define spi_flash_ctrl_BASE       0x80007000
#define spi_flash_ctrl_SIZE_BYTES 4096

#define irq_ctrl_BASE       0x80008000
#define irq_ctrl_SIZE_BYTES 4096

#define timer_BASE       0x80009000
#define timer_SIZE_BYTES 4096

#define watchdog_BASE       0x8000A000
#define watchdog_SIZE_BYTES 4096

#define caravel_wrapper_BASE       0x8000B000
#define caravel_wrapper_SIZE_BYTES 4096

#define clk_rst_mgr_BASE       0x8000C000
#define clk_rst_mgr_SIZE_BYTES 4096

#define custom_timer_BASE       0x8000D000
#define custom_timer_SIZE_BYTES 4096


/* ── Register Accessors ──────────────── */
#define REG_READ(addr)    (*(volatile uint32_t*)((uintptr_t)(addr)))
#define REG_WRITE(addr,v) (*(volatile uint32_t*)((uintptr_t)(addr)) = (v))

/* ── uart_0 ─────────────────────────── */
#define uart_0_BASE       0x80000000
/* No register-level details in memory_map.json — see RTL for register map */

/* ── uart_1 ─────────────────────────── */
#define uart_1_BASE       0x80001000
/* No register-level details in memory_map.json — see RTL for register map */

/* ── uart_2 ─────────────────────────── */
#define uart_2_BASE       0x80002000
/* No register-level details in memory_map.json — see RTL for register map */

/* ── spi_0 ─────────────────────────── */
#define spi_0_BASE       0x80003000
/* No register-level details in memory_map.json — see RTL for register map */

/* ── i2c_0 ─────────────────────────── */
#define i2c_0_BASE       0x80004000
/* No register-level details in memory_map.json — see RTL for register map */

/* ── dshot_pwm ─────────────────────────── */
#define dshot_pwm_BASE       0x80005000
/* No register-level details in memory_map.json — see RTL for register map */

/* ── gpio ─────────────────────────── */
#define gpio_BASE       0x80006000
/* No register-level details in memory_map.json — see RTL for register map */

/* ── spi_flash_ctrl ─────────────────────────── */
#define spi_flash_ctrl_BASE       0x80007000
/* No register-level details in memory_map.json — see RTL for register map */

/* ── irq_ctrl ─────────────────────────── */
#define irq_ctrl_BASE       0x80008000
/* No register-level details in memory_map.json — see RTL for register map */

/* ── timer ─────────────────────────── */
#define timer_BASE       0x80009000
/* No register-level details in memory_map.json — see RTL for register map */

/* ── watchdog ─────────────────────────── */
#define watchdog_BASE       0x8000A000
/* No register-level details in memory_map.json — see RTL for register map */

/* ── caravel_wrapper ─────────────────────────── */
#define caravel_wrapper_BASE       0x8000B000
/* No register-level details in memory_map.json — see RTL for register map */

/* ── clk_rst_mgr ─────────────────────────── */
#define clk_rst_mgr_BASE       0x8000C000
/* No register-level details in memory_map.json — see RTL for register map */

/* ── custom_timer ─────────────────────────── */
#define custom_timer_BASE       0x8000D000
/* No register-level details in memory_map.json — see RTL for register map */

/* ── Bit Manipulation ─────────────────── */
static inline void reg_set(volatile uint32_t *reg, uint32_t mask) { REG_WRITE(reg, REG_READ(reg) | mask); }
static inline void reg_clear(volatile uint32_t *reg, uint32_t mask) { REG_WRITE(reg, REG_READ(reg) & ~mask); }

#endif /* SOC_H */
