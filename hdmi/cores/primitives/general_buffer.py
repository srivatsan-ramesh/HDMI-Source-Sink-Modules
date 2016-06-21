from myhdl import block, always_comb

inst_count = 0


@block
def buffer(inp, output):
    global inst_count

    @always_comb
    def BUFG_primitive():
        output.next = inp

    inst_count += 1

    return BUFG_primitive


buffer.verilog_code = """
    BUFG bufg_$inst_count (.I($inp), .O($output));
"""
