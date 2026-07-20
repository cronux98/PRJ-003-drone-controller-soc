/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* gpio — 8-bit GPIO driver header */
#ifndef GPIO_DRIVER_H
#define GPIO_DRIVER_H
#include "soc.h"
#include "gpio.h"

#define GPIO_DATA_OFFSET    0x00
#define GPIO_DIR_OFFSET     0x04
#define GPIO_IRQ_EN_OFFSET  0x08
#define GPIO_IRQ_STS_OFFSET 0x0C

void gpio_init(void);
void gpio_set_dir(uint8_t mask, uint8_t dir);
void gpio_write(uint8_t val);
uint8_t gpio_read(void);
int  gpio_selftest(void);

#endif
