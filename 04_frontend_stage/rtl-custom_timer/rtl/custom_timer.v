// =========================================================================
// Module: custom_timer
// Description: DShot RPM Telemetry Timer Extensions
//              4-channel RPM pulse measurement via input capture
//              Wishbone B4 slave interface
//
// Source: IP-010 v4 Architecture §4.15, CREATE
// Clock: 16.67 MHz (60 ns tick)
//
// Register Map (offsets from base 0x8000_D000):
//   0x00 TICK_DELTA_CH0  R     Channel 0 tick delta (28-bit) — fw computes RPM
//   0x04 TICK_DELTA_CH1  R     Channel 1 tick delta
//   0x08 TICK_DELTA_CH2  R     Channel 2 tick delta
//   0x0C TICK_DELTA_CH3  R     Channel 3 tick delta
//   0x10 POLE_PAIRS      R/W   Motor pole pairs (default: 7)
//   0x14 CTRL            R/W   bit[0]=enable, bit[3:1]=filter depth
//   0x18 STATUS          R     bit[3:0]=ch_valid, bit[4]=measurement active
//
// RPM formula (firmware): RPM = 60 * 16,666,667 / (ticks * pole_pairs)
//
// Edge Cases:
//   - No pulse detected: TICK_DELTA holds last valid value. STATUS[ch_valid]=0.
//   - Pulse too fast (<3 cycles): skipped (anti-glitch filter)
//   - Pulse too slow (>1 sec): TICK_DELTA=0, STATUS[ch_valid]=0
//   - Pole pairs = 0: treated as 1 internally
//   - Reset state: All TICK_DELTA=0, POLE_PAIRS=7, CTRL=0 (disabled), STATUS=0
// =========================================================================

module custom_timer (
    input  wire        wb_clk_i,
    input  wire        wb_rst_ni,

    // Wishbone B4 slave
    input  wire [31:0] wb_adr_i,
    input  wire [31:0] wb_dat_i,
    output reg  [31:0] wb_dat_o,
    input  wire [ 3:0] wb_sel_i,
    input  wire        wb_we_i,
    input  wire        wb_stb_i,
    input  wire        wb_cyc_i,
    output reg         wb_ack_o,
    output reg         wb_err_o,

    // RPM capture inputs (one per DShot channel)
    input  wire [ 3:0] rpm_capture_i,

    // Interrupt
    output reg         irq_rpm_o
);

    // -----------------------------------------------------------------
    // Parameters
    // -----------------------------------------------------------------
    localparam TIMEOUT_CYCLES = 28'd16666667;  // 1 second at 16.67 MHz

    // -----------------------------------------------------------------
    // Registers
    // -----------------------------------------------------------------
    reg [27:0] tick_delta   [0:3];  // Tick delta registers (28-bit)
    reg [ 3:0] ch_valid;            // channel valid flags
    reg [15:0] pole_pairs;          // motor pole pairs (default 7)
    reg        ctrl_enable;         // global enable
    reg [ 2:0] ctrl_filter;         // anti-glitch filter depth (0-7)

    // -----------------------------------------------------------------
    // Input capture per channel
    // -----------------------------------------------------------------
    reg [27:0] capture_timer   [0:3];  // free-running timer for each channel
    reg [27:0] last_capture    [0:3];  // timestamp of last valid edge
    reg [27:0] tick_delta_reg  [0:3];  // registered tick delta
    reg [ 1:0] capture_sync    [0:3];  // 2-stage synchronizer
    reg        capture_edge    [0:3];  // edge detect: 0→1
    reg [ 2:0] glitch_filter   [0:3];  // anti-glitch counter
    reg        pulse_valid     [0:3];  // pulse passed filter

    // Wishbone
    wire wb_valid = wb_cyc_i && wb_stb_i;
    wire [5:0] wb_offset = wb_adr_i[5:0];

    integer j;

    always @(posedge wb_clk_i or negedge wb_rst_ni) begin
        if (!wb_rst_ni) begin
            for (j = 0; j < 4; j = j + 1) tick_delta[j]  <= 28'd0;
            for (j = 0; j < 4; j = j + 1) tick_delta_reg[j] <= 28'd0;
            ch_valid       <= 4'd0;
            pole_pairs     <= 16'd7;
            ctrl_enable    <= 1'b0;
            ctrl_filter    <= 3'd3;
            wb_ack_o       <= 1'b0;
            wb_err_o       <= 1'b0;
            wb_dat_o       <= 32'd0;
            irq_rpm_o      <= 1'b0;

            for (j = 0; j < 4; j = j + 1) begin
                capture_timer[j] <= 28'd0;
                last_capture[j]  <= 28'd0;
                capture_sync[j]  <= 2'd0;
                capture_edge[j]  <= 1'b0;
                glitch_filter[j] <= 3'd0;
                pulse_valid[j]   <= 1'b0;
            end
        end else begin
            // Defaults
            wb_ack_o  <= 1'b0;
            wb_err_o  <= 1'b0;
            irq_rpm_o <= 1'b0;

            // ---------------------------------------------------------
            // Wishbone register access
            // ---------------------------------------------------------
            if (wb_valid && !wb_ack_o) begin
                wb_ack_o <= 1'b1;
                if (wb_we_i) begin
                    case (wb_offset)
                        6'h10: pole_pairs  <= wb_dat_i[15:0];
                        6'h14: begin
                            ctrl_enable <= wb_dat_i[0];
                            ctrl_filter <= wb_dat_i[3:1];
                        end
                        default: wb_err_o <= 1'b1;
                    endcase
                end else begin
                    case (wb_offset)
                        6'h00: wb_dat_o <= {4'd0, tick_delta[0]};
                        6'h04: wb_dat_o <= {4'd0, tick_delta[1]};
                        6'h08: wb_dat_o <= {4'd0, tick_delta[2]};
                        6'h0C: wb_dat_o <= {4'd0, tick_delta[3]};
                        6'h10: wb_dat_o <= {16'd0, pole_pairs};
                        6'h14: wb_dat_o <= {27'd0, ctrl_filter, ctrl_enable};
                        6'h18: wb_dat_o <= {27'd0, ctrl_enable, ch_valid};
                        default: begin wb_dat_o <= 32'd0; wb_err_o <= 1'b1; end
                    endcase
                end
            end

            // ---------------------------------------------------------
            // RPM capture engine (4 channels)
            // ---------------------------------------------------------
            if (ctrl_enable) begin
                for (j = 0; j < 4; j = j + 1) begin
                    // 2-stage synchronizer
                    capture_sync[j] <= {capture_sync[j][0], rpm_capture_i[j]};

                    // Rising edge detect
                    capture_edge[j] <= (capture_sync[j] == 2'b01);

                    // Free-running timer with timeout detection
                    if (capture_timer[j] < TIMEOUT_CYCLES)
                        capture_timer[j] <= capture_timer[j] + 28'd1;
                    else begin
                        // Timeout: >1 second without pulse
                        capture_timer[j] <= 28'd0;
                        ch_valid[j]      <= 1'b0;
                        tick_delta[j]    <= 28'd0;
                    end

                    // Anti-glitch filter
                    if (capture_edge[j]) begin
                        if (glitch_filter[j] < ctrl_filter) begin
                            // Still in filter window — reject
                            glitch_filter[j] <= glitch_filter[j] + 3'd1;
                        end else begin
                            // Valid pulse edge detected
                            glitch_filter[j]  <= 3'd0;
                            tick_delta[j]     <= capture_timer[j] - last_capture[j];
                            last_capture[j]   <= capture_timer[j];
                            capture_timer[j]  <= 28'd0;  // restart counter
                            ch_valid[j]       <= 1'b1;
                            irq_rpm_o         <= 1'b1;
                        end
                    end else begin
                        // Decrement filter counter when no edge
                        if (glitch_filter[j] > 3'd0)
                            glitch_filter[j] <= glitch_filter[j] - 3'd1;
                    end
                end
            end else begin
                // Disabled: reset all capture state
                for (j = 0; j < 4; j = j + 1) begin
                    capture_timer[j] <= 28'd0;
                    last_capture[j]  <= 28'd0;
                    capture_sync[j]  <= 2'd0;
                    capture_edge[j]  <= 1'b0;
                    glitch_filter[j] <= 3'd0;
                end
                ch_valid <= 4'd0;
            end
        end
    end

endmodule
