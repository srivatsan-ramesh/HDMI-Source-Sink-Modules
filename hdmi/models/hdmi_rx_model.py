from myhdl import Signal, always_comb, intbv, always, ConcatSignal, instance, traceSignals

from hdmi.models import DecoderModel


class HDMIRxModel:

    def __init__(self, video_interface, aux_interface, hdmi_interface):
        self.video_interface = video_interface
        self.aux_interface = aux_interface
        self.hdmi_interface = hdmi_interface

    def process(self):
        red = Signal(intbv(0)[10:0])
        green = Signal(intbv(0)[10:0])
        blue = Signal(intbv(0)[10:0])

        video_preamble = Signal(bool(0))
        data_island_preamble = Signal(bool(0))

        red_decoder = DecoderModel(self.hdmi_interface.TMDS_CLK_P, red, video_preamble, data_island_preamble,
                                   video_out=self.video_interface.red,
                                   audio_out=self.aux_interface.aux2, channel='RED')
        green_decoder = DecoderModel(self.hdmi_interface.TMDS_CLK_P, green, video_preamble, data_island_preamble,
                                     video_out=self.video_interface.green,
                                     audio_out=self.aux_interface.aux1, channel='GREEN')
        blue_decoder = DecoderModel(self.hdmi_interface.TMDS_CLK_P, blue, video_preamble, data_island_preamble,
                                    video_out=self.video_interface.blue,
                                    audio_out=self.aux_interface.aux0, channel='BLUE')

        @always_comb
        def continuous_assignment():
            self.video_interface.vde.next = red_decoder.vde
            self.aux_interface.ade.next = red_decoder.ade
            self.video_interface.hsync.next = self.aux_interface.aux0[0] if blue_decoder.ade else blue_decoder.c0
            self.video_interface.vsync.next = self.aux_interface.aux0[1] if blue_decoder.ade else blue_decoder.c1

        @always(self.hdmi_interface.TMDS_CLK_P.posedge)
        def sequential():
            control = ConcatSignal(green_decoder.c0, green_decoder.c1, red_decoder.c0, red_decoder.c1)
            video_preamble.next = 1 if control == int('1000', 2) else 0
            data_island_preamble.next = 1 if control == int('1010', 2) else 0

        @instance
        def deserialize():
            while True:
                red_list = []
                green_list = []
                blue_list = []
                for _ in range(10):
                    yield self.hdmi_interface.read_data()
                    data = self.hdmi_interface.get_TMDS_data()
                    red_list.append('1' if data[0] else '0')
                    green_list.append('1' if data[1] else '0')
                    blue_list.append('1' if data[2] else '0')
                red_decoder.data_in.next = int(''.join(red_list[::-1]), 2)
                green_decoder.data_in.next = int(''.join(green_list[::-1]), 2)
                blue_decoder.data_in.next = int(''.join(blue_list[::-1]), 2)

        return continuous_assignment, sequential, deserialize, \
            red_decoder.process(), green_decoder.process(), blue_decoder.process()
