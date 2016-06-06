from myhdl import block

inst_count = 0


@block
def pll_buffer(pll_in, g_clock, locked, io_clock, serdes_strobe, lock, divide=5):
    global inst_count
    # TODO complete function definition
    inst_count += 1

pll_buffer.verilog_code = """
    BUFPLL #(.DIVIDE($divide)) pll_buf_$inst_count (.PLLIN($pll_in), .GCLK($g_clock), .LOCKED($locked),
           .IOCLK($io_clock), .SERDESSTROBE($serdes_strobe), .LOCK($lock));
"""
