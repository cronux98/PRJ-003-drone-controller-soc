#!/usr/bin/env python3
"""gen_linker_script.py — memory_map.json → link.ld.
Handles base_address/size_bytes schema (IP-010 v4)."""
import json, sys, hashlib

BANNER = "/* GENERATED-FROM: memory_map.json@<md5> — DO NOT HAND-EDIT */\n"

def parse_addr(val):
    return int(val, 0) if isinstance(val, str) else int(val)

def main():
    mm_path = sys.argv[1]
    with open(mm_path) as f:
        mm = json.load(f)
    md5 = hashlib.md5(open(mm_path,'rb').read()).hexdigest()

    regions = mm.get("regions", [])
    core = mm.get("core", {})

    lines = [BANNER.replace("<md5>", md5)]
    lines.append(f"/* IP-010 v4 — {core.get('isa','rv32imc')} {core.get('abi','ilp32')} */")
    lines.append("")

    # MEMORY
    lines.append("MEMORY")
    lines.append("{")
    for r in regions:
        name = r.get("name", "UNKNOWN")
        base = parse_addr(r.get("base_address", r.get("base", 0)))
        size = r.get("size_bytes", r.get("size", 0))
        attrs = r.get("attrs", "rwx")
        if not attrs:
            attrs = "rx" if r.get("type") == "ROM" else "rwx"
        base_hex = f"0x{base:08X}"
        lines.append(f"    {name} ({attrs})  : ORIGIN = {base_hex}, LENGTH = {size}")
    lines.append("}")
    lines.append("")
    lines.append("ENTRY(_start)")
    lines.append("")

    # Find writable region
    writable = None
    for r in regions:
        attrs = r.get("attrs", "rwx")
        if "w" in attrs or r.get("type", "") == "RAM":
            writable = r
            break
    if not writable:
        writable = regions[0]
    wr_name = writable.get("name", "SRAM")
    wr_base = parse_addr(writable.get("base_address", writable.get("base", 0)))

    lines.append("SECTIONS")
    lines.append("{")
    lines.append(f"    . = 0x{wr_base:08X};")
    lines.append("")
    lines.append("    .text : {")
    lines.append("        *(.text._start)")
    lines.append("        *(.text*)")
    lines.append(f"    }} > {wr_name}")
    lines.append("")
    lines.append("    .rodata : {")
    lines.append("        *(.rodata*)")
    lines.append(f"    }} > {wr_name}")
    lines.append("")
    lines.append("    .data : {")
    lines.append("        *(.data*)")
    lines.append(f"    }} > {wr_name}")
    lines.append("")
    lines.append("    .bss : {")
    lines.append("        _bss_start = .;")
    lines.append("        *(.bss*)")
    lines.append("        *(COMMON)")
    lines.append("        _bss_end = .;")
    lines.append(f"    }} > {wr_name}")
    lines.append("")
    lines.append(f"    _stack_top = ORIGIN({wr_name}) + LENGTH({wr_name});")
    lines.append("}")

    out_path = "link.ld" if len(sys.argv) < 3 else sys.argv[2]
    content = "\n".join(lines) + "\n"
    with open(out_path, "w") as f:
        f.write(content)
    print(f"gen_linker_script: wrote {len(content)} bytes to {out_path}")
    print(f"gen_linker_script: source md5={md5}")

if __name__ == "__main__":
    main()
