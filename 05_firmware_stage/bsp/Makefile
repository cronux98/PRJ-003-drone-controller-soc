# GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT
# IP-010 v4 — BSP Makefile (run from 05_firmware_stage/)
# Toolchain: riscv32-unknown-elf-gcc 14.2.1 (pinned)
# ISA: rv32imc, ABI: ilp32 (from memory_map.json core block)

TOOLCHAIN_DIR := /opt/OpenROAD/riscv/gcc14-no-zcmp/bin
CC      := $(TOOLCHAIN_DIR)/riscv32-unknown-elf-gcc
OBJCOPY := $(TOOLCHAIN_DIR)/riscv32-unknown-elf-objcopy
OBJDUMP := $(TOOLCHAIN_DIR)/riscv32-unknown-elf-objdump
SIZE    := $(TOOLCHAIN_DIR)/riscv32-unknown-elf-size

ARCH_FLAGS := -march=rv32imc_zicsr -mabi=ilp32
CFLAGS := $(ARCH_FLAGS) -nostdlib -nostartfiles -ffreestanding -Os \
          -Wall -Wextra -Werror \
          -I bsp/include

LDFLAGS := -T bsp/link.ld -nostdlib -Wl,-Map=bsp/firmware.map

SRCS := bsp/crt0.S bsp/main.c
OBJS := bsp/crt0.o bsp/main.o
ELF  := bsp/firmware.elf
HEX  := bsp/firmware.hex
BIN  := bsp/firmware.bin
DISASM := bsp/firmware.disasm

.PHONY: all clean

all: $(HEX) $(DISASM)

$(HEX): $(ELF)
	$(OBJCOPY) -O ihex $< $@
	$(OBJCOPY) -O binary $< $(BIN)

$(ELF): $(OBJS)
	$(CC) $(ARCH_FLAGS) $(LDFLAGS) -o $@ $^
	$(SIZE) $@

bsp/crt0.o: bsp/crt0.S
	$(CC) $(CFLAGS) -c -o $@ $<

bsp/main.o: bsp/main.c bsp/include/soc.h
	$(CC) $(CFLAGS) -c -o $@ $<

$(DISASM): $(ELF)
	$(OBJDUMP) -d $< > $@

clean:
	rm -f $(OBJS) $(ELF) $(HEX) $(BIN) $(DISASM) bsp/firmware.map
