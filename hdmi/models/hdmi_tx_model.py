from myhdl import Signal, always, always_comb, intbv, instance, traceSignals, block

from hdmi.models import EncoderModel


class HDMITxModel:
    def __init__(self, clock, clock5x, clock5x_not, reset, video_interface, aux_interface, hdmi_interface):

        self.clock = clock
        self.clock5x = clock5x
        self.clock5x_not = clock5x_not
        self.reset = reset
        self.video_interface = video_interface
        self.aux_interface = aux_interface
        self.hdmi_interface = hdmi_interface

    @block
    def process(self):

        data_island_preamble = (1, 0, 1, 0)
        video_preamble = (1, 0, 0, 0)
        null_control = (0, 0, 0, 0)

        _vde = [Signal(bool(0)) for _ in range(10)]
        _ade = [Signal(bool(0)) for _ in range(10)]

        _hsync = [Signal(bool(0)) for _ in range(10)]
        _vsync = [Signal(bool(0)) for _ in range(10)]

        _red = [Signal(intbv(0)[self.video_interface.color_depth[0]:]) for _ in range(10)]
        _green = [Signal(intbv(0)[self.video_interface.color_depth[1]:]) for _ in range(10)]
        _blue = [Signal(intbv(0)[self.video_interface.color_depth[2]:]) for _ in range(10)]

        _aux0 = [Signal(intbv(0)[self.aux_interface.aux_depth[0]:]) for _ in range(10)]
        _aux1 = [Signal(intbv(0)[self.aux_interface.aux_depth[1]:]) for _ in range(10)]
        _aux2 = [Signal(intbv(0)[self.aux_interface.aux_depth[2]:]) for _ in range(10)]

        blue_encoder = EncoderModel(self.clock, self.reset, _blue[9], _aux0[9],
                                    vde=_vde[9], ade=_ade[9], c0=_hsync[9], c1=_vsync[9], channel='BLUE')

        green_encoder = EncoderModel(self.clock, self.reset, _green[9], _aux1[9],
                                     vde=_vde[9], ade=_ade[9], channel='GREEN')

        red_encoder = EncoderModel(self.clock, self.reset, _red[9], _aux2[9],
                                   vde=_vde[9], ade=_ade[9], channel='RED')

        blue_encoder_inst = blue_encoder.process()
        blue_encoder_inst.name = 'blue_encoder'
        green_encoder_inst = green_encoder.process()
        green_encoder_inst.name = 'green_encoder'
        red_encoder_inst = red_encoder.process()
        red_encoder_inst.name = 'red_encoder'

        @always(self.clock.posedge)
        def serial_delay():

            _red[0].next = self.video_interface.red
            _green[0].next = self.video_interface.green
            _blue[0].next = self.video_interface.blue

            _aux0[0].next = self.aux_interface.aux0
            _aux1[0].next = self.aux_interface.aux1
            _aux2[0].next = self.aux_interface.aux2

            _vde[0].next = self.video_interface.vde
            _ade[0].next = self.aux_interface.ade

            _hsync[0].next = self.video_interface.hsync
            _vsync[0].next = self.video_interface.vsync

            for i in range(1, 10):
                _red[i].next = _red[i-1]
                _green[i].next = _green[i-1]
                _blue[i].next = _blue[i-1]

                _aux0[i].next = _aux0[i-1]
                _aux1[i].next = _aux1[i-1]
                _aux2[i].next = _aux2[i-1]

                _vde[i].next = _vde[i-1]
                _ade[i].next = _ade[i-1]

                _hsync[i].next = _hsync[i-1]
                _vsync[i].next = _vsync[i-1]

            if self.video_interface.vde:
                green_encoder.c0.next, green_encoder.c1.next, red_encoder.c0.next, red_encoder.c1.next = video_preamble
            elif self.aux_interface.ade:
                green_encoder.c0.next, green_encoder.c1.next, red_encoder.c0.next, red_encoder.c1.next = \
                    data_island_preamble
            else:
                green_encoder.c0.next, green_encoder.c1.next, red_encoder.c0.next, red_encoder.c1.next = null_control

        @instance
        def serialize():
            while True:
                for i in range(10):
                    yield self.hdmi_interface.write_data(red_encoder.data_out[i],
                                                         green_encoder.data_out[i],
                                                         blue_encoder.data_out[i],
                                                         self.clock)

        return serial_delay, serialize, \
            blue_encoder_inst, green_encoder_inst, red_encoder_inst
