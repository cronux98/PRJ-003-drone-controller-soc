# GENERATED-FROM: memory_map.json@3455a1e3258d23f4da89752e4aba0ac4 — DO NOT HAND-EDIT
# IP-010 v4 — bootrom Makefile
# Boot ROM: crt0 + boot_main. Must fit in < 4KB.

TOOLCHAIN_DIR := /opt/OpenROAD/riscv/gcc14-no-zcmp/bin
CC      := $(TOOLCHAIN_DIR)/riscv32-unknown-elf-gcc
OBJCOPY := $(TOOLCHAIN_DIR)/riscv32-unknown-elf-objcopy
OBJDUMP := $(TOOLCHAIN_DIR)/riscv32-unknown-elf-objdump
SIZE    := $(TOOLCHAIN_DIR)/riscv32-unknown-elf-size

ARCH_FLAGS := -march=rv32imc_zicsr -mabi=ilp32
CFLAGS := $(ARCH_FLAGS) -nostdlib -nostartfiles -ffreestanding -Os \
          -Wall -Wextra -Werror \
          -I ../bsp/include

LDFLAGS := -T ../bsp/link.ld -nostdlib -Wl,-Map=bootrom.map

SRCS := crt0.S boot_main.c
OBJS := crt0.o boot_main.o
ELF  := bootrom.elf
HEX  := bootrom.hex
BIN  := bootrom.bin
DISASM := bootrom.disasm

all: $(HEX) $(DISASM) bootrom_report.json

$(HEX): $(ELF)
	$(OBJCOPY) -O ihex $< $@
	$(OBJCOPY) -O binary $< $(BIN)
	@stat --format=%s $(BIN) > bootrom.size

$(ELF): $(OBJS)
	$(CC) $(ARCH_FLAGS) $(LDFLAGS) -o $@ $^
	$(SIZE) $@

crt0.o: crt0.S
	$(CC) $(CFLAGS) -c -o $@ $<

boot_main.o: boot_main.c ../bsp/include/soc.h
	$(CC) $(CFLAGS) -c -o $@ $<

$(DISASM): $(ELF)
	$(OBJDUMP) -d $< > $@

bootrom_report.json: $(BIN) bootrom.size
	@echo '{' > $@
	@echo '  "_metadata": { "source": "memory_map.json@3455a1e3258d23f4da89752e4aba0ac4" },' >> $@
	@echo '  "bootrom_size_bytes": '$$(cat bootrom.size)',' >> $@
	@echo '  "max_budget_bytes": 4096,' >> $@
	@printf '  "verdict": "' >> $@
	@[ $$(cat bootrom.size) -le 4096 ] && printf 'PASS' >> $@ || printf 'FAIL' >> $@
	@echo '"' >> $@
	@echo '}' >> $@

clean:
	rm -f $(OBJS) $(ELF) $(HEX) $(BIN) $(DISASM) bootrom.map bootrom.size bootrom_report.json

.PHONY: all clean
