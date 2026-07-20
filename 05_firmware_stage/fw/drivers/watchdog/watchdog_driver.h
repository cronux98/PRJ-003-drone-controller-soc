/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT */
/* watchdog — Polled-mode driver header */
#ifndef WATCHDOG_DRIVER_H
#define WATCHDOG_DRIVER_H

#include "soc.h"
#include "watchdog.h"

void watchdog_init(void);
int watchdog_selftest(void);

#endif /* WATCHDOG_DRIVER_H */
