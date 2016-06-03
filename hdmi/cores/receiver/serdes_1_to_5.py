from myhdl import block


@block
def serdes_1_to_5(use_phase_detector, data_in_p, data_in_n, rx_io_clock,
                  rx_serdes_strobe, reset, g_clock, bit_slip, data_out,
                  diff_term='FALSE', bit_slip_enable='TRUE'):

    pass