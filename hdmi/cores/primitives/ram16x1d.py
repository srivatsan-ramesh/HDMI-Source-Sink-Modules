from myhdl import block, Signal, intbv, always_comb, always


@block
def ram16x1d(data_in, write_enable, clock, address, dual_port_address,
             single_port_output, dual_port_output, data_width):

    """

    A RAM of 16 bit width modelled with a list of signals.

    Args:
        data_in: The input data
        write_enable: write enable
        clock: write clock
        address: single port address
        dual_port_address: dual port address
        single_port_output: single port output
        dual_port_output: dual port output
        data_width: Number of 16bit words stored.

    Returns:
        myhdl.instances() : A list of myhdl instances.

    """

    mem = [Signal(intbv(0)[16:0]) for _ in range(data_width)]

    @always_comb
    def assign():
        for i in range(data_width):
            single_port_output.next[i] = mem[i][address]
            dual_port_output.next[i] = mem[i][dual_port_address]

    @always(clock.posedge)
    def seq_logic():
        if write_enable:
            for i in range(data_width):
                mem[i].next[address] = data_in[i]

    return assign, seq_logic
