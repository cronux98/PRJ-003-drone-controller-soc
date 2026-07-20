// =========================================================================
// Module: sram_8kb_blackbox
// Description: Blackbox wrapper for sram_8kb — synthesis/PD stub
//              Same port interface as sram_8kb, no internal logic.
//              Used during synthesis and physical design to prevent
//              the 2048×32 inferred BRAM from being synthesized as DFFs.
//              At P&R, the actual SRAM macro (OpenRAM or pre-built) is
//              placed as a hard macro.
//
// Source: IP-010 v2 — SRAM blackbox directive (v1 postmortem fix)
// v4 fix: Added wb_err_o port (missing from original blackbox, required
//         by drone_soc instantiation which connects .wb_err_o(s_wb_err[0])).
// Usage: Include this file in synth/PD flows INSTEAD of sram_8kb.v
//        RTL simulation uses the full behavioral model (sram_8kb.v).
// =========================================================================

(* blackbox *)
module sram_8kb (
    input  wire        clk_i,
    input  wire        rst_ni,

    // Wishbone B4 slave
    input  wire [12:0] wb_adr_i,
    input  wire [31:0] wb_dat_i,
    output wire [31:0] wb_dat_o,
    input  wire [ 3:0] wb_sel_i,
    input  wire        wb_we_i,
    input  wire        wb_stb_i,
    input  wire        wb_cyc_i,
    output wire        wb_ack_o,
    output wire        wb_err_o
);

    // No logic — blackbox for synthesis/PD.
    // The place-and-route tool will place the actual SRAM macro here.
    // Tie outputs to safe defaults to prevent undriven-net errors.
    assign wb_dat_o = 32'b0;
    assign wb_ack_o = 1'b0;
    assign wb_err_o = 1'b0;

endmodule
