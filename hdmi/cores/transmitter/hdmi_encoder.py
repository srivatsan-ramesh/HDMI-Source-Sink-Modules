from myhdl import Signal, intbv, always_seq, always, always_comb, ConcatSignal, block, instances

from hdmi.cores.transmitter import serdes_n_to_1, encode, convert_30_to_15


@block
def hdmi_encoder(p_clock, p_clockx2, p_clockx10, reset, serdes_strobe,
                 video_interface, aux_interface, hdmi_interface):

    control0, control1, control2, control3 = [Signal(bool(0)) for _ in range(4)]

    @always_comb
    def assign_control():

        if video_interface.vde:     # video_preamble
            control0.next, control1.next, control2.next, control3.next = 1, 0, 0, 0
        elif aux_interface.ade:     # data_island_preamble
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
            tmds_clock_init.next = 31   # int('11111', 2)
        else:
            tmds_clock_init.next = 0

    clock_out = serdes_n_to_1(p_clockx10, serdes_strobe, reset, p_clockx2, tmds_clock_init, tmds_init3, 5)
    oserdes0 = serdes_n_to_1(p_clockx10, serdes_strobe, reset, p_clockx2, tmds_data0, tmds_init0, 5)
    oserdes1 = serdes_n_to_1(p_clockx10, serdes_strobe, reset, p_clockx2, tmds_data1, tmds_init1, 5)
    oserdes2 = serdes_n_to_1(p_clockx10, serdes_strobe, reset, p_clockx2, tmds_data2, tmds_init2, 5)

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

    # A list of signals used to delay vde and ade by 10 clock cycles
    _vde = [Signal(bool(0)) for _ in range(10)]
    _ade = [Signal(bool(0)) for _ in range(10)]

    # A list of signals used to delay hsync and vsync by 10 clock cycles
    _hsync = [Signal(bool(0)) for _ in range(10)]
    _vsync = [Signal(bool(0)) for _ in range(10)]

    # # A list of signals used to delay red, green, blue by 10 clock cycles
    _red = [Signal(intbv(0)[video_interface.color_depth[0]:]) for _ in range(10)]
    _green = [Signal(intbv(0)[video_interface.color_depth[1]:]) for _ in range(10)]
    _blue = [Signal(intbv(0)[video_interface.color_depth[2]:]) for _ in range(10)]

    # A list of signals used to delay aux signal by 10 clock cycles
    _aux0 = [Signal(intbv(0)[aux_interface.aux_depth[0]:]) for _ in range(10)]
    _aux1 = [Signal(intbv(0)[aux_interface.aux_depth[1]:]) for _ in range(10)]
    _aux2 = [Signal(intbv(0)[aux_interface.aux_depth[2]:]) for _ in range(10)]

    @always(p_clock.posedge)
    def serial_delay():

        _red[0].next = video_interface.red
        _green[0].next = video_interface.green
        _blue[0].next = video_interface.blue

        _aux0[0].next = aux_interface.aux0
        _aux1[0].next = aux_interface.aux1
        _aux2[0].next = aux_interface.aux2

        _vde[0].next = video_interface.vde
        _ade[0].next = aux_interface.ade

        _hsync[0].next = video_interface.hsync
        _vsync[0].next = video_interface.vsync

        for i in range(1, 10):
            _red[i].next = _red[i - 1]
            _green[i].next = _green[i - 1]
            _blue[i].next = _blue[i - 1]

            _aux0[i].next = _aux0[i - 1]
            _aux1[i].next = _aux1[i - 1]
            _aux2[i].next = _aux2[i - 1]

            _vde[i].next = _vde[i - 1]
            _ade[i].next = _ade[i - 1]

            _hsync[i].next = _hsync[i - 1]
            _vsync[i].next = _vsync[i - 1]

    encode_b = encode(p_clock, reset, _blue[9], _aux0[9], _hsync[9],
                      _vsync[9], _vde[9], _ade[9], blue, 'BLUE')
    encode_g = encode(p_clock, reset, _green[9], _aux1[9], control0,
                      control1, _vde[9], _ade[9], green, 'GREEN')
    encode_r = encode(p_clock, reset, _red[9], _aux2[9], control2,
                      control3, _vde[9], _ade[9], red, 'RED')

    s_data = ConcatSignal(red(10, 5), green(10, 5), blue(10, 5),
                          red(5, 0), green(5, 0), blue(5,0))

    pixel2x = convert_30_to_15(reset, p_clock, p_clockx2, s_data, tmds_data2, tmds_data1, tmds_data0)

    return instances()
