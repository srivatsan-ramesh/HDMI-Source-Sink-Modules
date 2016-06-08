from myhdl import block


@block
def cascaded_io_delay(data_in, data_out_master, data_out_slave, io_clock_0, clock, calibration_master,
                      calibration_slave, inc_data, ce_data, reset_data, busy, sim_tap_delay):
    # TODO complete function definition
    pass

cascaded_io_delay.verilog_code = """
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
  .COUNTER_WRAPAROUND   ("STAY_AT_LIMIT"),
  .DELAY_SRC            ("IDATAIN"),
  .SERDES_MODE          ("MASTER"),
  .SIM_TAPDELAY_VALUE   ($sim_tap_delay)
) iodelay_m (
  .IDATAIN              ($data_in),            // data from IBUFDS
  .TOUT                 (),                    // tri-state signal to IOB
  .DOUT                 (),                    // output data to IOB
  .T                    (1'b1),                // tri-state control from OLOGIC/OSERDES2
  .ODATAIN              (1'b0),                // data from OLOGIC/OSERDES2
  .DATAOUT              ($data_out_master),    // Output data 1 to ILOGIC/ISERDES2
  .DATAOUT2             (),                    // Output data 2 to ILOGIC/ISERDES2
  .IOCLK0               ($io_clock_0),         // High speed clock for calibration
  .IOCLK1               (1'b0),                // High speed clock for calibration
  .CLK                  ($clock),              // Fabric clock (GCLK) for control signals
  .CAL                  ($calibration_master), // Calibrate control signal
  .INC                  ($inc_data),           // Increment counter
  .CE                   ($ce_data),            // Clock Enable
  .RST                  ($reset_data),         // Reset delay line
  .BUSY                 ()                     // output signal indicating sync circuit has finished / calibration has finished
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
  .IDATAIN              ($data_in),           // data from IBUFDS
  .TOUT                 (),                   // tri-state signal to IOB
  .DOUT                 (),                   // output data to IOB
  .T                    (1'b1),               // tri-state control from OLOGIC/OSERDES2
  .ODATAIN              (1'b0),               // data from OLOGIC/OSERDES2
  .DATAOUT              ($data_out_slave),             // Slave output data to ILOGIC/ISERDES2
  .DATAOUT2             (),                   //
  .IOCLK0               ($io_clock_0),        // High speed IO clock for calibration
  .IOCLK1               (1'b0),
  .CLK                  ($clock),             // Fabric clock (GCLK) for control signals
  .CAL                  ($calibration_slave), // Calibrate control signal
  .INC                  ($inc_data),          // Increment counter
  .CE                   ($ce_data),           // Clock Enable
  .RST                  ($reset_data),        // Reset delay line
  .BUSY                 ($busy)               // output signal indicating sync circuit has finished / calibration has finished
);
"""