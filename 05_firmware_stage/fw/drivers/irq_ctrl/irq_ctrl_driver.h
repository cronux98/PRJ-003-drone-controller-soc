/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* irq_ctrl — 16-source interrupt controller driver header */
#ifndef IRQ_CTRL_DRIVER_H
#define IRQ_CTRL_DRIVER_H
#include "soc.h"
#include "irq_ctrl.h"

#define IRQ_ENABLE_OFFSET    0x00
#define IRQ_PENDING_OFFSET   0x04
#define IRQ_PRIORITY_OFFSET  0x08
#define IRQ_THRESHOLD_OFFSET 0x0C
#define IRQ_CLAIM_OFFSET     0x10
#define IRQ_COMPLETE_OFFSET  0x14

void irq_ctrl_init(void);
void irq_enable(int irq_num);
void irq_disable(int irq_num);
void irq_set_priority(int irq_num, int priority);
int  irq_selftest(void);

#endif
