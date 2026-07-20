#!/usr/bin/env python3
"""Rename the top cell in a GDS from drone_soc to user_project_wrapper.
Run via: klayout -b -r rename_topcell.py
Uses KLayout's embedded Python (pya module)."""

import pya

GDS_IN  = "~/hermes_workspace/projects/IP-010/v4/09_caravel_stage/precheck_input/gds/user_project_wrapper.gds"
GDS_OUT = GDS_IN  # overwrite
OLD_NAME = "drone_soc"
NEW_NAME = "user_project_wrapper"

layout = pya.Layout()
layout.read(GDS_IN)

# Find top cell (last cell defined)
top_cell_idx = layout.cells() - 1
old_cell_name = layout.cell(top_cell_idx).name
print(f"Top cell index {top_cell_idx}, current name: '{old_cell_name}'")
assert old_cell_name == OLD_NAME, f"Expected '{OLD_NAME}', found '{old_cell_name}'"
layout.cell(top_cell_idx).name = NEW_NAME
print(f"Renamed to: '{NEW_NAME}'")

layout.write(GDS_OUT)
print(f"Wrote: {GDS_OUT}")

# Verify
layout2 = pya.Layout()
layout2.read(GDS_OUT)
top_name = layout2.cell(layout2.cells() - 1).name
assert top_name == NEW_NAME, f"Verification failed: '{top_name}' != '{NEW_NAME}'"
print(f"VERIFIED: top cell is '{NEW_NAME}'")
