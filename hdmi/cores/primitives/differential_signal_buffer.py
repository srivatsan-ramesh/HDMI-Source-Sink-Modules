from myhdl import block, always_comb

inst_count = 0


@block
def buffer_ds(input_p, input_n, output, diff_term='FALSE'):

    """

    This is a Differential Signalling Buffer modelled after the xilinx primitive IBUFDS.
    This block will be replaced by the xilinx primitive declaration during conversion.

    Args:
        input_p: Positive differential signal
        input_n: Negative differential signal
        output: Output signal derived from the inputs
        diff_term: A parameter used in the xilinx primitive

    Returns:
        myhdl.instances() : A list of myhdl instances.

    """

    global inst_count

    @always_comb
    def IBUFDS_primitive():
        if input_p and not input_n:
            output.next = 1
        elif not input_p and input_n:
            output.next = 0

    inst_count += 1

    return IBUFDS_primitive

buffer_ds.verilog_code = """
    IBUFDS  #(.IOSTANDARD("TMDS_33"), .DIFF_TERM($diff_term)) ibuf_$inst_count (.I($input_p), .IB($input_n), .O($output));
"""