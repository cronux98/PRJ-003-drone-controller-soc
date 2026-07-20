#!/usr/bin/env python3
"""gen_headers.py — memory_map.json → soc.h + per-peripheral headers.
Handles base_address/size_bytes schema (IP-010 v4)."""
import json, sys, hashlib
from pathlib import Path

BANNER = "/* GENERATED-FROM: memory_map.json@<md5> — DO NOT HAND-EDIT */\n"

def parse_addr(val):
    return int(val, 0) if isinstance(val, str) else int(val)

def sanitize(name):
    return name.replace("-","_").replace(" ","_")

def hex_val(val):
    v = parse_addr(val)
    return f"0x{v:08X}" if v > 0xFFFF else f"0x{v:04X}"

def field_mask(width, lo_bit):
    return f"0x{(((1 << width) - 1) << lo_bit):08X}"

def main():
    mm_path = sys.argv[1]
    out_idx = sys.argv.index("--out-dir")
    out_dir = sys.argv[out_idx + 1]

    with open(mm_path) as f:
        mm = json.load(f)
    md5 = hashlib.md5(open(mm_path,'rb').read()).hexdigest()
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    regions = mm.get("regions", [])
    peripherals = mm.get("peripherals", [])
    core = mm.get("core", {})

    # === soc.h ===
    banner = BANNER.replace("<md5>", md5)
    lines = [banner]
    lines.append("/* IP-010 v4 — Peripheral Register Map */")
    lines.append("#ifndef SOC_H")
    lines.append("#define SOC_H")
    lines.append("")
    lines.append("#include <stdint.h>")
    lines.append("")

    # Core
    lines.append("/* ── Core ─────────────────────────────── */")
    isa = core.get("isa", "rv32imc")
    lines.append(f'#define CPU_ISA           "{isa}"')
    lines.append(f'#define CPU_ABI           "{core.get("abi", "ilp32")}"')
    lines.append(f"#define CLOCK_HZ           16670000")
    lines.append("")

    # Regions
    lines.append("/* ── Memory Regions ───────────────────── */")
    for r in regions:
        name = sanitize(r.get("name","UNKNOWN"))
        base = hex_val(r.get("base_address", r.get("base", 0)))
        size = r.get("size_bytes", r.get("size", 0))
        lines.append(f"#define {name}_BASE       {base}")
        lines.append(f"#define {name}_SIZE_BYTES {size}")
        lines.append("")
    lines.append("")

    # Accessor macros
    lines.append("/* ── Register Accessors ──────────────── */")
    lines.append("#define REG_READ(addr)    (*(volatile uint32_t*)((uintptr_t)(addr)))")
    lines.append("#define REG_WRITE(addr,v) (*(volatile uint32_t*)((uintptr_t)(addr)) = (v))")
    lines.append("")

    # Peripherals
    for p in peripherals:
        pname = sanitize(p.get("name","UNKNOWN"))
        pbase = hex_val(p.get("base_address", p.get("base", 0)))
        lines.append(f"/* ── {pname} ─────────────────────────── */")
        lines.append(f"#define {pname}_BASE       {pbase}")

        registers = p.get("registers", [])
        if registers:
            for reg in registers:
                rname = sanitize(reg.get("name","UNKNOWN"))
                offset = hex_val(reg.get("offset", 0))
                lines.append(f"#define {pname}_{rname}_OFFSET  {offset}")
                fields = reg.get("fields", [])
                for fld in fields:
                    fname = sanitize(fld.get("name","UNKNOWN"))
                    if "bits" in fld:
                        b = fld["bits"]
                        w = b[0]-b[1]+1 if len(b)==2 else 1
                        l = b[1] if len(b)==2 else b[0]
                    else:
                        w = fld.get("width",1)
                        l = fld.get("lo_bit",0)
                    lines.append(f"#define {pname}_{rname}_{fname}_MASK  {field_mask(w,l)}")
        else:
            # No register details — provide generic note
            lines.append(f"/* No register-level details in memory_map.json — see RTL for register map */")

        lines.append("")

    # Bit helpers
    lines.append("/* ── Bit Manipulation ─────────────────── */")
    lines.append("static inline void reg_set(volatile uint32_t *reg, uint32_t mask) { REG_WRITE(reg, REG_READ(reg) | mask); }")
    lines.append("static inline void reg_clear(volatile uint32_t *reg, uint32_t mask) { REG_WRITE(reg, REG_READ(reg) & ~mask); }")
    lines.append("")

    lines.append("#endif /* SOC_H */")

    soc_path = Path(out_dir) / "soc.h"
    content = "\n".join(lines) + "\n"
    with open(soc_path, "w") as f:
        f.write(content)
    print(f"gen_headers: wrote {len(content)} bytes to {soc_path}")

    # Also generate per-peripheral headers with what we know
    for p in peripherals:
        pname = sanitize(p.get("name","UNKNOWN"))
        pbase = hex_val(p.get("base_address", p.get("base", 0)))
        ph_lines = [banner]
        ph_lines.append(f"/* {pname} — Register header */")
        ph_lines.append(f"#ifndef {pname}_H")
        ph_lines.append(f"#define {pname}_H")
        ph_lines.append("")
        ph_lines.append('#include "soc.h"')
        ph_lines.append("")
        ph_lines.append(f"#define {pname}_BASE_ADDR  {pbase}")
        ph_lines.append("")
        registers = p.get("registers", [])
        if registers:
            for reg in registers:
                rname = sanitize(reg.get("name","UNKNOWN"))
                offset = hex_val(reg.get("offset", 0))
                ph_lines.append(f"#define {pname}_{rname}  ((volatile uint32_t*)({pname}_BASE + {offset}))")
        ph_lines.append("")
        ph_lines.append(f"#endif /* {pname}_H */")

        periph_path = Path(out_dir) / f"{p.get('name','unknown')}.h"
        pc = "\n".join(ph_lines) + "\n"
        with open(periph_path, "w") as f:
            f.write(pc)
        print(f"gen_headers: wrote {len(pc)} bytes to {periph_path}")

    print(f"gen_headers: source md5={md5}")

if __name__ == "__main__":
    main()
