from myhdl import Signal, intbv, always_seq, always, always_comb, ConcatSignal

from hdmi.cores.transmitter import serdes_n_to_1, encode, convert_30_to_15


def hdmi_encoder(p_clock, p_clockx2, p_clockx10, serdes_strobe, reset,
                 video_interface, aux_interface, hdmi_interface):

    control0, control1, control2, control3 = [Signal(bool(0)) for _ in range(4)]

    @always_comb
    def assign_control():

        if video_interface.vde: # video_preamble
            control0.next, control1.next, control2.next, control3.next = 1, 0, 0, 0
        elif aux_interface.ade: # data_island_preamble
            control0.next, control1.next, control2.next, control3.next = 1, 0, 1, 0
        else:   # null_control
            control0.next, control1.next, control2.next, control3.next = 0, 0, 0, 0

    red = Signal(intbv(0)[10:0])
    green = Signal(intbv(0)[10:0])
    blue = Signal(intbv(0)[10:0])

    tmds_data0, tmds_data1, tmds_data2 = [Signal(intbv(0)[5:0]) for _ in range(3)]

    tmds_init0, tmds_init1, tmds_init2, tmds_init3 = [Signal(bool(0)) for _ in range(4)]

    tmds_clock_init = Signal(intbv(0)[5:0])

    toggle = Signal(bool(0))

    @always_seq(p_clockx2.posedge, reset)
    def toggle_toggle():

        toggle.next = not toggle

    @always(p_clockx2.posedge)
    def init_tmds_clock():

        if toggle:
            tmds_clock_init.next = 31 # int('11111', 2)
        else:
            tmds_clock_init.next = 0

    tmds_clock = Signal(bool(0))

    clock_out = serdes_n_to_1(p_clockx10, serdes_strobe, reset, p_clockx2, tmds_clock_init, tmds_clock, 5)
    oserdes0 = serdes_n_to_1(p_clockx10, serdes_strobe, reset, p_clockx2, tmds_data0, tmds_init0)
    oserdes1 = serdes_n_to_1(p_clockx10, serdes_strobe, reset, p_clockx2, tmds_data1, tmds_init1)
    oserdes2 = serdes_n_to_1(p_clockx10, serdes_strobe, reset, p_clockx2, tmds_data2, tmds_init2)

    @always_comb
    def OBUFDS():
        hdmi_interface.TMDS_B_P.next = tmds_init0
        hdmi_interface.TMDS_B_N.next = not tmds_init0
        hdmi_interface.TMDS_G_P.next = tmds_init1
        hdmi_interface.TMDS_G_N.next = not tmds_init1
        hdmi_interface.TMDS_R_P.next = tmds_init2
        hdmi_interface.TMDS_R_N.next = not tmds_init2
        hdmi_interface.TMDS_CLK_P.next = tmds_init3
        hdmi_interface.TMDS_CLK_N.next = not tmds_init3

    encode_b = encode(p_clock, reset, video_interface.blue, aux_interface.aux0, video_interface.hsync,
                      video_interface.vsync, video_interface.vde, aux_interface.ade, blue, 'BLUE')
    encode_g = encode(p_clock, reset, video_interface.green, aux_interface.aux1, control0,
                      control1, video_interface.vde, aux_interface.ade, green, 'GREEN')
    encode_r = encode(p_clock, reset, video_interface.red, aux_interface.aux2, control2,
                      control3, video_interface.vde, aux_interface.ade, red, 'RED')

    s_data = Signal(intbv(0)[30:0])
    s_data = ConcatSignal(red[10:5], green[10:5], blue[10:5],
                          red[5:0], green[5:0], blue[5:0])

    pixel2x = convert_30_to_15(reset, p_clock, p_clockx2, s_data, tmds_data2, tmds_data1, tmds_data0)

    return assign_control, toggle_toggle, init_tmds_clock, \
           clock_out, oserdes0, oserdes1, oserdes2, \
           OBUFDS, encode_b,encode_g, encode_r, pixel2x
