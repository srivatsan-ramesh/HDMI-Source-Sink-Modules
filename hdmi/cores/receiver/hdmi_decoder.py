from myhdl import block, Signal, concat, always_comb, always, intbv, instances, ConcatSignal

from hdmi.cores.primitives import buffer_ds, buffer_io, buffer, pll_clock_generator, pll_buffer
from hdmi.cores.receiver import decode


@block
def hdmi_decoder(ext_reset, hdmi_interface, video_interface, aux_interface, simulation=True):

    p_clock, p_clockx2, p_clockx10, pll_clock_0, pll_clock_1, pll_clock_2, \
        pll_locked, serdes_strobe, tmds_clock, blue_valid, green_valid, red_valid, \
        blue_ready, green_ready, red_ready, phase_align_err, reset = [Signal(False) for _ in range(17)]

    s_data_out = Signal(intbv(0)[30:0])

    s_data_out_red, s_data_out_green, s_data_out_blue = [Signal(intbv(0)[10:0]) for _ in range(3)]

    @always_comb
    def data_out():
        s_data_out.next = concat(s_data_out_red[10:5], s_data_out_green[10:5], s_data_out_blue[10:5],
                                 s_data_out_red[5:0], s_data_out_green[5:0], s_data_out_blue[5:0])

    vde_r, vde_g, vde_b, ade_r, ade_g, ade_b = [Signal(False) for _ in range(6)]

    @always_comb
    def assign_de():
        video_interface.vde.next = vde_r
        aux_interface.ade.next = ade_r

    blue_c0, blue_c1, control0, control1, control2, control3 = [Signal(False) for _ in range(6)]

    @always_comb
    def assign_sync():
        video_interface.hsync.next = aux_interface.aux0[0] if ade_b else blue_c0
        video_interface.vsync.next = aux_interface.aux0[1] if ade_b else blue_c1

    control = ConcatSignal(control0, control1, control2, control3)
    video_preamble, data_island_preamble = [Signal(False) for _ in range(2)]

    @always(p_clock.posedge)
    def assign_preamble():
        video_preamble.next = 1 if control == 8 else 0
        data_island_preamble.next = 1 if control == 10 else 0

    blue_phase_align_err, green_phase_align_err, red_phase_align_err = [Signal(False) for _ in range(3)]
    rx_clock, rx_clock_int = [Signal(False) for _ in range(2)]

    ibuf_rx_clock = buffer_ds(hdmi_interface.TMDS_CLK_P, hdmi_interface.TMDS_CLK_N, rx_clock_int)
    bufio_tmds_clock = buffer_io(rx_clock_int, rx_clock)
    tmds_clock_bufg = buffer(rx_clock, tmds_clock)

    pll_clock_feedback = Signal(False)

    pll_iserdes = pll_clock_generator(pll_clock_feedback, pll_clock_0, pll_clock_1, pll_clock_2,
                                      pll_locked, pll_clock_feedback, rx_clock, ext_reset)

    p_clock_bufg = buffer(pll_clock_1, p_clock)
    p_clockx2_bufg = buffer(pll_clock_2, p_clockx2)

    buf_pll_lock = Signal(False)
    io_clock_buf = pll_buffer(pll_clock_0, p_clockx2, pll_locked, p_clockx10, serdes_strobe, buf_pll_lock)

    @always_comb
    def assign_reset():
        reset.next = not buf_pll_lock

    decode_b = decode(reset, p_clock, p_clockx2, p_clockx10, serdes_strobe,
                      hdmi_interface.TMDS_B_P, hdmi_interface.TMDS_B_N, green_valid, red_valid,
                      green_ready, red_ready, video_preamble, data_island_preamble, blue_ready, blue_valid,
                      blue_phase_align_err, blue_c0, blue_c1, vde_b, ade_b, s_data_out_blue,
                      video_interface.blue, aux_interface.aux0, 'BLUE', simulation)

    decode_g = decode(reset, p_clock, p_clockx2, p_clockx10, serdes_strobe,
                      hdmi_interface.TMDS_G_P, hdmi_interface.TMDS_G_N, blue_valid, red_valid,
                      blue_ready, red_ready, video_preamble, data_island_preamble, green_ready, green_valid,
                      green_phase_align_err, control0, control1, vde_g, ade_g, s_data_out_green,
                      video_interface.green, aux_interface.aux1, 'GREEN', simulation)

    decode_r = decode(reset, p_clock, p_clockx2, p_clockx10, serdes_strobe,
                      hdmi_interface.TMDS_R_P, hdmi_interface.TMDS_R_N, blue_valid, green_valid,
                      blue_ready, green_ready, video_preamble, data_island_preamble, red_ready, red_valid,
                      red_phase_align_err, control2, control3, vde_r, ade_r, s_data_out_red,
                      video_interface.red, aux_interface.aux2, 'RED', simulation)

    @always_comb
    def phase_error():
        phase_align_err.next = red_phase_align_err or green_phase_align_err or blue_phase_align_err

    return instances()
