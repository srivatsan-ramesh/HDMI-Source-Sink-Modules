from myhdl import block, Signal, intbv, ConcatSignal


@block
def serdes_n_to_1(io_clock, serdes_strobe, reset, g_clock, data_in, iob_data_out, factor=8):

    cascade_di, cascade_do, cascade_ti, cascade_to = [Signal(bool(0)) for _ in range(4)]
    mdata_in = Signal(intbv(0)[9:0])

    ones_data_in = [Signal(bool(1)) for _ in range(factor - 8)] + [data_in]

    mdata_in = ConcatSignal(*ones_data_in)
