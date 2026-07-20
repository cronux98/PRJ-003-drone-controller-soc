/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* timer — 32-bit timer driver header */
#ifndef TIMER_DRIVER_H
#define TIMER_DRIVER_H
#include "soc.h"
#include "timer.h"

#define TIMER_CTRL_OFFSET     0x00
#define TIMER_PRESCALE_OFFSET 0x04
#define TIMER_COUNT_OFFSET    0x08
#define TIMER_COMPARE_OFFSET  0x0C

void     timer_init(uint32_t prescale, uint32_t reload);
void     timer_start(void);
void     timer_stop(void);
uint32_t timer_read(void);
int      timer_selftest(void);

#endif
