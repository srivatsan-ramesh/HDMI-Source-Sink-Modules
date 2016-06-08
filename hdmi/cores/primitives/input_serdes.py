from myhdl import block


@block
def cascaded_iserdes(data_in_master, data_in_slave, clock_0, io_ce, reset, clock_div, pd_edge,
                     cascade, bit_slip, valid_data, incdec_data, data_out, bit_slip_enable):
    # TODO complete function definition
    pass

cascaded_iserdes.verilog_code = """
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
  .D                ($data_in_master),
  .CE0              (1'b1),
  .CLK0             ($clock_0),
  .CLK1             (1'b0),
  .IOCE             ($io_ce),
  .RST              ($reset),
  .CLKDIV           ($clock_div),
  .SHIFTIN          ($pd_edge),
  .BITSLIP          ($bit_slip),
  .FABRICOUT        (),
  .Q4               ($data_out[4]),
  .Q3               ($data_out[3]),
  .Q2               ($data_out[2]),
  .Q1               ($data_out[1]),
  .DFB              (),
  .CFB0             (),
  .CFB1             (),
  .VALID            ($valid_data),
  .INCDEC           ($incdec_data),
  .SHIFTOUT         ($cascade));

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
  .D                ($data_in_slave),
  .CE0              (1'b1),
  .CLK0             ($clock_0),
  .CLK1             (1'b0),
  .IOCE             ($io_ce),
  .RST              ($reset),
  .CLKDIV           ($clock_div),
  .SHIFTIN          ($cascade),
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
  .SHIFTOUT         ($pd_edge));

"""
