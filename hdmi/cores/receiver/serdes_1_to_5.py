from myhdl import block, Signal, modbv, intbv, always, instance


@block
def serdes_1_to_5(use_phase_detector, data_in_p, data_in_n, rx_io_clock,
                  rx_serdes_strobe, reset, g_clock, bit_slip, data_out,
                  diff_term='TRUE', bit_slip_enable='TRUE', sim_tap_delay = 49):

    data = ['0' for _ in range(5)]

    @instance
    def deserialize():
        while True:
            yield rx_io_clock.posedge
            # print('rx : ', self.hdmi_interface.get_TMDS_data(), now())
            data.append('1' if data_in_p else '0')
            data.pop(0)

    @instance
    def assign():
        while True:
            yield g_clock.posedge
            data_out.next = int(''.join(data), 2)

    return deserialize, assign


serdes_1_to_5.verilog_code = """
  wire       ddly_m;
  wire       ddly_s;
  wire       busys;
  wire       rx_data_in;
  wire       cascade;
  wire       pd_edge;
  reg  [8:0] counter;
  reg  [3:0] state;
  reg        cal_data_sint;
  wire       busy_data;
  reg        busy_data_d;
  wire       cal_data_slave;
  reg        enable;
  reg        cal_data_master;
  reg        rst_data;
  reg        inc_data_int;
  wire       inc_data;
  reg        ce_data;
  reg        valid_data_d;
  reg        incdec_data_d;
  reg  [4:0] pdcounter;
  wire       valid_data;
  wire       incdec_data;
  reg        flag;
  reg        mux;
  reg        ce_data_inta ;
  wire [1:0] incdec_data_or;
  wire       incdec_data_im;
  wire [1:0] valid_data_or;
  wire       valid_data_im;
  wire [1:0] busy_data_or;
  wire       all_ce;

  wire [1:0] debug_in = 2'b00;

  assign busy_data = busys ;

  assign cal_data_slave = cal_data_sint ;

  /////////////////////////////////////////////////
  //
  // IDELAY Calibration FSM
  //
  /////////////////////////////////////////////////
  always @ (posedge $g_clock or posedge $reset)
  begin
  if ($reset == 1'b1) begin
    state <= 0 ;
    cal_data_master <= 1'b0 ;
    cal_data_sint <= 1'b0 ;
    counter <= 9'h000 ;
    enable <= 1'b0 ;
    mux <= 1'h1 ;
  end
  else begin
      counter <= counter + 9'h001 ;
      if (counter[8] == 1'b1) begin
      counter <= 9'h000 ;
      end
      if (counter[5] == 1'b1) begin
      enable <= 1'b1 ;
      end
      if (state == 0 && enable == 1'b1) begin       // Wait for IODELAY to be available
      cal_data_master <= 1'b0 ;
      cal_data_sint <= 1'b0 ;
      rst_data <= 1'b0 ;
        if (busy_data_d == 1'b0) begin
        state <= 1 ;
      end
      end
      else if (state == 1) begin          // Issue calibrate command to both master and slave, needed for simulation, not for the silicon
        cal_data_master <= 1'b1 ;
        cal_data_sint <= 1'b1 ;
        if (busy_data_d == 1'b1) begin        // and wait for command to be accepted
          state <= 2 ;
        end
      end
      else if (state == 2) begin          // Now RST master and slave IODELAYs needed for simulation, not for the silicon
        cal_data_master <= 1'b0 ;
        cal_data_sint <= 1'b0 ;
        if (busy_data_d == 1'b0) begin
          rst_data <= 1'b1 ;
          state <= 3 ;
        end
      end
      else if (state == 3) begin          // Wait for IODELAY to be available
        rst_data <= 1'b0 ;
        if (busy_data_d == 1'b0) begin
          state <= 4 ;
        end
      end
      else if (state == 4) begin          // Wait for occasional enable
        if (counter[8] == 1'b1) begin
          state <= 5 ;
        end
        end
        else if (state == 5) begin          // Calibrate slave only
        if (busy_data_d == 1'b0) begin
          cal_data_sint <= 1'b1 ;
          state <= 6 ;
        end
      end
        else if (state == 6) begin          // Wait for command to be accepted
        cal_data_sint <= 1'b0 ;
        if (busy_data_d == 1'b1) begin
          state <= 7 ;
        end
      end
      else if (state == 7) begin          // Wait for all IODELAYs to be available, ie CAL command finished
          cal_data_sint <= 1'b0 ;
        if (busy_data_d == 1'b0) begin
          state <= 4 ;
        end
      end
  end
  end

always @ (posedge $g_clock or posedge $reset)        // Per-bit phase detection state machine
begin
if ($reset == 1'b1) begin
  pdcounter <= 5'b1000 ;
  ce_data_inta <= 1'b0 ;
  flag <= 1'b0 ;              // flag is there to only allow one inc or dec per cal (test)
end
else begin
  busy_data_d <= busy_data_or[1] ;
    if ($use_phase_detector == 1'b1) begin       // decide whther pd is used
    incdec_data_d <= incdec_data_or[1] ;
    valid_data_d <= valid_data_or[1] ;
    if (ce_data_inta == 1'b1) begin
      ce_data = mux ;
    end
    else begin
      ce_data = 64'h0000000000000000 ;
    end
      if (state == 7) begin
      flag <= 1'b0 ;
    end
      else if (state != 4 || busy_data_d == 1'b1) begin // Reset filter if state machine issues a cal command or unit is busy
      pdcounter <= 5'b10000 ;
        ce_data_inta <= 1'b0 ;
      end
      else if (pdcounter == 5'b11111 && flag == 1'b0) begin // Filter has reached positive max - increment the tap count
        ce_data_inta <= 1'b1 ;
        inc_data_int <= 1'b1 ;
      pdcounter <= 5'b10000 ;
      flag <= 1'b1 ;
    end
        else if (pdcounter == 5'b00000 && flag == 1'b0) begin // Filter has reached negative max - decrement the tap count
        ce_data_inta <= 1'b1 ;
        inc_data_int <= 1'b0 ;
      pdcounter <= 5'b10000 ;
      flag <= 1'b1 ;
      end
    else if (valid_data_d == 1'b1) begin      // increment filter
        ce_data_inta <= 1'b0 ;
      if (incdec_data_d == 1'b1 && pdcounter != 5'b11111) begin
        pdcounter <= pdcounter + 5'b00001 ;
      end
      else if (incdec_data_d == 1'b0 && pdcounter != 5'b00000) begin  // decrement filter
        pdcounter <= pdcounter + 5'b11111 ;
      end
      end
      else begin
        ce_data_inta <= 1'b0 ;
      end
    end
    else begin
    ce_data = all_ce ;
    inc_data_int = debug_in[1] ;
    end
end
end

assign inc_data = inc_data_int ;

assign incdec_data_or[0] = 1'b0 ;             // Input Mux - Initialise generate loop OR gates
assign valid_data_or[0] = 1'b0 ;
assign busy_data_or[0] = 1'b0 ;

assign incdec_data_im = incdec_data & mux;          // Input muxes
assign incdec_data_or[1] = incdec_data_im | incdec_data_or;      // AND gates to allow just one signal through at a tome
assign valid_data_im = valid_data & mux;          // followed by an OR
assign valid_data_or[1] = valid_data_im | valid_data_or;     // for the three inputs from each PD
assign busy_data_or[1] = busy_data | busy_data_or;       // The busy signals just need an OR gate

assign all_ce = debug_in[0] ;

IBUFDS #(
  .DIFF_TERM    ("$diff_term"))
data_in (
  .I            ($data_in_p),
  .IB           ($data_in_n),
  .O            (rx_data_in)
);

//
// Master IDELAY
//
IODELAY2 #(
  .DATA_RATE            ("SDR"),
  .IDELAY_VALUE         (0),
  .IDELAY2_VALUE        (0),
  .IDELAY_MODE          ("NORMAL" ),
  .ODELAY_VALUE         (0),
  .IDELAY_TYPE          ("DIFF_PHASE_DETECTOR"),
  .COUNTER_WRAPAROUND   ("STAY_AT_LIMIT"), //("WRAPAROUND"),
  .DELAY_SRC            ("IDATAIN"),
  .SERDES_MODE          ("MASTER"),
  .SIM_TAPDELAY_VALUE   ($sim_tap_delay)
) iodelay_m (
  .IDATAIN              (rx_data_in),      // data from IBUFDS
  .TOUT                 (),                // tri-state signal to IOB
  .DOUT                 (),                // output data to IOB
  .T                    (1'b1),            // tri-state control from OLOGIC/OSERDES2
  .ODATAIN              (1'b0),            // data from OLOGIC/OSERDES2
  .DATAOUT              (ddly_m),          // Output data 1 to ILOGIC/ISERDES2
  .DATAOUT2             (),                // Output data 2 to ILOGIC/ISERDES2
  .IOCLK0               ($rx_io_clock),    // High speed clock for calibration
  .IOCLK1               (1'b0),            // High speed clock for calibration
  .CLK                  ($g_clock),            // Fabric clock (GCLK) for control signals
  .CAL                  (cal_data_master), // Calibrate control signal
  .INC                  (inc_data),        // Increment counter
  .CE                   (ce_data),         // Clock Enable
  .RST                  (rst_data),        // Reset delay line
  .BUSY                 ()                 // output signal indicating sync circuit has finished / calibration has finished
);

//
// Slave IDELAY
//
IODELAY2 #(
  .DATA_RATE            ("SDR"),
  .IDELAY_VALUE         (0),
  .IDELAY2_VALUE        (0),
  .IDELAY_MODE          ("NORMAL" ),
  .ODELAY_VALUE         (0),
  .IDELAY_TYPE          ("DIFF_PHASE_DETECTOR"),
  .COUNTER_WRAPAROUND   ("WRAPAROUND"),
  .DELAY_SRC            ("IDATAIN"),
  .SERDES_MODE          ("SLAVE"),
  .SIM_TAPDELAY_VALUE   ($sim_tap_delay)
) iodelay_s (
  .IDATAIN              (rx_data_in),  // data from IBUFDS
  .TOUT                 (),            // tri-state signal to IOB
  .DOUT                 (),            // output data to IOB
  .T                    (1'b1),        // tri-state control from OLOGIC/OSERDES2
  .ODATAIN              (1'b0),        // data from OLOGIC/OSERDES2
  .DATAOUT              (ddly_s),      // Slave output data to ILOGIC/ISERDES2
  .DATAOUT2             (),            //
  .IOCLK0               ($rx_io_clock),     // High speed IO clock for calibration
  .IOCLK1               (1'b0),
  .CLK                  ($g_clock),        // Fabric clock (GCLK) for control signals
  .CAL                  (cal_data_slave), // Calibrate control signal
  .INC                  (inc_data),       // Increment counter
  .CE                   (ce_data),        // Clock Enable
  .RST                  (rst_data),       // Reset delay line
  .BUSY                 (busys)        // output signal indicating sync circuit has finished / calibration has finished
);

//
// Master ISERDES
//

ISERDES2 #(
  .DATA_WIDTH       (5),
  .DATA_RATE        ("SDR"),
  .BITSLIP_ENABLE   ("$bit_slip_enable"),
  .SERDES_MODE      ("MASTER"),
  .INTERFACE_TYPE   ("RETIMED"))
iserdes_m (
  .D                (ddly_m),
  .CE0              (1'b1),
  .CLK0             ($rx_io_clock),
  .CLK1             (1'b0),
  .IOCE             ($rx_serdes_strobe),
  .RST              ($reset),
  .CLKDIV           ($g_clock),
  .SHIFTIN          (pd_edge),
  .BITSLIP          ($bit_slip),
  .FABRICOUT        (),
  .Q4               ($data_out[4]),
  .Q3               ($data_out[3]),
  .Q2               ($data_out[2]),
  .Q1               ($data_out[1]),
  .DFB              (),
  .CFB0             (),
  .CFB1             (),
  .VALID            (valid_data),
  .INCDEC           (incdec_data),
  .SHIFTOUT         (cascade));

//
// Slave ISERDES
//

ISERDES2 #(
  .DATA_WIDTH       (5),
  .DATA_RATE        ("SDR"),
  .BITSLIP_ENABLE   ("$bit_slip_enable"),
  .SERDES_MODE      ("SLAVE"),
  .INTERFACE_TYPE   ("RETIMED")
) iserdes_s (
  .D                (ddly_s),
  .CE0              (1'b1),
  .CLK0             ($rx_io_clock),
  .CLK1             (1'b0),
  .IOCE             ($rx_serdes_strobe),
  .RST              ($reset),
  .CLKDIV           ($g_clock),
  .SHIFTIN          (cascade),
  .BITSLIP          ($bit_slip),
  .FABRICOUT        (),
  .Q4               ($data_out[0]),
  .Q3               (),
  .Q2               (),
  .Q1               (),
  .DFB              (),
  .CFB0             (),
  .CFB1             (),
  .VALID            (),
  .INCDEC           (),
  .SHIFTOUT         (pd_edge));


reg [7:0] rxpdcntr = 8'h7f;
always @ (posedge $g_clock or posedge $reset) begin
  if ($reset)
    rxpdcntr <= 8'h7f;
  else if (ce_data)
    if (inc_data)
      rxpdcntr <= rxpdcntr + 1'b1;
    else
      rxpdcntr <= rxpdcntr - 1'b1;
end
"""