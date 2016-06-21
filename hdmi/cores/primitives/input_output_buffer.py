from myhdl import block, always_comb

inst_count = 0


@block
def buffer_io(inp, output):

    global inst_count

    @always_comb
    def BUFIO2_primitive():
        output.next = inp

    inst_count += 1

    return BUFIO2_primitive

buffer_io.verilog_code = """
    BUFIO2 #(.DIVIDE_BYPASS("TRUE"), .DIVIDE(1))
    bufio_$inst_count (.DIVCLK($output), .IOCLK(), .SERDESSTROBE(), .I($inp));
"""