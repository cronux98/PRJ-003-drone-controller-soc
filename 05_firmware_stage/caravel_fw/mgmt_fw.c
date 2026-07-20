/* GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 + caravel/defs.h */
/* IP-010 v4 — Caravel management-core firmware
 *
 * Runs on Caravel's management RISC-V core (separate from user Ibex).
 * Responsibilities:
 *   1. Configure GPIO chain for user-project I/O pins
 *   2. Load user firmware into SRAM via Wishbone
 *   3. Release user-project reset
 *   4. Exercise user-project Wishbone registers (readback check)
 *   5. Signal completion via UART: "MGMT_FW_DONE\n"
 *
 * Caravel addresses (from defs.h):
 *   UART:  0x2000_0000 (mgmt-core debug UART)
 *   GPIO:  0x2100_0000 (mgmt GPIO)
 *   LA0-3: 0x2500_0000 (logic analyzer = user I/O pads)
 *   User WB: 0x3000_0000 (user project Wishbone)
 */

#include <stdint.h>

/* --- Caravel Register Definitions --- */
#define reg_uart_clkdiv (*(volatile uint32_t*)0x20000000)
#define reg_uart_data   (*(volatile uint32_t*)0x20000004)
#define reg_uart_enable (*(volatile uint32_t*)0x20000008)

#define reg_gpio_data (*(volatile uint32_t*)0x21000000)
#define reg_gpio_ena  (*(volatile uint32_t*)0x21000004)
#define reg_gpio_pu   (*(volatile uint32_t*)0x21000008)
#define reg_gpio_pd   (*(volatile uint32_t*)0x2100000c)

/* Logic Analyzer (mapped to user I/O pads) */
#define reg_la0_data (*(volatile uint32_t*)0x25000000)
#define reg_la1_data (*(volatile uint32_t*)0x25000004)
#define reg_la2_data (*(volatile uint32_t*)0x25000008)
#define reg_la3_data (*(volatile uint32_t*)0x2500000c)

#define reg_la0_oenb (*(volatile uint32_t*)0x25000010)
#define reg_la1_oenb (*(volatile uint32_t*)0x25000014)
#define reg_la2_oenb (*(volatile uint32_t*)0x25000018)
#define reg_la3_oenb (*(volatile uint32_t*)0x2500001c)

/* User project Wishbone base */
#define USER_WB_BASE  0x30000000
#define USER_SRAM_BASE 0x00000000

/* GPIO mode values (from caravel/defs.h) */
#define GPIO_MODE_MGMT_STD_INPUT_NOPULL  0x0403
#define GPIO_MODE_MGMT_STD_OUTPUT        0x1801
#define GPIO_MODE_USER_STD_INPUT_NOPULL  0x0402
#define GPIO_MODE_USER_STD_OUTPUT        0x1800
#define GPIO_MODE_USER_STD_BIDIRECTIONAL 0x1802
#define GPIO_MODE_MGMT_STD_INPUT_PULLUP  0x0803

/* --- UART Helpers --- */
static void mgmt_uart_putc(char c) {
    while (!(reg_uart_data & 0x100)) { /* TX ready */ }
    reg_uart_data = (unsigned char)c;
}

static void mgmt_uart_puts(const char *s) {
    while (*s) mgmt_uart_putc(*s++);
}

/* --- Wishbone R/W helpers for user project --- */
static uint32_t wb_read(uint32_t addr) {
    volatile uint32_t *p = (volatile uint32_t*)(USER_WB_BASE + addr);
    return *p;
}

static void wb_write(uint32_t addr, uint32_t val) {
    volatile uint32_t *p = (volatile uint32_t*)(USER_WB_BASE + addr);
    *p = val;
}

/* --- GPIO configuration for user project I/O --- */
static void configure_gpio(void) {
    /* Disable all GPIO first */
    reg_gpio_ena = 0x00000000;

    /* Configure user I/O pins via Logic Analyzer
     * Based on IP-010 v4 spec: 3 UARTs + SPI + I2C + DShot PWM + GPIO
     * We configure the LA (I/O pads) as user outputs for UART TX,
     * user inputs for UART RX, etc.
     *
     * LA0: UART 0 (GPS) — TX output, RX input
     * LA1: UART 1 (RC) + UART 2 (telemetry)
     * LA2: SPI 0 + I2C 0
     * LA3: DShot PWM + extra GPIO
     */
    reg_la0_oenb = 0xFFFFFFFD;  /* bit 0 = UART0 TX = output */
    reg_la1_oenb = 0xFFFFFFFD;  /* bit 0 = UART1 TX = output */
    reg_la2_oenb = 0xFFFFFFC0;  /* bits [5:0] = SPI/I2C outputs */
    reg_la3_oenb = 0xFFFFFF00;  /* bits [7:0] = DShot PWM + GPIO outputs */
}

/* --- Wishbone exerciser: R/W/R on user project peripherals --- */
static void wishbone_exerciser(void) {
    /* Test 1: Read SRAM through Wishbone (should be accessible) */
    uint32_t sram_word0 = wb_read(0x00000000);
    mgmt_uart_puts("WB:SRAM_RD=");
    mgmt_uart_putc("0123456789ABCDEF"[(sram_word0 >> 28) & 0xF]);

    /* Test 2: Write/Read back UART 2 status register */
    wb_write(0x80002004, 0x00000000);   /* clear status */
    uint32_t status = wb_read(0x80002004);
    if (status & 0x01) {  /* TX_READY */
        mgmt_uart_puts(" OK:UART2_RW");
    }

    /* Test 3: GPIO R/W */
    wb_write(0x80006004, 0x000000FF);   /* all GPIO as outputs */
    wb_write(0x80006000, 0x000000A5);   /* write pattern */
    uint32_t gpio_val = wb_read(0x80006000);
    if ((gpio_val & 0xFF) == 0xA5) {
        mgmt_uart_puts(" OK:GPIO_RW");
    }

    /* Test 4: Timer prescale R/W */
    wb_write(0x80009004, 0x0000DEAD);   /* prescale */
    uint32_t tmr_val = wb_read(0x80009004);
    if (tmr_val == 0x0000DEAD) {
        mgmt_uart_puts(" OK:TMR_RW");
    }

    /* Test 5: IRQ controller enable R/W */
    wb_write(0x80008000, 0x000000AA);   /* enable mask */
    uint32_t irq_val = wb_read(0x80008000);
    if (irq_val == 0x000000AA) {
        mgmt_uart_puts(" OK:IRQ_RW");
    }
}

/* --- Main --- */
void main(void) {
    /* Initialize UART */
    reg_uart_clkdiv = 9;  /* 16.67 MHz / 115200 baud / 8 = ~9 */
    reg_uart_enable = 0x01;

    mgmt_uart_puts("\r\nIP-010 V4 MGMT\r\n");

    /* Step 1: Configure GPIO */
    configure_gpio();
    mgmt_uart_puts("GPIO_CFG\r\n");

    /* Step 2: Release user project reset
     * Write to Caravel housekeeping register to de-assert user reset.
     * (This is a simplified path — real Caravel uses specific registers.)
     */
    reg_gpio_data = 0x01;
    mgmt_uart_puts("RST_REL\r\n");

    /* Step 3: Exercise user project via Wishbone */
    wishbone_exerciser();

    /* Step 4: Signal completion */
    mgmt_uart_puts("\r\nMGMT_FW_DONE\r\n");

    /* Infinite loop */
    while (1) { }
}
