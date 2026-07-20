// =========================================================================
// Module: dshot_pwm
// Description: DShot 300 frame generator for 4 ESC channels + 2 standard PWM
//              channels with prescaler. Wishbone B4 slave interface.
//
// Source: IP-010 v4 Architecture §4.7, CREATE
// Clock: 16.67 MHz (60 ns tick)
//
// Register Map (offsets from base 0x8000_5000):
//   0x00 THROTTLE0_NEXT  R/W  DShot ch0 next throttle [10:0]
//   0x04 THROTTLE1_NEXT  R/W  DShot ch1 next throttle [10:0]
//   0x08 THROTTLE2_NEXT  R/W  DShot ch2 next throttle [10:0]
//   0x0C THROTTLE3_NEXT  R/W  DShot ch3 next throttle [10:0]
//   0x10 TELEMETRY       R/W  Telemetry request bits [3:0]
//   0x14 COMMIT          W    Atomic copy NEXT→active
//   0x18 PWM0_DUTY       R/W  PWM ch4 duty (ticks, prescaled)
//   0x1C PWM0_PERIOD     R/W  PWM ch4 period (ticks, default 0x5161)
//   0x20 PWM1_DUTY       R/W  PWM ch5 duty (ticks, prescaled)
//   0x24 PWM1_PERIOD     R/W  PWM ch5 period (ticks, default 0x5161)
//   0x28 STATUS          R    bit[0]=update pending, bit[1]=frame active
//   0x2C CTRL            R/W  bit[0]=DShot en, bit[1]=PWM en, bit[2]=auto-commit, bit[4:3]=PWM prescaler
//
// DShot 300 timing (16.67 MHz, 60 ns tick):
//   Bit period = 55 ticks (3333 ns). Spec: 3333 ns ±2%.
//   T0H = 21 ticks (1260 ns), T0L = 34 ticks (2040 ns)
//   T1H = 42 ticks (2520 ns), T1L = 13 ticks (780 ns)
//   CRC-4 polynomial: 0x1D (x^4+x^3+x^2+1) over 12-bit payload
//
// PWM prescaler (CTRL[4:3]): 00=/1, 01=/4, 10=/16, 11=/64
//   Default: /16 → 20 ms = 333,333/16 = 20,833 ticks = 0x5161
// =========================================================================

module dshot_pwm (
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

    // DShot outputs
    output reg  [ 3:0] dshot_out_o,

    // Standard PWM outputs
    output reg  [ 1:0] pwm_out_o,

    // Interrupt
    output reg         irq_update_o
);

    // -----------------------------------------------------------------
    // DShot 300 timing parameters (16.67 MHz clock → 60 ns tick)
    // -----------------------------------------------------------------
    localparam DSHOT_BIT_PERIOD = 8'd55;
    localparam DSHOT_T0H_TICKS  = 8'd21;
    localparam DSHOT_T0L_TICKS  = 8'd34;
    localparam DSHOT_T1H_TICKS  = 8'd42;
    localparam DSHOT_T1L_TICKS  = 8'd13;

    // -----------------------------------------------------------------
    // FSM states
    // -----------------------------------------------------------------
    localparam [2:0]
        FSM_IDLE    = 3'd0,
        FSM_BIT_HI  = 3'd1,
        FSM_BIT_LO  = 3'd2;

    // -----------------------------------------------------------------
    // Registers
    // -----------------------------------------------------------------
    reg [10:0] throttle_next [0:3];
    reg [10:0] throttle_act  [0:3];
    reg [ 3:0] telemetry_req;
    reg [15:0] pwm_duty   [0:1];
    reg [15:0] pwm_period [0:1];
    reg        ctrl_dshot_en;
    reg        ctrl_pwm_en;
    reg        ctrl_auto_commit;
    reg [ 1:0] pwm_prescaler;

    // -----------------------------------------------------------------
    // CRC-4 generator (polynomial 0x1D = x^4+x^3+x^2+1)
    // Combinational — 1 cycle latency
    // -----------------------------------------------------------------
    function [3:0] crc4_calc;
        input [11:0] data;
        reg [3:0] crc;
        integer i;
        begin
            crc = 4'h0;
            for (i = 11; i >= 0; i = i - 1) begin
                crc = {crc[2:0], 1'b0} ^ ((crc[3] ^ data[i]) ? 4'hD : 4'h0);
            end
            crc4_calc = crc;
        end
    endfunction

    // -----------------------------------------------------------------
    // DShot frame generator state
    // -----------------------------------------------------------------
    reg [ 2:0] dshot_state     [0:3];
    reg [ 7:0] dshot_timer     [0:3];
    reg [ 3:0] dshot_bit_cnt   [0:3];
    reg [15:0] dshot_frame     [0:3];
    reg [ 1:0] dshot_ch_sel;
    reg        dshot_frame_active;
    reg        dshot_update_pending;
    reg [ 3:0] dshot_out_reg;

    // -----------------------------------------------------------------
    // PWM generators with prescaler
    // -----------------------------------------------------------------
    reg [15:0] pwm_counter [0:1];
    reg [ 5:0] pwm_prescale_cnt [0:1];
    reg        pwm_prescale_tick [0:1];

    // -----------------------------------------------------------------
    // Wishbone register access + DShot FSM + PWM (single always block)
    // -----------------------------------------------------------------
    wire wb_valid = wb_cyc_i && wb_stb_i;
    wire [5:0] wb_offset = wb_adr_i[5:0];

    integer i, j;

    always @(posedge wb_clk_i or negedge wb_rst_ni) begin
        if (!wb_rst_ni) begin
            // Reset all registers
            for (i = 0; i < 4; i = i + 1) throttle_next[i] <= 11'd0;
            for (i = 0; i < 4; i = i + 1) throttle_act[i]  <= 11'd0;
            telemetry_req     <= 4'd0;
            for (i = 0; i < 2; i = i + 1) pwm_duty[i]   <= 16'd0;
            pwm_period[0]     <= 16'h5161;  // 20,833 ticks (20ms @ /16 prescaler)
            pwm_period[1]     <= 16'h5161;
            ctrl_dshot_en     <= 1'b0;
            ctrl_pwm_en       <= 1'b0;
            ctrl_auto_commit  <= 1'b0;
            pwm_prescaler     <= 2'b10;     // /16 default
            wb_ack_o          <= 1'b0;
            wb_err_o          <= 1'b0;
            wb_dat_o          <= 32'd0;
            dshot_update_pending <= 1'b0;
            dshot_frame_active   <= 1'b0;
            dshot_out_reg        <= 4'd0;
            dshot_ch_sel         <= 2'd0;
            irq_update_o         <= 1'b0;
            for (i = 0; i < 4; i = i + 1) begin
                dshot_state[i]   <= FSM_IDLE;
                dshot_timer[i]   <= 8'd0;
                dshot_bit_cnt[i] <= 4'd0;
                dshot_frame[i]   <= 16'd0;
            end
            for (i = 0; i < 2; i = i + 1) begin
                pwm_counter[i]      <= 16'd0;
                pwm_prescale_cnt[i] <= 6'd0;
                pwm_prescale_tick[i]<= 1'b0;
            end
            pwm_out_o   <= 2'b00;
            dshot_out_o <= 4'd0;
        end else begin
            // Defaults
            wb_ack_o <= 1'b0;
            wb_err_o <= 1'b0;
            irq_update_o <= 1'b0;

            // ---------------------------------------------------------
            // Wishbone register access
            // ---------------------------------------------------------
            if (wb_valid && !wb_ack_o) begin
                wb_ack_o <= 1'b1;
                if (wb_we_i) begin
                    // Write
                    case (wb_offset)
                        6'h00: throttle_next[0] <= wb_dat_i[10:0];
                        6'h04: throttle_next[1] <= wb_dat_i[10:0];
                        6'h08: throttle_next[2] <= wb_dat_i[10:0];
                        6'h0C: throttle_next[3] <= wb_dat_i[10:0];
                        6'h10: telemetry_req     <= wb_dat_i[3:0];
                        6'h14: begin
                            // COMMIT — atomic copy NEXT→active
                            if (ctrl_dshot_en) begin
                                for (j = 0; j < 4; j = j + 1)
                                    throttle_act[j] <= throttle_next[j];
                                dshot_update_pending <= 1'b1;
                            end
                        end
                        6'h18: pwm_duty[0]   <= wb_dat_i[15:0];
                        6'h1C: pwm_period[0] <= wb_dat_i[15:0];
                        6'h20: pwm_duty[1]   <= wb_dat_i[15:0];
                        6'h24: pwm_period[1] <= wb_dat_i[15:0];
                        6'h2C: begin
                            ctrl_dshot_en    <= wb_dat_i[0];
                            ctrl_pwm_en      <= wb_dat_i[1];
                            ctrl_auto_commit <= wb_dat_i[2];
                            pwm_prescaler    <= wb_dat_i[4:3];
                        end
                        default: wb_err_o <= 1'b1;
                    endcase
                end else begin
                    // Read
                    case (wb_offset)
                        6'h00: wb_dat_o <= {21'd0, throttle_next[0]};
                        6'h04: wb_dat_o <= {21'd0, throttle_next[1]};
                        6'h08: wb_dat_o <= {21'd0, throttle_next[2]};
                        6'h0C: wb_dat_o <= {21'd0, throttle_next[3]};
                        6'h10: wb_dat_o <= {28'd0, telemetry_req};
                        6'h14: wb_dat_o <= 32'd0; // COMMIT is write-only
                        6'h18: wb_dat_o <= {16'd0, pwm_duty[0]};
                        6'h1C: wb_dat_o <= {16'd0, pwm_period[0]};
                        6'h20: wb_dat_o <= {16'd0, pwm_duty[1]};
                        6'h24: wb_dat_o <= {16'd0, pwm_period[1]};
                        6'h28: wb_dat_o <= {30'd0, dshot_update_pending, dshot_frame_active};
                        6'h2C: wb_dat_o <= {26'd0, pwm_prescaler, 1'b0, ctrl_auto_commit, ctrl_pwm_en, ctrl_dshot_en};
                        default: begin wb_dat_o <= 32'd0; wb_err_o <= 1'b1; end
                    endcase
                end
            end

            // ---------------------------------------------------------
            // PWM prescaler ticks
            // ---------------------------------------------------------
            for (j = 0; j < 2; j = j + 1) begin
                pwm_prescale_tick[j] <= 1'b0;
                if (ctrl_pwm_en) begin
                    case (pwm_prescaler)
                        2'b00: pwm_prescale_tick[j] <= 1'b1;       // /1
                        2'b01: begin  // /4
                            if (pwm_prescale_cnt[j] == 6'd3) begin
                                pwm_prescale_tick[j] <= 1'b1;
                                pwm_prescale_cnt[j]  <= 6'd0;
                            end else begin
                                pwm_prescale_cnt[j] <= pwm_prescale_cnt[j] + 6'd1;
                            end
                        end
                        2'b10: begin  // /16
                            if (pwm_prescale_cnt[j] == 6'd15) begin
                                pwm_prescale_tick[j] <= 1'b1;
                                pwm_prescale_cnt[j]  <= 6'd0;
                            end else begin
                                pwm_prescale_cnt[j] <= pwm_prescale_cnt[j] + 6'd1;
                            end
                        end
                        2'b11: begin  // /64
                            if (pwm_prescale_cnt[j] == 6'd63) begin
                                pwm_prescale_tick[j] <= 1'b1;
                                pwm_prescale_cnt[j]  <= 6'd0;
                            end else begin
                                pwm_prescale_cnt[j] <= pwm_prescale_cnt[j] + 6'd1;
                            end
                        end
                    endcase
                end
            end

            // ---------------------------------------------------------
            // PWM generators (channels 4-5)
            // ---------------------------------------------------------
            for (j = 0; j < 2; j = j + 1) begin
                if (ctrl_pwm_en && pwm_prescale_tick[j]) begin
                    if (pwm_counter[j] >= pwm_period[j]) begin
                        pwm_counter[j] <= 16'd0;
                        pwm_out_o[j]   <= 1'b0;  // rollover: start LOW
                    end else begin
                        pwm_counter[j] <= pwm_counter[j] + 16'd1;
                        // Glitch-free: duty loaded at rollover boundary
                        if (pwm_counter[j] < pwm_duty[j])
                            pwm_out_o[j] <= 1'b1;
                        else
                            pwm_out_o[j] <= 1'b0;
                    end
                end else if (!ctrl_pwm_en) begin
                    pwm_out_o[j]   <= 1'b0;
                    pwm_counter[j] <= 16'd0;
                    pwm_prescale_cnt[j] <= 6'd0;
                end
            end

            // ---------------------------------------------------------
            // DShot frame generator (channels 0-3)
            // ---------------------------------------------------------
            if (ctrl_dshot_en && dshot_update_pending && !dshot_frame_active) begin
                // Start new frame sequence for channel 0
                dshot_frame_active <= 1'b1;
                dshot_ch_sel       <= 2'd0;
                // Build frame for channel 0
                dshot_frame[0] <= {throttle_act[0], telemetry_req[0], crc4_calc({throttle_act[0], telemetry_req[0]})};
                dshot_state[0]   <= FSM_BIT_HI;
                dshot_timer[0]   <= 8'd0;
                dshot_bit_cnt[0] <= 4'd15;
                dshot_out_reg[0] <= 1'b1;  // start with HIGH
            end

            if (dshot_frame_active) begin
                // Process current channel's DShot FSM
                case (dshot_state[dshot_ch_sel])
                    FSM_BIT_HI: begin
                        dshot_timer[dshot_ch_sel] <= dshot_timer[dshot_ch_sel] + 8'd1;
                        dshot_out_reg[dshot_ch_sel] <= 1'b1;

                        // Determine T1H or T0H based on current bit
                        if (dshot_frame[dshot_ch_sel][dshot_bit_cnt[dshot_ch_sel]] == 1'b1) begin
                            if (dshot_timer[dshot_ch_sel] == DSHOT_T1H_TICKS - 1) begin
                                dshot_state[dshot_ch_sel] <= FSM_BIT_LO;
                                dshot_timer[dshot_ch_sel] <= 8'd0;
                            end
                        end else begin
                            if (dshot_timer[dshot_ch_sel] == DSHOT_T0H_TICKS - 1) begin
                                dshot_state[dshot_ch_sel] <= FSM_BIT_LO;
                                dshot_timer[dshot_ch_sel] <= 8'd0;
                            end
                        end
                    end

                    FSM_BIT_LO: begin
                        dshot_timer[dshot_ch_sel] <= dshot_timer[dshot_ch_sel] + 8'd1;
                        dshot_out_reg[dshot_ch_sel] <= 1'b0;

                        if (dshot_frame[dshot_ch_sel][dshot_bit_cnt[dshot_ch_sel]] == 1'b1) begin
                            if (dshot_timer[dshot_ch_sel] == DSHOT_T1L_TICKS - 1) begin
                                // Bit complete
                                if (dshot_bit_cnt[dshot_ch_sel] == 4'd0) begin
                                    // Frame complete for this channel
                                    dshot_state[dshot_ch_sel] <= FSM_IDLE;
                                    dshot_out_reg[dshot_ch_sel] <= 1'b0;

                                    // Move to next channel or finish
                                    if (dshot_ch_sel == 2'd3) begin
                                        // All 4 channels done
                                        dshot_frame_active <= 1'b0;
                                        dshot_update_pending <= 1'b0;
                                        irq_update_o <= 1'b1;

                                        // Auto-commit: latch new values if available
                                        if (ctrl_auto_commit) begin
                                            for (j = 0; j < 4; j = j + 1)
                                                throttle_act[j] <= throttle_next[j];
                                            dshot_update_pending <= 1'b1;
                                        end
                                    end else begin
                                        // Start next channel
                                        dshot_ch_sel <= dshot_ch_sel + 2'd1;
                                        dshot_frame[dshot_ch_sel + 2'd1] <= {throttle_act[dshot_ch_sel + 2'd1],
                                            telemetry_req[dshot_ch_sel + 2'd1],
                                            crc4_calc({throttle_act[dshot_ch_sel + 2'd1], telemetry_req[dshot_ch_sel + 2'd1]})};
                                        dshot_state[dshot_ch_sel + 2'd1] <= FSM_BIT_HI;
                                        dshot_bit_cnt[dshot_ch_sel + 2'd1] <= 4'd15;
                                        dshot_timer[dshot_ch_sel + 2'd1] <= 8'd0;
                                    end
                                end else begin
                                    // Next bit
                                    dshot_bit_cnt[dshot_ch_sel] <= dshot_bit_cnt[dshot_ch_sel] - 4'd1;
                                    dshot_state[dshot_ch_sel] <= FSM_BIT_HI;
                                    dshot_timer[dshot_ch_sel] <= 8'd0;
                                end
                            end
                        end else begin
                            if (dshot_timer[dshot_ch_sel] == DSHOT_T0L_TICKS - 1) begin
                                if (dshot_bit_cnt[dshot_ch_sel] == 4'd0) begin
                                    dshot_state[dshot_ch_sel] <= FSM_IDLE;
                                    dshot_out_reg[dshot_ch_sel] <= 1'b0;

                                    if (dshot_ch_sel == 2'd3) begin
                                        dshot_frame_active <= 1'b0;
                                        dshot_update_pending <= 1'b0;
                                        irq_update_o <= 1'b1;
                                        if (ctrl_auto_commit) begin
                                            for (j = 0; j < 4; j = j + 1)
                                                throttle_act[j] <= throttle_next[j];
                                            dshot_update_pending <= 1'b1;
                                        end
                                    end else begin
                                        dshot_ch_sel <= dshot_ch_sel + 2'd1;
                                        dshot_frame[dshot_ch_sel + 2'd1] <= {throttle_act[dshot_ch_sel + 2'd1],
                                            telemetry_req[dshot_ch_sel + 2'd1],
                                            crc4_calc({throttle_act[dshot_ch_sel + 2'd1], telemetry_req[dshot_ch_sel + 2'd1]})};
                                        dshot_state[dshot_ch_sel + 2'd1] <= FSM_BIT_HI;
                                        dshot_bit_cnt[dshot_ch_sel + 2'd1] <= 4'd15;
                                        dshot_timer[dshot_ch_sel + 2'd1] <= 8'd0;
                                    end
                                end else begin
                                    dshot_bit_cnt[dshot_ch_sel] <= dshot_bit_cnt[dshot_ch_sel] - 4'd1;
                                    dshot_state[dshot_ch_sel] <= FSM_BIT_HI;
                                    dshot_timer[dshot_ch_sel] <= 8'd0;
                                end
                            end
                        end
                    end

                    default: begin
                        // FSM_IDLE — wait for next frame trigger
                        dshot_out_reg[dshot_ch_sel] <= 1'b0;
                        dshot_timer[dshot_ch_sel] <= 8'd0;
                    end
                endcase
            end else begin
                // No frame active: all DShot outputs low
                dshot_out_reg <= 4'd0;
            end

            // Drive external outputs
            dshot_out_o <= dshot_out_reg;
        end
    end

endmodule
